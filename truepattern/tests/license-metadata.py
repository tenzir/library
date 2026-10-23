# Metadata is informational, not an execution filter. Exercise every selector,
# version changes, duplicate Sigma IDs, and preservation of attribution/notices.
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

package = Path(os.environ["TENZIR_PACKAGE_ROOT"])
cases = json.loads((package / "tests/inputs/license-metadata.json").read_text())
executor = Executor.from_env(os.environ)


def indicator(index, case):
    record = {
        "type": "indicator",
        "id": f"indicator--{index:012d}",
        "created": "2026-10-01T00:00:00Z",
        "modified": "2026-10-01T00:00:00Z",
        "pattern_type": "sigma",
        "name": case["case"],
        "pattern": (
            "# Copyright Synthetic Author; retain this header\n"
            "--- # Start notice\n"
            f"title: Synthetic {case['case']}\n"
            f"id: 00000000-0000-4000-8000-{index:012d}\n"
            "author: Synthetic Author\n"
            "license: Synthetic terms embedded in YAML\n"
            "references:\n  - https://example.com/upstream\n"
            "logsource:\n  product: windows\n  service: security\n"
            "detection:\n  selection:\n    CommandLine: trigger\n"
            "  condition: selection\n"
            "... # End notice\n# Retain this trailing notice\n"
        ),
    }
    if "external_references" in case:
        record["external_references"] = case["external_references"]
    return record


records = [indicator(index, case) for index, case in enumerate(cases, 1)]
expected = records.copy()
# The newest STIX version wins even after losing license metadata.
older = indicator(100, cases[-2])
newer = older | {
    "modified": "2026-10-02T00:00:00Z",
    "external_references": None,
    "pattern": older["pattern"].replace("title: Synthetic name-and-url", "title: New STIX version"),
}
# The same applies to a newer copy with a duplicate Sigma ID.
older_copy = indicator(200, cases[-2])
newer_copy = older_copy | {
    "id": "indicator--000000000201",
    "modified": "2026-10-02T00:00:00Z",
    "external_references": [],
    "pattern": older_copy["pattern"].replace("title: Synthetic name-and-url", "title: New copy"),
}
records.extend([older, newer, older_copy, newer_copy])
expected.extend([newer, newer_copy])
expected_ids = [record["pattern"].split("\nid: ", 1)[1].splitlines()[0] for record in expected]

with TemporaryDirectory(prefix="truepattern-license-metadata-") as directory:
    root = Path(directory)
    source = root / "rules.ndjson"
    target = root / "sigma.yaml"

    def detect():
        result = executor.run(
            f'from {{CommandLine: "trigger"}}\nsigma path="{target}"\n'
            "select id=finding_info.analytic.uid\nsort id\nwrite_ndjson"
        )
        assert result.returncode == 0, result.stderr.decode()
        assert not result.stderr, result.stderr.decode()
        ids = [json.loads(line)["id"] for line in result.stdout.splitlines()]
        assert ids == expected_ids, ids

    source.write_text("".join(json.dumps(record) + "\n" for record in records))
    for selector in ("", ', product="windows"', ', logsource={product: "windows", service: "security"}'):
        result = executor.run(
            f'from_file "{source}" {{ read_ndjson }}\n'
            f'truepattern::sigma::update_rules path="{target}"{selector}\n'
            "select id, pattern\nwrite_ndjson"
        )
        assert result.returncode == 0, result.stderr.decode()
        assert not result.stderr, result.stderr.decode()
        forwarded = [json.loads(line) for line in result.stdout.splitlines()]
        assert forwarded == [{"id": item["id"], "pattern": item["pattern"]} for item in expected], forwarded
        text = target.read_text()
        # Comments on both document markers and before/after them must survive.
        for notice in ("# Copyright Synthetic Author; retain this header", "# Start notice",
                       "# End notice", "# Retain this trailing notice"):
            assert text.count(notice) == len(expected), (notice, text)
        for field in ("author: Synthetic Author", "references:\n  - https://example.com/upstream",
                      "license: Synthetic terms embedded in YAML"):
            assert text.count(field) == len(expected), (field, text)
        headers = [
            json.loads(line.removeprefix("# TruePattern external references: "))
            for line in text.splitlines() if line.startswith("# TruePattern external references: ")
        ]
        supplied = [record["external_references"] for record in expected if record.get("external_references") is not None]
        # TQL can unify record shapes, adding null fields. Preserve every
        # supplied value, including blank metadata, without inventing values.
        for source_refs, stored_refs in zip(supplied, headers, strict=True):
            for source_ref, stored_ref in zip(source_refs, stored_refs, strict=True):
                if source_ref is None:
                    assert stored_ref is None, stored_ref
                else:
                    assert source_ref.items() <= stored_ref.items(), (source_ref, stored_ref)
        detect()
    print("all/product/exact logsource: absent/null/empty/whitespace metadata does not suppress rules")
    print("latest STIX versions and duplicate Sigma IDs: newest copy runs even without license metadata")
    print("source references, original YAML fields, and header/marker/trailing notices: preserved")
    # A later complete snapshot without any external references still runs all
    # the rules and forwards them for cataloging.
    missing = [{key: value for key, value in record.items() if key != "external_references"} for record in expected]
    source.write_text("".join(json.dumps(record) + "\n" for record in missing))
    result = executor.run(
        f'from_file "{source}" {{ read_ndjson }}\n'
        f'truepattern::sigma::update_rules path="{target}"\n'
        "select id\nwrite_ndjson"
    )
    assert result.returncode == 0 and not result.stderr, result.stderr.decode()
    assert [json.loads(line)["id"] for line in result.stdout.splitlines()] == [record["id"] for record in missing]
    assert "# TruePattern external references:" not in target.read_text()
    detect()
    print("complete snapshot without license metadata: all rules written, forwarded, and executed")
    # Only a final end marker can be removed. A marker followed by more rule
    # content must not silently merge two documents.
    multiple = expected[0] | {"pattern": expected[0]["pattern"] + "title: Another document\n"}
    source.write_text(json.dumps(multiple) + "\n")
    result = executor.run(
        f'from_file "{source}" {{ read_ndjson }}\n'
        f'truepattern::sigma::update_rules path="{target}"'
    )
    assert result.returncode == 0, result.stderr.decode()
    assert "not a single YAML document" in result.stderr.decode(), result.stderr.decode()
    assert not result.stdout and target.read_bytes() == b"\n"
    print("nonfinal document end marker: rejected, not merged with subsequent content")
