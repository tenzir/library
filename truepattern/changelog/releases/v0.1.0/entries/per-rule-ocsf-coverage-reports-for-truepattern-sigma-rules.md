---
title: Per-rule OCSF coverage reports for TruePattern Sigma rules
type: feature
authors:
  - mavam
created: 2026-11-15T10:26:13.178747Z
---

The new `scripts/sigma-ocsf-coverage.py` script reports how the `sigma` operator
of your Tenzir build treats every TruePattern Sigma rule on OCSF input. Run it
on the rule file that `truepattern::sigma::update_rules` writes:

```sh
python3 truepattern/scripts/sigma-ocsf-coverage.py \
  /var/lib/tenzir/truepattern/sigma.yaml --format csv --output coverage.csv
```

The script asks the engine instead of estimating the mapping. It classifies
every rule as translated, skipped for OCSF input, rejected, or invalid, and lists
the fields that block a translation, such as the Windows `Channel` field. It
also flags translated keyword-only rules, because their keywords match any
string in an event. The JSON and CSV reports keep each rule's upstream
`rule-source` reference, and the JSON report also summarizes the statuses per
logsource and the most frequent unresolved fields.

A translated rule loads, but that alone doesn't prove that it matches: the
normalized events must carry the OCSF attributes that the translation reads.
