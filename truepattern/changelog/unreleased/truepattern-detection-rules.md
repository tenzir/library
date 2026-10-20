---
title: TruePattern detection rules
type: feature
authors:
  - mavam
prs:
  - 202
created: 2026-10-15T11:45:53.237736Z
---

The new `truepattern` package brings the curated detection rules of [TruePattern](https://truepattern.io) to Tenzir. `truepattern::feed` fetches the rules from the TruePattern TAXII collection, and `truepattern::sigma::update_rules` keeps one file with the latest version of every Sigma rule for the `sigma` operator. `truepattern::update_context` and `truepattern::enrich` add the rule metadata, such as the upstream source, ATT&CK techniques, and license, to the resulting detection findings:

```tql
cron "0 0 6 * * *" {
  truepattern::feed credential=secret("TRUEPATTERN_CREDENTIAL")
  truepattern::sigma::update_rules path="/var/lib/tenzir/truepattern/sigma.yaml"
  truepattern::ocsf::normalize
  truepattern::update_context
}
```

After the rule update populates the rule file and catalog, read an OCSF NDJSON export and write enriched findings to files:

```tql
from_file "/var/log/ocsf/events.ndjson" {
  read_ndjson
}
sigma path="/var/lib/tenzir/truepattern/sigma.yaml"
truepattern::enrich
to_file "/var/lib/tenzir/truepattern/findings/ocsf-{uuid}.ndjson" {
  write_ndjson
}
```

Adapt the paths to your node. This detection pipeline processes the export once; the `{uuid}` filenames preserve findings across runs.

Rules in other formats, such as Splunk, KQL, or YARA, map to OCSF OSINT Inventory Info with `truepattern::ocsf::normalize`. The routing example archives them as NDJSON files by format, preserving rule text and attribution without installing rules in the target engines.

Pass `product="windows"` to `truepattern::sigma::update_rules` to write a file with only the Windows rules, which run directly on native Windows event logs after `parse_winlog`.
