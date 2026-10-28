"""Export one development showcase with all six color/shape combinations.

Run from the root with: python -m scripts.export_examples --annotations ... --output ...
"""

import argparse
from pathlib import Path

from quality_inspection.cli import annotated_samples, fingerprint, prepare_output, write_json
from quality_inspection.config import load_config
from quality_inspection.detector import detect_objects
from quality_inspection.models import Detection, LABELS, SHAPES
from quality_inspection.visualization import annotate, save_image


def export(annotations: str | Path, config_path: str | Path, destination: str | Path) -> None:
    manifest, samples = annotated_samples(annotations)
    if manifest["split"] != "development":
        raise ValueError("README showcase must come from development data")
    expected = {(color, shape) for color in LABELS for shape in SHAPES}
    for row, image in samples:
        if {(o["label"], o.get("shape")) for o in row["objects"]} == expected:
            break
    else:
        raise ValueError("No development image contains all six color/shape combinations")
    truth = [Detection(o["label"], tuple(o["bbox"]), o["shape"]) for o in row["objects"]]
    predictions = detect_objects(image, load_config(config_path))
    output = prepare_output(destination)
    save_image(output / "images/showcase.png", image)
    save_image(output / "showcase_ground_truth.png", annotate(image, truth, "Ground Truth (synthetic)"))
    save_image(output / "showcase_prediction.png", annotate(image, predictions, "Prediction (synthetic)"))
    record = dict(row, file="images/showcase.png")
    write_json(output / "annotations.json", dict(manifest, images=[record]))
    write_json(output / "detections.json", {"synthetic": True, "source": row["file"],
                                            "fingerprint": fingerprint(config_path),
                                            "detections": [p.to_dict() for p in predictions]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--config", default="config/default.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    export(args.annotations, args.config, args.output)
