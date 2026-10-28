"""Write a short, factual Markdown report from measured results."""

from pathlib import Path


def format_metric(value: float | None) -> str:
    return "undefined" if value is None else f"{value:.3f}"


def write_report(path: Path, report: dict) -> None:
    overall = report["overall"]
    lines = ["# Inspection evaluation", "",
             f"Dataset: **{'SYNTHETIC' if report['synthetic'] else 'real'}**, split: {report['split']}.",
             f"Images: {overall['images']}; same-color AND same-shape matching at IoU >= {report['iou_threshold']}.",
             "Metrics below are measured; examples rendered from labels are not predictions.", "",
             "| Group | TP | FP | FN | Precision | Recall | F1 | Count MAE |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, metrics in [("overall", overall), *report["by_condition"].items()]:
        lines.append(f"| {name} | {metrics['tp']} | {metrics['fp']} | {metrics['fn']} | "
                     f"{format_metric(metrics['precision'])} | {format_metric(metrics['recall'])} | "
                     f"{format_metric(metrics['f1'])} | {format_metric(metrics['count_mae'])} |")
    lines += ["", f"Exact total counts: {overall['exact_count_images']}/{overall['images']} images.",
              f"Exact per-color counts: {overall['exact_class_count_images']}/{overall['images']} images.",
              f"Exact per-shape counts: {overall['exact_shape_count_images']}/{overall['images']} images.",
              f"Color-count accuracy: {format_metric(overall['color_count_accuracy'])}.",
              f"Shape-count accuracy: {format_metric(overall['shape_count_accuracy'])}.",
              "Count accuracy means the entire per-image count vector is correct, including empty scenes.",
              "A correct count alone does not establish correct localization.", "",
              "Per-color TP/FP/FN:", ""]
    for label, metrics in report["by_class"].items():
        lines.append(f"- {label}: {metrics['tp']}/{metrics['fp']}/{metrics['fn']}")
    lines += ["", "Per-shape TP/FP/FN (matches require correct color too):", ""]
    for shape, metrics in report["by_shape"].items():
        lines.append(f"- {shape}: {metrics['tp']}/{metrics['fp']}/{metrics['fn']}")
    lines += ["", "## Images with errors", "",
              "See results.json for every box, match, and unmatched index.", ""]
    errors = [r for r in report["images"] if r["fp"] or r["fn"]]
    if not errors:
        lines.append("No false positives or missed objects at the stated matching threshold.")
    for row in errors:
        lines.append(f"- {row['file']} ({row['condition']}): FP={row['fp']}, FN={row['fn']}, "
                     f"count error={row['count_error']:+d}.")
    lines += ["", "## Scope", "",
              "These generated scenes do not establish performance on real production photographs.",
              "Record any post-evaluation changes as a new experiment; do not retune on this final set.", ""]
    path.write_text("\n".join(lines))
