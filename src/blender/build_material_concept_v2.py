#!/usr/bin/env python3
import hashlib
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rainforest_hall.concept_v2 import (  # noqa: E402
    CAMERA_CONFIGS,
    LOCKED_DIMENSIONS,
    MIN_ROUTE_WIDTH_M,
    OUTPUT_PATHS,
    PROVISIONAL_ITEMS,
    V1_BLEND_PATH,
    select_render_engine,
    validate_locked_dimensions,
)


V1_PATH = ROOT / V1_BLEND_PATH
V2_PATH = ROOT / OUTPUT_PATHS["blend"]
GLB_PATH = ROOT / OUTPUT_PATHS["glb"]
PREVIEWS = {
    "V2_Camera_Entrance": ROOT / OUTPUT_PATHS["entrance_preview"],
    "V2_Camera_LifeTree": ROOT / OUTPUT_PATHS["life_tree_preview"],
    "V2_Camera_Banquet": ROOT / OUTPUT_PATHS["banquet_preview"],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def material(name, color, roughness=0.6, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, alpha)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, alpha)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        mat.surface_render_method = "DITHERED"
    return mat


def link_only(obj, collection):
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def box(name, location, scale, mat, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_only(obj, collection)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new("Soft_Edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    return obj


def cylinder(name, location, radius, depth, mat, collection, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    link_only(obj, collection)
    obj.data.materials.append(mat)
    return obj


def sphere(name, location, radius, mat, collection):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    link_only(obj, collection)
    obj.data.materials.append(mat)
    return obj


def camera(name, location, target, collection, lens=36):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    data.lens = lens
    data.sensor_width = 36
    return obj


def add_table_set(prefix, x, y, furniture, wood, rattan, green):
    cylinder(f"{prefix}_TableTop", (x, y, 0.72), 0.58, 0.07, wood, furniture)
    cylinder(f"{prefix}_TableBase", (x, y, 0.36), 0.10, 0.68, rattan, furniture)
    for index, (dx, dy) in enumerate(((-0.82, 0), (0.82, 0), (0, 0.82))):
        cylinder(f"{prefix}_Seat_{index}", (x + dx, y + dy, 0.42), 0.32, 0.10, green, furniture)
        cylinder(f"{prefix}_SeatLeg_{index}", (x + dx, y + dy, 0.21), 0.08, 0.42, rattan, furniture)


def main():
    if not V1_PATH.exists():
        raise RuntimeError(f"V1 baseline missing: {V1_PATH}")
    v1_hash = sha256(V1_PATH)
    bpy.ops.wm.open_mainfile(filepath=str(V1_PATH))
    scene = bpy.context.scene

    source_values = {
        "clear_width_m": float(scene.get("clear_width_m", -1)),
        "clear_length_m": float(scene.get("clear_length_m", -1)),
        "constant_width_samples_m": (14.8, 14.8, 14.8),
        "stage_height_m": float(scene.get("eave_height_m", -1)),
        "entrance_frame_width_m": float(scene.get("entrance_frame_width_m", -1)),
        "double_door_clear_width_m": float(scene.get("double_door_clear_width_m", -1)),
    }
    errors = validate_locked_dimensions(source_values)
    if errors:
        raise RuntimeError("V1 locked dimension validation failed: " + "; ".join(errors))

    for name in tuple(bpy.data.collections.keys()):
        if name.startswith("V2_"):
            bpy.data.collections.remove(bpy.data.collections[name])
    collections = {}
    for name in (
        "V2_MATERIAL_CONCEPT",
        "V2_OPERABLE_LEFT_SYSTEM",
        "V2_CANOPY_PLANTS",
        "V2_BAR_PHOTO",
        "V2_LIFE_TREE_PROVISIONAL",
        "V2_MODULAR_FURNITURE",
        "V2_ROUTE_REFERENCE",
        "V2_LIGHTS_CAMERAS",
    ):
        collection = bpy.data.collections.new(name)
        scene.collection.children.link(collection)
        collections[name] = collection

    sand = material("V2_Natural_Sand", (0.58, 0.38, 0.18), roughness=0.95)
    timber = material("V2_Warm_Timber", (0.27, 0.10, 0.035), roughness=0.55)
    rattan = material("V2_Rattan", (0.55, 0.31, 0.11), roughness=0.72)
    leaf = material("V2_Tropical_Leaf", (0.035, 0.24, 0.07), roughness=0.76)
    leaf_light = material("V2_Tropical_Leaf_Light", (0.14, 0.42, 0.12), roughness=0.72)
    fabric = material("V2_Sheer_Fabric", (0.86, 0.91, 0.78), roughness=0.86, alpha=0.48)
    bronze = material("V2_Bronze", (0.22, 0.11, 0.045), roughness=0.33, metallic=0.55)
    cream = material("V2_Cream_Upholstery", (0.72, 0.62, 0.46), roughness=0.82)
    accent = material("V2_Moss_Seat", (0.13, 0.30, 0.10), roughness=0.82)
    dark_screen = material("V2_Old_Interface_Masking", (0.055, 0.075, 0.052), roughness=0.92)
    route_mat = material("V2_Route_Reference", (0.15, 0.55, 0.95), roughness=0.5, alpha=0.14)

    sand_floor = bpy.data.objects.get("sand_floor")
    if sand_floor:
        sand_floor.data.materials.clear()
        sand_floor.data.materials.append(sand)
        sand_floor["v2_finish"] = "natural sand concept; non-construction"
    glass_reference = bpy.data.objects.get("double_door_reference")
    if glass_reference:
        glass_reference.hide_render = True
        glass_reference["v2_render_note"] = "hidden in concept previews only; geometry preserved"

    # Upper masking layer for the old dark interface.
    box("V2_Left_Upper_Masking", (-7.28, 12.5, 3.08), (0.08, 25.0, 1.72), dark_screen,
        collections["V2_OPERABLE_LEFT_SYSTEM"])
    for i, y in enumerate((2.1, 5.6, 9.1, 12.6, 16.1, 19.6, 23.1)):
        frame = box(f"V2_Operable_Panel_{i:02d}", (-7.15, y, 1.20), (0.12, 2.55, 2.15), rattan,
                    collections["V2_OPERABLE_LEFT_SYSTEM"], 0.035)
        frame["system_type"] = "semi-enclosed operable folding/sliding concept"
        frame["operable"] = True
        # Infill slats leave visual permeability and avoid a fixed solid wall.
        for j in range(5):
            box(f"V2_Panel_{i:02d}_Slat_{j:02d}", (-7.05, y - 0.92 + j * 0.46, 1.20),
                (0.05, 0.08, 1.85), timber, collections["V2_OPERABLE_LEFT_SYSTEM"])

    # Lightweight fabric ribbons and hanging planting remain below the existing roof.
    for i, (x, y, angle) in enumerate(((-4.8, 4.5, -5), (3.8, 7.2, 7), (-3.8, 10.5, 6),
                                       (4.6, 14.0, -7), (-4.6, 18.0, 5), (3.5, 21.6, -5))):
        ribbon = box(f"V2_Sheer_Canopy_{i:02d}", (x, y, 3.48), (4.3, 1.5, 0.025), fabric,
                     collections["V2_CANOPY_PLANTS"])
        ribbon.rotation_euler[2] = math.radians(angle)
        ribbon["lightweight_removable"] = True
        for j in range(3):
            sphere(f"V2_Hanging_Plant_{i:02d}_{j:02d}", (x - 1.2 + j * 1.2, y, 3.22),
                   0.34 + 0.08 * (j % 2), leaf if j != 1 else leaf_light,
                   collections["V2_CANOPY_PLANTS"])

    # Right-side bar stops before the original opening; photo frame marks rather than closes it.
    bar = collections["V2_BAR_PHOTO"]
    box("V2_Bar_Counter", (5.65, 8.5, 0.55), (2.7, 0.9, 1.1), timber, bar, 0.08)
    box("V2_Bar_Top", (5.65, 8.5, 1.13), (2.9, 1.05, 0.08), bronze, bar, 0.04)
    for i in range(3):
        cylinder(f"V2_Bar_Stool_{i:02d}", (4.8 + i * 0.85, 7.55, 0.42), 0.27, 0.72, rattan, bar)
    box("V2_Photo_Frame_Left", (6.85, 11.45, 1.45), (0.12, 0.15, 2.9), bronze, bar)
    box("V2_Photo_Frame_Right", (6.85, 13.55, 1.45), (0.12, 0.15, 2.9), bronze, bar)
    box("V2_Photo_Frame_Top", (6.85, 12.50, 2.90), (0.12, 2.25, 0.12), bronze, bar)
    for y in (11.7, 12.15, 12.85, 13.3):
        sphere(f"V2_Photo_Greenery_{str(y).replace('.', '_')}", (6.62, y, 2.55), 0.34, leaf, bar)

    # Adjustable life-tree placeholder is offset from the protected central route.
    tree = collections["V2_LIFE_TREE_PROVISIONAL"]
    trunk = cylinder("V2_LifeTree_Trunk_PROVISIONAL", (-3.35, 14.0, 1.65), 0.42, 3.3, timber, tree, 24)
    trunk["provisional"] = True
    trunk["adjustable_parameters"] = "location,height,canopy_diameter,foundation"
    for i, (dx, dy, dz, radius) in enumerate(((-0.9, 0.0, 3.1, 1.15), (0.25, -0.55, 3.25, 1.2),
                                               (0.65, 0.6, 3.05, 1.05), (-0.35, 0.75, 3.45, 0.9))):
        crown = sphere(f"V2_LifeTree_Canopy_{i:02d}_PROVISIONAL",
                       (-3.35 + dx, 14.0 + dy, dz), radius, leaf if i % 2 == 0 else leaf_light, tree)
        crown["provisional"] = True

    furniture = collections["V2_MODULAR_FURNITURE"]
    for index, (x, y) in enumerate(((-4.5, 3.4), (4.5, 4.6), (-4.5, 8.0), (4.45, 16.4),
                                     (-4.55, 19.0), (4.4, 21.0))):
        add_table_set(f"V2_TeaCoffee_{index:02d}", x, y, furniture, timber, rattan, accent)
    for index, (x, y, rot) in enumerate(((4.5, 2.1, 0), (-4.4, 22.2, 0), (4.5, 18.6, 0))):
        sofa = box(f"V2_Modular_Sofa_{index:02d}", (x, y, 0.42), (2.2, 0.78, 0.55), cream, furniture, 0.16)
        sofa.rotation_euler[2] = math.radians(rot)
        sofa["modular"] = True

    route = box("V2_Main_Customer_Route_REFERENCE", (0, 12.5, 0.018),
                (MIN_ROUTE_WIDTH_M, 25.0, 0.025), route_mat, collections["V2_ROUTE_REFERENCE"])
    route["clear_width_m"] = MIN_ROUTE_WIDTH_M
    route["route"] = "entrance to banquet hall; keep clear"
    route.hide_render = True
    for name, x in (("Left", -2.35), ("Right", 2.35)):
        post = box(f"V2_Banquet_Transition_{name}_PROVISIONAL", (x, 24.35, 1.55),
                   (0.16, 0.16, 3.10), bronze, collections["V2_ROUTE_REFERENCE"])
        post["provisional"] = True
    transition_header = box("V2_Banquet_Transition_Header_PROVISIONAL", (0, 24.35, 3.08),
                            (4.85, 0.16, 0.16), bronze, collections["V2_ROUTE_REFERENCE"])
    transition_header["provisional"] = True
    transition_header["purpose"] = "adjustable wayfinding frame toward banquet hall"

    lights = collections["V2_LIGHTS_CAMERAS"]
    world = scene.world or bpy.data.worlds.new("V2_Daylight_World")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.70, 0.82, 1.0, 1.0)
    background.inputs["Strength"].default_value = 0.55

    sun_data = bpy.data.lights.new("V2_Daylight_Sun", "SUN")
    sun_data.energy = 2.2
    sun_data.angle = math.radians(18)
    sun = bpy.data.objects.new("V2_Daylight_Sun", sun_data)
    lights.objects.link(sun)
    sun.rotation_euler = (math.radians(28), math.radians(-18), math.radians(-28))
    for index, (location, energy, size) in enumerate((((0, 5, 4.8), 850, 5.0), ((0, 17, 4.6), 1000, 6.0))):
        data = bpy.data.lights.new(f"V2_Daylight_Fill_{index}", "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(f"V2_Daylight_Fill_{index}", data)
        lights.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (0, 0, 0)

    cameras = {
        name: camera(name, config["location"], config["target"], lights, config["lens"])
        for name, config in CAMERA_CONFIGS.items()
    }

    supported_engines = tuple(
        item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items
    )
    scene.render.engine = select_render_engine(supported_engines)
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"

    scene["v2_status"] = "material concept generated from V1 baseline"
    scene["v2_replaces"] = "V1 for material-concept review only; V1 remains locked white-model baseline"
    scene["v1_source_relative_path"] = V1_BLEND_PATH.as_posix()
    scene["v1_source_sha256"] = v1_hash
    scene["blender_generated_version"] = bpy.app.version_string
    scene["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    scene["constant_width_samples_m"] = "14.8,14.8,14.8"
    scene["stage_height_m"] = 4.0
    scene["min_customer_route_width_m"] = MIN_ROUTE_WIDTH_M
    scene["provisional_items"] = ",".join(sorted(PROVISIONAL_ITEMS))

    V2_PATH.parent.mkdir(parents=True, exist_ok=True)
    GLB_PATH.parent.mkdir(parents=True, exist_ok=True)
    for path in PREVIEWS.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.save_as_mainfile(filepath=str(V2_PATH))
    for camera_name, path in PREVIEWS.items():
        scene.camera = cameras[camera_name]
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Render failed: {path}")

    scene.camera = cameras["V2_Camera_Entrance"]
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )
    if not GLB_PATH.exists() or GLB_PATH.read_bytes()[:4] != b"glTF":
        raise RuntimeError("Blender GLB export did not produce a valid header")
    bpy.ops.wm.save_as_mainfile(filepath=str(V2_PATH))
    print(f"V2_BLEND={V2_PATH}")
    print(f"V2_GLB={GLB_PATH}")
    for path in PREVIEWS.values():
        print(f"V2_PREVIEW={path}")
    print(f"BLENDER_VERSION={bpy.app.version_string}")


if __name__ == "__main__":
    main()
