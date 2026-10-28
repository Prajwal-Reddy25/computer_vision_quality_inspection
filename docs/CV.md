# Portfolio and CV wording

## Project heading

**Computer Vision Quality Inspection — Python & OpenCV (AI-assisted project)**

## Two concise CV bullets

- Specified an AI-assisted Python/OpenCV inspection project to segment, count and
  locate red and blue parts using HSV thresholds, morphology and contour analysis.
- Required a separate development/holdout evaluation: the frozen pipeline matched
  all 74 objects in 30 synthetic images (IoU ≥ 0.5; precision/recall/F1 1.00), with
  documented lighting/background failures and 48 passing tests.

These bullets deliberately describe the verified requirements and the repository
result. They do not claim independent student code authorship or personal
debugging. Revise them after completing and recording your own modifications.

## Technologies

Python, OpenCV, NumPy, pytest, Git; JSON configuration/annotations and a CLI.

## Strongest verified result

All 74 labeled parts matched on the separate 30-image synthetic set after
development-only parameter selection; no FP or FN at same-class IoU≥0.5.
The full result reproduced exactly in a clean source replay.

## Personal contribution and attribution

Verified student contribution: project scope, requirements, tool constraints,
experimental requirements and direction. AI generated the implementation,
tests, threshold investigation, evaluation execution and documentation.
No independently written student implementation is recorded yet.

## Capabilities demonstrated by the repository

- Classical color segmentation and contour-based localization.
- Input validation, deterministic results and structured Python functions.
- Unit, boundary and real-detector integration testing.
- Labeled datasets, one-to-one matching and precision/recall/F1 evaluation.
- Lighting/background failure investigation and explicit limitations.
- Frozen experiments, recorded provenance and reproducible command-line use.

These are repository capabilities, not proof of personal proficiency. Use the
learning guide and commit your own explained change before claiming them as
independent skills. No robotics integration, real manufacturing deployment,
deep learning or camera-based validation should be claimed.
