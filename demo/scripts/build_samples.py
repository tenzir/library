"""Rebuild the Zeek and Suricata samples that ship with the package.

Runs both sensors offline over the traffic from make_traffic.py and writes
operators/zeek/sample.tql and operators/suricata/sample.tql. Sensor identifiers
are replaced by deterministic ones, so equal sensor versions give equal files.

    python3 -I build_samples.py [--zeek zeek] [--suricata suricata]
"""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
OPERATORS = HERE.parent / "operators"
ZEEK_LOGS = ("conn", "dhcp", "dns", "files", "http", "smtp", "ssh", "ssl")
SURICATA_CONFIG = """%YAML 1.1
---
vars:
  address-groups: {{HOME_NET: "[10.20.0.0/16]", EXTERNAL_NET: "!$HOME_NET"}}
default-rule-path: {rules}
rule-files: [demo.rules]
classification-file: {classification}
outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      community-id: true
      types: [alert, http, dns, tls, files, smtp, ssh, dhcp, flow]
app-layer:
  protocols:
    http: {{enabled: yes}}
    dns: {{udp: {{enabled: yes, detection-ports: {{dp: 53}}}}, tcp: {{enabled: yes}}}}
    tls: {{enabled: yes}}
    smtp: {{enabled: yes}}
    ssh: {{enabled: yes}}
    dhcp: {{enabled: yes}}
"""
CLASSIFICATION = """config classification: trojan-activity,A Network Trojan was detected, 1
config classification: web-application-attack,Web Application Attack,1
config classification: policy-violation,Potential Corporate Privacy Violation,1
config classification: bad-unknown,Potentially Bad Traffic, 2
"""
TEMPLATE = '''---
description: Emits a small recorded {sensor} sample of invented traffic, one record per event.
---

// Written by scripts/build_samples.py with {version}.
from {{raw: r#"
{lines}
"#}}
raw = raw.trim().split("\\n")
unroll raw
'''


def run(command, **kwargs):
    env = {**os.environ, "TZ": "UTC"}
    return subprocess.run(command, check=True, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True, **kwargs).stdout


def digest(text, length):
    return hashlib.sha256(text.encode()).hexdigest()[:length]


def stamp(text):
    return datetime.datetime.fromisoformat(re.sub(r"\+0000$", "+00:00", text.replace("Z", "+00:00")))


def rename(lines, pattern, make):
    """Replace every distinct match of `pattern` by make(index)."""
    names = {}
    for line in lines:
        for found in re.findall(pattern, line):
            names.setdefault(found, make(len(names)))
    return [re.sub(pattern, lambda m: names[m[0]], line) for line in lines]


def tidy(value):
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, dict):
        return {k: tidy(v) for k, v in value.items()}
    return [tidy(v) for v in value] if isinstance(value, list) else value


def ordered(event):
    """Zeek writes sets in random order."""
    return {k: sorted(v) if k in ("analyzers", "tags") else v for k, v in event.items()}


def zeek(binary, pcap, work):
    (work / "seeds").write_text("".join(f"{i}\n" for i in range(1, 22)))
    run([binary, "-C", "-G", work / "seeds", "-r", pcap, "LogAscii::use_json=T",
         "LogAscii::json_timestamps=JSON::TS_ISO8601",
         "Site::local_nets={10.20.0.0/16}", "Site::private_address_space_is_local=F",
         "policy/frameworks/files/hash-all-files",
         "policy/protocols/conn/community-id-logging"], cwd=work)
    rows = []
    for name in ZEEK_LOGS:
        for line in (work / f"{name}.log").read_text().splitlines():
            event = {"_path": name, **ordered(tidy(json.loads(line)))}
            written = stamp(event["ts"]) + datetime.timedelta(seconds=event.get("duration", 0) or 0)
            rows.append((written, name, event))
    rows.sort(key=lambda r: (r[0], r[1], json.dumps({k: v for k, v in r[2].items() if "uid" not in k})))
    lines = [json.dumps({"_write_ts": w.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), **e}, separators=(",", ":"))
             for w, _, e in rows]
    lines = rename(lines, r'(?<=")C[0-9A-Za-z]{11,17}(?=")', lambda i: "C" + digest(f"uid{i}", 17))
    return rename(lines, r'(?<=")F[0-9A-Za-z]{11,17}(?=")', lambda i: "F" + digest(f"fuid{i}", 17))


def suricata(binary, pcap, work):
    (work / "classification.config").write_text(CLASSIFICATION)
    (work / "suricata.yaml").write_text(SURICATA_CONFIG.format(
        rules=HERE, classification=work / "classification.config"))
    run([binary, "-c", work / "suricata.yaml", "-r", pcap, "-l", work, "-k", "none", "--runmode", "single"])
    events = [json.loads(line) for line in (work / "eve.json").read_text().splitlines()]
    for event in events:
        # Flow records carry the time of the shutdown; write them at flow end.
        if event["event_type"] == "flow":
            event["timestamp"] = event["flow"]["end"]
            event["flow"]["reason"] = "timeout"
    events.sort(key=lambda e: (stamp(e["timestamp"]), e["event_type"], e.get("pcap_cnt", 0),
                               e["src_ip"], e.get("src_port", 0), e.get("tx_id", 0)))
    lines = [json.dumps(e, separators=(",", ":")) for e in events]
    return rename(lines, r'(?<="flow_id":)\d+', lambda i: str(10**14 + int(digest(f"flow{i}", 11), 16)))


def write(sensor, version, lines):
    assert all('"#' not in line and "\x1f" not in line for line in lines)
    target = OPERATORS / sensor.lower() / "sample.tql"
    target.parent.mkdir(exist_ok=True)
    target.write_text(TEMPLATE.format(sensor=sensor, version=version, lines="\n".join(lines)))
    print(f"{target}: {len(lines)} records, {target.stat().st_size} bytes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zeek", default="zeek")
    parser.add_argument("--suricata", default="suricata")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temporary:
        work = pathlib.Path(temporary)
        pcap = work / "traffic.pcap"
        run([sys.executable, "-I", HERE / "make_traffic.py", pcap])
        for sensor, function, binary in (("Zeek", zeek, args.zeek), ("Suricata", suricata, args.suricata)):
            flag = "--version" if sensor == "Zeek" else "-V"
            version = re.search(r"\d+\.\d+\.\d+", run([binary, flag]))[0]
            folder = work / sensor
            folder.mkdir()
            write(sensor, f"{sensor} {version}", function(binary, pcap, folder))


if __name__ == "__main__":
    main()
