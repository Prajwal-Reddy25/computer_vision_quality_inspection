# Color-and-shape evaluation

All images are **synthetic**. No real camera or manufacturing system was tested.
The new benchmark covers red and blue rectangles, circles and triangles.

## Procedure and results

Development: 15 images, seed 31415, 56 objects.
Final: 30 new images, seed 271828, 110 objects.
Code/configuration/runtime were frozen in [evidence/frozen.json](../evidence/frozen.json)
before final generation. No final-driven tuning occurred.

Matching requires correct color AND shape plus IoU≥0.5, one-to-one.
See the [metric definitions](DATASET_AND_EVALUATION.md).

| Experiment | TP | FP | FN | Precision | Recall | F1 | Count MAE |
|---|---:|---:|---:|---:|---:|---:|---:|
| New development, historical HSV baseline | 45 | 1 | 11 | 0.9783 | 0.8036 | 0.8824 | 0.6667 |
| New development, selected HSV + shape rules | 56 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| New frozen final | 110 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

The historical baseline uses the same new shape classifier with the old color
bounds S≥120/V≥80. The selected configuration reuses prior development-selected
HSV values; no new threshold search was performed. The comparison is an ablation,
not evidence that changing polygon rules caused the color improvements.

| Count metric | Development | Final |
|---|---|---|
| Exact total-count images | 15/15 | 30/30 |
| Exact color-count images / accuracy | 15/15 / 100% | 30/30 / 100% |
| Exact shape-count images / accuracy | 15/15 / 100% | 30/30 / 100% |

Count accuracy measures full per-image marginal vectors, including empty scenes.
Final has 25 nonempty and five empty scenes. All 57 red and 53 blue objects
matched. By shape: 36 rectangles, 37 circles, 37 triangles. No unknown predictions.
Minimum matched final IoU was approximately **0.8879**, illustrating small box
changes from rasterization/morphology despite successful matching.

| Final condition | Images | Objects / TP | FP | FN | Precision / recall / F1 |
|---|---:|---:|---:|---:|---|
| Nominal | 6 | 24 | 0 | 0 | 1.000 / 1.000 / 1.000 |
| Rotation | 6 | 21 | 0 | 0 | 1.000 / 1.000 / 1.000 |
| Dim | 6 | 20 | 0 | 0 | 1.000 / 1.000 / 1.000 |
| Bright | 6 | 22 | 0 | 0 | 1.000 / 1.000 / 1.000 |
| Blue background | 6 | 23 | 0 | 0 | 1.000 / 1.000 / 1.000 |

Full [final results](../evidence/final/results.json),
[generated report](../evidence/final/report.md), and
[annotation manifest](../evidence/evaluation_annotations.json) are preserved.
Manifest image paths refer to the regenerated dataset root.
Representative comparisons are retained; replay generates all 30.

## Observed development failures in the color baseline

- 006_dim: all six objects missed because the high V threshold rejected them.
- 008_dim: all three objects missed.
- 013_blue_background: a full-frame blue rectangle replaced two actual blue
  objects (circle and rectangle): one FP, two FN. Two red objects still matched.

Before/after comparisons and mask stages are retained in evidence/development/.
No current final false positives or misses occurred at the stated criterion.
These new results are separate from the old rectangle experiment in commit
9aef72d; they should not be presented as a direct like-for-like improvement.

## Limits and explicit failures

The frozen pipeline was also run on three separate deterministic stress cases,
without parameter changes: a 20×20 part is rejected (one FN); a five-pixel dark
stripe creates two boxes (two FP, one FN); a saturated blue background becomes
one full-frame box (one FP, one FN). They are outside the benchmark, not another
random generalization estimate.

Geometry heuristics can confuse ellipses or rounded regular polygons with
circles, or some quadrilaterals with rectangles. Unknown geometry is retained
as unknown when no rule passes; this is not a general-purpose shape recognizer.
Touching parts may merge, shadows/markings may split shapes, and morphology may
remove triangle tips or distort circular boundaries. Area depends on image scale.

Balanced, isolated, filled synthetic shapes are deliberately easy. There are
only six images per condition, no occlusion/perspective, and no real optics,
material variation, texture or camera calibration. A real deployment requires
new labeled photographs, development and holdout data, and fresh validation.
