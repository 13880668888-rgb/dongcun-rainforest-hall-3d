from pathlib import Path

from .geometry import Scene

MATERIALS = {
    "White_Model": (0.82, 0.84, 0.82),
    "Sand": (0.72, 0.58, 0.38),
    "Structure": (0.24, 0.27, 0.25),
    "Screen": (0.46, 0.57, 0.48),
    "Glass_Reference": (0.45, 0.72, 0.78),
    "Roof_Reference": (0.72, 0.80, 0.74),
}


def write_obj(scene: Scene, obj_path: Path) -> tuple[Path, Path]:
    obj_path.parent.mkdir(parents=True, exist_ok=True)
    mtl_path = obj_path.with_suffix(".mtl")
    lines = ["# units: metres", f"mtllib {mtl_path.name}"]
    vertex_offset = 1
    for mesh in scene.meshes:
        lines.extend((f"", f"o {mesh.name}", f"usemtl {mesh.material}"))
        lines.extend(f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in mesh.vertices)
        for face in mesh.faces:
            indices = " ".join(str(index + vertex_offset) for index in face)
            lines.append(f"f {indices}")
        vertex_offset += len(mesh.vertices)
    obj_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    material_lines = ["# Dongcun Rainforest Hall white-model materials"]
    used = {mesh.material for mesh in scene.meshes}
    for name, color in MATERIALS.items():
        if name not in used:
            continue
        material_lines.extend(
            (
                "",
                f"newmtl {name}",
                f"Kd {color[0]:.3f} {color[1]:.3f} {color[2]:.3f}",
                "Ka 0.100 0.100 0.100",
                "Ks 0.050 0.050 0.050",
                "d 1.000",
            )
        )
    mtl_path.write_text("\n".join(material_lines) + "\n", encoding="utf-8")
    return obj_path, mtl_path
