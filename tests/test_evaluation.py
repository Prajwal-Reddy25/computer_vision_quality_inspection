import pytest

from quality_inspection.evaluation import evaluate_image, intersection_over_union, match_detections, summarize
from quality_inspection.models import Detection


def test_iou_half_open_boxes():
    assert intersection_over_union((0, 0, 10, 10), (5, 0, 10, 10)) == pytest.approx(1 / 3)
    assert intersection_over_union((0, 0, 10, 10), (10, 0, 10, 10)) == 0
    assert intersection_over_union((0, 0, 10, 10), (0, 0, 10, 10)) == 1


def test_duplicate_detection_is_false_positive():
    obj = Detection("red", (0, 0, 10, 10))
    row = evaluate_image("test.png", "nominal", [obj, obj], [obj])
    assert (row["tp"], row["fp"], row["fn"]) == (1, 1, 0)
    assert len(row["unmatched_prediction_indices"]) == 1


def test_wrong_color_has_correct_count_but_wrong_detection():
    truth = Detection("red", (0, 0, 10, 10))
    pred = Detection("blue", truth.bbox)
    row = evaluate_image("test.png", "nominal", [pred], [truth])
    summary = summarize([row])
    assert (summary["tp"], summary["fp"], summary["fn"]) == (0, 1, 1)
    assert summary["count_mae"] == 0
    assert summary["exact_class_count_images"] == 0
    assert row["by_class"]["red"]["fn"] == 1
    assert row["by_class"]["blue"]["fp"] == 1


def test_matching_reassigns_to_avoid_greedy_lost_match():
    truth = [Detection("red", (0, 0, 10, 10)), Detection("red", (5, 0, 10, 10))]
    predictions = [Detection("red", (2, 0, 10, 10)), Detection("red", (0, 0, 8, 10))]
    assert len(match_detections(predictions, truth)) == 2


def test_micro_metrics_and_empty_denominators():
    obj = Detection("red", (0, 0, 10, 10))
    empty = evaluate_image("empty.png", "nominal", [], [])
    missing = evaluate_image("missing.png", "dim", [], [obj])
    assert summarize([empty])["precision"] is None
    summary = summarize([empty, missing])
    assert summary["recall"] == 0
    assert summary["count_mae"] == 0.5
    assert summary["exact_count_images"] == 1


@pytest.mark.parametrize("threshold", [0, -1, 1.01])
def test_invalid_matching_threshold(threshold):
    with pytest.raises(ValueError):
        match_detections([], [], threshold)
