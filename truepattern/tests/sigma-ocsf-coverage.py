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
with TemporaryDirectory(prefix="truepattern-coverage-") as directory:
    rules = Path(directory) / "sigma.yaml"
    result = executor.run(
        source
        + f"truepattern::sigma::update_rules path={json.dumps(str(rules))}\ndiscard"
    )
    assert result.returncode == 0, result.stderr.decode()
    for output_format in ("json", "csv"):
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
        if output_format == "json":
            data = json.loads(report.stdout)
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
        else:
            rows = list(csv.DictReader(io.StringIO(report.stdout)))
            assert [row["status"] for row in rows] == [
                "translated",
                "skipped",
                "rejected",
                "translated",
            ], rows
            assert rows[1]["unresolved_fields"] == "Channel NewProcessName", rows[1]
            print("csv: one row per rule")
