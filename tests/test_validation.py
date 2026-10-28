import json

import pytest

from quality_inspection.config import load_config
from quality_inspection.dataset import load_annotations
from quality_inspection.diagnostics import save_diagnostics


@pytest.mark.parametrize("key,value", [("kernel_size", 0), ("kernel_size", 2),
                                       ("min_area", -1), ("open_iterations", True)])
def test_bad_filter_configuration(tmp_path, key, value):
    config = load_config("config/default.json")
    config[key] = value
    target = tmp_path / "config.json"
    target.write_text(json.dumps(config))
    with pytest.raises(ValueError):
        load_config(target)


def test_bad_hsv_configuration(tmp_path):
    config = load_config("config/default.json")
    config["hsv_ranges"]["blue"][0][1][0] = 180
    target = tmp_path / "config.json"
    target.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="HSV"):
        load_config(target)


@pytest.mark.parametrize("change", ["bounds", "duplicate", "metadata"])
def test_bad_annotations_rejected(tmp_path, change):
    row = {"file": "part.png", "width": 20, "height": 20,
           "condition": "nominal", "objects": []}
    manifest = {"schema_version": 1, "synthetic": True, "split": "development", "images": [row]}
    if change == "bounds":
        row["objects"] = [{"label": "red", "bbox": [10, 10, 11, 11]}]
    elif change == "duplicate":
        manifest["images"].append(row)
    else:
        manifest["split"] = "not_a_split"
    target = tmp_path / "annotations.json"
    target.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        load_annotations(target)


def test_diagnostics_mask_outputs_and_final_data_guard(tmp_path):
    import cv2
    import numpy as np

    assert cv2.imwrite(str(tmp_path / "blank.png"), np.zeros((40, 40, 3), dtype=np.uint8))
    manifest = {"schema_version": 1, "synthetic": True, "split": "development",
                "images": [{"file": "blank.png", "width": 40, "height": 40,
                            "condition": "nominal", "objects": []}]}
    path = tmp_path / "annotations.json"
    path.write_text(json.dumps(manifest))
    output = tmp_path / "masks"
    save_diagnostics(path, "config/default.json", output)
    assert len(list(output.rglob("*.png"))) == 4
    assert json.loads((output / "observations.json").read_text())["images"][0]["objects"] == []
    manifest["split"] = "evaluation"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="development data"):
        save_diagnostics(path, "config/default.json", tmp_path / "forbidden")
    assert not (tmp_path / "forbidden").exists()
