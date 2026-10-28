# Dataset and evaluation protocol

## Synthetic design

Red/blue rectangles, circles and equilateral triangles in 480×360 images.
Shapes are flat filled geometry, not photographs. There are no touching parts,
occlusion, perspective or defect labels. Placement in six separated cells keeps
bounding boxes apart.

Development uses seed **31415**, 15 images; final uses seed **271828**, 30 images.
These are new seeds and datasets, separate from the earlier rectangle experiment.
Both use the same generation rules. An empty scene occurs at indices divisible
by seven: 3/15 development and 5/30 final images. Nonempty scenes contain 3–6
parts, both colors and every shape. Index 001 has six parts, covering all six
color/shape combinations for a stable presentation example.

Rectangles have sampled width 60–80 and height 35–55 pixels before rasterization.
Circles use radius floor(width/2); triangles use circumradius width/2.
Triangles/circles therefore do not share the rectangle height parameter.
Boxes come from each rendered binary geometry mask before lighting/noise changes.

| Condition | Variation | Development | Final |
|---|---|---:|---:|
| nominal | Gray background, small pixel noise | 3 | 6 |
| rotation | Rectangle/triangle angles −60° to +60°; circles invariant | 3 | 6 |
| dim | Global intensity gain 0.25–0.55 | 3 | 6 |
| bright | Gain 1.3–1.7 and clipping at 255 | 3 | 6 |
| blue_background | Varying blue background saturation/value | 3 | 6 |

Gaussian pixel noise has standard deviation 2. Balanced coverage makes these
small scenes educational; it is not a realistic production frequency model.
Condition groups vary in counts/colors/shapes, so they are not paired causal
experiments. Six images per condition cannot establish broad generalization.

## Annotation format

Schema version **2** stores synthetic, split, seed and images metadata.
Each object has a color `label`, a `shape`, and `bbox`:

```json
{"label": "blue", "shape": "triangle", "bbox": [40, 30, 60, 50]}
```

This is a format example, not a claimed label for a particular file.
Boxes are integer [x,y,width,height], origin top left, x rightward, y downward.
They cover [x,x+width) and [y,y+height). Ground-truth shapes must be rectangle,
circle or triangle. Detections may use unknown; unknown never matches a supported
ground-truth shape.

A zero-object scene has an empty objects list. Labels describe physical presence,
even if lighting makes segmentation difficult. Legacy schema-v1 rectangles and
two-argument Detection calls remain supported; v2 rejects missing shape labels.

## Matching and metrics

Only pairs with the same **color and shape** and IoU ≥ **0.5** can match.
IoU = intersection area / union area under half-open coordinates. Maximum-
cardinality bipartite matching maximizes valid pair count, visiting larger IoUs
first; it does not maximize summed IoU or compute average precision.

Each pair is one TP. Unmatched predictions are FP; unmatched objects are FN.
Duplicates cannot match the same object twice. Wrong shape or wrong color can
produce both an FP and an FN despite a correct total count.

- Precision = TP/(TP+FP).
- Recall = TP/(TP+FN).
- F1 = 2TP/(2TP+FP+FN).
- Count error = predicted total − annotated total.
- Count MAE = mean absolute count error per image.

Metrics are micro-aggregated; zero denominators are undefined (JSON null).
Exact-count images require correct total counts.
**Color-count accuracy** is the fraction of images with the entire red/blue
count vector correct. **Shape-count accuracy** requires the entire rectangle/
circle/triangle/unknown vector correct; truth unknown count is always zero.
These metrics include blank scenes. They are image-level marginal count metrics,
not object classification accuracy; correct marginal counts do not guarantee
correct color-shape associations or localization.

## Frozen experiment

Reused the previous development-selected HSV settings and checked fixed shape
heuristics on the new development data and regression tests. Compared the old
color-threshold baseline on the new data as an ablation. Then froze the new
package/config/runtime before generating or inspecting the new final images.
No code or parameter tuning followed final evaluation.

A clean replay reproduced the complete results JSON. Replaying the same seed
is reproducibility, not another independent trial. Generator seeds are public;
holdout separation is a documented workflow. Future tuning needs fresh final
data, not relabeling or repeatedly testing the observed set.
