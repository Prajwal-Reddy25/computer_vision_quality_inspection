# Dataset and evaluation protocol

## Fixed scope

Synthetic top-down rectangular tiles in two color classes. No touching,
occlusion, perspective distortion or defect classification. Object dimensions
are sampled at 45–80 by 30–55 pixels before rotation and integer rasterization.
Six separated placement cells prevent overlaps. An empty scene occurs at every
seventh image index, including index zero: 3/15 development and 5/30 final images.

| Condition | Change from nominal | Development | Final |
|---|---|---:|---:|
| nominal | Gray background; small pixel noise | 3 | 6 |
| rotation | Part angles sampled from −60° to +60° | 3 | 6 |
| dim | Whole-image intensity gain 0.25–0.55 | 3 | 6 |
| bright | Gain 1.3–1.7, with clipping at 255 | 3 | 6 |
| blue_background | Blue background with varying saturation/value | 3 | 6 |

Gaussian pixel noise has standard deviation 2 after intensity scaling. Colors,
sizes, positions and object counts vary independently across images; condition
results are descriptive, not paired causal estimates. Six final images per
condition support a small demonstration, not a precise generalization estimate.
Generation seeds are fixed in source for reproducibility; the split separation
is a development protocol, not secret benchmark protection. Final images were
generated only after freezing; they were not used for threshold selection.

## Annotation convention

`annotations.json` has schema version 1, `synthetic`, `split`, `seed`, and an
`images` list. Each image has a relative file path, width, height, condition and
an `objects` list. Each object has `label` (`red` or `blue`) and `bbox`.

```json
{
  "file": "images/001_nominal.png",
  "width": 480,
  "height": 360,
  "condition": "nominal",
  "objects": [{"label": "red", "bbox": [40, 30, 60, 40]}]
}
```

This fragment illustrates the schema, not a claimed label for that actual file.
Coordinates are integer **[x, y, width, height]**, origin at the top left, x to
the right, y downward. Boxes cover `[x, x + width)` and `[y, y + height)`.
The last included pixel is `(x + width − 1, y + height − 1)`. Boxes are tight,
axis-aligned enclosures of the rasterized geometry, even for rotated tiles.
No annotation confidence scores or defect labels are used. Negative scenes
have an empty `objects` list. No objects are ignored because they became dim.

## One-to-one detection evaluation

1. Match only boxes with the same class and IoU ≥ **0.5**, fixed before evaluation.
2. IoU is intersection area / union area using the half-open box convention.
3. Use maximum-cardinality bipartite matching so valid matches are not lost to a
   greedy assignment. Visit higher IoUs first; the objective is match count,
   not maximum total IoU. No confidence ranking or average precision is claimed.
4. Each matched pair is one true positive (TP). Unmatched predictions are false
   positives (FP); unmatched annotated objects are false negatives (FN).
5. Duplicate boxes cannot match the same object twice. A wrong class can yield
   both one FP and one FN even when the total count happens to be correct.

Precision = TP / (TP + FP). Recall = TP / (TP + FN).
F1 = 2TP / (2TP + FP + FN). Sum counts across images for micro metrics.
Undefined denominators are JSON `null` and displayed as `undefined`.
These definitions do not use true negatives or a loosely defined "accuracy".

Count error is predicted total minus annotated total. Count MAE is the mean
absolute count error per image. Report exact total counts and exact per-color
counts separately. Neither implies correct object locations.

## Experimental sequence

Used all 15 development images for implementation and threshold choices. Kept
the baseline, diagnosed errors and preserved before/after evidence. Ran tests,
froze code/configuration/environment, generated 30 final images and evaluated.
A clean replay verified the same results. Three separate post-evaluation stress
demonstrations exposed limitations without changing parameters. An independent
student improvement remains a future exercise, not a completed contribution.

Final JSON records include source/configuration hashes, library versions,
annotation and image hashes, predictions, ground truth, matching indices, every
image's errors, condition summaries, and per-color TP/FP/FN. PNG comparisons
show ground truth above predictions. Read `results.json` to identify individual
unmatched objects; do not infer correctness from the counts alone.

Write the report interpretation after inspecting actual results. Preserve
failures even if embarrassing. Future tuning after observing the final set
needs a new independently held-out set; a different seed alone is not proof
of independence if chosen based on favorable results.
