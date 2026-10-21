# Exercise both detection examples' file sources, parsing, Sigma matching, and
# file sinks. Enrichment needs a node and is covered by the catalog/enrichment
# suites; omit only that operator here so the I/O regression test is node-free.
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

package = Path(os.environ["TENZIR_PACKAGE_ROOT"])
readme = (package / "README.md").read_text()
changelog = package / "changelog/unreleased/truepattern-detection-rules.md"
rule_id = "00000000-0000-4000-8000-000000000001"
rule = f"""title: Synthetic file detection
id: {rule_id}
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    CommandLine: whoami /all
  condition: selection
level: low
"""
ocsf = {
    "metadata": {"version": "1.9.0", "product": {"name": "Synthetic EDR"}},
    "category_uid": 1,
    "class_uid": 1007,
    "activity_id": 1,
    "type_uid": 100701,
    "device": {"os": {"type_id": 100}},
    "process": {"cmd_line": "whoami /all"},
}
# Reuse the native event already covered by the Windows rule tests.
windows_test = (package / "tests/windows/03-detect.tql").read_text()
xml = windows_test.split('r#"', 1)[1].split('"#', 1)[0] + "\n"
cases = [
    ("ocsf", "detect-with-sigma-rules.tql", "/var/log/ocsf/events.ndjson",
     json.dumps(ocsf) + "\n", "sigma.yaml"),
    ("windows", "detect-in-windows-event-logs.tql", "/var/log/windows/events.xml",
     xml, "sigma-windows.yaml"),
]
with TemporaryDirectory(prefix="truepattern-detection-files-") as directory:
    root = Path(directory)
    executor = Executor.from_env(os.environ)
    for name, filename, input_path, content, rule_file in cases:
        example = (package / "examples" / filename).read_text().split("---", 2)[2]
        # Strip comments for comparisons with the user-facing snippets.
        pipeline = "\n".join(
            line for line in example.splitlines() if not line.startswith("//")
        ).strip()
        assert pipeline in readme, f"README example drifted: {filename}"
        # Released notes are historical snapshots, not current examples.
        if name == "ocsf" and changelog.exists():
            assert pipeline in changelog.read_text(), "Unreleased changelog example drifted"
        source = root / Path(input_path).name
        # Include a nonmatching event to check that only findings reach the sink.
        source.write_text(content + content.replace("whoami /all", "hostname"))
        (root / rule_file).write_text(rule)
        pipeline = pipeline.replace(input_path, str(source))
        pipeline = pipeline.replace("/var/lib/tenzir/truepattern/", f"{root}/")
        assert pipeline.count("truepattern::enrich\n") == 1
        pipeline = pipeline.replace("truepattern::enrich\n", "")
        for run in range(1, 3):
            result = executor.run(pipeline)
            assert result.returncode == 0, result.stderr.decode()
            assert not result.stderr, result.stderr.decode()
            assert not result.stdout, result.stdout.decode()
            findings = [
                json.loads(line)
                for path in (root / "findings").glob(f"{name}-*.ndjson")
                for line in path.read_text().splitlines()
            ]
            assert len(findings) == run, findings
            for finding in findings:
                assert finding["class_uid"] == 2004, finding
                assert finding["finding_info"]["analytic"]["uid"] == rule_id, finding
                event = finding["evidences"][0]["data"]
                command = event["process"]["cmd_line"] if name == "ocsf" else event["CommandLine"]
                assert command == "whoami /all", event
        print(f"{name}: file input, Sigma match, file output; repeated runs preserved")
print("README and any unreleased changelog snippet: consistent with the examples")
