# Exercise the example's routing body without a scheduler, network, or node.
# Replace only its source and sinks so the format filter and branches stay real.
import json
import os
import re
from pathlib import Path

package = Path(os.environ["TENZIR_TEST_ROOT"])
os.environ["TENZIR_PACKAGE_DIRS"] = f"{package},{package.parent / 'stix'}"
example = (package / "examples" / "route-new-rules.tql").read_text()
pipeline = example[example.index('cron "'):].strip()
assert pipeline in (package / "README.md").read_text(), "README example drifted"
routing = pipeline.split("  truepattern::latest\n", 1)[1].rsplit("\n}", 1)[0]
routing = re.sub(r'publish "([^"]+)"', r'route = "\1"', routing)

formats = ["sigma", "splunk", "kql", "sentinel", "yara", "sublime-security", "future-format"]
records = [
    {
        "id": f"indicator--{index}",
        "created": "2026-10-01T00:00:00Z",
        "modified": "2026-10-01T00:00:00Z",
        "pattern_type": format,
        "pattern": "id: synthetic",
    }
    for index, format in enumerate(formats)
]
source = "from " + ", ".join(json.dumps(record) for record in records) + "\n"
result = Executor.from_env(os.environ).run(
    source + routing + "\nselect format=osint[0].detection_pattern_type, route\nwrite_ndjson"
)
assert result.returncode == 0, result.stderr.decode()
assert not result.stderr, result.stderr.decode()
routes = [json.loads(line) for line in result.stdout.splitlines()]
expected = [
    {"format": "splunk", "route": "truepattern-splunk"},
    {"format": "kql", "route": "truepattern-kql"},
    {"format": "sentinel", "route": "truepattern-kql"},
    {"format": "yara", "route": "truepattern-yara"},
    {"format": "sublime-security", "route": "truepattern-other"},
    {"format": "future-format", "route": "truepattern-other"},
]
assert routes == expected, routes
for route in routes:
    print(f"{route['format']}: {route['route']}")
print("sigma: excluded")
