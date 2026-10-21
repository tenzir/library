# fixtures: [truepattern_taxii]
# timeout: 60

# Distinguish a successful empty snapshot from an incomplete walk, even when
# no qualifying event reaches the writer before the failure.
import json
import os
from pathlib import Path

executor = Executor.from_env(os.environ)
root = Path(os.environ["TRUEPATTERN_TEST_DIR"])
target = root / "empty-walk.yaml"
seed = """title: Last known good rule
id: 00000000-0000-4000-8000-000000000001
logsource:
  product: windows
detection:
  selection:
    CommandLine: whoami
  condition: selection
"""


def walk(collection):
    return f'''
truepattern::feed credential=env("TRUEPATTERN_TEST_CREDENTIAL"),
  collection="{collection}", base_url=env("TRUEPATTERN_TEST_URL")
'''


def update(source):
    return executor.run(source + f'\ntruepattern::sigma::update_rules path="{target}"')


# The first case exercises truly empty input, not merely a product filter.
target.write_text(seed)
result = update(walk("empty"))
assert result.returncode == 0, result.stderr.decode()
assert not result.stderr, result.stderr.decode()
assert not result.stdout, result.stdout.decode()
assert target.read_bytes() == b"\n", target.read_bytes()
print("empty collection: cleared, no indicators forwarded")

# A rule changing format must not resurrect its earlier Sigma version.
objects = [
    {"type": "indicator", "id": "indicator--1", "modified": "2026-10-01T00:00:00Z",
     "pattern_type": "sigma", "pattern": seed},
    {"type": "indicator", "id": "indicator--1", "modified": "2026-10-02T00:00:00Z",
     "pattern_type": "splunk", "pattern": "search index=main"},
]
source = root / "objects.ndjson"
for label, records, warning in (
    ("latest version is not Sigma", objects, False),
    ("all Sigma YAML is invalid", [objects[0] | {"pattern": "broken: ["}], True),
):
    source.write_text("".join(json.dumps(record) + "\n" for record in records))
    target.write_text(seed)
    result = update(f'from_file "{source}" {{ read_ndjson }}')
    assert result.returncode == 0, result.stderr.decode()
    assert bool(result.stderr) == warning, result.stderr.decode()
    assert not result.stdout, result.stdout.decode()
    assert target.read_bytes() == b"\n", target.read_bytes()
    print(f"{label}: cleared, no indicators forwarded")

for collection in ("unauthorized", "failing-empty", "malformed", "incomplete", "incomplete-later"):
    target.write_text(seed)
    result = update(walk(collection))
    assert result.returncode != 0, result.stdout.decode()
    assert target.read_bytes() == seed.encode(), (collection, target.read_bytes())
    if collection.startswith("incomplete"):
        assert b"without a usable continuation" in result.stderr, result.stderr.decode()
    assert not result.stdout, result.stdout.decode()
    print(f"{collection}: failed, last-known-good file retained")
