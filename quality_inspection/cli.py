"""Directory inspection, dataset generation, label previews and evaluation."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform

import cv2
import numpy as np

from .config import load_config
from .dataset import generate_dataset, load_annotations
from .detector import detect_objects
from .evaluation import evaluate_image, summarize
from .models import Detection, LABELS, PREDICTED_SHAPES
from .reporting import write_report
from .visualization import annotate, read_image, save_image


def write_json(path: str | Path, value: dict) -> None:
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(config: str | Path) -> dict:
    sources = Path(__file__).parent
    return {"source_sha256": {p.name: sha256(p) for p in sorted(sources.glob("*.py"))},
            "config_sha256": sha256(config),
            "environment": {"python": platform.python_version(), "opencv": cv2.__version__,
                            "numpy": np.__version__}}


def require_frozen(path: str | Path | None, config: str | Path) -> dict:
    if path is None:
        raise ValueError("Final evaluation requires --frozen artifacts/frozen.json; run freeze first")
    record = json.loads(Path(path).read_text())
    if record["fingerprint"] != fingerprint(config):
        raise ValueError("Code, config or environment changed since freeze. Final evaluation refused. "
                         "Develop further using development data and document a new experiment.")
    return record


def prepare_output(path: str | Path) -> Path:
    path = Path(path)
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"Use a new or empty output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def validated_predictions(image: np.ndarray, config: dict) -> list[Detection]:
    predictions = detect_objects(image, config)
    if not isinstance(predictions, list) or any(not isinstance(p, Detection) for p in predictions):
        raise ValueError("detect_objects must return a list of Detection objects")
    height, width = image.shape[:2]
    for pred in predictions:
        x, y, w, h = pred.bbox
        if x + w > width or y + h > height:
            raise ValueError("Detector returned a box outside the input image")
    return predictions


def annotated_samples(path: str | Path) -> tuple[dict, list[tuple[dict, np.ndarray]]]:
    manifest = load_annotations(path)
    samples = []
    for row in manifest["images"]:
        image = read_image(Path(path).parent / row["file"])
        if image.shape[:2] != (row["height"], row["width"]):
            raise ValueError(f"Image dimensions disagree with annotations: {row['file']}")
        samples.append((row, image))
    return manifest, samples


def generate(args: argparse.Namespace) -> None:
    if args.split == "evaluation":
        require_frozen(args.frozen, args.config)
    manifest = generate_dataset(args.output, args.split)
    print(f"Generated {len(manifest['images'])} SYNTHETIC {args.split} images at {args.output}")


def labels(args: argparse.Namespace) -> None:
    _, samples = annotated_samples(args.annotations)
    output = prepare_output(args.output)
    for row, image in samples:
        truth = [Detection(obj["label"], tuple(obj["bbox"]), obj.get("shape", "rectangle"))
                 for obj in row["objects"]]
        save_image(output / (Path(row["file"]).name + ".labels.png"),
                   annotate(image, truth, "GROUND TRUTH (synthetic)"))
    print(f"Saved {len(samples)} label previews; these are not detector results")


def inspect(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    directory = Path(args.images)
    files = sorted(p for p in directory.iterdir() if p.is_file()
                   and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"})
    if not files:
        raise ValueError("No supported images found in the input directory")
    # Detect before writing so a processing error cannot leave a plausible partial report.
    results = []
    for path in files:
        image = read_image(path)
        predictions = validated_predictions(image, config)
        results.append((path, image, predictions))
    output = prepare_output(args.output)
    rows = []
    for path, image, predictions in results:
        save_image(output / (path.name + ".annotated.png"), annotate(image, predictions))
        counts = Counter(p.label for p in predictions)
        shapes = Counter(p.shape for p in predictions)
        rows.append({"file": path.name, "total_count": len(predictions),
                     "counts": {label: counts[label] for label in LABELS},
                     "shape_counts": {shape: shapes[shape] for shape in PREDICTED_SHAPES},
                     "detections": [p.to_dict() for p in predictions]})
    write_json(output / "detections.json", {"fingerprint": fingerprint(args.config), "images": rows})
    print(f"Inspected {len(rows)} images; results saved at {output}")


def freeze(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    manifest, samples = annotated_samples(args.development)
    if manifest["split"] != "development":
        raise ValueError("Freeze requires development annotations")
    for _, image in samples:
        validated_predictions(image, config)
    target = Path(args.output)
    if target.exists():
        raise ValueError("Freeze record exists; use a new filename for a documented new experiment")
    target.parent.mkdir(parents=True, exist_ok=True)
    write_json(target, {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
                        "fingerprint": fingerprint(args.config), "config": config,
                        "development_annotations_sha256": sha256(args.development),
                        "iou_threshold": 0.5})
    print(f"Frozen code, config and environment at {target}. Preserve this experiment record.")


def evaluate(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    manifest, samples = annotated_samples(args.annotations)
    frozen = require_frozen(args.frozen, args.config) if manifest["split"] == "evaluation" else None
    rows = []
    rendered = []
    for row, image in samples:
        predictions = validated_predictions(image, config)
        truth = [Detection(obj["label"], tuple(obj["bbox"]), obj.get("shape", "rectangle"))
                 for obj in row["objects"]]
        result = evaluate_image(row["file"], row["condition"], predictions, truth)
        result["detections"] = [p.to_dict() for p in predictions]
        result["truth"] = [t.to_dict() for t in truth]
        result["input_sha256"] = sha256(Path(args.annotations).parent / row["file"])
        rows.append(result)
        # Top: ground truth. Bottom: predictions. Explicit labels prevent confusion.
        comparison = np.vstack([annotate(image, truth, "GROUND TRUTH"),
                                annotate(image, predictions, "PREDICTIONS")])
        rendered.append((Path(row["file"]).name + ".comparison.png", comparison))
    report = {"synthetic": manifest["synthetic"], "split": manifest["split"],
              "iou_threshold": 0.5, "fingerprint": fingerprint(args.config),
              "config": config, "frozen": frozen,
              "annotations_sha256": sha256(args.annotations),
              "overall": summarize(rows),
              "by_condition": {c: summarize([r for r in rows if r["condition"] == c])
                               for c in sorted({r["condition"] for r in rows})},
              "by_class": {label: {key: sum(r["by_class"][label][key] for r in rows)
                                     for key in ("tp", "fp", "fn")} for label in LABELS},
              "by_shape": {shape: {key: sum(r["by_shape"][shape][key] for r in rows)
                                     for key in ("tp", "fp", "fn")} for shape in PREDICTED_SHAPES},
              "matching_rule": "same color and shape; maximum-cardinality one-to-one IoU >= 0.5",
              "dataset_seed": manifest.get("seed"),
              "schema_version": manifest["schema_version"],
              "images": rows}
    output = prepare_output(args.output)
    for name, image in rendered:
        save_image(output / "images" / name, image)
    write_json(output / "results.json", report)
    write_report(output / "report.md", report)
    print(json.dumps(report["overall"], indent=2))
    print(f"Saved measured results and comparisons at {output}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthetic red/blue rectangle, circle and triangle inspection")
    commands = parser.add_subparsers(dest="command", required=True)
    gen = commands.add_parser("generate", help="Generate synthetic annotated images")
    gen.add_argument("--split", choices=["development", "evaluation"], default="development")
    gen.add_argument("--output", required=True)
    gen.set_defaults(action=generate)
    preview = commands.add_parser("labels", help="Render ground-truth boxes, not detections")
    preview.add_argument("--annotations", required=True)
    preview.add_argument("--output", required=True)
    preview.set_defaults(action=labels)
    run = commands.add_parser("inspect", help="Inspect every supported image in a directory")
    run.add_argument("--images", required=True)
    run.add_argument("--output", required=True)
    run.set_defaults(action=inspect)
    lock = commands.add_parser("freeze", help="Freeze the implemented detector before final evaluation")
    lock.add_argument("--development", required=True)
    lock.add_argument("--output", default="artifacts/frozen.json")
    lock.set_defaults(action=freeze)
    ev = commands.add_parser("evaluate", help="Evaluate predictions against annotations")
    ev.add_argument("--annotations", required=True)
    ev.add_argument("--output", required=True)
    ev.set_defaults(action=evaluate)
    for command in (gen, run, lock, ev):
        command.add_argument("--config", default="config/default.json")
    for command in (gen, ev):
        command.add_argument("--frozen", help="Required for the final evaluation split")
    args = parser.parse_args(argv)
    try:
        args.action(args)
    except (ValueError, OSError, KeyError, TypeError, NotImplementedError) as error:
        parser.exit(2, f"error: {error}\n")
    return 0
