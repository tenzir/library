# Exercise the example's routing body with real file input and output.
# Replace the scheduled TAXII source with a deterministic local export and
# redirect output paths; leave the transformations and file sinks unchanged.
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

package = Path(os.environ["TENZIR_PACKAGE_ROOT"])
example = (package / "examples" / "route-new-rules.tql").read_text()
pipeline = example[example.index('cron "'):].strip()
assert pipeline in (package / "README.md").read_text(), "README example drifted"
assert 'credential=secret("TRUEPATTERN_CREDENTIAL"),' in pipeline
assert "added_after=now() - 2h" in pipeline
routing = "  truepattern::latest\n" + pipeline.split("  truepattern::latest\n", 1)[1].rsplit("\n}", 1)[0]

formats = ["sigma", "splunk", "kql", "sentinel", "yara", "sublime-security", "future-format"]
# External references retain their required STIX source_name; license fields
# and the external_references field itself can be absent or empty.
cases = json.loads((package / "tests/inputs/license-metadata.json").read_text())
records = []
retained = {}
for format in formats:
    for index, case in enumerate(cases):
        record = {
            "id": f"indicator--{format}-{index}",
            "name": f"Synthetic {format} rule",
            "created": "2026-10-01T00:00:00Z",
            "modified": "2026-10-01T00:00:00Z",
            "pattern_type": format,
            "pattern": "# Copyright Synthetic Author; retain this notice\nSynthetic rule text",
        }
        if "external_references" in case:
            record["external_references"] = case["external_references"]
        records.append(record)
        if format != "sigma":
            retained[record["id"]] = record
    # Test the example's latest-before-filter ordering on every output branch.
    older = record | {"id": f"indicator--{format}-loses-metadata"}
    newer = older | {"modified": "2026-10-02T00:00:00Z", "external_references": None}
    records.extend([older, newer])
    if format != "sigma":
        retained[newer["id"]] = newer
expected = {
    "splunk": "splunk",
    "kql": "kql",
    "sentinel": "kql",
    "yara": "yara",
    "sublime-security": "other",
    "future-format": "other",
}
with TemporaryDirectory() as directory:
    root = Path(directory)
    source = root / "rules.ndjson"
    source.write_text("".join(json.dumps(record) + "\n" for record in records))
    routing = routing.replace("/var/lib/tenzir/truepattern/rules/", f"{root}/output/")
    body = f'from_file "{source}" {{ read_ndjson }}\n' + routing
    executor = Executor.from_env(os.environ)
    # A second poll must create new files rather than overwrite the first poll.
    for run in range(1, 3):
        result = executor.run(body)
        assert result.returncode == 0, result.stderr.decode()
        assert not result.stderr, result.stderr.decode()
        assert not result.stdout, result.stdout.decode()
        routes = []
        for path in (root / "output").glob("*/*.ndjson"):
            for line in path.read_text().splitlines():
                event = json.loads(line)
                rule = event["osint"][0]
                original = retained[rule["external_uid"]]
                assert rule["detection_pattern"] == original["pattern"], rule
                assert rule["modified_time"] == original["modified"], rule
                source_refs = original.get("external_references")
                stored_refs = event["unmapped"].get("external_references")
                if source_refs is None:
                    assert stored_refs is None, stored_refs
                else:
                    for source_ref, stored_ref in zip(source_refs, stored_refs, strict=True):
                        if source_ref is None:
                            assert stored_ref is None, stored_ref
                        else:
                            assert source_ref.items() <= stored_ref.items(), (source_ref, stored_ref)
                routes.append((rule["external_uid"], path.parent.name))
        expected_routes = [(id, expected[record["pattern_type"]]) for id, record in retained.items()]
        assert sorted(routes) == sorted(expected_routes * run), routes

for format, route in expected.items():
    print(f"{format}: {route}")
print("sigma: excluded")
print("absent/null/empty/whitespace license metadata: retained on every route, including newer versions")
print("rule text, notices, license and source references: preserved")
print("repeated polls: separate files")
