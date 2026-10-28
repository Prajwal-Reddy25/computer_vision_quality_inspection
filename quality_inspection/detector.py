"""Classical color segmentation for isolated red and blue parts."""

import cv2
import numpy as np

from .models import Detection


def validate_image(bgr: np.ndarray) -> None:
    """Reject invalid arrays before OpenCV can raise a less useful error."""
    if not isinstance(bgr, np.ndarray):
        raise ValueError("Image must be a NumPy array")
    if bgr.ndim != 3 or bgr.shape[2] != 3:
        raise ValueError("Image must have shape (height, width, 3) in BGR order")
    if bgr.dtype != np.uint8:
        raise ValueError("Image dtype must be uint8")
    if bgr.shape[0] == 0 or bgr.shape[1] == 0:
        raise ValueError("Image height and width must be positive")


def threshold_color(hsv: np.ndarray, ranges: list) -> np.ndarray:
    """OR inclusive HSV intervals, including both ends of red's hue range."""
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lower, upper in ranges:
        interval = cv2.inRange(hsv, np.array(lower, dtype=np.uint8),
                               np.array(upper, dtype=np.uint8))
        mask = cv2.bitwise_or(mask, interval)
    return mask


def filter_mask(mask: np.ndarray, config: dict) -> np.ndarray:
    """Open away speckles, then close small gaps; never alter the input mask."""
    size = config["kernel_size"]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
    result = mask.copy()
    for operation, key in ((cv2.MORPH_OPEN, "open_iterations"),
                           (cv2.MORPH_CLOSE, "close_iterations")):
        if config[key] > 0:
            result = cv2.morphologyEx(result, operation, kernel, iterations=config[key])
    return result


def detect_objects(bgr: np.ndarray, config: dict) -> list[Detection]:
    """Return class-labeled boxes ordered by label, y, x, width, height.

    Accept a nonempty uint8 BGR image and a validated load_config dictionary.
    Reject invalid images with ValueError; return [] for valid blank scenes.
    Each external contour with area >= min_area produces one axis-aligned box.
    The input image is unchanged. Touching same-color parts are outside scope.
    """
    validate_image(bgr)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    detections = []
    for label, ranges in config["hsv_ranges"].items():
        mask = filter_mask(threshold_color(hsv, ranges), config)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) >= config["min_area"]:
                box = tuple(int(value) for value in cv2.boundingRect(contour))
                detections.append(Detection(label, box))
    return sorted(detections, key=lambda obj: (obj.label, obj.bbox[1], obj.bbox[0],
                                                obj.bbox[2], obj.bbox[3]))
