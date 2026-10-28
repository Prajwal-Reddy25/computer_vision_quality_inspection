# Inspection evaluation

Dataset: **SYNTHETIC**, split: development.
Images: 3; same-color AND same-shape matching at IoU >= 0.5.
Metrics below are measured; examples rendered from labels are not predictions.

| Group | TP | FP | FN | Precision | Recall | F1 | Count MAE |
|---|---:|---:|---:|---:|---:|---:|---:|
| overall | 0 | 3 | 3 | 0.000 | 0.000 | 0.000 | 0.667 |
| dark_stripe | 0 | 2 | 1 | 0.000 | 0.000 | 0.000 | 1.000 |
| same_color_background | 0 | 1 | 1 | 0.000 | 0.000 | 0.000 | 0.000 |
| small_part | 0 | 0 | 1 | undefined | 0.000 | 0.000 | 1.000 |

Exact total counts: 1/3 images.
Exact per-color counts: 1/3 images.
Exact per-shape counts: 1/3 images.
Color-count accuracy: 0.333.
Shape-count accuracy: 0.333.
Count accuracy means the entire per-image count vector is correct, including empty scenes.
A correct count alone does not establish correct localization.

Per-color TP/FP/FN:

- red: 0/0/0
- blue: 0/3/3

Per-shape TP/FP/FN (matches require correct color too):

- rectangle: 0/3/3
- circle: 0/0/0
- triangle: 0/0/0
- unknown: 0/0/0

## Images with errors

See results.json for every box, match, and unmatched index.

- images/small_part.png (small_part): FP=0, FN=1, count error=-1.
- images/dark_stripe.png (dark_stripe): FP=2, FN=1, count error=+1.
- images/same_color_background.png (same_color_background): FP=1, FN=1, count error=+0.

## Scope

These generated scenes do not establish performance on real production photographs.
Record any post-evaluation changes as a new experiment; do not retune on this final set.
