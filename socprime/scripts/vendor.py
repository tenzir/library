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
(HoS) rules, and the Active Threats. Name new HoS rules in `HOS_NAMES` below,
and list rules that the `sigma` operator cannot evaluate on OCSF in
`UNSUPPORTED`.
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

_PS_SCRIPT = "Uses `ScriptBlockText` without `category: ps_script`."

# Rules that cannot run on OCSF, with the reason. The `sigma` operator maps the
# standard Sigma taxonomy only, not vendor variants of it. The HoS rules leave
# these rules out, so that their stages only count rules that can fire.
UNSUPPORTED = {
    "ce152116-1d05-408a-a1a7-a4091528dc74": _PS_SCRIPT,
    "4ab60adc-7117-4f20-80de-77ecf2a1ef99": _PS_SCRIPT,
    "93ec52aa-776a-4976-8209-bc68321c75b7": _PS_SCRIPT,
    "0c128c4f-9323-4e7a-9e46-cff7c51f6b92": _PS_SCRIPT,
    "991bc36f-3348-4aeb-868a-380294c7fd36": _PS_SCRIPT,
    "ca5427f8-ede3-48df-b98c-5fa254010b2a": _PS_SCRIPT,
    "42e2973c-cf5e-47fa-b0e6-e73792578684": _PS_SCRIPT,
    "309111d8-89ad-4c98-a799-10053a40bd0a": _PS_SCRIPT,
    "4586d131-5d2a-4582-b028-a5841eea1d35": "Uses the Sysmon field `QueryName` in a generic `dns` rule instead of `query`.",
    "a8d99db6-5f54-4b53-a600-0bca8bec3884": "Uses the non-standard field `dns_query_name` instead of `query`.",
    "63f2ae8a-6912-4ea9-ad2c-369f4555a549": "Uses `DestinationHostname`, which DNS queries do not have, instead of `QueryName`.",
    "ac652c9a-dd0b-11ec-9d64-0242ac120002": "Uses raw auditd fields that OCSF Process Activity does not preserve.",
    "c135e89f-a9e5-4cbe-a86c-a25ffa674f1a": "Uses the scheduled task XML in `TaskContent`, which OCSF does not preserve.",
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
        items = [
            f"{pad}  {k if k.isidentifier() else json.dumps(k)}: {tql(v, indent + 1)},"
            for k, v in value.items()
        ]
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
    unsupported = []
    skipped = []
    for key, stage in rule["detection"].items():
        if not key.startswith("seq"):
            continue
        stage_lines = []
        for uid in stage["ruleid|contains"]:
            if uid not in by_uid:
                warn(f"HoS {rule['id']} references missing rule {uid}")
                stage_lines.append(f'        // "{uid}", // Missing from the snapshot.')
            elif uid in UNSUPPORTED:
                stage_lines.append(f'        // "{uid}", // {by_uid[uid]["name"]}: Cannot run on OCSF.')
                unsupported.append(uid)
            else:
                stage_lines.append(f'        "{uid}", // {by_uid[uid]["name"]}')
                rules.append(uid)
        if any(not line.lstrip().startswith("//") for line in stage_lines):
            lines += [f"      {key}: [", *stage_lines, "      ],"]
        else:
            # A stage without runnable rules can never be covered.
            skipped.append(key)
            lines += [f"      // {key}: No rule of this stage can run on OCSF.", *[
                f"      {line.strip()}" for line in stage_lines
            ]]
    lines += [
        "    },",
        f"    rules: {tql(list(dict.fromkeys(rules)), 2)},",
        f"    unsupported: {tql(list(dict.fromkeys(unsupported)), 2)},",
        f"    skipped_stages: {tql(skipped, 2)},",
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
        "// The Sigma rules that cannot run on OCSF, with the reason.",
        f"let $unsupported = {tql(UNSUPPORTED)}",
        "",
        "// The SOC Prime High-Order Sigma rules, keyed by name. `stages` maps",
        "// every stage to the Sigma rule IDs that cover it on OCSF, and `rules`",
        "// lists all of them. `unsupported` lists the stage rules that cannot",
        "// run on OCSF, and `skipped_stages` the stages without runnable rules,",
        "// which the HoS rule leaves out.",
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
