"""Same-class one-to-one matching and dataset-level metrics."""

from .models import Detection, LABELS, PREDICTED_SHAPES


def intersection_over_union(a: tuple[int, int, int, int],
                            b: tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    intersection = max(0, min(ax + aw, bx + bw) - max(ax, bx)) * max(
        0, min(ay + ah, by + bh) - max(ay, by))
    return intersection / (aw * ah + bw * bh - intersection)


def match_detections(predictions: list[Detection], truth: list[Detection],
                     threshold: float = 0.5) -> list[dict]:
    """Match color AND shape; maximize pair count, visiting higher IoUs first.

    An augmenting path prevents a greedy assignment from needlessly losing TPs.
    This maximizes valid match count, not the sum of matched IoUs.
    """
    if not 0 < threshold <= 1:
        raise ValueError("IoU threshold must lie in (0, 1]")
    edges = []
    for pred in predictions:
        candidates = [(intersection_over_union(pred.bbox, obj.bbox), j)
                      for j, obj in enumerate(truth)
                      if (pred.label, pred.shape) == (obj.label, obj.shape)]
        edges.append([j for score, j in sorted(candidates, reverse=True) if score >= threshold])
    owners = {}

    def augment(i, seen):
        for j in edges[i]:
            if j in seen:
                continue
            seen.add(j)
            if j not in owners or augment(owners[j], seen):
                owners[j] = i
                return True
        return False

    for i in range(len(predictions)):
        augment(i, set())
    return [{"prediction_index": i, "truth_index": j,
             "iou": intersection_over_union(predictions[i].bbox, truth[j].bbox)}
            for j, i in sorted(owners.items())]


def summarize(rows: list[dict]) -> dict:
    """Micro metrics; undefined precision/recall is null, never a guessed score."""
    tp = sum(row["tp"] for row in rows)
    fp = sum(row["fp"] for row in rows)
    fn = sum(row["fn"] for row in rows)
    exact_color = sum(all(v == 0 for v in r["class_count_errors"].values()) for r in rows)
    exact_shape = sum(all(v == 0 for v in r["shape_count_errors"].values()) for r in rows)
    return {"images": len(rows), "tp": tp, "fp": fp, "fn": fn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
            "count_mae": sum(abs(r["count_error"]) for r in rows) / len(rows) if rows else None,
            "exact_count_images": sum(r["count_error"] == 0 for r in rows),
            "exact_class_count_images": exact_color,  # Backward-compatible color-count name.
            "exact_color_count_images": exact_color,
            "exact_shape_count_images": exact_shape,
            "color_count_accuracy": exact_color / len(rows) if rows else None,
            "shape_count_accuracy": exact_shape / len(rows) if rows else None}


def evaluate_image(filename: str, condition: str, predictions: list[Detection],
                   truth: list[Detection], threshold: float = 0.5) -> dict:
    matches = match_detections(predictions, truth, threshold)
    matched_p = {m["prediction_index"] for m in matches}
    matched_t = {m["truth_index"] for m in matches}
    return {"file": filename, "condition": condition, "tp": len(matches),
            "fp": len(predictions) - len(matches), "fn": len(truth) - len(matches),
            "predicted_count": len(predictions), "true_count": len(truth),
            "count_error": len(predictions) - len(truth),
            "class_count_errors": {label: sum(p.label == label for p in predictions)
                                   - sum(t.label == label for t in truth) for label in LABELS},
            "shape_count_errors": {shape: sum(p.shape == shape for p in predictions)
                                   - sum(t.shape == shape for t in truth) for shape in PREDICTED_SHAPES},
            "by_class": {label: {
                "tp": sum(predictions[i].label == label for i in matched_p),
                "fp": sum(p.label == label and i not in matched_p for i, p in enumerate(predictions)),
                "fn": sum(t.label == label and j not in matched_t for j, t in enumerate(truth))
            } for label in LABELS},
            "by_shape": {shape: {
                "tp": sum(predictions[i].shape == shape for i in matched_p),
                "fp": sum(p.shape == shape and i not in matched_p for i, p in enumerate(predictions)),
                "fn": sum(t.shape == shape and j not in matched_t for j, t in enumerate(truth))
            } for shape in PREDICTED_SHAPES},
            "matches": matches,
            "unmatched_prediction_indices": [i for i in range(len(predictions)) if i not in matched_p],
            "unmatched_truth_indices": [j for j in range(len(truth)) if j not in matched_t]}
