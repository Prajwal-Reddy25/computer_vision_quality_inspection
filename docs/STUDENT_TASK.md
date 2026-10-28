# Independent practice

The detector is AI-assisted and complete for red/blue rectangle, circle and
triangle inspection. Independent student implementation is not claimed.

detect_objects accepts a nonempty uint8 BGR array and validated configuration.
It returns ordered Detection(label, bbox, shape) instances; label is color.
Shapes are rectangle/circle/triangle or unknown for unmatched geometry.
Boxes use integer half-open coordinates and fit inside the image. Invalid image
inputs raise ValueError; valid blank scenes return an empty list.

Read the [learning guide](LEARNING_GUIDE.md), explain thresholds and shape rules,
then implement its exercises without AI-generated code. Preserve test expectations.
Record actual authorship and assistance in CONTRIBUTIONS.md.

Use development/new exercise images. The final set is already observed and is
not an unseen benchmark for future changes.
