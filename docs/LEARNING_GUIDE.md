# Learning and independent modification guide

The implementation is complete and AI-assisted. Your next objective is to
understand, explain and independently modify it. Use development or separate
exercise images; the final set has already been observed and cannot become
unseen again. Do not describe a future improvement against this set as a fresh
unbiased evaluation.

## 1. Follow one image through the repository

Start at `cli.main`: argparse selects a command. `load_config` validates the
JSON settings. `read_image` produces a BGR NumPy array; failed reads raise a
clear error. `detect_objects` returns a list of `Detection` instances.
The CLI derives counts and passes detections to annotation/output helpers.

Evaluation also loads ground truth, matches boxes, and saves numeric errors and
comparison images. Keep image processing separate from I/O: the detector can
be tested with a small array without creating any files.

Read the modules in this order:
`models.py` → `config.py` → `detector.py` → `visualization.py` →
`evaluation.py` → `cli.py`. Then inspect the actual integration tests.

## 2. Python concepts to explain

- A dataclass groups `label` and `bbox`; `frozen=True` prevents reassignment.
  Its validation rejects unknown labels and invalid box coordinates.
- Type hints describe expected types but do not validate values at runtime.
  `validate_image` performs the actual checks.
- Guard clauses reject bad inputs early. Check array type before accessing
  `.ndim`, then dimensions before reading `.shape[2]`.
- Lists hold detections; dictionaries map class names to threshold intervals.
  A loop handles each class instead of duplicating red and blue code.
- `sorted(..., key=...)` returns canonical ordering, independent of contour
  traversal or configuration insertion order.
- Exceptions signal invalid inputs. A valid object-free image returns an empty
  list instead of raising an error.
- `Path` handles paths; JSON stores plain values. NumPy integer scalars are
  explicitly converted to Python integers when constructing boxes.

Explain why returning a fixed count or swallowing every exception would hide
bugs rather than make the detector correct.

## 3. NumPy arrays and coordinates

An image has shape `(height, width, 3)`; index a pixel as `image[y, x]`.
An image slice `image[y:y+h, x:x+w]` uses half-open bounds.
A 60×40-pixel box beginning at (40,30) includes x=40…99 and y=30…69.

The dtype `uint8` represents integers 0…255. Arithmetic can overflow: adding
255-valued masks is not a safe substitute for OR. Use bitwise OR to combine
threshold intervals. A binary mask has shape `(height, width)`.

Slices often share memory with their parent arrays. Assigning to a crop may
change the original image. Use `.copy()` before intentional modification.
Noncontiguous views can have unusual strides; a reversed view is included in
the tests to confirm correct behavior without changing the parent image.

## 4. BGR and HSV

OpenCV's usual loaded channel order is BGR. The pure red pixel [0,0,255]
converts to ordinary 8-bit HSV [0,255,255]. Hue uses 0…179; saturation/value
use 0…255. Hue is circular, so red has intervals near both 0 and 179.

`cv2.cvtColor` changes the representation once per image. `cv2.inRange`
accepts pixels whose three channels all satisfy inclusive bounds.
`threshold_color` combines every interval for one class.

Selected bounds in `config/default.json`:

| Class | Hue | Minimum S | Minimum V |
|---|---|---:|---:|
| Red | 0–10 OR 170–179 | 120 | 50 |
| Blue | 100–130 | 175 | 50 |

Upper saturation/value bounds are 255. These choices came from development
failures, not a universal lookup table. See the baseline and rejected candidate
in the experiment log. Lower V can recover dim parts but admit dark noise.
Higher S can reject a background but lose a clipped bright part. HSV does not
remove illumination, white-balance or reflection effects.

## 5. Morphology and contours

Erosion shrinks foreground regions; dilation expands them. Opening is erosion
then dilation and can remove small speckles. Closing is dilation then erosion
and can fill narrow gaps. The implementation uses a 3×3 rectangular kernel and
one iteration of each, with zero iterations supported as a true no-op.

Predict a kernel's effect before changing it. A larger closing kernel might join
a dark-striped part but also merge two neighboring parts. An opening that is
too large can erase a thin object.

`findContours` traces binary foreground. `RETR_EXTERNAL` keeps outer
boundaries, so an internal hole is not another part. `CHAIN_APPROX_SIMPLE`
compresses redundant boundary points. `contourArea` filters geometry before
`boundingRect` returns an axis-aligned box.

A solid 21×21-pixel square has contour area 20×20=400 and is accepted at
`min_area=400`. A 20×20 square has area 361 and is rejected. This is why box
area and contour area must not be confused. Touching same-color parts can form
one contour; there is no instance-separation or tracking algorithm.

## 6. Evaluation

IoU = intersection area / union area. At IoU≥0.5, matching only allows equal
classes and uses each prediction/annotation once. Maximum-cardinality matching
avoids losing a valid match through an unfortunate greedy assignment.

- TP: matched pair.
- FP: unmatched prediction.
- FN: unmatched annotated object.
- Precision = TP/(TP+FP).
- Recall = TP/(TP+FN).
- F1 = 2TP/(2TP+FP+FN).
- Count error = predicted count − true count.
- Count MAE = mean absolute count error over images.

A red object predicted as blue can produce one FP and one FN while total count
error is zero. Likewise, a full-frame box can have the right count and wrong
location. Empty denominators are undefined, not automatically perfect scores.

Understand both the original matching tests and the real CLI integration test.
The final 74/0/0 result applies only to the documented synthetic distribution.

## 7. Debug systematically

1. Select a development error and write the expected class/box/count first.
2. Inspect shape, dtype and BGR values to rule out loading/indexing mistakes.
3. Inspect HSV pixels in the part and nearby background.
4. Compare raw and filtered masks: was the part rejected by thresholds or lost
   during morphology?
5. Inspect contour areas: was a valid region discarded or a background accepted?
6. Inspect boxes and matched/unmatched indices; count alone is insufficient.
7. Change one factor, keep the old result, rerun regression tests and report the
   tradeoff. Use a new holdout for a later unbiased evaluation.

For development masks and observations:

```bash
python -m quality_inspection.diagnostics --annotations data/development/annotations.json --config config/baseline.json --output runs/my_baseline_diagnostics
```

The diagnostics module rejects an evaluation split. It samples center patches
and background outside boxes; those samples are diagnostic observations, not
pixel-perfect segmentation ground truth.

## 8. Ten interview questions

1. What are an OpenCV image's shape, dtype and channel order? Explain x/y indexing.
2. Why convert BGR to HSV, and why does red need two hue intervals?
3. How would you justify S/V thresholds using foreground/background evidence?
4. Explain opening and closing. What might doubling the kernel size break?
5. Why use external contours? What happens with a hole or two touching parts?
6. Why are contour area and bounding-box area different? Explain rotated boxes.
7. How does one-to-one IoU matching prevent duplicate predictions inflating recall?
8. Give an example with correct total count but wrong precision/recall.
9. Walk through the dim-part or blue-background failure using saved masks.
10. What does the freeze protect, what is data leakage, and why does a perfect
    synthetic result not establish performance on a real camera?

Answer aloud while referring to actual code/evidence, without generated answers.

## 9. Three independent coding exercises

### Exercise A — Derived object locations

Write a separate function that returns each box center and class without changing
the detector. Use floating-point centers and document your coordinate convention.
Check empty input and boxes with odd/even widths. Add your own focused tests.

Evidence to keep: code, coordinate explanation, tests and one plotted example.

### Exercise B — Diagnose and improve the dark-stripe case

Use the supplied stress image plus new development-only marked/unmarked controls.
Explain why one physical part becomes two contours. Independently implement one
small morphology improvement in a separate branch/configuration. Test stripe
widths 3, 5 and 9 pixels and include closely spaced separate parts to reveal
unwanted merging. Do not ask AI for the implementation.

Evidence: baseline and changed masks, box/count results, a regression check and
an explanation of the tradeoff. Do not overwrite the preserved frozen release
or report the observed final set as a new holdout.

### Exercise C — Independent metric checker

Write a function computing precision, recall and F1 from TP/FP/FN, including
undefined cases, and check the baseline numbers by hand. Then write a small
reader that lists images with correct total counts but an FP or FN from an
evaluation JSON file. It should find the same-color-background stress case.

Evidence: your code, hand calculation, tests and a short interpretation.

Record personal work and assistance in CONTRIBUTIONS.md. A completed, explained
exercise commit can support stronger personal CV claims than this AI-generated
implementation alone.
