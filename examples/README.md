# Six-object synthetic showcase

The original image is copied from new development image 001 (seed 31415).
It contains every color/shape pair exactly once: red/blue rectangles, circles
and triangles. This is development data, not independent final performance evidence.

![Ground Truth](showcase_ground_truth.png)

![Prediction](showcase_prediction.png)

The images are separate executed overlays, with explicit synthetic titles.
Input: images/showcase.png. Ground truth: annotations.json (schema 2).
Predictions: detections.json, including shapes and the package fingerprint.

Reproduce into a fresh directory from the repository root:

```bash
python -m scripts.export_examples --annotations data/shapes_development/annotations.json --output runs/showcase
```
