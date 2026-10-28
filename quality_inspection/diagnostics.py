"""Save development-only masks and HSV observations for failure analysis."""

import argparse
from pathlib import Path

import cv2
import numpy as np

from .cli import annotated_samples, prepare_output, write_json
from .config import load_config
from .detector import filter_mask, threshold_color
from .visualization import save_image


def save_diagnostics(annotations: str | Path, config_path: str | Path,
                     output_path: str | Path) -> None:
    """Record mask stages and S/V percentiles; never tune against final labels."""
    config = load_config(config_path)
    manifest, samples = annotated_samples(annotations)
    if manifest["split"] != "development":
        raise ValueError("Diagnostics requires development data; final data is for evaluation only")
    output = prepare_output(output_path)
    observations = []
    for row, image in samples:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        stem = Path(row["file"]).stem
        for label, ranges in config["hsv_ranges"].items():
            raw = threshold_color(hsv, ranges)
            save_image(output / stem / f"{label}_raw.png", raw)
            save_image(output / stem / f"{label}_filtered.png", filter_mask(raw, config))
        outside = np.ones(image.shape[:2], dtype=bool)
        objects = []
        for obj in row["objects"]:
            x, y, w, h = obj["bbox"]
            outside[y:y + h, x:x + w] = False
            # Center patch avoids rotated box corners. It is a diagnostic sample,
            # not a ground-truth segmentation mask or a new annotation.
            patch = hsv[y + h // 3:y + max(h // 3 + 1, 2 * h // 3),
                        x + w // 3:x + max(w // 3 + 1, 2 * w // 3), 1:]
            objects.append({**obj, "center_sv_p01_p50_p99":
                            np.percentile(patch, [1, 50, 99], axis=(0, 1)).tolist()})
        background = hsv[outside, 1:]
        observations.append({"file": row["file"], "objects": objects,
                             "background_sv_p01_p50_p99":
                             np.percentile(background, [1, 50, 99], axis=0).tolist()
                             if len(background) else None})
    write_json(output / "observations.json", {"synthetic": manifest["synthetic"],
                                             "config": config, "images": observations})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--config", default="config/default.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        save_diagnostics(args.annotations, args.config, args.output)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
