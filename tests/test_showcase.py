import json

import cv2

from quality_inspection.dataset import generate_dataset
from quality_inspection.models import LABELS, SHAPES
from scripts.export_examples import export


def test_stable_showcase_has_both_colors_all_shapes_and_separate_images(tmp_path):
    data = tmp_path / "development"
    generate_dataset(data)
    output = tmp_path / "examples"
    export(data / "annotations.json", "config/default.json", output)
    annotations = json.loads((output / "annotations.json").read_text())
    truth = annotations["images"][0]["objects"]
    predictions = json.loads((output / "detections.json").read_text())["detections"]
    expected = {(color, shape) for color in LABELS for shape in SHAPES}
    assert {(o["label"], o["shape"]) for o in truth} == expected
    assert {(o["label"], o["shape"]) for o in predictions} == expected
    assert len(truth) == len(predictions) == 6
    for filename in ("showcase_ground_truth.png", "showcase_prediction.png"):
        image = cv2.imread(str(output / filename))
        assert image.shape == (360, 480, 3)
