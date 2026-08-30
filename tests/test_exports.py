import json
import struct
import subprocess
import sys
import tempfile
import unittest
import shutil
from pathlib import Path

from src.rainforest_hall.export_glb import write_glb
from src.rainforest_hall.export_obj import write_obj
from src.rainforest_hall.geometry import build_white_model


class ExportTests(unittest.TestCase):
    def test_obj_preserves_named_components_and_metre_units(self):
        with tempfile.TemporaryDirectory() as temp:
            obj_path, mtl_path = write_obj(
                build_white_model(), Path(temp) / "hall.obj"
            )
            text = obj_path.read_text(encoding="utf-8")
            self.assertIn("# units: metres", text)
            self.assertIn("o sand_floor", text)
            self.assertIn("o double_door_reference", text)
            self.assertTrue(mtl_path.exists())

    def test_glb_has_valid_header_json_and_locked_dimension_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            path = write_glb(build_white_model(), Path(temp) / "hall.glb")
            data = path.read_bytes()
            magic, version, total = struct.unpack_from("<4sII", data, 0)
            self.assertEqual((magic, version, total), (b"glTF", 2, len(data)))
            json_length, json_type = struct.unpack_from("<I4s", data, 12)
            self.assertEqual(json_type, b"JSON")
            payload = json.loads(
                data[20 : 20 + json_length].decode("utf-8").rstrip(" ")
            )
            extras = payload["asset"]["extras"]
            self.assertEqual(extras["units"], "metres")
            self.assertEqual(
                (
                    extras["clear_width"],
                    extras["clear_length"],
                    extras["eave_height"],
                ),
                (14.8, 25.0, 4.0),
            )
            self.assertEqual(len(payload["nodes"]), len(build_white_model().meshes))

    def test_build_command_writes_models_and_dimension_report(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_white_model.py",
                    "--output-root",
                    temp,
                ],
                cwd=Path(__file__).parents[1],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            root = Path(temp)
            self.assertTrue(
                (root / "models/exports/rainforest-hall-white-v1.glb").exists()
            )
            report = json.loads(
                (root / "docs/dimensions/white-model-v1.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(report["clear_envelope"]["width_samples"], [14.8] * 3)

    def test_blender_adapter_check_reports_target_and_locked_dimensions(self):
        result = subprocess.run(
            [sys.executable, "src/blender/build_white_model.py", "--check"],
            cwd=Path(__file__).parents[1],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["target"], "models/source/rainforest-hall-white-v1.blend")
        self.assertEqual(report["clear_envelope"], [14.8, 25.0, 4.0])
        self.assertEqual(report["status"], "ready")

    @unittest.skipUnless(shutil.which("blender"), "Blender is not installed")
    def test_blender_adapter_generates_an_editable_source_model(self):
        root = Path(__file__).parents[1]
        target = root / "models/source/rainforest-hall-white-v1.blend"
        target.unlink(missing_ok=True)
        result = subprocess.run(
            [
                "blender",
                "--background",
                "--python-exit-code",
                "1",
                "--python",
                "src/blender/build_white_model.py",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertNotIn("Traceback", output)
        self.assertTrue(target.exists())
        self.assertGreater(target.stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
