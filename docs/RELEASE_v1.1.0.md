# Proposed v1.1.0 — Synthetic color and shape inspection

Draft only. No tag, push or release was performed for this upgrade.

- Added red/blue rectangle, circle and triangle generation with schema-v2 labels.
- Added classical polygon/fill/circularity shape rules and unknown predictions.
- Added strict color+shape matching, shape summaries and count-vector accuracies.
- Added a stable six-object README showcase with separate labeled images.
- Preserved all 48 existing tests and expanded coverage to 81 passing tests.
- New frozen final evaluation: 30 images, 110 TP / 0 FP / 0 FN; precision/
  recall/F1 1.000; exact color/shape count vectors on all 30 images.
- Clean replay reproduced complete recorded results.
- Documented synthetic-data limits and AI implementation assistance.

The schema adds shape to detections/annotations. Legacy constructor/schema-v1
rectangle inputs remain supported; new schema-v2 objects require shape.
Evaluation now requires correct color and shape and is stricter than color-only
matching. The new dataset differs from the old benchmark, so scores are not a
direct like-for-like comparison.

Recommended commit:
`Add classical shape inspection and reproducible mixed-object evaluation`

Review local changes before committing. GitHub publication, tags and release
creation require owner approval; do not rewrite or force-push existing history.
