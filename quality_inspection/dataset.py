"""Reproducible SYNTHETIC colored parts, not photographs of manufactured parts."""

import json
from pathlib import Path

import cv2
import numpy as np

from .models import Detection


CONDITIONS = ("nominal", "rotation", "dim", "bright", "blue_background")
SEEDS = {"development": 1729, "evaluation": 92173}


def generate_dataset(root: str | Path, split: str = "development") -> dict:
    """Generate 15 development or 30 evaluation PNGs and annotations."""
    if split not in SEEDS:
        raise ValueError("Unknown split")
    root = Path(root)
    # Refuse an existing nonempty directory to protect datasets and local edits.
    if root.exists() and any(root.iterdir()):
        raise ValueError(f"Refusing to overwrite nonempty dataset: {root}")
    root.mkdir(parents=True, exist_ok=True)
    (root / "images").mkdir()
    rng = np.random.default_rng(SEEDS[split])
    records = []
    per_condition = 3 if split == "development" else 6
    for condition in CONDITIONS:
        for _ in range(per_condition):
            index = len(records)
            background = np.array([55, 55, 55], dtype=np.uint8)
            if condition == "blue_background":
                hsv = np.uint8([[[int(rng.integers(100, 116)),
                                  int(rng.integers(90, 161)),
                                  int(rng.integers(100, 146))]]])
                background = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0]
            canvas = np.full((360, 480, 3), background, dtype=np.uint8)
            count = 0 if index % 7 == 0 else int(rng.integers(1, 7))
            cells = rng.permutation(6)[:count]
            objects = []
            for cell in cells:
                cx = int(80 + (cell % 3) * 160 + rng.integers(-12, 13))
                cy = int(90 + (cell // 3) * 180 + rng.integers(-12, 13))
                width, height = int(rng.integers(45, 81)), int(rng.integers(30, 56))
                angle = float(rng.uniform(-60, 60)) if condition == "rotation" else 0.0
                label = "red" if rng.integers(2) == 0 else "blue"
                # Small hue variation includes both ends of the red hue interval.
                hue = int(rng.choice([0, 3, 177])) if label == "red" else int(rng.integers(108, 119))
                hsv = np.uint8([[[hue, int(rng.integers(200, 256)), int(rng.integers(190, 241))]]])
                color = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0].tolist()
                polygon = np.rint(cv2.boxPoints(((cx, cy), (width, height), angle))).astype(np.int32)
                cv2.fillConvexPoly(canvas, polygon, color)
                bbox = tuple(int(v) for v in cv2.boundingRect(polygon))
                objects.append(Detection(label, bbox).to_dict())
            gain = 1.0
            if condition == "dim":
                gain = float(rng.uniform(0.25, 0.55))
            elif condition == "bright":
                gain = float(rng.uniform(1.3, 1.7))
            noise = rng.normal(0, 2, canvas.shape)
            canvas = np.clip(canvas.astype(float) * gain + noise, 0, 255).astype(np.uint8)
            filename = f"images/{index:03d}_{condition}.png"
            if not cv2.imwrite(str(root / filename), canvas):
                raise OSError(f"Could not write {filename}")
            records.append({"file": filename, "width": 480, "height": 360,
                            "condition": condition, "objects": objects})
    manifest = {"schema_version": 1, "synthetic": True, "split": split,
                "seed": SEEDS[split], "images": records}
    (root / "annotations.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def load_annotations(path: str | Path) -> dict:
    path = Path(path)
    manifest = json.loads(path.read_text())
    if manifest["schema_version"] != 1 or not manifest["images"]:
        raise ValueError("Expected schema version 1 and a nonempty image list")
    seen = set()
    for record in manifest["images"]:
        relative = Path(record["file"])
        if relative.is_absolute() or ".." in relative.parts or str(relative) in seen:
            raise ValueError("Image paths must be unique relative paths within the dataset")
        seen.add(str(relative))
        if not (path.parent / relative).resolve().is_relative_to(path.parent.resolve()):
            raise ValueError("Image path escapes dataset")
        if record["width"] <= 0 or record["height"] <= 0:
            raise ValueError("Invalid image dimensions")
        for obj in record["objects"]:
            detection = Detection(obj["label"], tuple(obj["bbox"]))
            x, y, w, h = detection.bbox
            if x + w > record["width"] or y + h > record["height"]:
                raise ValueError("Annotation box exceeds image bounds")
    if manifest.get("split") not in SEEDS or type(manifest.get("synthetic")) is not bool:
        raise ValueError("Annotations require a development/evaluation split and a synthetic boolean")
    return manifest
