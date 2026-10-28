# Student practice after AI-assisted completion

The original workflow reserved the detector for student implementation.
The owner subsequently explicitly authorized AI completion of remaining code.
The detector is now implemented and tested; this file no longer asks the
student to replace a placeholder.

## Detector contract

`detect_objects(bgr, config)` accepts a nonempty uint8 NumPy array of shape
(height,width,3), in BGR order, plus a configuration validated by load_config.
Invalid image type/shape/dtype/size raises ValueError. A valid blank scene returns
an empty list. Input pixels are unchanged.

Return a deterministic list of Detection(label, (x,y,width,height)) instances,
ordered by label, y, x, width and height. Labels are red or blue, coordinates
are Python integers, widths/heights are positive and boxes fit inside the image.
Coordinates use half-open bounds. Accept external contours with area ≥ min_area.

## Independent work remains valuable

Study the [learning guide](LEARNING_GUIDE.md), explain the implementation, and
complete its three exercises without AI-generated code. Preserve existing test
expectations. Record your actual changes, diagnosis and assistance rather than
claiming the current implementation as independent work.

Use development/additional exercise data for experiments. The 30-image final
set has already been generated and evaluated after freezing; do not reuse it
as an unseen test for future improvements.
