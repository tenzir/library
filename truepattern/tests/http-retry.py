# fixtures: [truepattern_taxii]
# timeout: 60
# assertions: {fixtures: {truepattern_taxii: {collection: recovering, pages: 3, retries: 2}}}

# A transient failure on page two must not turn a complete walk into a partial
# replacement, nor fail under the feed's strict operator.
import json
import os
from pathlib import Path

# Work around the Python runner's missing package loading (TNZ-1733).
package = Path(os.environ["TENZIR_TEST_ROOT"])
os.environ["TENZIR_PACKAGE_DIRS"] = f"{package},{package.parent / 'stix'}"
executor = Executor.from_env(os.environ)
root = Path(os.environ["TRUEPATTERN_TEST_DIR"])
source = root / "objects.ndjson"
objects = json.loads((package / "tests/inputs/objects.json").read_text())
source.write_text("".join(json.dumps(record) + "\n" for record in objects))
reference = root / "reference.yaml"
target = root / "recovered.yaml"
expected = executor.run(f'''
from_file "{source}" {{ read_ndjson }}
truepattern::sigma::update_rules path="{reference}"
select id, modified, name
''')
assert expected.returncode == 0, expected.stderr.decode()
assert reference.stat().st_size > 0
target.write_text("last-known-good file\n")
result = executor.run(f'''
truepattern::feed credential=env("TRUEPATTERN_TEST_CREDENTIAL"),
  collection="recovering", base_url=env("TRUEPATTERN_TEST_URL")
truepattern::sigma::update_rules path="{target}"
select id, modified, name
''')
assert result.returncode == 0, result.stderr.decode()
# Invalid rules in the synthetic feed still warn; intermediate HTTP retries do not.
assert b"retrying" not in result.stderr, result.stderr.decode()
assert target.read_bytes() == reference.read_bytes()
assert result.stdout == expected.stdout, result.stdout.decode()
print("two transient HTTP 503 responses: recovered under strict")
print("rule file and forwarded indicators: match the complete collection")
