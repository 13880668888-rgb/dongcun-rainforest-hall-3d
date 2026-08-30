import unittest
from dataclasses import replace

from src.rainforest_hall.parameters import DEFAULT_PARAMETERS, validate_parameters


class ParameterTests(unittest.TestCase):
    def test_locked_dimensions_drive_the_approved_clear_envelope(self):
        p = DEFAULT_PARAMETERS
        self.assertEqual(
            (p.clear_width, p.clear_length, p.eave_height),
            (14.8, 25.0, 4.0),
        )
        self.assertEqual(
            (p.entrance_frame_width, p.double_door_clear_width),
            (4.8, 2.2),
        )

    def test_historic_wrong_dimensions_are_rejected(self):
        cases = (
            ("clear_width", 13.0),
            ("clear_width", 12.0),
            ("clear_length", 24.5),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                changed = replace(DEFAULT_PARAMETERS, **{field: value})
                self.assertTrue(validate_parameters(changed))

    def test_unmeasured_geometry_remains_explicitly_provisional(self):
        p = DEFAULT_PARAMETERS
        self.assertTrue(p.ridge_height_provisional)
        self.assertTrue(p.structure_grid_provisional)
        self.assertTrue(p.life_tree_provisional)


if __name__ == "__main__":
    unittest.main()
