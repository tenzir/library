"""Check a demo recording before publishing it, or the output of a replay.

    python3 -I check.py privacy FILE...            exit 1 on anything that looks real
    python3 -I check.py replay --start T FILE      exit 1 on stale dates or IDs

`privacy` reads text or NDJSON. `replay` reads the NDJSON of exactly two cycles
that start at T (`pace=false, cycles=2, start=T`), one record per line. Reports
name the kind of a finding and the line, never the value.
"""

import argparse
import collections
import datetime
import ipaddress
import re
import sys

RESERVED = [ipaddress.ip_network(n) for n in (
    "0.0.0.0/8", "10.0.0.0/8", "127.0.0.0/8", "169.254.0.0/16", "172.16.0.0/12", "192.0.2.0/24",
    "192.168.0.0/16", "198.18.0.0/15", "198.51.100.0/24", "203.0.113.0/24", "224.0.0.0/3")]
RESERVED_NAMES = re.compile(
    r"(?:^|\.)(?:example(?:\.(?:com|net|org))?|test|invalid|localhost|local)$", re.I)
DEMO_SID = "S-1-5-21-1111111111-2222222222-3333333333-"
TLDS = "com|net|org|io|dev|eu|de|ch|at|uk|us|info|biz|cloud|ai|app|tools|lab|internal|lan|corp"
SECRETS = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY|\bgh[pousr]_\w{20,}|\bgithub_pat_\w{20,}|\bsk-[\w-]{20,}"
    r"|\bxox[abp]-[\w-]{10,}|\bAKIA[0-9A-Z]{16}\b|\bAIza[\w-]{30,}|\beyJ[\w-]{20,}\.[\w-]{10,}"
    r"|(?i:(?:password|passwd|secret|api[_-]?key)['\"]?\s*[=:]\s*['\"]?[A-Za-z0-9/+_-]{12,})")
UUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"


def findings(line, internal):
    """Yield the kinds of real-looking values in one line."""
    for address in re.findall(r"(?<![\w.-])(?:\d{1,3}\.){3}\d{1,3}(?![\w.]*\d)", line):
        try:
            parsed = ipaddress.ip_address(address)
        except ValueError:
            continue
        if not any(parsed in network for network in RESERVED):
            yield "public IPv4 address", address
    for mail, host in re.findall(r"([\w.+-]+@((?:[\w-]+\.)+[A-Za-z]{2,}))", line):
        if not RESERVED_NAMES.search(host):
            yield "mail address", mail
    for host in re.findall(rf"(?<![\w@.-])((?:[A-Za-z0-9_-]+\.)+(?:{TLDS}))(?![\w.-]*[A-Za-z0-9])", line):
        if not RESERVED_NAMES.search(host):
            yield "host name", host.lower()
    for sid in re.findall(r"S-1-5-21(?:-\d+){3,4}", line):
        if not sid.startswith(DEMO_SID):
            yield "security identifier", sid
    for mac in re.findall(r"(?<![\w:])(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}(?![\w:])", line):
        if not int(mac[:2], 16) & 0x02:
            yield "vendor MAC address", mac
    for address in re.findall(r"\bfe80:[0-9a-fA-F:]+", line):
        yield "link-local IPv6 address", address
    if SECRETS.search(line):
        yield "secret", ""
    for word in internal:
        if word.lower() in line.lower():
            yield "internal name", word


def privacy(args):
    internal = args.internal.split(",") if args.internal else []
    allowed = {a.lower() for a in args.allow.split(",")} if args.allow else set()
    kinds, lines = collections.defaultdict(set), collections.Counter()
    for path in args.files:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                for kind, value in set(findings(line, internal)):
                    if value.lower() not in allowed:
                        kinds[kind].add(value)
                        lines[kind] += 1
    for kind in sorted(kinds):
        print(f"{kind}: {len(kinds[kind])} distinct in {lines[kind]} lines")
    return bool(kinds)


def identifiers(lines):
    """Identifier-shaped values that a cycle must renew."""
    text = "\n".join(lines)
    found = set(re.findall(UUID, text)) | set(re.findall(r'"([CF][0-9a-f]{17})"', text))
    found |= set(re.findall(r"\b(?:toolu|call|req)_[0-9A-Za-z]{10,}", text))
    found |= set(re.findall(r'"(?:trace_id|span_id)":"([0-9a-f]+)"', text))
    found |= set(re.findall(r'(?:"flow_id":|<EventRecordID>|"(?:record_id|EventRecordID)\W+)(\d+)', text))
    return {f for f in found if not re.fullmatch(r"[0-]+", f)}


def replay(args):
    start = datetime.datetime.fromisoformat(args.start.replace("Z", "+00:00")).date()
    with open(args.file, encoding="utf-8") as handle:
        lines = handle.read().rstrip("\n").split("\n")
    failures = []
    if not lines or len(lines) % 2:
        failures.append(f"expected two equal cycles, got {len(lines)} records")
    half = len(lines) // 2
    near = {str(start + datetime.timedelta(days=d)) for d in (-2, -1, 0, 1, 2)}
    stale = collections.Counter()
    for line in lines:
        for date in re.findall(r"(?<!\d)(20[0-9]{2}-[01]\d-[0-3]\d)(?=[T ]\d\d:\d\d)", line):
            stale[date] += date not in near
    if sum(stale.values()):
        failures.append(f"{sum(stale.values())} timestamps outside the replayed days")
    epochs = [e for line in lines for e in re.findall(r"(?<![\w.-])1[5-9]\d{8}(?:\.\d+|\d{3}|\d{6}|\d{9})?(?![\w.-])", line)]
    if epochs and not args.epochs:
        failures.append(f"{len(epochs)} numbers look like epoch timestamps")
    kept = identifiers(lines[:half]) & identifiers(lines[half:])
    kept -= set(args.stable.split(",")) if args.stable else set()
    if kept:
        failures.append(f"{len(kept)} identifiers are equal in both cycles")
    if "\u001e" in "".join(lines) or "\\u001e" in "".join(lines):
        failures.append("unrendered tokens")
    for failure in failures:
        print(failure)
    if args.show:
        print(sorted(kept)[:20], [d for d in stale if stale[d]][:20])
    return bool(failures)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("privacy")
    p.add_argument("files", nargs="+")
    p.add_argument("--internal", help="comma-separated internal names to reject")
    p.add_argument("--allow", help="comma-separated values to accept")
    r = commands.add_parser("replay")
    r.add_argument("file")
    r.add_argument("--start", required=True)
    r.add_argument("--stable", help="comma-separated identifiers that may repeat")
    r.add_argument("--epochs", action="store_true", help="accept numbers that look like epochs")
    r.add_argument("--show", action="store_true", help="print offending values")
    args = parser.parse_args()
    return {"privacy": privacy, "replay": replay}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
