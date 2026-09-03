---
title: Behavioral baseline detection operators
type: feature
authors:
  - mavam
  - claude
prs:
  - 185
created: 2026-09-02T18:30:00Z
---

The `tenzir` package now learns per-entity behavioral baselines and turns
unfamiliar feature values into Detection Findings with three composable stages
in the `tenzir::detect::behavior` namespace.

The `model` operator summarizes a stream into one row per entity that holds a
`frequency_table` of a categorical feature, a 24-bin `histogram` of the hour
of day, and the number of observations. Storage stays with the caller, who
appends `context_update` and merges new rows into stored ones with
`model_merge`:

```tql
subscribe "ocsf"
where class_uid == 1007 and activity_id == 1
tenzir::detect::behavior::model entity=device.hostname, feature=process.name
context_update "behavior-baselines", key=entity
```

The `score` operator reads the baseline row that `context_enrich` attached to
each event, classifies it as missing, immature, stale, or ready, and scores
ready events by how familiar the value is and, when the caller supplies a
frequency table of the current window, by Jensen-Shannon drift. The `finding`
operator turns the events that pass the caller's threshold into OCSF Detection
Findings:

```tql
subscribe "ocsf"
where class_uid == 1007 and activity_id == 1
context_enrich "behavior-baselines", key=device.hostname, into=baseline
tenzir::detect::behavior::score feature=process.name
where baseline_status == "ready" and score >= 0.5
tenzir::detect::behavior::finding entity=device.hostname, feature=process.name, feature_name="process.name"
publish "findings"
```

The `feature_name` argument labels the analytic, so findings from separate
deployments carry distinct `finding_info.analytic.uid` values such as
`tenzir::detect::behavior::abnormal_features:process.name`.
