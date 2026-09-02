---
title: Behavioral baseline detection operators
type: feature
authors:
  - mavam
  - claude
prs:
  - 185
created: 2026-09-02T18:23:54Z
---

The `tenzir` package now learns per-entity behavioral baselines and turns
unfamiliar feature values into Detection Findings.

The `tenzir::detect::behavior::learn_baseline` operator folds a stream into a
lookup-table context: for every entity it keeps a `frequency_table` of a
categorical feature, a 24-bin `histogram` of the hour of day, and the number
of observations, merging new windows into the stored models with
`model_merge`. The `tenzir::detect::behavior::abnormal_features` operator
enriches events with their entity's baseline, scores each value by how familiar
it is and by the Jensen-Shannon drift between the current window and the
baseline, and emits a finding once the score crosses a threshold:

```tql
context_create_lookup_table "behavior-baselines"
```

```tql
subscribe "ocsf"
tenzir::detect::behavior::learn_baseline entity=device.hostname, feature=process.name
```

```tql
subscribe "ocsf"
tenzir::detect::behavior::abnormal_features entity=device.hostname, feature=process.name
publish "findings"
```

Both operators take the entity and feature as field arguments and the context
name as a string, and the detector exposes `min_samples`, `max_age`,
`lambda`, `threshold`, and its window settings as named arguments.
