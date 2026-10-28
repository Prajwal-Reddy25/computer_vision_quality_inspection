"""Color/shape coverage supplements the unchanged rectangle-era tests."""

from collections import Counter
import json

import cv2
import numpy as np
import pytest

from quality_inspection.cli import main
from quality_inspection.config import load_config
from quality_inspection.dataset import draw_part, generate_dataset, load_annotations
from quality_inspection.detector import classify_shape, detect_objects
from quality_inspection.evaluation import evaluate_image, intersection_over_union, summarize
from quality_inspection.models import Detection, LABELS, SHAPES


def part_image(shape, label, angle=0):
    image = np.zeros((120, 160, 3), dtype=np.uint8)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    draw_part(mask, shape, (80, 60), 70, 44, angle)
    image[mask != 0] = (230, 0, 0) if label == "blue" else (0, 0, 230)
    return image, cv2.boundingRect(cv2.findNonZero(mask))


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("label", LABELS)
@pytest.mark.parametrize("angle", [0, 27, -53])
def test_shape_and_color_across_rotations(shape, label, angle):
    image, box = part_image(shape, label, angle)
    original = image.copy()
    result = detect_objects(image, load_config("config/default.json"))
    assert len(result) == 1
    assert (result[0].label, result[0].shape) == (label, shape)
    assert intersection_over_union(result[0].bbox, box) >= 0.9
    np.testing.assert_array_equal(image, original)


def test_mixed_scene_and_order_independent_of_config():
    image = np.zeros((280, 480, 3), dtype=np.uint8)
    expected = Counter()
    for row, label in enumerate(LABELS):
        for column, shape in enumerate(SHAPES):
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            draw_part(mask, shape, (80 + column * 160, 70 + row * 140), 70, 44, 23)
            image[mask != 0] = (230, 0, 0) if label == "blue" else (0, 0, 230)
            expected[label, shape] += 1
    config = load_config("config/default.json")
    first = detect_objects(image, config)
    assert Counter((p.label, p.shape) for p in first) == expected
    assert first == sorted(first, key=lambda p: (p.label, p.bbox[1], p.bbox[0],
                                                 p.bbox[2], p.bbox[3], p.shape))
    config["hsv_ranges"] = dict(reversed(list(config["hsv_ranges"].items())))
    assert detect_objects(image, config) == first


def test_unsupported_contour_remains_unknown_and_degenerate_is_safe():
    image = np.zeros((160, 160, 3), dtype=np.uint8)
    angles = np.linspace(0, 2 * np.pi, 10, endpoint=False)
    radii = np.array([55, 22] * 5)
    points = np.rint(np.column_stack((80 + radii * np.cos(angles),
                                      80 + radii * np.sin(angles)))).astype(np.int32)
    cv2.fillPoly(image, [points], (230, 0, 0))
    config = load_config("config/default.json")
    result = detect_objects(image, config)
    assert len(result) == 1 and result[0].shape == "unknown"
    assert classify_shape(np.array([[[1, 1]]], dtype=np.int32), config) == "unknown"


def test_wrong_shape_does_not_match_despite_correct_color_and_count():
    truth = [Detection("blue", (10, 20, 40, 40), "circle")]
    predictions = [Detection("blue", truth[0].bbox, "rectangle")]
    row = evaluate_image("fixture.png", "nominal", predictions, truth)
    result = summarize([row])
    assert (result["tp"], result["fp"], result["fn"]) == (0, 1, 1)
    assert result["color_count_accuracy"] == 1
    assert result["shape_count_accuracy"] == 0
    assert result["exact_count_images"] == 1
    assert row["by_shape"]["circle"]["fn"] == 1
    assert row["by_shape"]["rectangle"]["fp"] == 1


def test_blank_scene_count_vectors_and_unknown_penalty():
    empty = summarize([evaluate_image("blank.png", "nominal", [], [])])
    assert empty["color_count_accuracy"] == empty["shape_count_accuracy"] == 1
    assert empty["precision"] is None
    truth = [Detection("red", (0, 0, 30, 30), "triangle")]
    row = evaluate_image("unknown.png", "nominal", [Detection("red", truth[0].bbox, "unknown")], truth)
    assert row["shape_count_errors"]["unknown"] == 1
    assert summarize([row])["shape_count_accuracy"] == 0


def test_generated_development_coverage_and_real_evaluation(tmp_path):
    data = tmp_path / "development"
    manifest = generate_dataset(data)
    assert manifest["schema_version"] == 2 and manifest["seed"] == 31415
    assert load_annotations(data / "annotations.json") == manifest
    showcase = manifest["images"][1]["objects"]
    assert Counter((o["label"], o["shape"]) for o in showcase) == Counter(
        (label, shape) for label in LABELS for shape in SHAPES)
    for row in manifest["images"]:
        if row["objects"]:
            assert len(row["objects"]) >= 3
            assert {obj["shape"] for obj in row["objects"]} == set(SHAPES)
            assert {obj["label"] for obj in row["objects"]} == set(LABELS)
    output = tmp_path / "evaluation"
    main(["evaluate", "--annotations", str(data / "annotations.json"), "--output", str(output)])
    report = json.loads((output / "results.json").read_text())
    assert sum(len(r["truth"]) for r in report["images"]) == sum(
        len(r["objects"]) for r in manifest["images"])
    assert set(report["by_shape"]) == {*SHAPES, "unknown"}
    assert all("shape" in obj for row in report["images"] for obj in row["detections"])
    assert "same color and shape" in report["matching_rule"]
    assert "Shape-count accuracy" in (output / "report.md").read_text()


@pytest.mark.parametrize("shape", [None, "hexagon", "unknown", "missing"])
def test_v2_annotation_requires_supported_shape(tmp_path, shape):
    obj = {"label": "red", "shape": shape, "bbox": [1, 1, 20, 20]}
    if shape == "missing":
        del obj["shape"]
    manifest = {"schema_version": 2, "synthetic": True, "split": "development", "images": [
        {"file": "part.png", "width": 40, "height": 40, "condition": "nominal", "objects": [obj]}]}
    path = tmp_path / "annotations.json"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="shape"):
        load_annotations(path)


@pytest.mark.parametrize("key,value", [("epsilon_ratio", 0), ("epsilon_ratio", 0.1),
                                       ("min_circularity", 1.1), ("min_rectangle_fill", False)])
def test_invalid_shape_settings(tmp_path, key, value):
    config = load_config("config/default.json")
    config["shape"][key] = value
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="shape"):
        load_config(path)


def test_detection_rejects_unsupported_shape_and_legacy_default():
    with pytest.raises(ValueError, match="shape"):
        Detection("red", (0, 0, 20, 20), "hexagon")
    assert Detection("red", (0, 0, 20, 20)).shape == "rectangle"
