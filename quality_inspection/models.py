"""Shared data types. Boxes use half-open pixel coordinates [x, y, w, h]."""

from dataclasses import dataclass


LABELS = ("red", "blue")


@dataclass(frozen=True)
class Detection:
    label: str
    bbox: tuple[int, int, int, int]

    def __post_init__(self):
        if self.label not in LABELS:
            raise ValueError(f"Unknown label: {self.label}")
        if len(self.bbox) != 4 or any(type(v) is not int for v in self.bbox):
            raise ValueError("bbox must contain four Python integers")
        x, y, w, h = self.bbox
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            raise ValueError("bbox requires nonnegative x/y and positive width/height")

    def to_dict(self) -> dict:
        return {"label": self.label, "bbox": list(self.bbox)}
