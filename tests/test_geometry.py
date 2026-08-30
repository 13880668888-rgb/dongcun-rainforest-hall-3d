import unittest

from src.rainforest_hall.geometry import build_white_model, scene_bounds
from src.rainforest_hall.parameters import DEFAULT_PARAMETERS


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.scene = build_white_model(DEFAULT_PARAMETERS)

    def test_clear_envelope_stays_constant_width_for_full_length(self):
        envelope = self.scene.metadata["clear_envelope"]
        self.assertEqual(envelope["width_samples"], [14.8, 14.8, 14.8])
        self.assertEqual(envelope["sample_positions"], [0.0, 12.5, 25.0])
        self.assertEqual(envelope["length"], 25.0)
        self.assertEqual(envelope["eave_height"], 4.0)

    def test_white_model_contains_required_spatial_components(self):
        names = {mesh.name for mesh in self.scene.meshes}
        required = {
            "sand_floor",
            "left_lower_operable_placeholder",
            "left_upper_screen",
            "right_wall_front",
            "right_wall_back",
            "entrance_frame_left",
            "entrance_frame_right",
            "entrance_frame_header",
            "double_door_reference",
            "roof_left",
            "roof_right",
            "ridge",
        }
        self.assertTrue(required.issubset(names), required - names)

    def test_entrance_openings_keep_approved_clear_widths(self):
        entrance = self.scene.metadata["entrance"]
        self.assertEqual(entrance["frame_clear_width"], 4.8)
        self.assertEqual(entrance["door_clear_width"], 2.2)

    def test_right_opening_and_roof_are_marked_provisional(self):
        self.assertEqual(self.scene.metadata["right_opening"]["status"], "provisional")
        self.assertEqual(self.scene.metadata["roof"]["status"], "provisional")

    def test_scene_bounds_include_roof_without_reducing_clear_envelope(self):
        low, high = scene_bounds(self.scene)
        self.assertLessEqual(low[0], -7.4)
        self.assertGreaterEqual(high[0], 7.4)
        self.assertEqual(high[1], 25.0)
        self.assertEqual(high[2], 5.5)


if __name__ == "__main__":
    unittest.main()
