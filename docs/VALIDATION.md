# Validation record — color and shape scope

## Tests

Executed **81 tests, all passed, zero skipped** in both:

- Pinned CPython 3.12.3 / NumPy 2.5.4 / OpenCV 4.14.0.94 / pytest 9.2.0.
- Original environment: NumPy 1.26.4 / OpenCV 4.6.0 / pytest 7.4.4.

All 48 pre-upgrade cases are unchanged. The 33 new cases cover both colors and
three shapes at three rotations, mixed six-object scenes, deterministic ordering,
unsupported/degenerate geometry, shape-aware matching/count metrics, schema-v2
labels, heuristic settings, actual generated-data evaluation and showcase export.
Original input/blank/border/area/integration/freeze checks still run.

## Full replay

Executed scripts/verify_workflow.py in a temporary clean source copy containing
package, config, tests and scripts. It ran all 81 tests, generated 15 development
images, rendered labels, inspected all images, exported the six-object example,
evaluated development data, regenerated the frozen final set and evaluated all
30 final images. Complete final results JSON matched the preserved record exactly.

Replaying observed final images is reproducibility, not another independent
experiment. The final set was first generated only after freezing; no parameters
or package source changed afterward.

## Measured data

New development: 56 TP / 0 FP / 0 FN over 15 images.
New final: 110 TP / 0 FP / 0 FN over 30 images.
Precision/recall/F1 1.000, exact total/color/shape counts on every image.
Historical color-baseline ablation on new development data: 45 TP / 1 FP / 11 FN.
Separate stress cases retain clear failures without changing the frozen pipeline.

The six-object Ground Truth/Prediction images were visually inspected and show
both colors and all shapes. No real-camera validation or independent student
implementation is implied.
