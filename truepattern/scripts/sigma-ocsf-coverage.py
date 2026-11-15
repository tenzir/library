#!/usr/bin/env python3
"""Reports how the `sigma` operator treats every rule of a rule set on OCSF input.

The report asks the Tenzir engine itself instead of approximating its mapping
catalog: it loads the rules into the `sigma` operator, feeds a single
OCSF-shaped probe event, and classifies every rule by the diagnostics that the
operator emits while it plans the rules for that schema:

- `translated`: the operator plans the rule for OCSF input.
- `skipped`: the operator skips the rule for OCSF input, for example because
  it uses a field without an OCSF equivalent. The rule may still run on native
  events.
- `rejected`: the operator rejects the rule for every input, for example
  because it uses an unsupported modifier such as `expand`.
- `invalid`: the document does not parse as a Sigma rule, or its `detection`
  or `logsource` is not a record.

A `translated` rule loads, but that alone does not prove that it can match:
the normalized events must carry the OCSF attributes that the translation
reads. Keyword-only rules search every string of an event; the report flags
them because the logsource does not necessarily scope them.

The input is a rule file that `truepattern::sigma::update_rules` writes, any
other single- or multi-document Sigma file, or a directory of `.yml` and
`.yaml` files. The script needs only the Python standard library and a Tenzir
binary.

Usage:
    sigma-ocsf-coverage.py RULES [--tenzir "tenzir run"] [--format json|csv]
        [--output FILE]
"""

from __future__ import annotations

import argparse
import collections
import csv
import io
import json
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

# The comment that `truepattern::sigma::update_rules` prepends to every rule.
REFERENCES_PREFIX = "# TruePattern external references: "
DOCUMENT_MARKER = re.compile(r"^---[ \t]*(#.*)?$")
DIAGNOSTIC = re.compile(
    r"^(warning|error): sigma operator (skips|ignores) rule '(?P<rule>[^']*)'"
)
NOTE = re.compile(r"^\s*= (note|hint): (?P<text>.*)$")
UNRESOLVED = re.compile(r"unresolved Sigma fields: (?P<fields>.*)$")
UNMAPPED = re.compile(r"field `(?P<field>[^`]+)` is unmapped")
BACKTICKED = re.compile(r"`([^`]*)`")

# A minimal OCSF-shaped event: the operator recognizes OCSF input by a string
# `metadata.version` and an integer `class_uid`.
PROBE = (
    "from {class_uid: 0, category_uid: 0, activity_id: 0, type_uid: 0, "
    "severity_id: 1, time: 2026-01-01T00:00:00Z, "
    'metadata: {version: "1.9.0", product: {name: "sigma-ocsf-coverage"}}}'
)


def split_documents(text: str) -> list[str]:
    """Splits a YAML stream at document markers that start a line."""
    documents, current = [], []
    for line in text.replace("\r\n", "\n").split("\n"):
        if DOCUMENT_MARKER.match(line):
            documents.append("\n".join(current))
            current = []
        else:
            current.append(line)
    documents.append("\n".join(current))
    # Drop documents that hold only whitespace and comments.
    return [
        document
        for document in documents
        if any(
            line.strip() and not line.lstrip().startswith("#")
            for line in document.split("\n")
        )
    ]


def load_documents(path: Path) -> list[tuple[str, str]]:
    """Returns (origin, text) pairs for every rule document under `path`."""
    if path.is_dir():
        files = sorted(
            {file for suffix in ("*.yml", "*.yaml") for file in path.rglob(suffix)}
        )
    else:
        files = [path]
    result = []
    for file in files:
        documents = split_documents(file.read_text(encoding="utf-8"))
        name = str(file.relative_to(path)) if path.is_dir() else file.name
        for index, document in enumerate(documents):
            origin = name if len(documents) == 1 else f"{name}#{index}"
            result.append((origin, document))
    return result


def references(document: str) -> list[dict]:
    for line in document.split("\n"):
        if line.startswith(REFERENCES_PREFIX):
            try:
                value = json.loads(line[len(REFERENCES_PREFIX) :])
            except json.JSONDecodeError:
                return []
            return value if isinstance(value, list) else []
    return []


def detection_fields(detection) -> set[str]:
    """Collects the field names that a detection references.

    A key names its field before the first modifier. A `fieldref` item also
    references the fields that its values name.
    """
    fields: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                name, _, modifiers = str(key).partition("|")
                fields.add(name)
                if "fieldref" in modifiers.split("|"):
                    values = value if isinstance(value, list) else [value]
                    fields.update(item for item in values if isinstance(item, str))
        elif isinstance(node, list):
            for item in node:
                walk(item)

    if isinstance(detection, dict):
        for name, value in detection.items():
            if name not in ("condition", "timeframe"):
                walk(value)
    return fields


def run_tenzir(
    tenzir: list[str], pipeline: str, directory: Path
) -> subprocess.CompletedProcess:
    script = directory / "pipeline.tql"
    script.write_text(pipeline + "\n", encoding="utf-8")
    return subprocess.run(
        [*tenzir, "--bare-mode", "--console-verbosity=warning", "-f", str(script)],
        capture_output=True,
        check=False,
        text=True,
    )


def parse_diagnostics(stderr: str) -> dict[str, dict]:
    """Maps rule file names to the diagnostic that the operator emitted."""
    result: dict[str, dict] = {}
    current = None
    for line in stderr.splitlines():
        match = DIAGNOSTIC.match(line)
        if match:
            rule = Path(match["rule"].split("#", 1)[0]).name
            current = result.setdefault(
                rule,
                {
                    "status": "skipped" if match[2] == "skips" else "rejected",
                    "notes": [],
                },
            )
            continue
        if not line.strip():
            current = None
            continue
        note = NOTE.match(line)
        if current is not None and note:
            current["notes"].append(note["text"])
    return result


def shape_problem(rule) -> str | None:
    """Describes why a parsed document cannot be a Sigma rule, if it can't."""
    if not isinstance(rule, dict):
        return "the document is not a YAML mapping"
    if not isinstance(rule.get("detection"), dict):
        return "`detection` is not a record"
    if "logsource" in rule and not isinstance(rule["logsource"], dict):
        return "`logsource` is not a record"
    return None


def text_attribute(rule, name: str) -> str | None:
    value = rule.get(name) if isinstance(rule, dict) else None
    return value if isinstance(value, str) else None


def unresolved_fields(notes: list[str]) -> list[str]:
    fields: list[str] = []
    for note in notes:
        if match := UNRESOLVED.search(note):
            fields.extend(BACKTICKED.findall(match["fields"]))
        elif match := UNMAPPED.search(note):
            fields.append(match["field"])
    return sorted(set(fields))


def analyze(rules: Path, tenzir: list[str]) -> dict:
    documents = load_documents(rules)
    with tempfile.TemporaryDirectory(prefix="sigma-ocsf-coverage-") as scratch:
        scratch = Path(scratch)
        rule_directory = scratch / "rules"
        rule_directory.mkdir()
        manifest = scratch / "documents.ndjson"
        with manifest.open("w", encoding="utf-8") as handle:
            for index, (_, document) in enumerate(documents):
                (rule_directory / f"{index:06d}.yml").write_text(
                    document + "\n", encoding="utf-8"
                )
                handle.write(json.dumps({"index": index, "text": document}) + "\n")
        # Parse every document with Tenzir's YAML parser.
        parsed = run_tenzir(
            tenzir,
            f"from_file {json.dumps(str(manifest))} {{\n  read_ndjson\n}}\n"
            "select index, rule=text.parse_yaml()\n"
            "write_ndjson",
            scratch,
        )
        if parsed.returncode != 0:
            raise RuntimeError(f"failed to parse the rules:\n{parsed.stderr}")
        metadata = {}
        for line in parsed.stdout.splitlines():
            record = json.loads(line)
            metadata[record["index"]] = record["rule"]
        version = run_tenzir(tenzir, "version\nwrite_ndjson", scratch)
        engine = (
            json.loads(version.stdout.splitlines()[0])
            if version.returncode == 0
            else {}
        )
        # Plan every rule for the OCSF probe schema.
        planned = run_tenzir(
            tenzir,
            f"{PROBE}\nsigma path={json.dumps(str(rule_directory))}\ndiscard",
            scratch,
        )
        if planned.returncode != 0:
            raise RuntimeError(f"failed to load the rules:\n{planned.stderr}")
        diagnostics = parse_diagnostics(planned.stderr)
    report_rules = []
    for index, (origin, document) in enumerate(documents):
        rule = metadata.get(index)
        entry = {
            "source": origin,
            "id": None,
            "title": None,
            "logsource": None,
            "status": "invalid",
            "reasons": [],
            "unresolved_fields": [],
            "keywords_only": False,
            "rule_source": None,
        }
        refs = references(document)
        entry["rule_source"] = next(
            (ref.get("url") for ref in refs if ref.get("source_name") == "rule-source"),
            None,
        )
        diagnostic = diagnostics.get(f"{index:06d}.yml")
        entry.update(id=text_attribute(rule, "id"), title=text_attribute(rule, "title"))
        if problem := shape_problem(rule):
            # Prefer the operator's own reason, which names the offending
            # attribute; it rejects these documents as well.
            entry["reasons"] = diagnostic["notes"] if diagnostic else [problem]
        else:
            entry.update(
                logsource=rule.get("logsource"),
                status=diagnostic["status"] if diagnostic else "translated",
                reasons=diagnostic["notes"] if diagnostic else [],
                unresolved_fields=unresolved_fields(diagnostic["notes"])
                if diagnostic
                else [],
                keywords_only=not detection_fields(rule["detection"]),
            )
        report_rules.append(entry)
    statuses = collections.Counter(entry["status"] for entry in report_rules)
    unresolved = collections.Counter(
        field for entry in report_rules for field in entry["unresolved_fields"]
    )
    logsources = collections.defaultdict(collections.Counter)
    for entry in report_rules:
        logsource = entry["logsource"] or {}
        key = "/".join(
            str(logsource.get(name) or "-")
            for name in ("product", "category", "service")
        )
        logsources[key][entry["status"]] += 1
    return {
        "engine": {key: engine.get(key) for key in ("version", "tag")},
        "rules": len(report_rules),
        "statuses": {
            status: statuses.get(status, 0)
            for status in ("translated", "skipped", "rejected", "invalid")
        },
        "keywords_only": sum(
            entry["keywords_only"] and entry["status"] == "translated"
            for entry in report_rules
        ),
        "unresolved_fields": dict(unresolved.most_common()),
        "logsources": {key: dict(counts) for key, counts in sorted(logsources.items())},
        "details": report_rules,
    }


def write_csv(report: dict, handle) -> None:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(
        [
            "source",
            "id",
            "title",
            "product",
            "category",
            "service",
            "status",
            "keywords_only",
            "unresolved_fields",
            "reasons",
            "rule_source",
        ]
    )
    for entry in report["details"]:
        logsource = entry["logsource"] or {}
        writer.writerow(
            [
                entry["source"],
                entry["id"] or "",
                entry["title"] or "",
                logsource.get("product") or "",
                logsource.get("category") or "",
                logsource.get("service") or "",
                entry["status"],
                str(entry["keywords_only"]).lower(),
                " ".join(entry["unresolved_fields"]),
                " | ".join(entry["reasons"]),
                entry["rule_source"] or "",
            ]
        )


def summary(report: dict) -> str:
    statuses = report["statuses"]
    lines = [
        f"engine: {report['engine'].get('version') or 'unknown'}",
        f"rules: {report['rules']}",
        *(f"{status}: {count}" for status, count in statuses.items()),
        f"translated keyword-only rules: {report['keywords_only']}",
    ]
    if report["unresolved_fields"]:
        top = list(report["unresolved_fields"].items())[:10]
        lines.append(
            "top unresolved fields: "
            + ", ".join(f"{name} ({count})" for name, count in top)
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("rules", type=Path, help="rule file or directory")
    parser.add_argument(
        "--tenzir",
        default="tenzir run",
        help="command that runs a TQL file (default: %(default)s)",
    )
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("--output", type=Path, help="write the report to this file")
    args = parser.parse_args()
    if not args.rules.exists():
        parser.error(f"{args.rules} does not exist")
    try:
        report = analyze(args.rules, shlex.split(args.tenzir))
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    buffer = io.StringIO()
    if args.format == "csv":
        write_csv(report, buffer)
    else:
        json.dump(report, buffer, indent=2)
        buffer.write("\n")
    if args.output:
        args.output.write_text(buffer.getvalue(), encoding="utf-8")
    else:
        sys.stdout.write(buffer.getvalue())
    print(summary(report), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
