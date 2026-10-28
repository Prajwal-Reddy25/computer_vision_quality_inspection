# Completion report

## Implementation

Completed BGR image validation, HSV red/blue masks, rectangular opening/closing,
external contours, inclusive minimum-area filtering, integer bounding boxes and
deterministic ordering. Directory inspection saves counts, detections and
annotated images. Evaluation saves matches/errors, condition/class summaries,
comparisons and JSON/Markdown reports. Development diagnostics support mask
and pixel inspection without using final labels for tuning.

## Verified execution

- 48 tests passed, zero skipped, in both original and fresh pinned environments.
- All four original test files match the pre-implementation archive byte for byte.
- Development baseline: 35 TP, 21 FP, 2 FN. Selected thresholds: 37/0/0.
- Frozen final set: 30 synthetic images, 74 objects, 74 TP, 0 FP, 0 FN.
- Precision/recall/F1: 1.000; count MAE: 0; correct per-color counts: 30/30 images.
- Nominal/rotation/dim/bright/blue-background groups each contain six images.
- Clean source replay regenerated all images/outputs and exactly matched the
  complete final results JSON. No post-final tuning occurred.
- Six representative final inputs/comparisons and actual development predictions
  are retained. Local documentation links resolve; published PNGs are readable.

## Failures and limits

Development investigation recovered a dim blue part and removed blue-background
false positives. A rejected threshold candidate missed a bright red part.
Separate frozen-detector stress cases show small-object rejection, splitting
by a dark marking, and false localization on a same-color background. No real
camera, manufacturing line or robotic integration was tested. See EVALUATION.md.

## Portfolio and authorship

README, architecture, evaluation protocol/results, environment lock, release
draft and contribution record are prepared. AI generated the code, tests and
executed experiments under student-defined requirements. Independent student
implementation/modification has not yet been demonstrated. CV.md provides two
appropriately attributed bullets and the strongest verified result.

## Learning

LEARNING_GUIDE.md explains the pipeline and supplies ten interview questions.
Three independent exercises cover box centers, a controlled dark-stripe
improvement, and metric/error checking. Record actual personal changes before
strengthening independent-development claims.

## Git and publication

Source, tests, documentation and evidence form the local implementation commit;
use `git log -1 --oneline` for its identifier. The original scaffold checkpoint is retained under ignored artifacts/.
Scratch runs, datasets, environments, caches and credential locations are excluded.
No remote is configured. No push, tag or GitHub release has been performed.
Proposed release: v1.0.0; publication instructions and approval requirements are
in RELEASE_v1.0.0.md. Publishing remains the owner's decision.
