"""These checks activate once the student replaces the explicit placeholder.

They are small development examples, not the final evaluation dataset.
No detector implementation is provided by this test module.
"""

import cv2
import numpy as np
import pytest

from quality_inspection.config import load_config
from quality_inspection.detector import detect_objects
from quality_inspection.evaluation import intersection_over_union
from quality_inspection.models import Detection


@pytest.fixture
def config():
    config = load_config("config/default.json")
    try:
        detect_objects(np.zeros((120, 160, 3), dtype=np.uint8), config)
    except NotImplementedError:
        pytest.skip("Student detector not implemented; project validation remains incomplete")
    return config


def test_blank_image(config):
    assert detect_objects(np.zeros((120, 160, 3), dtype=np.uint8), config) == []


@pytest.mark.parametrize("hue,label", [(0, "red"), (177, "red"), (115, "blue")])
def test_single_solid_part(config, hue, label):
    image = np.zeros((120, 160, 3), dtype=np.uint8)
    image[30:70, 40:100] = cv2.cvtColor(np.uint8([[[hue, 240, 220]]]), cv2.COLOR_HSV2BGR)[0, 0]
    result = detect_objects(image, config)
    assert len(result) == 1
    assert isinstance(result[0], Detection)
    assert result[0].label == label
    assert intersection_over_union(result[0].bbox, (40, 30, 60, 40)) >= 0.9


def test_speckles_rejected_and_input_unchanged(config):
    image = np.zeros((120, 160, 3), dtype=np.uint8)
    image[10, 10] = (0, 0, 255)
    image[80, 90] = (255, 0, 0)
    original = image.copy()
    assert detect_objects(image, config) == []
    np.testing.assert_array_equal(image, original)


def test_multiple_parts(config):
    image = np.zeros((140, 200, 3), dtype=np.uint8)
    image[20:60, 20:70] = (0, 0, 230)
    image[80:120, 120:180] = (230, 0, 0)
    first = detect_objects(image, config)
    assert sorted(p.label for p in first) == ["blue", "red"]
    assert first == detect_objects(image, config)


@pytest.mark.parametrize("image", [np.zeros((10, 10), dtype=np.uint8),
                                   np.zeros((10, 10, 3), dtype=float),
                                   np.zeros((0, 10, 3), dtype=np.uint8)])
def test_invalid_images_raise_value_error(config, image):
    with pytest.raises(ValueError):
        detect_objects(image, config)
