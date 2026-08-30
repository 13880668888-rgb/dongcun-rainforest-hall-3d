#!/usr/bin/env python3
import json
import math
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from src.rainforest_hall.geometry import build_white_model
from src.rainforest_hall.parameters import DEFAULT_PARAMETERS

TARGET_RELATIVE = Path("models/source/rainforest-hall-white-v1.blend")


def check_report() -> dict[str, object]:
    p = DEFAULT_PARAMETERS
    return {
        "status": "ready",
        "target": TARGET_RELATIVE.as_posix(),
        "clear_envelope": [p.clear_width, p.clear_length, p.eave_height],
        "entrance": [p.entrance_frame_width, p.double_door_clear_width],
        "provisional": ["roof", "structure_grid", "right_opening", "life_tree"],
    }


def _material(bpy, name: str, color: tuple[float, float, float, float]):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = 0.82
    principled.inputs["Alpha"].default_value = color[3]
    if color[3] < 1:
        if hasattr(material, "surface_render_method"):
            material.surface_render_method = "DITHERED"
        else:
            material.blend_method = "BLEND"
    return material


def build_blender_scene() -> Path:
    try:
        import bpy
    except ImportError as exc:
        raise SystemExit(
            "Blender Python API not found. Run with: "
            "blender --background --python src/blender/build_white_model.py"
        ) from exc

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in tuple(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene["clear_width_m"] = 14.8
    scene["clear_length_m"] = 25.0
    scene["eave_height_m"] = 4.0
    scene["entrance_frame_width_m"] = 4.8
    scene["double_door_clear_width_m"] = 2.2
    scene["provisional_geometry"] = "roof, structure_grid, right_opening, life_tree"

    default_collection = bpy.data.collections.get("Collection")
    if default_collection:
        bpy.data.collections.remove(default_collection)
    collection_names = (
        "00_REFERENCE",
        "10_ARCHITECTURE",
        "20_PROVISIONAL_STRUCTURE",
        "30_MATERIALS",
        "90_CAMERAS",
    )
    collections = {}
    for name in collection_names:
        collection = bpy.data.collections.new(name)
        scene.collection.children.link(collection)
        collections[name] = collection

    palette = {
        "White_Model": (0.82, 0.84, 0.82, 1.0),
        "Sand": (0.72, 0.58, 0.38, 1.0),
        "Structure": (0.24, 0.27, 0.25, 1.0),
        "Screen": (0.46, 0.57, 0.48, 1.0),
        "Glass_Reference": (0.45, 0.72, 0.78, 0.45),
        "Roof_Reference": (0.72, 0.80, 0.74, 0.45),
    }
    materials = {name: _material(bpy, name, color) for name, color in palette.items()}
    model = build_white_model()
    for item in model.meshes:
        mesh_data = bpy.data.meshes.new(f"{item.name}_mesh")
        mesh_data.from_pydata(item.vertices, [], item.faces)
        mesh_data.update()
        obj = bpy.data.objects.new(item.name, mesh_data)
        target = (
            "20_PROVISIONAL_STRUCTURE"
            if item.material in {"Structure", "Roof_Reference"}
            else "00_REFERENCE"
            if item.material == "Glass_Reference"
            else "10_ARCHITECTURE"
        )
        collections[target].objects.link(obj)
        obj.data.materials.append(materials[item.material])

    camera_data = bpy.data.cameras.new("Dimension_Check_Camera")
    camera = bpy.data.objects.new("Dimension_Check_Camera", camera_data)
    collections["90_CAMERAS"].objects.link(camera)
    camera.location = (22.0, -22.0, 16.0)
    camera.rotation_euler = (math.radians(63), 0, math.radians(43))
    camera.data.lens = 38
    scene.camera = camera

    target = REPOSITORY_ROOT / TARGET_RELATIVE
    target.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(target))
    return target


def main() -> int:
    if "--check" in sys.argv:
        print(json.dumps(check_report(), ensure_ascii=False, sort_keys=True))
        return 0
    target = build_blender_scene()
    print(f"Saved editable Blender model: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
