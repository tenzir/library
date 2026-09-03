---
title: Categorical behavioral baseline operators
type: feature
authors:
  - mavam
prs:
  - 185
created: 2026-09-02T18:30:00Z
---

The `tenzir` package now provides three composable operators for categorical
behavioral baselines in the `tenzir::detect::behavior::categorical` namespace.
Two records form the contract between them:

- `model` summarizes a finite input into one row per entity of the shape
  `{entity, baseline: {distribution: <frequency_table>, trained_at: <time>}}`.
- `score` reads such a `baseline` record from the event and writes
  `{status, baseline_count, familiarity, drift, score}` into a caller-selected
  field.
- `finding` reads that result and emits an OCSF Detection Finding.

Storage stays in the caller's pipeline. Whether a freshly modeled baseline
replaces the stored row or accumulates into it is one line:
`baseline.distribution = model_merge([previous?.distribution?, baseline.distribution])`.
The package also provides the `process-name-baselines` lookup-table context.

For an unbounded stream, score each window before you merge its observations
into the context. Keeping both steps in one pipeline prevents the current window
from training its own baseline:

```tql
subscribe "ocsf"
where class_uid == 1007 and activity_id == 1
window size=5min, on=time, tolerance=1min, idle_timeout=5min {
  summarize device.hostname,
            current=frequency_table(process.name),
            options={output: "events"}
  start = $window.start
  end = $window.end
  context_enrich "process-name-baselines",
    key=device.hostname,
    into=baseline
  tenzir::detect::behavior::categorical::score \
    feature=process.name,
    baseline=baseline,
    current=current,
    into=behavior
  fork {
    where behavior.status == "ready" and behavior.score >= 0.5
    tenzir::detect::behavior::categorical::finding \
      entity=device.hostname,
      feature=process.name,
      feature_name="process.name",
      result=behavior,
      start=start,
      end=end
    deduplicate finding_info.uid, create_timeout=1h
    publish "findings"
  }
  tenzir::detect::behavior::categorical::model \
    entity=device.hostname,
    feature=process.name
  context_enrich "process-name-baselines", key=entity, into=previous
  baseline.distribution = model_merge([
    previous?.distribution?,
    baseline.distribution,
  ])
  drop previous
  context_update "process-name-baselines", key=entity, value=baseline
}
```

The `score` operator classifies an observation as missing, immature, stale, or
ready. It leaves observations with a null feature value unscored. For ready
observations, it measures how familiar the feature value is and can mix that
local score with Jensen-Shannon drift from a current frequency table. The result
goes into a caller-selected field, so several behavioral detectors can score the
same event without colliding.

The `finding` operator accepts optional `start` and `end` fields for the scoring
window. With them, it populates `start_time` and `end_time` and derives
`finding_info.uid` from the analytic, entity, value, and window end, so repeated
launches of the same unfamiliar value within one window share one identity that
`deduplicate finding_info.uid` collapses. Without a window, the identifier is a
random UUID. The analytic carries `type_id: 2` (Behavioral) and
`uid: tenzir::detect::behavior::abnormal_features:<feature_name>`.

The baseline uses the frequency table's own `count` as its sample count and
ignores observations without an entity identifier or feature value. Empty
windows therefore neither make a model ready nor refresh an existing baseline.
The `min_samples` argument must be positive. The `drift_weight` argument must
stay between `0.0` and `1.0`, which keeps the composite score and the resulting
OCSF risk score bounded.
