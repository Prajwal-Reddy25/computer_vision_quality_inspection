# Synthetic development examples

These two inputs are fixed-seed development examples, not photographs.

| Example | Input | Ground-truth preview | Actual detector output |
|---|---|---|---|
| Nominal | [Input](images/001_nominal.png) | [Labels](ground_truth/001_nominal.png.labels.png) | [Prediction](predictions/001_nominal.png.annotated.png) |
| Rotation | [Input](images/003_rotation.png) | [Labels](ground_truth/003_rotation.png.labels.png) | [Prediction](predictions/003_rotation.png.annotated.png) |

Ground-truth previews are annotations, not predictions. The separate predictions
directory contains real executed detector output and counts in detections.json.
Both examples are development data, not independent final performance evidence.
The annotation subset is compatible with the labels/evaluate commands.

Regenerate the original development set from seed 1729 using the root README.
The same filenames identify the inputs. For final representative inputs and
ground-truth/prediction comparisons, see evidence/ and its README.
