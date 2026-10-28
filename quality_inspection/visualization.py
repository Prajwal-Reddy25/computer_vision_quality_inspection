"""Image I/O and labeled overlays."""

from pathlib import Path

import cv2
import numpy as np

from .models import Detection


COLORS = {"red": (40, 180, 255), "blue": (255, 220, 40)}


def read_image(path: str | Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image


def annotate(image: np.ndarray, detections: list[Detection], title: str = "Predictions") -> np.ndarray:
    result = image.copy()
    for obj in detections:
        x, y, w, h = obj.bbox
        color = COLORS[obj.label]
        cv2.rectangle(result, (x, y), (x + w - 1, y + h - 1), color, 2)
        cv2.putText(result, f"{obj.label} {obj.shape}", (x, max(15, y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    cv2.putText(result, f"{title}: {len(detections)}", (10, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return result


def save_image(path: str | Path, image: np.ndarray) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise OSError(f"Could not write image: {path}")
