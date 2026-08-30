#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from src.rainforest_hall.export_glb import write_glb
from src.rainforest_hall.export_obj import write_obj
from src.rainforest_hall.geometry import build_white_model
from src.rainforest_hall.parameters import DEFAULT_PARAMETERS, validate_parameters


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Stage-A white model.")
    parser.add_argument("--output-root", type=Path, default=REPOSITORY_ROOT)
    args = parser.parse_args()

    errors = validate_parameters(DEFAULT_PARAMETERS)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2

    root = args.output_root.resolve()
    export_dir = root / "models" / "exports"
    report_path = root / "docs" / "dimensions" / "white-model-v1.json"
    export_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    scene = build_white_model(DEFAULT_PARAMETERS)
    write_obj(scene, export_dir / "rainforest-hall-white-v1.obj")
    write_glb(scene, export_dir / "rainforest-hall-white-v1.glb")
    report_path.write_text(
        json.dumps(scene.metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"White model written to {export_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
