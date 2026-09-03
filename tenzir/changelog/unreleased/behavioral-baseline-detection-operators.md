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
- `score` reads such a `baseline` record from the event and writes a
  self-describing result `{feature, entity, value, status, baseline_count,
  familiarity, drift, score}` into a caller-selected field. With
  `window_size`, it also models each entity's current window, mixes its
  Jensen-Shannon drift into the score, and records the window as
  `{start, end}` in the result.
- `finding` turns that result into an OCSF Detection Finding. Without
  arguments it replaces the event, like the `normalize` operators of our
  source packages; with `into`, it writes the finding next to the event.

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
context_enrich "process-name-baselines",
  key=device.hostname,
  into=baseline
tenzir::detect::behavior::categorical::score \
  entity=device.hostname,
  feature=process.name,
  feature_name="process.name",
  baseline=baseline,
  window_size=5min,
  into=behavior
fork {
  where behavior.status == "ready" and behavior.score >= 0.5
  tenzir::detect::behavior::categorical::finding result=behavior
  deduplicate finding_info.uid, create_timeout=1h
  publish "findings"
}
window size=1min {
  tenzir::detect::behavior::categorical::model \
    entity=device.hostname,
    feature=process.name
}
context_enrich "process-name-baselines", key=entity, into=previous
baseline.distribution = model_merge([
  previous?.distribution?,
  baseline.distribution,
])
drop previous
context_update "process-name-baselines", key=entity, value=baseline
```

The `score` operator classifies an observation as missing, immature, stale, or
ready. It leaves observations with a null feature value unscored. For ready
observations, it measures how familiar the feature value is and, when
`window_size` is set, mixes that local score with the drift of the entity's
current window from the baseline. A window delays each event until the window
closes. The result goes into a caller-selected field, so several behavioral
detectors can score the same event without colliding; set `feature_name` per
detector so each one identifies its own analytic.

The `finding` operator reports a scored window as `start_time` and `end_time`
and derives `finding_info.uid` from the analytic, entity, value, and window
end, so repeated launches of the same unfamiliar value within one window share
one identity that `deduplicate finding_info.uid` collapses. Without a window,
the identifier is a random UUID. The analytic carries `type_id: 2` (Behavioral)
and `uid: tenzir::detect::behavior::abnormal_features:<feature_name>`.

The baseline uses the frequency table's own `count` as its sample count and
ignores observations without an entity identifier or feature value. Empty
windows therefore neither make a model ready nor refresh an existing baseline.
The `min_samples` argument must be positive. The `drift_weight` argument must
stay between `0.0` and `1.0`, which keeps the composite score and the resulting
OCSF risk score bounded.
