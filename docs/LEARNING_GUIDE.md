# Learning and interview guide

This is an AI-assisted implementation. Study and independently modify it before
claiming personal proficiency. Use development/exercise data; the final set has
already been observed.

## Architecture and Python

Follow models → config → detector → evaluation → CLI. Detection is a frozen
dataclass with color label, integer box and shape. Type hints document intent;
runtime checks enforce valid arrays, parameters and annotations. The detector
has no file I/O. CLI functions derive counts, load/save images and assemble reports.
A sorted result is deterministic even if contour/config traversal order changes.

Schema-v2 objects require shape explicitly. Legacy two-argument Detection and
schema-v1 annotations assume rectangle for compatibility only.

## NumPy, color and morphology

Images are uint8 arrays of shape (height,width,3), indexed image[y,x] in BGR order.
Slices often share memory; copy before modifying a crop. uint8 arithmetic can
overflow, so combine threshold masks with bitwise OR rather than addition.

BGR→HSV conversion separates hue, saturation and value. Ordinary uint8 OpenCV
hue uses 0–179; S/V use 0–255. Red crosses the hue boundary and needs two
intervals. inRange requires all three channels within inclusive bounds.
HSV does not remove lighting, clipping, reflection or white-balance effects.

Opening erodes then dilates; closing dilates then erodes. Kernel scale controls
which speckles/gaps disappear. Larger kernels may merge parts or erase triangle
tips. Zero iterations is a no-op. Current settings use a rectangular 3×3 kernel.

## Contours, geometry and boxes

External contours describe outer boundaries, not internal holes. Contour area
filters tiny regions; it differs from pixel count and bounding-box area.
A solid 21×21 square has contour area 400; a 20×20 square has area 361.
The minimum accepted area is 400.

approxPolyDP simplifies a contour using epsilon=0.03×perimeter. Three convex
vertices indicate triangle; four plus rotated fill≥0.85 indicate rectangle.
At least five convex approximated vertices plus 4πA/P²≥0.80 indicate circle.
Otherwise shape is unknown. Explain why an ellipse or regular polygon might
still pass the circle rule, and why some trapezoids can pass the rectangle rule.

boundingRect always returns an axis-aligned [x,y,width,height] box, including
for rotated objects. Masks filtered by morphology may yield slightly smaller
boxes than rendered ground truth. Color/shape counts are derived from the list.

## Evaluation

At IoU≥0.5, valid matches require both color and shape. One-to-one maximum-
cardinality matching prevents duplicates from inflating recall.
Precision=TP/(TP+FP), recall=TP/(TP+FN), F1=2TP/(2TP+FP+FN).
Undefined denominators are null. Count MAE averages absolute total-count errors.

Color-count accuracy requires every image-level color count correct; shape-count
accuracy requires every shape count correct, including unknown count zero.
Correct total or marginal counts do not prove correct associations/localization.
The 110/0/0 result covers only the documented synthetic generator.

## Failure investigation

State the expected color, shape and box first. Inspect input dtype/channel order,
HSV pixels, raw mask, filtered mask, contour area, approximation vertex count,
rectangle fill and circularity. Identify the first failing stage before changing
a parameter. Save one-factor before/after results and rerun regressions.

```bash
python -m quality_inspection.diagnostics --annotations data/shapes_development/annotations.json --config config/baseline.json --output runs/my_diagnostics
```

Diagnostic center patches are samples, not exact foreground segmentation labels.
The module rejects final data for tuning. For future unbiased evaluation, freeze
the changed algorithm before generating new independent final images.

## Ten technical interview questions

1. Explain NumPy image shape, dtype, BGR order and x/y indexing.
2. Why use HSV, and why does red need two hue intervals?
3. How can increasing saturation reject a blue background yet lose a bright part?
4. Explain opening/closing and their effect on triangle tips and touching parts.
5. Why external contours, and how does contour area differ from box area?
6. How does polygon approximation identify triangles and candidate rectangles?
7. Derive circularity for an ideal circle and explain its limitations on ellipses/polygons.
8. Why require both color and shape in matching? Give a correct-count but wrong-label example.
9. Explain image-level color/shape count accuracy versus object precision/recall.
10. What does the freeze protect, and what cannot synthetic holdout results establish?

## Three independent coding exercises

1. **Locations and count table:** write a function returning box centers and a
   color×shape count table. Handle blank inputs and odd/even box sizes. Add tests
   without changing the detector.
2. **Dark stripe diagnosis:** explain the supplied stripe failure, then independently
   modify morphology on a separate branch/config. Try stripe widths 3,5,9 and
   closely spaced separate parts. Preserve baseline/results and discuss merging.
3. **Shape diagnostics:** independently write a helper reporting vertex count,
   circularity and rotated fill. Use circles, ellipses, triangles and trapezoids
   to find one misclassification. Explain a possible improvement and test a
   personal implementation on development-only cases, without generated code.

Record dates, code, tests, reasoning and assistance. Preserve the frozen experiment
and use a new holdout for future modified algorithms.
