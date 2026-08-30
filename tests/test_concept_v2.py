import unittest

from src.rainforest_hall.concept_v2 import (
    CAMERA_CONFIGS,
    LOCKED_DIMENSIONS,
    OUTPUT_PATHS,
    PROVISIONAL_ITEMS,
    REQUIRED_BASELINE_OBJECTS,
    REQUIRED_V2_OBJECTS,
    select_render_engine,
    validate_locked_dimensions,
)


class ConceptV2ContractTests(unittest.TestCase):
    def test_locked_dimensions_match_approved_baseline(self):
        self.assertEqual(LOCKED_DIMENSIONS["clear_width_m"], 14.8)
        self.assertEqual(LOCKED_DIMENSIONS["clear_length_m"], 25.0)
        self.assertEqual(LOCKED_DIMENSIONS["constant_width_samples_m"], (14.8, 14.8, 14.8))
        self.assertEqual(LOCKED_DIMENSIONS["stage_height_m"], 4.0)
        self.assertEqual(LOCKED_DIMENSIONS["entrance_frame_width_m"], 4.8)
        self.assertEqual(LOCKED_DIMENSIONS["double_door_clear_width_m"], 2.2)

    def test_validation_rejects_dimension_drift(self):
        values = dict(LOCKED_DIMENSIONS)
        values["clear_length_m"] = 24.5
        self.assertIn("clear_length_m", validate_locked_dimensions(values)[0])

    def test_v2_outputs_never_overwrite_v1(self):
        self.assertEqual(len(OUTPUT_PATHS), len(set(OUTPUT_PATHS.values())))
        for path in OUTPUT_PATHS.values():
            self.assertIn("v2", path.lower())
            self.assertNotIn("white-v1", path.lower())

    def test_site_dependent_items_are_explicitly_provisional(self):
        self.assertTrue(
            {"roof", "structure_grid", "right_opening", "life_tree", "fixture_positions"}
            .issubset(PROVISIONAL_ITEMS)
        )

    def test_render_engine_uses_runtime_supported_eevee_identifier(self):
        self.assertEqual(
            select_render_engine(("BLENDER_EEVEE", "BLENDER_WORKBENCH", "CYCLES")),
            "BLENDER_EEVEE",
        )
        self.assertEqual(
            select_render_engine(("BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH")),
            "BLENDER_EEVEE_NEXT",
        )

    def test_v1_entrance_frame_contract_uses_its_three_real_objects(self):
        self.assertTrue(
            {"entrance_frame_left", "entrance_frame_right", "entrance_frame_header"}
            .issubset(REQUIRED_BASELINE_OBJECTS)
        )
        self.assertNotIn("entrance_frame", REQUIRED_BASELINE_OBJECTS)

    def test_banquet_view_keeps_enough_hall_depth_in_frame(self):
        config = CAMERA_CONFIGS["V2_Camera_Banquet"]
        self.assertLessEqual(config["location"][1], 19.0)
        self.assertGreaterEqual(config["target"][1], 24.5)

    def test_banquet_transition_is_an_explicit_v2_concept_object(self):
        self.assertIn("V2_Banquet_Transition_Header_PROVISIONAL", REQUIRED_V2_OBJECTS)


if __name__ == "__main__":
    unittest.main()
