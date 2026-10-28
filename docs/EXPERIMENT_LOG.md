# Experiment log — shapes upgrade

All implementation and execution below were AI-assisted under student requirements.
The previous rectangle experiment remains recoverable at commit 9aef72d and in
an ignored local checkpoint. Its observed final set was not reused for tuning.

## New design

Development seed 31415, final seed 271828. Same five conditions; added circles
and equilateral triangles alongside rectangles. Nonempty scenes contain 3–6
separated objects, both colors and every shape. Image 001 contains all six
color/shape combinations for the README.

Reused prior development-selected HSV settings (red S≥120, blue S≥175, V≥50).
Added fixed shape rules: epsilon/perimeter 0.03, rotated rectangle fill≥0.85,
circle circularity≥0.80. No shape-parameter search was performed.

## Development and baseline comparison

The initial new pipeline matched all 56 objects in 15 images. Shape tests were
added, with no old expectations changed. All 81 tests passed in two environments.

As an ablation, evaluated the historical HSV baseline (S≥120 and V≥80 for both
colors) with the same shape rules on the new development data:
45 TP, 1 FP, 11 FN; precision 0.978261, recall 0.803571, F1 0.882353.
The baseline missed six parts in 006_dim and three in 008_dim.
In 013_blue_background, a full-frame rectangle replaced two actual blue objects.
These failures disappeared with the reused selected HSV settings.

Saved baseline JSON, comparisons and raw/filtered masks. This is a controlled
color-threshold comparison, not a claim that shape classification fixed lighting.

## Freeze and final evaluation

After source/config finalization and tests, froze the new package and generated
the new 30-image final set for the first time. It contained 110 objects:
57 red, 53 blue; 36 rectangles, 37 circles and 37 triangles.
Strict color+shape matching at IoU≥0.5 gave 110 TP / 0 FP / 0 FN.
Every total/color/shape count vector was correct. Minimum matched IoU: 0.8879.

No code or parameter tuning followed final generation/evaluation. Clean replay
reproduced all final JSON values, detections and input hashes exactly.

## Separate limitations demonstrations

Recreated the three deterministic stress examples with explicit shape labels:
small part, dark stripe and same-color background. Frozen detector results:
0 TP, 3 FP, 3 FN in total. They remain separate from the benchmark and caused
no changes. They illustrate why favorable simple synthetic results do not
establish real-camera robustness.
