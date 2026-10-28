from collections import Counter
import hashlib
import json

import pytest

from quality_inspection.dataset import CONDITIONS, generate_dataset, load_annotations
from quality_inspection.visualization import read_image


def test_development_reproducible_and_annotations_valid(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    manifest = generate_dataset(first)
    assert generate_dataset(second) == manifest
    assert load_annotations(first / "annotations.json") == manifest
    assert Counter(r["condition"] for r in manifest["images"]) == {c: 3 for c in CONDITIONS}
    assert any(not row["objects"] for row in manifest["images"])
    for row in manifest["images"]:
        image = read_image(first / row["file"])
        assert image.shape == (360, 480, 3)
        assert hashlib.sha256((first / row["file"]).read_bytes()).digest() == hashlib.sha256(
            (second / row["file"]).read_bytes()).digest()
        # Nonoverlap is an explicit scope assumption, including rotated boxes.
        for i, obj in enumerate(row["objects"]):
            x, y, w, h = obj["bbox"]
            for other in row["objects"][i + 1:]:
                ox, oy, ow, oh = other["bbox"]
                assert x + w <= ox or ox + ow <= x or y + h <= oy or oy + oh <= y
    with pytest.raises(ValueError, match="overwrite"):
        generate_dataset(first)


def test_annotation_path_traversal_rejected(tmp_path):
    manifest = {"schema_version": 1, "images": [
        {"file": "../outside.png", "width": 10, "height": 10, "objects": []}]}
    target = tmp_path / "annotations.json"
    target.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="relative paths"):
        load_annotations(target)
