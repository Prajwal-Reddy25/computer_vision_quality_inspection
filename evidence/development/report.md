# Inspection evaluation

Dataset: **SYNTHETIC**, split: development.
Images: 15; same-color AND same-shape matching at IoU >= 0.5.
Metrics below are measured; examples rendered from labels are not predictions.

| Group | TP | FP | FN | Precision | Recall | F1 | Count MAE |
|---|---:|---:|---:|---:|---:|---:|---:|
| overall | 56 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| blue_background | 8 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| bright | 15 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| dim | 9 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| nominal | 10 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| rotation | 14 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |

Exact total counts: 15/15 images.
Exact per-color counts: 15/15 images.
Exact per-shape counts: 15/15 images.
Color-count accuracy: 1.000.
Shape-count accuracy: 1.000.
Count accuracy means the entire per-image count vector is correct, including empty scenes.
A correct count alone does not establish correct localization.

Per-color TP/FP/FN:

- red: 28/0/0
- blue: 28/0/0

Per-shape TP/FP/FN (matches require correct color too):

- rectangle: 19/0/0
- circle: 18/0/0
- triangle: 19/0/0
- unknown: 0/0/0

## Images with errors

See results.json for every box, match, and unmatched index.

No false positives or missed objects at the stated matching threshold.

## Scope

These generated scenes do not establish performance on real production photographs.
Record any post-evaluation changes as a new experiment; do not retune on this final set.
