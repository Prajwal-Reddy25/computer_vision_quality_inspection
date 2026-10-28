# Inspection evaluation

Dataset: **SYNTHETIC**, split: evaluation.
Images: 30; same-color AND same-shape matching at IoU >= 0.5.
Metrics below are measured; examples rendered from labels are not predictions.

| Group | TP | FP | FN | Precision | Recall | F1 | Count MAE |
|---|---:|---:|---:|---:|---:|---:|---:|
| overall | 110 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| blue_background | 23 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| bright | 22 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| dim | 20 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| nominal | 24 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| rotation | 21 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |

Exact total counts: 30/30 images.
Exact per-color counts: 30/30 images.
Exact per-shape counts: 30/30 images.
Color-count accuracy: 1.000.
Shape-count accuracy: 1.000.
Count accuracy means the entire per-image count vector is correct, including empty scenes.
A correct count alone does not establish correct localization.

Per-color TP/FP/FN:

- red: 57/0/0
- blue: 53/0/0

Per-shape TP/FP/FN (matches require correct color too):

- rectangle: 36/0/0
- circle: 37/0/0
- triangle: 37/0/0
- unknown: 0/0/0

## Images with errors

See results.json for every box, match, and unmatched index.

No false positives or missed objects at the stated matching threshold.

## Scope

These generated scenes do not establish performance on real production photographs.
Record any post-evaluation changes as a new experiment; do not retune on this final set.
