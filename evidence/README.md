# Current synthetic color-and-shape evidence

All images are synthetic. These records replace the earlier rectangle-only
experiment in the current presentation; the prior commit and ignored local
checkpoint preserve that historical evidence.

- frozen.json: new package/config/runtime fingerprint before final generation.
- development_annotations.json / evaluation_annotations.json: complete manifests
  for seeds 31415/271828. Image paths are relative to the regenerated dataset root.
- development/results.json: all 15 selected-configuration results.
- development/color_baseline_results.json: historical-color-threshold ablation
  using the same new shape classifier; 45 TP, 1 FP, 11 FN.
- development/baseline_images and masks: representative baseline errors and stages.
- final/results.json: all 30 final results, boxes, shapes, matches and input hashes.
- final/report.md: generated metrics, including shape/count summaries.
- development/images and final/images: six representative comparisons each;
  full replay generates every comparison.
- stress/: separate post-evaluation limitations demonstrations with explicit shapes.

Current development result is 56/0/0; final is 110/0/0 at strict color+shape
IoU≥0.5 matching. No tuning followed final generation. A clean replay exactly
reproduced the full final JSON. See docs/EVALUATION.md for interpretation.
