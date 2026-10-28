# Validation record

## Executed checks

- Original scaffold: 16 passed, nine intentional skips.
- Detector implementation: all 25 original tests passed with zero skips.
- Expanded suite: **48 passed, zero skipped**, in both the original system
  environment and a newly created isolated virtual environment.
- Existing four test files were left unchanged. Added 23 cases covering malformed
  arrays, borders/noncontiguous views, contour-area equality, internal holes,
  rotation, order independence, morphology disabling, actual CLI detection,
  unreadable inputs, configuration/annotation validation, diagnostics and freezing.
- Clean environment: CPython 3.12.3, NumPy 2.5.4, OpenCV 4.14.0.94, pytest 9.2.0;
  dependency versions are in `requirements-lock.txt`. `pip check` found no
  broken requirements.
- Original environment: NumPy 1.26.4, OpenCV 4.6.0, pytest 7.4.4.
- The isolated environment initially inherited ROS import/plugin paths from
  `PYTHONPATH`. Clearing that inherited variable fixed collection without adding
  unrelated dependencies or changing any test.

## Complete workflow verification

Executed `scripts/verify_workflow.py` with the pinned virtual environment.
It copied source/config/tests into a temporary directory, ran all 48 tests,
regenerated development images, rendered labels, inspected all 15 images,
evaluated development data, regenerated the same frozen final dataset and
evaluated all 30 images. The entire final `results.json` matched the preserved
record exactly, including input hashes and detections. All 30 comparison PNGs
and all 15 inspection PNGs were produced.

The replay reused the frozen final experiment; it was not another unseen test.
No final-driven code or parameter modifications were made.

## Results and inspection

Development baseline: 35 TP, 21 FP, 2 FN. Selected configuration: 37/0/0.
Final synthetic evaluation: 74/0/0, precision/recall/F1 1.0, count MAE 0,
correct per-color counts on all 30 images. Per-image and per-condition records
are preserved. Development error overlays and representative final dim,
rotation and blue-background outputs were visually inspected.

Three separate synthetic stress examples expose small-part rejection, splitting
by a dark marking and false localization on a same-color background. Those
results are preserved without tuning the frozen algorithm.

## Scope of completion

Application, tests, measured evaluation and reproducible documentation are
complete. Student independent implementation, personal debugging/modification,
and real-camera validation have not been demonstrated. GitHub publication and
release creation remain subject to owner approval.
