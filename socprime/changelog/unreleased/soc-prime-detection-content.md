---
title: SOC Prime detection content
type: feature
authors:
  - mavam
prs:
  - 235
created: 2026-11-16T09:18:22.571697Z
---

The new `socprime` package brings the detection content of [SOC Prime](https://socprime.com) to Tenzir. It bundles a snapshot of the behavior rules, High-Order Sigma (HoS) rules, and Active Threats that SOC Prime ships with DetectFlow.

`socprime::detect` matches OCSF events against all behavior rules with the `sigma` operator:

```tql
from_file "/var/log/windows/events.xml" {
  read_delimited "</Event>\n", include_separator=true
}
microsoft::windows::ocsf::normalize data
socprime::detect
```

`socprime::hos::detect` runs the attack chain of a HoS rule in a single pipeline: it matches the stage rules, correlates the findings per host, and emits an OCSF Detection Finding once the host covers enough stages. Later stages update the finding. It links the contributing findings and source events, and reports the stage coverage as `confidence_score`:

```tql
socprime::hos::detect "kimsuky_diplomats", threshold=1.0
```

The building blocks work for your own chains, too: `socprime::correlate` correlates stage records from any source, such as Sigma findings, raw events, or aggregates, and `socprime::ocsf::finding` turns the chains into Detection Findings. `socprime::native::php2shell` shows a TQL-native chain that follows the exploited process instead of the host, so unrelated activity on a busy web server cannot complete it.

`socprime::enrich` attaches the Active Threats of a rule as OCSF `osint` objects to its findings. The lookup table `socprime-active-threats` holds them; fill it once with `socprime::active_threats`, `socprime::ocsf::map`, and `socprime::update_context`.
