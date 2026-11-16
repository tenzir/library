#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Vendors a SOC Prime detection content snapshot into the package.

The snapshot is the `detection_content` directory of
https://github.com/socprime/detectflow-backend. Run from the package root:

    scripts/vendor.py /path/to/detectflow-backend/detection_content

The script writes `constants.tql` with the Sigma rules, the High-Order Sigma
(HoS) rules, and the Active Threats. Name new HoS rules in `HOS_NAMES` below.
"""

import datetime
import json
import pathlib
import sys

import yaml

PACKAGE = pathlib.Path(__file__).resolve().parent.parent

# Names of the HoS rules, keyed by TDM ID.
HOS_NAMES = {
    "r0LqNjnpT21W": "kimsuky_diplomats",
    "Zk2Qr9RO5Dth": "remcos_purchase_order",
    "YAXTrTrvQXoi": "gamaredon",
    "gTSmKZquRCYV": "uac_0247",
    "p6ndiutIHfyH": "janaware",
    "jhP5r9lpFLqg": "node2shell",
    "Riwu9NconRzw": "php2shell",
    "UfhULfdvVPtu": "n8n_abuse",
    "JVLEu7LOwbcg": "dragon_boss",
    "knjkfvZHX16t": "windows_privesc_persistence",
}


def warn(message):
    print(f"warning: {message}", file=sys.stderr)
    return False


def tql(value, indent=0):
    """Renders a Python value as a TQL literal."""
    pad = "  " * indent
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, datetime.datetime):
        return value.astimezone(datetime.UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        if not value:
            return "[]"
        items = [f"{pad}  {tql(v, indent + 1)}," for v in value]
        return "[\n" + "\n".join(items) + f"\n{pad}]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        items = [f"{pad}  {k}: {tql(v, indent + 1)}," for k, v in value.items()]
        return "{\n" + "\n".join(items) + f"\n{pad}}}"
    raise TypeError(f"unsupported value: {value!r}")


def duration(text):
    units = {"s": "s", "m": "min", "h": "h", "d": "d"}
    return text[:-1] + units[text[-1]]


def load(directory):
    return [yaml.safe_load(f.read_text()) for f in sorted(directory.glob("*.yml"))]


def hos_constant(name, rule, by_uid):
    """Renders one HoS rule as an entry of `$hos`, with rule titles as comments."""
    lines = [
        f"  {name}: {{",
        f'    uid: "{rule["id"]}",',
        f"    name: {json.dumps(rule['title'], ensure_ascii=False)},",
        f'    level: "{rule["level"]}",',
        f"    timeframe: {duration(rule['detection']['timeframe'])},",
        f"    tags: {tql(rule.get('tags') or [], 2)},",
        "    stages: {",
    ]
    rules = []
    for key, stage in rule["detection"].items():
        if not key.startswith("seq"):
            continue
        lines.append(f"      {key}: [")
        for uid in stage["ruleid|contains"]:
            if uid in by_uid:
                lines.append(f'        "{uid}", // {by_uid[uid]["name"]}')
                rules.append(uid)
            else:
                warn(f"HoS {rule['id']} references missing rule {uid}")
                lines.append(f'        // "{uid}", // Missing from the snapshot.')
        lines.append("      ],")
    lines += [
        "    },",
        f"    rules: {tql(list(dict.fromkeys(rules)), 2)},",
        "  },",
    ]
    return lines, rules


def main(snapshot):
    snapshot = pathlib.Path(snapshot)
    version = (snapshot / "VERSION").read_text().strip()
    # Sigma rules, keyed by their TDM ID.
    rules = {}
    for item in load(snapshot / "rules"):
        body = item["body"].strip() + "\n"
        assert '"#' not in body, f"rule {item['id']} breaks the raw string"
        rule = yaml.safe_load(body)
        rules[item["id"]] = {"uid": rule["id"], "name": rule["title"], "body": body}
    by_uid = {r["uid"]: r for r in rules.values()}
    # HoS rules, keyed by their TDM ID.
    hos = {}
    hos_lines = []
    for item in load(snapshot / "hos"):
        rule = yaml.safe_load(item["body"])
        lines, stage_rules = hos_constant(HOS_NAMES[item["id"]], rule, by_uid)
        hos[item["id"]] = {"uid": rule["id"], "name": rule["title"], "rules": stage_rules}
        hos_lines.append((HOS_NAMES[item["id"]], lines))
    # Active Threats with resolved rule references.
    threats = []
    for item in load(snapshot / "active_threats"):
        behavior = [
            rules[i]["uid"]
            for i in item.get("related_behavioral_rules") or []
            if i in rules or warn(f"Active Threat {item['id']} references missing rule {i}")
        ]
        related_hos = [
            hos[i]
            for i in item.get("related_high_order_sigma_rules") or []
            if i in hos or warn(f"Active Threat {item['id']} references missing HoS {i}")
        ]
        stage_rules = [uid for h in related_hos for uid in h["rules"]]
        threats.append(
            {
                "id": item["id"],
                "name": item["name"],
                "created": datetime.datetime.fromisoformat(item["created"]),
                "updated": datetime.datetime.fromisoformat(item["updated"]),
                "summary": item.get("summary"),
                "severity": item.get("severity"),
                "investigation": item.get("investigation"),
                "response": item.get("response"),
                "mitigation": item.get("mitigation"),
                "attack_flow": item.get("attack_flow"),
                "industries": item.get("industries") or [],
                "geographies": item.get("geographies") or [],
                "threat_types": item.get("threat_types") or [],
                "threat_actors": item.get("threat_actors") or [],
                "techniques": item.get("techniques") or [],
                "high_order_sigma_rules": [
                    {"uid": h["uid"], "name": h["name"]} for h in related_hos
                ],
                # The behavior rules of the threat and the stage rules of its
                # HoS rules.
                "rules": [
                    {"uid": uid, "name": by_uid[uid]["name"]}
                    for uid in dict.fromkeys(behavior + stage_rules)
                ],
            }
        )
    out = [
        "// Generated by scripts/vendor.py from the SOC Prime DetectFlow detection",
        f"// content snapshot {version}. Do not edit by hand.",
        "",
        f'let $version = "{version}"',
        "",
        "// The SOC Prime Sigma rules, keyed by Sigma rule ID.",
        "let $rules = {",
    ]
    for rule in sorted(rules.values(), key=lambda r: r["uid"]):
        out.append(f"  // {rule['name']}")
        out.append(f'  "{rule["uid"]}": r#"{rule["body"]}"#,')
    out += [
        "}",
        "",
        "// The SOC Prime High-Order Sigma rules, keyed by name. `stages` maps",
        "// every stage to the Sigma rule IDs that cover it, `rules` lists all of",
        "// them.",
        "let $hos = {",
    ]
    for _, lines in sorted(hos_lines):
        out += lines
    out += [
        "}",
        "",
        "// The SOC Prime Active Threats. Rule references are Sigma rule IDs.",
        f"let $active_threats = {tql(sorted(threats, key=lambda t: t['id']))}",
        "",
    ]
    (PACKAGE / "constants.tql").write_text("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
