"""Additional boundary and configuration checks; original tests are unchanged."""

from copy import deepcopy

import cv2
import numpy as np
import pytest

from quality_inspection.config import load_config
from quality_inspection.detector import detect_objects, filter_mask
from quality_inspection.evaluation import intersection_over_union


@pytest.mark.parametrize("image", [None, [], np.zeros((3,)),
                                   np.zeros((2, 2, 4), dtype=np.uint8),
                                   np.zeros((2, 0, 3), dtype=np.uint8),
                                   np.zeros((2, 2, 3), dtype=np.uint16)])
def test_invalid_input_variants(image):
    with pytest.raises(ValueError):
        detect_objects(image, load_config("config/default.json"))


def test_tiny_valid_image_and_noncontiguous_view():
    config = load_config("config/default.json")
    assert detect_objects(np.zeros((1, 1, 3), dtype=np.uint8), config) == []
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[0:40, 0:50] = (0, 0, 230)
    view = image[:, ::-1]
    original = image.copy()
    detections = detect_objects(view, config)
    assert len(detections) == 1
    assert detections[0].bbox == (50, 0, 50, 40)
    np.testing.assert_array_equal(image, original)


def test_area_cutoff_includes_equality_and_excludes_smaller():
    config = deepcopy(load_config("config/default.json"))
    config.update(open_iterations=0, close_iterations=0, min_area=400)
    image = np.zeros((80, 120, 3), dtype=np.uint8)
    image[10:31, 10:31] = (0, 0, 230)  # Contour area 20*20 = 400.
    image[40:60, 70:90] = (230, 0, 0)  # Contour area 19*19 = 361.
    assert [(d.label, d.bbox) for d in detect_objects(image, config)] == [
        ("red", (10, 10, 21, 21))]


def test_internal_hole_is_not_a_second_object():
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[15:85, 15:85] = (230, 0, 0)
    image[35:65, 35:65] = 0
    result = detect_objects(image, load_config("config/default.json"))
    assert len(result) == 1
    assert result[0].bbox == (15, 15, 70, 70)


def test_rotated_part_localization_and_canonical_order():
    config = load_config("config/default.json")
    image = np.zeros((180, 240, 3), dtype=np.uint8)
    polygon = np.rint(cv2.boxPoints(((60, 60), (55, 35), 31))).astype(np.int32)
    cv2.fillConvexPoly(image, polygon, (0, 0, 230))
    image[110:150, 150:200] = (230, 0, 0)
    expected = cv2.boundingRect(polygon)
    result = detect_objects(image, config)
    assert [d.label for d in result] == ["blue", "red"]
    assert intersection_over_union(result[1].bbox, expected) >= 0.9
    config["hsv_ranges"] = dict(reversed(list(config["hsv_ranges"].items())))
    assert detect_objects(image, config) == result


def test_zero_morphology_iterations_preserve_mask():
    config = load_config("config/default.json")
    config.update(open_iterations=0, close_iterations=0)
    mask = np.zeros((10, 10), dtype=np.uint8)
    mask[4, 4] = 255
    original = mask.copy()
    result = filter_mask(mask, config)
    np.testing.assert_array_equal(result, original)
    np.testing.assert_array_equal(mask, original)
