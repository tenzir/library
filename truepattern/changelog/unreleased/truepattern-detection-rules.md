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

```tql
subscribe "ocsf"
sigma path="/var/lib/tenzir/truepattern/sigma.yaml"
truepattern::enrich
```

Rules in other formats, such as Splunk, KQL, or YARA, map to OCSF OSINT Inventory Info with `truepattern::ocsf::normalize`, so that you can route them to the systems that run them.
