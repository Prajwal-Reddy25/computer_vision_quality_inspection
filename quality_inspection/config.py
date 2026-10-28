"""Load and validate the small JSON configuration."""

import json
from pathlib import Path

from .models import LABELS


def load_config(path: str | Path) -> dict:
    config = json.loads(Path(path).read_text())
    if set(config["hsv_ranges"]) != set(LABELS):
        raise ValueError("hsv_ranges must define red and blue")
    for ranges in config["hsv_ranges"].values():
        if not ranges:
            raise ValueError("Each color needs at least one HSV range")
        for bounds in ranges:
            if len(bounds) != 2 or any(len(b) != 3 for b in bounds):
                raise ValueError("Each HSV range needs lower and upper triples")
            for lo, hi, maximum in zip(*bounds, (179, 255, 255)):
                if type(lo) is not int or type(hi) is not int or not 0 <= lo <= hi <= maximum:
                    raise ValueError("Invalid OpenCV HSV bounds")
    for name in ("kernel_size", "open_iterations", "close_iterations", "min_area"):
        if type(config[name]) is not int or config[name] < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
    if config["kernel_size"] < 1 or config["kernel_size"] % 2 == 0:
        raise ValueError("kernel_size must be positive and odd")
    shape = config["shape"]
    for name in ("epsilon_ratio", "min_circularity", "min_rectangle_fill"):
        value = shape[name]
        if type(value) not in (int, float) or not 0 < value <= 1:
            raise ValueError(f"shape.{name} must lie in (0, 1]")
    if shape["epsilon_ratio"] >= 0.1:
        raise ValueError("shape.epsilon_ratio must be below 0.1")
    return config
