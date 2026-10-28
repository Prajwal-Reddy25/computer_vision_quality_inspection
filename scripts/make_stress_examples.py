"""Three deterministic synthetic limitations, separate from the final benchmark.

Run from the repository root: python scripts/make_stress_examples.py --output runs/stress
These post-evaluation demonstrations do not influence the frozen detector.
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def generate(output: Path) -> None:
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Refusing to overwrite {output}")
    (output / "images").mkdir(parents=True, exist_ok=True)
    records = []
    for condition in ("small_part", "dark_stripe", "same_color_background"):
        image = np.full((120, 160, 3), 55, dtype=np.uint8)
        if condition == "small_part":
            box = [30, 30, 20, 20]
            image[30:50, 30:50] = (230, 0, 0)
        elif condition == "dark_stripe":
            box = [40, 40, 60, 40]
            image[40:80, 40:100] = (230, 0, 0)
            image[40:80, 67:72] = 0  # Five-pixel marking splits the colored region.
        else:
            box = [40, 40, 60, 40]
            image[:] = (220, 20, 20)
            image[40:80, 40:100] = (230, 20, 20)
        filename = f"images/{condition}.png"
        if not cv2.imwrite(str(output / filename), image):
            raise OSError(f"Could not write {filename}")
        records.append({"file": filename, "width": 160, "height": 120,
                        "condition": condition, "objects": [
                            {"label": "blue", "shape": "rectangle", "bbox": box}]})
    manifest = {"schema_version": 2, "synthetic": True, "split": "development",
                "purpose": "post-evaluation limitations demonstration; not used for tuning",
                "seed": None, "images": records}
    (output / "annotations.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    generate(parser.parse_args().output)
