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


def classify_shape(contour: np.ndarray, config: dict) -> str:
    """Classify a simple outer contour; unsupported geometry remains unknown.

    Three convex approximated vertices indicate a triangle. Four indicate a
    rectangle only if the contour fills its rotated minimum rectangle. Other
    polygons with >=5 vertices need sufficient circularity to be called circles.
    These heuristics describe the synthetic shapes, not arbitrary real parts.
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    if area <= 0 or perimeter <= 0:
        return "unknown"
    settings = config["shape"]
    polygon = cv2.approxPolyDP(contour, settings["epsilon_ratio"] * perimeter, True)
    vertices = len(polygon)
    if vertices == 3 and cv2.isContourConvex(polygon):
        return "triangle"
    if vertices == 4 and cv2.isContourConvex(polygon):
        _, (width, height), _ = cv2.minAreaRect(contour)
        if width * height > 0 and area / (width * height) >= settings["min_rectangle_fill"]:
            return "rectangle"
    circularity = 4 * np.pi * area / perimeter ** 2
    if vertices >= 5 and cv2.isContourConvex(polygon) and circularity >= settings["min_circularity"]:
        return "circle"
    return "unknown"


def detect_objects(bgr: np.ndarray, config: dict) -> list[Detection]:
    """Return color/shape boxes ordered by color, y, x, width, height, shape.

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
                detections.append(Detection(label, box, classify_shape(contour, config)))
    return sorted(detections, key=lambda obj: (obj.label, obj.bbox[1], obj.bbox[0],
                                              obj.bbox[2], obj.bbox[3], obj.shape))
