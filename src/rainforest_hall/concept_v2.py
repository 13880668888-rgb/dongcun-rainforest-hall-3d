from pathlib import Path
from typing import Mapping

from .parameters import DEFAULT_PARAMETERS


LOCKED_DIMENSIONS = {
    "clear_width_m": DEFAULT_PARAMETERS.clear_width,
    "clear_length_m": DEFAULT_PARAMETERS.clear_length,
    "constant_width_samples_m": (
        DEFAULT_PARAMETERS.clear_width,
        DEFAULT_PARAMETERS.clear_width,
        DEFAULT_PARAMETERS.clear_width,
    ),
    "stage_height_m": DEFAULT_PARAMETERS.eave_height,
    "entrance_frame_width_m": DEFAULT_PARAMETERS.entrance_frame_width,
    "double_door_clear_width_m": DEFAULT_PARAMETERS.double_door_clear_width,
}

OUTPUT_PATHS = {
    "blend": "models/source/rainforest-hall-material-concept-v2.blend",
    "glb": "models/exports/rainforest-hall-material-concept-v2.glb",
    "entrance_preview": "renders/concept-v2/entrance-to-rainforest-hall-v2.png",
    "life_tree_preview": "renders/concept-v2/middle-life-tree-v2.png",
    "banquet_preview": "renders/concept-v2/rainforest-hall-to-banquet-hall-v2.png",
    "report": "docs/dimensions/material-concept-v2.json",
}

V1_BLEND_PATH = Path("models/source/rainforest-hall-white-v1.blend")
MIN_ROUTE_WIDTH_M = 2.2

PROVISIONAL_ITEMS = frozenset(
    {"roof", "structure_grid", "right_opening", "life_tree", "fixture_positions"}
)

REQUIRED_BASELINE_OBJECTS = frozenset(
    {
        "sand_floor",
        "right_wall_front",
        "right_wall_back",
        "entrance_frame_left",
        "entrance_frame_right",
        "entrance_frame_header",
        "roof_left",
        "roof_right",
    }
)

REQUIRED_V2_OBJECTS = frozenset(
    {
        "V2_Bar_Counter",
        "V2_LifeTree_Trunk_PROVISIONAL",
        "V2_Main_Customer_Route_REFERENCE",
        "V2_Banquet_Transition_Header_PROVISIONAL",
        "V2_Camera_Entrance",
        "V2_Camera_LifeTree",
        "V2_Camera_Banquet",
    }
)

CAMERA_CONFIGS = {
    "V2_Camera_Entrance": {
        "location": (0.1, -3.7, 1.75), "target": (0, 11.8, 1.5), "lens": 30,
    },
    "V2_Camera_LifeTree": {
        "location": (4.9, 9.0, 1.65), "target": (-3.25, 14.0, 2.0), "lens": 38,
    },
    "V2_Camera_Banquet": {
        "location": (0.2, 16.6, 1.70), "target": (0, 24.6, 1.55), "lens": 34,
    },
}


def validate_locked_dimensions(values: Mapping[str, object]) -> list[str]:
    errors: list[str] = []
    for name, expected in LOCKED_DIMENSIONS.items():
        actual = values.get(name)
        if actual != expected:
            errors.append(f"{name}: expected {expected!r}, got {actual!r}")
    return errors


def select_render_engine(supported: tuple[str, ...]) -> str:
    for candidate in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        if candidate in supported:
            return candidate
    raise ValueError(f"No Eevee render engine is available: {supported!r}")
