import json
import struct
from pathlib import Path

from .export_obj import MATERIALS
from .geometry import Mesh, Scene


def _triangles(mesh: Mesh) -> list[int]:
    indices: list[int] = []
    for face in mesh.faces:
        for index in range(1, len(face) - 1):
            indices.extend((face[0], face[index], face[index + 1]))
    return indices


def _align(data: bytearray) -> None:
    data.extend(b"\x00" * ((-len(data)) % 4))


def write_glb(scene: Scene, glb_path: Path) -> Path:
    glb_path.parent.mkdir(parents=True, exist_ok=True)
    binary = bytearray()
    buffer_views: list[dict[str, int]] = []
    accessors: list[dict[str, object]] = []
    gltf_meshes: list[dict[str, object]] = []
    nodes: list[dict[str, object]] = []

    used_materials = list(dict.fromkeys(mesh.material for mesh in scene.meshes))
    material_lookup = {name: index for index, name in enumerate(used_materials)}
    materials = []
    for name in used_materials:
        color = MATERIALS[name]
        alpha = 0.45 if name in {"Glass_Reference", "Roof_Reference"} else 1.0
        materials.append(
            {
                "name": name,
                "pbrMetallicRoughness": {
                    "baseColorFactor": [*color, alpha],
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.85,
                },
                "alphaMode": "BLEND" if alpha < 1 else "OPAQUE",
                "doubleSided": True,
            }
        )

    for mesh in scene.meshes:
        _align(binary)
        position_offset = len(binary)
        for vertex in mesh.vertices:
            binary.extend(struct.pack("<3f", *vertex))
        position_length = len(mesh.vertices) * 12
        position_view = len(buffer_views)
        buffer_views.append(
            {
                "buffer": 0,
                "byteOffset": position_offset,
                "byteLength": position_length,
                "target": 34962,
            }
        )
        position_accessor = len(accessors)
        accessors.append(
            {
                "bufferView": position_view,
                "componentType": 5126,
                "count": len(mesh.vertices),
                "type": "VEC3",
                "min": [min(v[axis] for v in mesh.vertices) for axis in range(3)],
                "max": [max(v[axis] for v in mesh.vertices) for axis in range(3)],
            }
        )

        indices = _triangles(mesh)
        _align(binary)
        index_offset = len(binary)
        for index in indices:
            binary.extend(struct.pack("<I", index))
        index_view = len(buffer_views)
        buffer_views.append(
            {
                "buffer": 0,
                "byteOffset": index_offset,
                "byteLength": len(indices) * 4,
                "target": 34963,
            }
        )
        index_accessor = len(accessors)
        accessors.append(
            {
                "bufferView": index_view,
                "componentType": 5125,
                "count": len(indices),
                "type": "SCALAR",
                "min": [min(indices)],
                "max": [max(indices)],
            }
        )
        gltf_meshes.append(
            {
                "name": mesh.name,
                "primitives": [
                    {
                        "attributes": {"POSITION": position_accessor},
                        "indices": index_accessor,
                        "material": material_lookup[mesh.material],
                    }
                ],
            }
        )
        nodes.append({"name": mesh.name, "mesh": len(gltf_meshes) - 1})

    envelope = scene.metadata["clear_envelope"]
    entrance = scene.metadata["entrance"]
    document = {
        "asset": {
            "version": "2.0",
            "generator": "Dongcun Rainforest Hall deterministic exporter",
            "extras": {
                "units": "metres",
                "clear_width": envelope["width_samples"][0],
                "clear_length": envelope["length"],
                "eave_height": envelope["eave_height"],
                "entrance_frame_width": entrance["frame_clear_width"],
                "double_door_clear_width": entrance["door_clear_width"],
            },
        },
        "scene": 0,
        "scenes": [{"nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": gltf_meshes,
        "materials": materials,
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": buffer_views,
        "accessors": accessors,
    }

    json_bytes = json.dumps(
        document, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    json_bytes += b" " * ((-len(json_bytes)) % 4)
    _align(binary)
    total_length = 12 + 8 + len(json_bytes) + 8 + len(binary)
    payload = (
        struct.pack("<4sII", b"glTF", 2, total_length)
        + struct.pack("<I4s", len(json_bytes), b"JSON")
        + json_bytes
        + struct.pack("<I4s", len(binary), b"BIN\x00")
        + binary
    )
    glb_path.write_bytes(payload)
    return glb_path
