# Inspection evaluation

Dataset: **SYNTHETIC**, split: evaluation.
Images: 30; same-class matching at IoU >= 0.5.
Metrics below are measured; examples rendered from labels are not predictions.

| Group | TP | FP | FN | Precision | Recall | F1 | Count MAE |
|---|---:|---:|---:|---:|---:|---:|---:|
| overall | 74 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| blue_background | 16 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| bright | 8 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| dim | 18 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| nominal | 17 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |
| rotation | 15 | 0 | 0 | 1.000 | 1.000 | 1.000 | 0.000 |

Exact total counts: 30/30 images.
Exact per-color counts: 30/30 images.
A correct count alone does not establish correct localization.

Per-color TP/FP/FN:

- red: 34/0/0
- blue: 40/0/0

## Images with errors

See results.json for every box, match, and unmatched index.

No false positives or missed objects at the stated matching threshold.

## Scope

These generated scenes do not establish performance on real production photographs.
Record any post-evaluation changes as a new experiment; do not retune on this final set.
