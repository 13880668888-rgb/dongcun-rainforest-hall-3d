from dataclasses import dataclass


@dataclass(frozen=True)
class HallParameters:
    clear_width: float = 14.8
    clear_length: float = 25.0
    eave_height: float = 4.0
    entrance_frame_width: float = 4.8
    double_door_clear_width: float = 2.2
    wall_thickness: float = 0.10
    slab_thickness: float = 0.08
    roof_rise: float = 1.50
    right_opening_width: float = 2.40
    right_opening_offset: float = 12.50
    ridge_height_provisional: bool = True
    structure_grid_provisional: bool = True
    life_tree_provisional: bool = True


DEFAULT_PARAMETERS = HallParameters()


def validate_parameters(params: HallParameters) -> list[str]:
    errors: list[str] = []
    locked = {
        "clear_width": 14.8,
        "clear_length": 25.0,
        "eave_height": 4.0,
        "entrance_frame_width": 4.8,
        "double_door_clear_width": 2.2,
    }
    for name, expected in locked.items():
        actual = getattr(params, name)
        if abs(actual - expected) > 1e-9:
            errors.append(
                f"{name} must be {expected:.2f} m, got {actual:.2f} m"
            )
    if params.wall_thickness <= 0 or params.slab_thickness <= 0:
        errors.append("wall_thickness and slab_thickness must be positive")
    if params.roof_rise <= 0:
        errors.append("roof_rise must be positive and remain provisional")
    return errors
