# Recorded synthetic evidence

All images here are synthetic. The experiment is reproducible from code and
the pinned environment; see the root README.

- `frozen.json`: package/config/runtime fingerprint recorded before final generation.
- `evaluation_annotations.json`: full 30-image manifest; image paths are relative
  to a regenerated dataset root (`data/evaluation`), not this evidence directory.
- `final/results.json`: every final detection, truth box, match, input hash and metric.
- `final/report.md`: generated metric report.
- `final/images/`: six representative comparisons (one per condition plus an
  empty scene), ground truth above predictions. Full replay writes all 30.
- `representative_inputs/`: matching six original inputs and subset annotations;
  this subset is for illustration, not a separate benchmark.
- `development/`: baseline, rejected candidate and selected results, mask stages,
  pixel statistics and comparisons documenting the threshold decisions.
- `stress/`: three post-evaluation limitations demonstrations with original
  images, annotations, predictions and metrics. They were not used for tuning.

Original baseline/candidate JSON includes the package fingerprints and environment
that existed at the time of those runs. Their historical fingerprints naturally
differ from the finalized package. The selected development record was produced
in the pinned environment before freeze; final report formatting and generator
loop cleanup followed, without detector/configuration changes. The final record
and frozen package fingerprint match.

Large scratch outputs, complete raw datasets, the initial-scaffold checkpoint
and other 24 final comparison PNGs remain under ignored local paths.
