"""Replay the frozen experiment in a temporary clean source copy.

Run from the repository root with the pinned environment. This regenerates the
same final set for reproduction; it is not a new independent experiment.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main() -> None:
    source = Path(__file__).resolve().parents[1]
    recorded = json.loads((source / "evidence/final/results.json").read_text())
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)  # Do not inherit unrelated ROS pytest plugins.
    with tempfile.TemporaryDirectory(prefix="cv-inspection-replay-") as temporary:
        root = Path(temporary)
        for directory in ("quality_inspection", "config", "tests", "scripts"):
            shutil.copytree(source / directory, root / directory,
                            ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copyfile(source / "pytest.ini", root / "pytest.ini")
        shutil.copyfile(source / "evidence/frozen.json", root / "frozen.json")

        def run(*arguments: str) -> None:
            subprocess.run([sys.executable, *arguments], cwd=root, env=environment, check=True)

        run("-m", "pytest", "-q", "-rs")
        run("-m", "quality_inspection", "generate", "--output", "development")
        run("-m", "quality_inspection", "labels", "--annotations",
            "development/annotations.json", "--output", "labels")
        run("-m", "quality_inspection", "inspect", "--images", "development/images",
            "--output", "inspection")
        run("-m", "scripts.export_examples", "--annotations", "development/annotations.json",
            "--output", "showcase")
        run("-m", "quality_inspection", "evaluate", "--annotations",
            "development/annotations.json", "--output", "development_results")
        run("-m", "quality_inspection", "generate", "--split", "evaluation",
            "--frozen", "frozen.json", "--output", "evaluation")
        run("-m", "quality_inspection", "evaluate", "--annotations",
            "evaluation/annotations.json", "--frozen", "frozen.json", "--output", "final_results")
        replay = json.loads((root / "final_results/results.json").read_text())
        if replay != recorded:
            raise RuntimeError("Replayed final results differ from the preserved experiment")
        assert len(list((root / "final_results/images").glob("*.png"))) == 30
        assert len(list((root / "inspection").glob("*.annotated.png"))) == 15
        print("Clean source replay reproduced the complete final results JSON and all expected outputs.")


if __name__ == "__main__":
    main()
