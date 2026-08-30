#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rainforest_hall.concept_v2 import (  # noqa: E402
    LOCKED_DIMENSIONS,
    MIN_ROUTE_WIDTH_M,
    OUTPUT_PATHS,
    PROVISIONAL_ITEMS,
    REQUIRED_BASELINE_OBJECTS,
    REQUIRED_V2_OBJECTS,
    V1_BLEND_PATH,
    validate_locked_dimensions,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    scene = bpy.context.scene
    v1_path = ROOT / V1_BLEND_PATH
    v2_path = ROOT / OUTPUT_PATHS["blend"]
    glb_path = ROOT / OUTPUT_PATHS["glb"]
    preview_paths = [
        ROOT / OUTPUT_PATHS["entrance_preview"],
        ROOT / OUTPUT_PATHS["life_tree_preview"],
        ROOT / OUTPUT_PATHS["banquet_preview"],
    ]
    report_path = ROOT / OUTPUT_PATHS["report"]

    require(Path(bpy.data.filepath).resolve() == v2_path.resolve(), "Validator must open the V2 blend")
    actual = {
        "clear_width_m": float(scene.get("clear_width_m", -1)),
        "clear_length_m": float(scene.get("clear_length_m", -1)),
        "constant_width_samples_m": tuple(
            float(value) for value in str(scene.get("constant_width_samples_m", "")).split(",") if value
        ),
        "stage_height_m": float(scene.get("stage_height_m", -1)),
        "entrance_frame_width_m": float(scene.get("entrance_frame_width_m", -1)),
        "double_door_clear_width_m": float(scene.get("double_door_clear_width_m", -1)),
    }
    dimension_errors = validate_locked_dimensions(actual)
    require(not dimension_errors, "; ".join(dimension_errors))
    require(v1_path.exists(), "V1 source is missing")
    require(scene.get("v1_source_sha256") == sha256(v1_path), "V1 source hash changed")
    require(float(scene.get("min_customer_route_width_m", 0)) >= MIN_ROUTE_WIDTH_M, "Main route is too narrow")

    required_collections = {
        "V2_OPERABLE_LEFT_SYSTEM", "V2_CANOPY_PLANTS", "V2_BAR_PHOTO",
        "V2_LIFE_TREE_PROVISIONAL", "V2_MODULAR_FURNITURE", "V2_ROUTE_REFERENCE",
        "V2_LIGHTS_CAMERAS",
    }
    missing_collections = sorted(required_collections.difference(bpy.data.collections.keys()))
    require(not missing_collections, f"Missing collections: {missing_collections}")
    required_objects = set(REQUIRED_BASELINE_OBJECTS) | set(REQUIRED_V2_OBJECTS)
    missing_objects = sorted(required_objects.difference(bpy.data.objects.keys()))
    require(not missing_objects, f"Missing objects: {missing_objects}")
    operable_panels = [obj for obj in bpy.data.objects if obj.name.startswith("V2_Operable_Panel_")]
    require(len(operable_panels) >= 7 and all(obj.get("operable") for obj in operable_panels),
            "Operable left system is incomplete")
    require(scene.get("v2_replaces"), "V2 replacement relationship is missing")
    require(set(str(scene.get("provisional_items", "")).split(",")) == set(PROVISIONAL_ITEMS),
            "Provisional item metadata mismatch")

    require(glb_path.exists() and glb_path.read_bytes()[:4] == b"glTF", "Invalid or missing GLB")
    for path in preview_paths:
        require(path.exists() and path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {path}")

    files = {}
    for path in [v1_path, v2_path, glb_path, *preview_paths]:
        files[path.relative_to(ROOT).as_posix()] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    report = {
        "status": "PASS",
        "generated_and_validated_by": f"Blender {bpy.app.version_string}",
        "baseline": {"path": V1_BLEND_PATH.as_posix(), "sha256": sha256(v1_path)},
        "replacement_relationship": scene.get("v2_replaces"),
        "locked_dimensions": {
            "clear_width_m": {"expected": 14.8, "actual": actual["clear_width_m"], "pass": True},
            "clear_length_m": {"expected": 25.0, "actual": actual["clear_length_m"], "pass": True},
            "constant_width_samples_m": {"expected": [14.8, 14.8, 14.8], "actual": list(actual["constant_width_samples_m"]), "pass": True},
            "stage_height_m": {"expected": 4.0, "actual": actual["stage_height_m"], "pass": True},
            "entrance_frame_width_m": {"expected": 4.8, "actual": actual["entrance_frame_width_m"], "pass": True},
            "double_door_clear_width_m": {"expected": 2.2, "actual": actual["double_door_clear_width_m"], "pass": True},
        },
        "main_route": {"minimum_clear_width_m": MIN_ROUTE_WIDTH_M, "pass": True},
        "required_collections": sorted(required_collections),
        "provisional_before_site_remeasurement": sorted(PROVISIONAL_ITEMS),
        "files": files,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
