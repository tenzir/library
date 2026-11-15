# The coverage report classifies every rule of a file that
# `truepattern::sigma::update_rules` writes by how the `sigma` operator treats
# it on OCSF input, and keeps the TruePattern source reference of each rule.
import csv
import io
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

package = Path(os.environ["TENZIR_PACKAGE_ROOT"])
script = package / "scripts/sigma-ocsf-coverage.py"


def indicator(index, title, body):
    sigma_id = f"00000000-0000-4000-8000-{index:012d}"
    return {
        "type": "indicator",
        "id": f"indicator--{sigma_id}",
        "modified": "2026-09-01T00:00:00Z",
        "pattern_type": "sigma",
        "pattern": f"title: {title}\nid: {sigma_id}\n{body}",
        "external_references": [
            {
                "source_name": "rule-source",
                "url": f"https://example.com/rules/{index}.yml",
            }
        ],
    }


process_creation = "logsource:\n  category: process_creation\n  product: windows\n"
records = [
    indicator(
        1,
        "Synthetic whoami",
        process_creation
        + "detection:\n  selection:\n    Image|endswith: '\\whoami.exe'\n"
        "  condition: selection\n",
    ),
    # Converted rule sets pin the Windows channel, which has no OCSF projection.
    indicator(
        2,
        "Synthetic channel-pinned whoami",
        process_creation
        + "detection:\n  process_creation:\n    EventID: 4688\n    Channel: Security\n"
        "  selection:\n    NewProcessName|endswith: '\\whoami.exe'\n"
        "  condition: process_creation and selection\n",
    ),
    # Placeholders need mappings that the operator does not provide.
    indicator(
        3,
        "Synthetic placeholder",
        process_creation + "detection:\n  selection:\n    User|expand: '%Admins%'\n"
        "  condition: selection\n",
    ),
    indicator(
        4,
        "Synthetic keywords",
        "logsource:\n  product: windows\n  service: security\n"
        "detection:\n  keywords:\n    - 'mimikatz'\n  condition: keywords\n",
    ),
]
source = "from " + ", ".join(json.dumps(record) for record in records) + "\n"
executor = Executor.from_env(os.environ)


def coverage(rules: Path, output_format: str) -> str:
    report = subprocess.run(
        [
            sys.executable,
            str(script),
            str(rules),
            "--tenzir",
            shlex.join(executor.binary),
            "--format",
            output_format,
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    assert report.returncode == 0, report.stderr
    return report.stdout


with TemporaryDirectory(prefix="truepattern-coverage-") as directory:
    rules = Path(directory) / "sigma.yaml"
    result = executor.run(
        source
        + f"truepattern::sigma::update_rules path={json.dumps(str(rules))}\ndiscard"
    )
    assert result.returncode == 0, result.stderr.decode()
    data = json.loads(coverage(rules, "json"))
    assert data["rules"] == len(records), data
    assert data["statuses"] == {
        "translated": 2,
        "skipped": 1,
        "rejected": 1,
        "invalid": 0,
    }, data["statuses"]
    assert data["keywords_only"] == 1, data
    for entry in data["details"]:
        fields = ", ".join(entry["unresolved_fields"]) or "none"
        keywords = " (keywords only)" if entry["keywords_only"] else ""
        print(f"{entry['title']}: {entry['status']}{keywords}")
        print(f"  unresolved fields: {fields}")
        print(f"  rule source: {entry['rule_source']}")
    print(f"unresolved fields: {data['unresolved_fields']}")
    rows = list(csv.DictReader(io.StringIO(coverage(rules, "csv"))))
    assert [row["status"] for row in rows] == [
        "translated",
        "skipped",
        "rejected",
        "translated",
    ], rows
    assert rows[1]["unresolved_fields"] == "Channel NewProcessName", rows[1]
    print("csv: one row per rule")

# Documents that are not Sigma rules become invalid with a reason, and the
# report still covers the valid rules next to them.
valid = (
    "title: Valid\n"
    + process_creation
    + "detection:\n  selection:\n    Image|endswith: '\\whoami.exe'\n"
    "  condition: selection\n"
)
selection = "detection:\n  selection:\n    Image: x\n  condition: selection\n"
malformed = [
    ("Valid", valid, None),
    (
        "Scalar logsource",
        "title: Scalar logsource\nlogsource: windows\n" + selection,
        "logsource",
    ),
    (
        "List logsource",
        "title: List logsource\nlogsource: [windows]\n" + selection,
        "logsource",
    ),
    (
        "Scalar detection",
        "title: Scalar detection\nlogsource:\n  product: windows\ndetection: x\n",
        "detection",
    ),
    (None, "- not\n- a rule\n", None),
]
with TemporaryDirectory(prefix="truepattern-coverage-") as directory:
    rules = Path(directory) / "malformed.yaml"
    rules.write_text("---\n".join(document for _, document, _ in malformed))
    data = json.loads(coverage(rules, "json"))
    assert data["statuses"] == {
        "translated": 1,
        "skipped": 0,
        "rejected": 0,
        "invalid": 4,
    }, data["statuses"]
    for (title, _, attribute), entry in zip(malformed, data["details"], strict=True):
        assert entry["title"] == title, entry
        assert entry["status"] == "translated" or entry["reasons"], entry
        if attribute:
            assert any(attribute in reason for reason in entry["reasons"]), entry
        print(f"{entry['title']}: {entry['status']}")
    assert data["logsources"] == {
        "-/-/-": {"invalid": 4},
        "windows/process_creation/-": {"translated": 1},
    }, data["logsources"]
    rows = list(csv.DictReader(io.StringIO(coverage(rules, "csv"))))
    assert [row["status"] for row in rows] == [
        "translated",
        "invalid",
        "invalid",
        "invalid",
        "invalid",
    ], rows
    assert all(row["product"] == "" for row in rows[1:]), rows
    print("malformed documents: invalid, valid rules still reported")
