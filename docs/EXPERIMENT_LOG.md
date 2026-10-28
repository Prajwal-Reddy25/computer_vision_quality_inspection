# Experiment log

All work below was AI implemented/executed under the student's requirements.
All images are synthetic. Code/configuration were finalized before the
30-image set was generated. No threshold changes followed final evaluation.

## 1. Baseline on development data

Seed 1729; 15 images; 37 objects. Original HSV saturation/value minima were
120/80 for both classes. Rectangular 3×3 opening then closing, one iteration
each; minimum contour area 400. Hue bounds stayed unchanged throughout.

Measured TP/FP/FN: **35/21/2**. Precision **0.625**, recall **0.945946**,
F1 **0.752688**, count MAE **1.4**. Evidence is in
`evidence/development/baseline_results.json` and baseline comparisons/masks.

- `006_dim.png`: blue inner-patch value percentiles (1/50/99%) around 69/74/78
  were below V≥80. It was rejected before contours. Background values were
  approximately 19/22/26.
- `013_blue_background.png`: the background passed the blue range and connected
  to the part. One full-frame box replaced the true part box: 1 FP and 1 FN,
  despite a correct total count of one.
- `014_blue_background.png`: an empty blue scene yielded 20 accepted components.
  Noise fragmented the thresholded background. Background saturation percentiles
  were approximately 145/155/164.

Comparisons were visually inspected. Raw/filtered masks and numeric observations
are preserved; the diagnostics module can reproduce the observations.

## 2. Rejected development candidate

Tried S≥180 and V≥50 for both classes: **36 TP, 0 FP, 1 FN**, stored in
`candidate_180_results.json`. It rejected a bright red part in `009_bright.png`:
clipping reduced saturation to about 166–170. Rejected before final images existed.

## 3. Selected configuration

Kept red S≥**120**, set blue S≥**175**, and lowered both value minima to **50**.
Blue's cutoff separates observed backgrounds and parts; the value cutoff adds
margin below observed dim parts while rejecting dark background. These are
development choices, not universal color constants. Area, hue and morphology
parameters were unchanged.

Measured **37 TP, 0 FP, 0 FN**, precision/recall/F1 all 1.0, correct per-color
counts on 15/15 development images. This is tuning feedback, not an independent
performance estimate. Verified again in the fresh pinned environment before freeze.

## 4. Frozen final evaluation

See `evidence/frozen.json` for UTC time, configuration, source hashes, environment
and development annotation hash. Final seed **92173**, 30 images, 74 objects:
TP/FP/FN **74/0/0**, precision/recall/F1 **1.0/1.0/1.0**, count MAE **0**,
correct per-color counts **30/30**. No final errors at IoU≥0.5.
Minimum matched IoU: approximately **0.9365**.

Complete JSON results reproduced exactly in a temporary clean source copy.
That replay reused the same experiment; it is not another independent test.

## 5. Post-evaluation limitations demonstrations

Three deterministic stress images were evaluated separately, with no code or
configuration changes. They are outside the benchmark and were not used for tuning:

- 20×20 blue part: contour area 361 < 400; no detection, one FN.
- Five-pixel dark stripe crossing a 60×40 tile: two boxes, both IoU < 0.5;
  two FP and one FN. A 3×3 closing kernel cannot bridge the stripe.
- Highly saturated blue background: the entire frame passes the threshold;
  one FP and one FN. Count is correct but localization is wrong.

See `evidence/stress/`. These cases demonstrate limits of the favorable benchmark
result and remain available for future independent modifications.
