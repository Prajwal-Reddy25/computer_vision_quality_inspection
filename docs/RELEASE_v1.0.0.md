# Proposed v1.0.0 — Classical color inspection

Status: release draft only. No tag, push or GitHub release has been created.

## Included

- Red/blue HSV segmentation with opening/closing, contour-area filtering,
  deterministic boxes, counts and annotated outputs.
- Synthetic dataset generator and documented box annotations.
- Development investigation, frozen 30-image evaluation and recorded results.
- 48 passing tests and a verified clean replay.
- Explicit failure demonstrations, learning guide and contribution disclosure.

Final synthetic evaluation: 74 TP, 0 FP, 0 FN; precision/recall/F1 1.000.
This release would demonstrate a focused student project with AI assistance,
not real-camera or industrial validation.

## Publication steps requiring owner approval

There is currently no configured remote. After reviewing the repository and
approving publication, create an **empty** repository named
`computer-vision-quality-inspection` on GitHub. Do not initialize another README
or commit there. Then configure its URL, replacing YOUR_USERNAME:

```bash
git remote add origin https://github.com/YOUR_USERNAME/computer-vision-quality-inspection.git
git push -u origin master
```

The current local branch is `master`; a different branch name can be agreed
before publication. Do not push until the owner explicitly approves.

If the owner also approves the proposed release, the corresponding commands are:

```bash
git tag -a v1.0.0 -m "Classical color inspection with reproducible synthetic evaluation"
git push origin v1.0.0
```

Then create a GitHub release from that tag using these notes. Pushing a tag and
creating a release both remain pending approval. No license is selected on
the owner's behalf; choose one if public reuse permissions are desired.
