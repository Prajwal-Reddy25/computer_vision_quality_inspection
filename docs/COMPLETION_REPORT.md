# Color-and-shape upgrade completion report

## Code changes

Added shape labels to Detection and schema-v2 annotations. Geometry generation
now renders rectangles, circles and triangles with independent color labels,
multiple parts and the previous five lighting/background conditions. New seeds
31415/271828 separate this experiment from the old observed rectangle set.

The detector preserves HSV/morphology/contour filtering and adds simple polygon,
rotated-fill and circularity rules, with an unknown outcome for unsupported
contours. Outputs include color/shape labels, total/color/shape counts and boxes.
Matching now requires both labels. Reports add shape metrics and exact-vector
color-count/shape-count accuracy.

The README has a stable six-object development example: both colors and all
three shapes, with separate Ground Truth and Prediction PNGs and one blank line
between the image Markdown lines.

## Executed verification

- **81 passed, zero skipped**, in pinned and original environments.
- All 48 pre-upgrade test cases/files preserved unchanged.
- Added 33 cases for shapes/colors/rotation, mixed scenes, geometry rejection,
  strict matching/counts, schema/config validation, integration and showcase assets.
- Development: 15 images, 56 objects, 56 TP / 0 FP / 0 FN.
- Final: 30 new images, 110 objects, 110 TP / 0 FP / 0 FN.
- Precision/recall/F1: 1.000 for both sets.
- Color-count accuracy and shape-count accuracy: 100% for both sets.
- Exact total counts: 15/15 development, 30/30 final; count MAE zero.
- Clean-source replay reproduced the complete final JSON and expected files.
- No code or parameter tuning after freeze/final generation.

## Limitations and authorship

All data is synthetic. Shape heuristics, HSV bounds and contour-area filtering
are intentionally limited. Touching objects, shadows, small parts and similar
backgrounds can fail; ellipses/polygons can confuse the shape rules.
Real-camera or industrial robustness is not claimed.

AI implemented this upgrade under student-defined scope and requirements.
Independent student coding remains to be demonstrated. CV.md preserves this
distinction.

## Repository handoff

Changed areas: models, dataset, detector, config, evaluation, CLI, visualization,
reporting, export/replay/stress scripts, new tests, example assets, evidence and
affected documentation. Previous tracked records are recoverable from commit
9aef72d; an ignored local checkpoint also preserves old source and artifacts.

Recommended commit message:
`Add classical shape inspection and reproducible mixed-object evaluation`

This upgrade is left reviewable as local changes. No commit, push, tag or release
was made for this upgrade. Proposed version: v1.1.0; publication needs approval.
