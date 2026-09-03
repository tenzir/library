---
title: Categorical behavioral baseline operators
type: feature
authors:
  - mavam
  - claude
prs:
  - 185
created: 2026-09-02T18:30:00Z
---

The `tenzir` package now provides four composable operators for categorical
behavioral baselines in the `tenzir::detect::behavior::categorical` namespace.
Each operator has one responsibility: `model` builds a baseline from a finite
population, `merge` combines it with an earlier baseline, `score` writes a
namespaced result onto each event, and `finding` turns that result into an OCSF
Detection Finding.

The caller defines the observation population and storage lifecycle. For an
unbounded stream, place `model` inside an explicit window before merging and
storing the baseline:

```tql
subscribe "ocsf"
where class_uid == 1007 and activity_id == 1
window size=5min, on=time, tolerance=1min, idle_timeout=5min {
  tenzir::detect::behavior::categorical::model \
    entity=device.hostname,
    feature=process.name
}
context_enrich "process-name-baselines", key=entity, into=previous
tenzir::detect::behavior::categorical::merge baseline, previous
context_update "process-name-baselines", key=entity, value=baseline
```

The `score` operator classifies a baseline as missing, immature, stale, or
ready. It measures how familiar the feature value is and can mix that local
score with Jensen-Shannon drift from a current frequency table. The result goes
into a caller-selected field, so several behavioral detectors can score the
same event without colliding:

```tql
context_enrich "process-name-baselines",
  key=device.hostname,
  into=baseline
tenzir::detect::behavior::categorical::score \
  feature=process.name,
  baseline=baseline,
  into=behavior
where behavior.status == "ready" and behavior.score >= 0.5
tenzir::detect::behavior::categorical::finding \
  entity=device.hostname,
  feature=process.name,
  feature_name="process.name",
  result=behavior
```

The baseline uses the frequency table's own `count` as its sample count, so
null feature values cannot make an empty model ready. The `drift_weight`
argument must stay between `0.0` and `1.0`, which keeps the composite score and
the resulting OCSF risk score bounded.
