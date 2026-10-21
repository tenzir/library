# Exact logsource selection must not admit extra constraints or stale versions.
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory


def indicator(index, logsource, version=1, sigma_id=None):
    return {
        "type": "indicator",
        "id": f"indicator--00000000-0000-4000-8000-{index:012d}",
        "modified": f"2026-09-0{version}T00:00:00Z",
        "pattern_type": "sigma",
        "pattern": (
            f"title: Rule {index}\nid: 00000000-0000-4000-8000-{sigma_id or index:012d}\n"
            "logsource:\n" + "".join(f"  {key}: {value}\n" for key, value in logsource.items())
        ),
    }


security = {"product": "windows", "service": "security"}
records = [
    indicator(1, security),
    indicator(2, {"service": "security", "product": "windows"}),
    indicator(3, {"product": "windows", "service": "sysmon"}),
    indicator(4, {**security, "category": "process_creation"}),
    indicator(5, {"product": "windows"}),
    indicator(6, {**security, "definition": "Extra audit policy required"}),
    indicator(7, {**security, "custom": "unknown constraint"}),
    indicator(8, {"product": "linux", "service": "security"}),
    indicator(9, security),
    indicator(9, {"product": "windows", "service": "system"}, version=2),
    indicator(10, security),
    indicator(11, {"product": "windows", "service": "system"}, version=2, sigma_id=10),
]
source = "from " + ", ".join(json.dumps(record) for record in records) + "\n"
package = Path(os.environ["TENZIR_PACKAGE_ROOT"])
# Exercise the exact selector used by the scheduled update example.
example = (package / "examples/update-sigma-rules.tql").read_text()
selector = 'logsource={product: "windows", service: "security"}'
assert selector in example
assert selector in (package / "README.md").read_text()
with TemporaryDirectory(prefix="truepattern-logsource-") as directory:
    target = Path(directory) / "security.yaml"
    executor = Executor.from_env(os.environ)
    pipeline = f'truepattern::sigma::update_rules path={json.dumps(str(target))}, {selector}\nwrite_ndjson'
    result = executor.run(source + pipeline)
    assert result.returncode == 0, result.stderr.decode()
    assert not result.stderr, result.stderr.decode()
    forwarded = [json.loads(line) for line in result.stdout.splitlines()]
    assert forwarded == records[:2], forwarded
    expected = "\n---\n".join(record["pattern"] for record in records[:2]) + "\n"
    assert target.read_text() == expected, target.read_text()
    print("exact logsource: only Security-service rules without extra constraints")
    print("latest version and duplicate Sigma IDs: resolved before logsource selection")
    # A complete walk with no matching logsource clears previously selected rules.
    result = executor.run("from " + json.dumps(records[2]) + "\n" + pipeline)
    assert result.returncode == 0, result.stderr.decode()
    assert not result.stderr, result.stderr.decode()
    assert not result.stdout, result.stdout.decode()
    assert target.read_text() == "\n", target.read_text()
    print("no matching logsource: rule file cleared")
