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
license_ref = {
    "source_name": "rule-vendor-license",
    "external_id": "MIT",
    "url": "https://opensource.org/license/mit",
}
records = [
    {
        "id": f"indicator--{index}",
        "name": f"Synthetic {format} rule",
        "created": "2026-10-01T00:00:00Z",
        "modified": "2026-10-01T00:00:00Z",
        "pattern_type": format,
        "pattern": "id: synthetic",
        "external_references": [license_ref],
    }
    for index, format in enumerate(formats)
]
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
                assert rule["detection_pattern"] == "id: synthetic", rule
                assert license_ref in event["unmapped"]["external_references"], event
                routes.append((rule["detection_pattern_type"], path.parent.name))
        assert sorted(routes) == sorted(list(expected.items()) * run), routes

for format, route in expected.items():
    print(f"{format}: {route}")
print("sigma: excluded")
print("rule text and license: preserved")
print("repeated polls: separate files")
