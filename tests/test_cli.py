import json

import cv2
import numpy as np
import pytest

from quality_inspection import cli
from quality_inspection.config import load_config
from quality_inspection.models import Detection
from quality_inspection.visualization import read_image


@pytest.fixture
def tiny_dataset(tmp_path):
    root = tmp_path / "dataset"
    root.mkdir()
    image = np.zeros((40, 40, 3), dtype=np.uint8)
    image[5:13, 5:15] = (0, 0, 255)
    assert cv2.imwrite(str(root / "one.png"), image)
    annotations = {"schema_version": 1, "split": "development", "synthetic": True,
                   "images": [{"file": "one.png", "width": 40, "height": 40,
                               "condition": "nominal", "objects": [
                                   {"label": "red", "bbox": [5, 5, 10, 8]}]}]}
    path = root / "annotations.json"
    path.write_text(json.dumps(annotations))
    return root, path


def fixture_detector(image, config):
    """Fixed test double; verifies plumbing, not real detector performance."""
    return [Detection("red", (5, 5, 10, 8))]


def test_inspect_and_evaluate_outputs_with_test_double(tmp_path, tiny_dataset, monkeypatch):
    root, annotations = tiny_dataset
    monkeypatch.setattr(cli, "detect_objects", fixture_detector)
    output = tmp_path / "inspection"
    assert cli.main(["inspect", "--images", str(root), "--output", str(output)]) == 0
    detected = json.loads((output / "detections.json").read_text())
    assert detected["images"][0]["counts"] == {"red": 1, "blue": 0}
    assert read_image(output / "one.png.annotated.png").shape == (40, 40, 3)
    output = tmp_path / "evaluation"
    cli.main(["evaluate", "--annotations", str(annotations), "--output", str(output)])
    report = json.loads((output / "results.json").read_text())
    assert report["overall"]["tp"] == 1
    assert report["overall"]["fp"] == report["overall"]["fn"] == 0
    assert report["images"][0]["matches"][0]["iou"] == 1
    assert report["images"][0]["input_sha256"] == cli.sha256(root / "one.png")
    assert "SYNTHETIC" in (output / "report.md").read_text()
    assert read_image(output / "images/one.png.comparison.png").shape == (80, 40, 3)


def test_labels_work_without_detector(tmp_path, tiny_dataset, monkeypatch):
    _, annotations = tiny_dataset

    def forbidden(*args):
        raise AssertionError("Label rendering must not run the detector")

    monkeypatch.setattr(cli, "detect_objects", forbidden)
    output = tmp_path / "labels"
    cli.main(["labels", "--annotations", str(annotations), "--output", str(output)])
    assert (output / "one.png.labels.png").exists()


def test_detector_failure_does_not_create_results(tmp_path, tiny_dataset, monkeypatch):
    root, _ = tiny_dataset

    def unimplemented(*args):
        raise NotImplementedError("student implementation required")

    monkeypatch.setattr(cli, "detect_objects", unimplemented)
    output = tmp_path / "inspection"
    with pytest.raises(SystemExit) as error:
        cli.main(["inspect", "--images", str(root), "--output", str(output)])
    assert error.value.code == 2
    assert not output.exists()


def test_freeze_and_changed_config_guard(tmp_path, tiny_dataset, monkeypatch):
    _, annotations = tiny_dataset
    monkeypatch.setattr(cli, "detect_objects", fixture_detector)
    config = tmp_path / "config.json"
    config.write_text(json.dumps(load_config("config/default.json")))
    frozen = tmp_path / "frozen.json"
    cli.main(["freeze", "--development", str(annotations), "--config", str(config),
              "--output", str(frozen)])
    assert cli.require_frozen(frozen, config)["iou_threshold"] == 0.5
    changed = load_config(config)
    changed["min_area"] += 1
    config.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match="changed since freeze"):
        cli.require_frozen(frozen, config)
    with pytest.raises(ValueError, match="requires --frozen"):
        cli.require_frozen(None, config)


def test_final_generation_requires_freeze(tmp_path):
    output = tmp_path / "final"
    with pytest.raises(SystemExit) as error:
        cli.main(["generate", "--split", "evaluation", "--output", str(output)])
    assert error.value.code == 2
    assert not output.exists()


def test_out_of_bounds_prediction_rejected(monkeypatch):
    monkeypatch.setattr(cli, "detect_objects", lambda *args: [Detection("red", (30, 30, 20, 20))])
    with pytest.raises(ValueError, match="outside"):
        cli.validated_predictions(np.zeros((40, 40, 3), dtype=np.uint8), {})
