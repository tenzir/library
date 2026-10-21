# A format change belongs to the newest Indicator, not the newest Sigma
# version. Check both the rule file and the records forwarded to the catalog.
import json
import os
import tempfile
from pathlib import Path


def rule(index, version, format, title, product="windows"):
    return {
        "type": "indicator",
        "id": f"indicator--00000000-0000-4000-8000-{index:012d}",
        "created": "2026-09-01T00:00:00Z",
        "modified": f"2026-09-0{version}T00:00:00Z",
        "pattern_type": format,
        "name": title,
        "pattern": (
            f"title: {title}\nid: 00000000-0000-4000-8000-{index:012d}\n"
            f"logsource:\n  product: {product}\n"
        ) if format == "sigma" else "synthetic native query",
    }


records = [
    rule(1, 1, "sigma", "Stale Sigma before Splunk"),
    rule(1, 2, "splunk", "Current Splunk"),
    rule(2, 1, "splunk", "Stale Splunk before Sigma"),
    rule(2, 2, "sigma", "Current Sigma from Splunk"),
    rule(3, 1, "sigma", "Stale Sigma revision"),
    rule(3, 2, "sigma", "Current Sigma revision"),
    rule(4, 1, "sigma", "Stale Windows product"),
    rule(4, 2, "sigma", "Current Linux product", product="linux"),
]
source = "from " + ", ".join(json.dumps(record) for record in records) + "\n"
with tempfile.TemporaryDirectory(prefix="truepattern-latest-format-") as directory:
    for product, expected in [(None, [2, 3, 4]), ("windows", [2, 3])]:
        path = Path(directory) / f"{product or 'all'}.yaml"
        product_arg = f", product={json.dumps(product)}" if product else ""
        result = Executor.from_env(os.environ).run(
            source
            + f"truepattern::sigma::update_rules path={json.dumps(str(path))}{product_arg}\n"
            + "select id, name\nwrite_ndjson"
        )
        assert result.returncode == 0, result.stderr.decode()
        assert not result.stderr, result.stderr.decode()
        forwarded = [json.loads(line) for line in result.stdout.splitlines()]
        expected_rules = [records[index * 2 - 1] for index in expected]
        assert forwarded == [{"id": rule["id"], "name": rule["name"]} for rule in expected_rules], forwarded
        expected_text = "\n---\n".join(rule["pattern"] for rule in expected_rules) + "\n"
        assert path.read_text() == expected_text, path.read_text()
        print(f"{product or 'all'}: current Sigma rules {expected}")
print("sigma -> splunk: excluded; splunk -> sigma: retained")
