from dataclasses import dataclass
from typing import Any

from .parameters import DEFAULT_PARAMETERS, HallParameters, validate_parameters

Point = tuple[float, float, float]
Face = tuple[int, ...]


@dataclass(frozen=True)
class Mesh:
    name: str
    vertices: tuple[Point, ...]
    faces: tuple[Face, ...]
    material: str


@dataclass(frozen=True)
class Scene:
    meshes: tuple[Mesh, ...]
    metadata: dict[str, Any]


def box_mesh(name: str, center: Point, size: Point, material: str) -> Mesh:
    cx, cy, cz = center
    sx, sy, sz = (value / 2 for value in size)
    vertices = (
        (cx - sx, cy - sy, cz - sz),
        (cx + sx, cy - sy, cz - sz),
        (cx + sx, cy + sy, cz - sz),
        (cx - sx, cy + sy, cz - sz),
        (cx - sx, cy - sy, cz + sz),
        (cx + sx, cy - sy, cz + sz),
        (cx + sx, cy + sy, cz + sz),
        (cx - sx, cy + sy, cz + sz),
    )
    faces = (
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    )
    return Mesh(name, vertices, faces, material)


def quad_mesh(
    name: str, vertices: tuple[Point, Point, Point, Point], material: str
) -> Mesh:
    return Mesh(name, vertices, ((0, 1, 2, 3),), material)


def build_white_model(params: HallParameters = DEFAULT_PARAMETERS) -> Scene:
    errors = validate_parameters(params)
    if errors:
        raise ValueError("; ".join(errors))

    half = params.clear_width / 2
    t = params.wall_thickness
    ridge_z = params.eave_height + params.roof_rise
    opening_start = params.right_opening_offset - params.right_opening_width / 2
    opening_end = params.right_opening_offset + params.right_opening_width / 2
    frame_half = params.entrance_frame_width / 2
    door_height = 2.4

    meshes = (
        box_mesh(
            "sand_floor",
            (0, params.clear_length / 2, -params.slab_thickness / 2),
            (params.clear_width, params.clear_length, params.slab_thickness),
            "Sand",
        ),
        box_mesh(
            "left_lower_operable_placeholder",
            (-half - t / 2, params.clear_length / 2, 1.0),
            (t, params.clear_length, 2.0),
            "Screen",
        ),
        box_mesh(
            "left_upper_screen",
            (-half - t / 2, params.clear_length / 2, 3.0),
            (t, params.clear_length, 2.0),
            "White_Model",
        ),
        box_mesh(
            "right_wall_front",
            (half + t / 2, opening_start / 2, 2.0),
            (t, opening_start, 4.0),
            "White_Model",
        ),
        box_mesh(
            "right_wall_back",
            (half + t / 2, (opening_end + params.clear_length) / 2, 2.0),
            (t, params.clear_length - opening_end, 4.0),
            "White_Model",
        ),
        box_mesh(
            "entrance_frame_left",
            (-frame_half - t / 2, -t / 2, door_height / 2),
            (t, t, door_height),
            "Structure",
        ),
        box_mesh(
            "entrance_frame_right",
            (frame_half + t / 2, -t / 2, door_height / 2),
            (t, t, door_height),
            "Structure",
        ),
        box_mesh(
            "entrance_frame_header",
            (0, -t / 2, door_height + t / 2),
            (params.entrance_frame_width + 2 * t, t, t),
            "Structure",
        ),
        box_mesh(
            "double_door_reference",
            (0, 0.01, door_height / 2),
            (params.double_door_clear_width, 0.02, door_height),
            "Glass_Reference",
        ),
        quad_mesh(
            "roof_left",
            (
                (-half, 0, params.eave_height),
                (0, 0, ridge_z),
                (0, params.clear_length, ridge_z),
                (-half, params.clear_length, params.eave_height),
            ),
            "Roof_Reference",
        ),
        quad_mesh(
            "roof_right",
            (
                (0, 0, ridge_z),
                (half, 0, params.eave_height),
                (half, params.clear_length, params.eave_height),
                (0, params.clear_length, ridge_z),
            ),
            "Roof_Reference",
        ),
        box_mesh(
            "ridge",
            (0, params.clear_length / 2, ridge_z - 0.025),
            (0.05, params.clear_length, 0.05),
            "Structure",
        ),
    )

    return Scene(
        meshes=meshes,
        metadata={
            "units": "metres",
            "clear_envelope": {
                "width_samples": [params.clear_width] * 3,
                "sample_positions": [0.0, params.clear_length / 2, params.clear_length],
                "length": params.clear_length,
                "eave_height": params.eave_height,
            },
            "entrance": {
                "frame_clear_width": params.entrance_frame_width,
                "door_clear_width": params.double_door_clear_width,
            },
            "right_opening": {
                "width": params.right_opening_width,
                "offset": params.right_opening_offset,
                "status": "provisional",
            },
            "roof": {"ridge_height": ridge_z, "status": "provisional"},
            "life_tree": {"status": "provisional", "included": False},
        },
    )


def scene_bounds(scene: Scene) -> tuple[Point, Point]:
    vertices = [vertex for mesh in scene.meshes for vertex in mesh.vertices]
    low = tuple(min(vertex[axis] for vertex in vertices) for axis in range(3))
    high = tuple(max(vertex[axis] for vertex in vertices) for axis in range(3))
    return low, high
