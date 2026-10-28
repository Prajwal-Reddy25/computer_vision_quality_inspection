"""Real detector integration checks, independent of the original CLI doubles."""

import json
import cv2
import numpy as np
import pytest

from quality_inspection.cli import fingerprint, main


def test_actual_detector_cli_outputs_and_evaluation(tmp_path):
    images = tmp_path / "input"
    images.mkdir()
    image = np.zeros((100, 160, 3), dtype=np.uint8)
    image[20:60, 30:90] = (0, 0, 230)
    assert cv2.imwrite(str(images / "part.png"), image)
    assert cv2.imwrite(str(images / "blank.png"), np.zeros_like(image))
    annotations = {"schema_version": 1, "synthetic": True, "split": "development",
                   "images": [
                       {"file": "part.png", "width": 160, "height": 100,
                        "condition": "nominal", "objects": [
                            {"label": "red", "bbox": [30, 20, 60, 40]}]},
                       {"file": "blank.png", "width": 160, "height": 100,
                        "condition": "nominal", "objects": []}]}
    labels = images / "annotations.json"
    labels.write_text(json.dumps(annotations))
    inspected = tmp_path / "inspected"
    main(["inspect", "--images", str(images), "--output", str(inspected)])
    detections = json.loads((inspected / "detections.json").read_text())
    assert [r["total_count"] for r in detections["images"]] == [0, 1]
    evaluated = tmp_path / "evaluated"
    main(["evaluate", "--annotations", str(labels), "--output", str(evaluated)])
    report = json.loads((evaluated / "results.json").read_text())
    assert (report["overall"]["tp"], report["overall"]["fp"], report["overall"]["fn"]) == (1, 0, 0)
    assert len(list((evaluated / "images").glob("*.png"))) == 2
    assert report["fingerprint"] == fingerprint("config/default.json")


def test_empty_directory_and_unreadable_image_fail(tmp_path):
    images = tmp_path / "images"
    images.mkdir()
    output = tmp_path / "output"
    with pytest.raises(SystemExit) as error:
        main(["inspect", "--images", str(images), "--output", str(output)])
    assert error.value.code == 2
    (images / "broken.png").write_text("not an image")
    with pytest.raises(SystemExit) as error:
        main(["inspect", "--images", str(images), "--output", str(output)])
    assert error.value.code == 2
    assert not output.exists()


def test_source_change_rejects_freeze(tmp_path, monkeypatch):
    from quality_inspection import cli

    original = fingerprint("config/default.json")
    record = tmp_path / "frozen.json"
    record.write_text(json.dumps({"fingerprint": original}))
    changed = dict(original, source_sha256={"detector.py": "changed"})
    monkeypatch.setattr(cli, "fingerprint", lambda config: changed)
    with pytest.raises(ValueError, match="changed since freeze"):
        cli.require_frozen(record, "config/default.json")
