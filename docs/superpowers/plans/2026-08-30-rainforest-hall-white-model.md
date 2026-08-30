# Rainforest Hall White Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dimensionally verified, editable white model of the Dongcun Rainforest Hall and export portable OBJ/GLB previews from the approved 14.80 × 25.00 × 4.00 m baseline.

**Architecture:** Keep all locked and provisional dimensions in one typed parameter module. A dependency-free geometry layer produces testable mesh primitives and portable exports; a separate Blender adapter consumes the same parameters to create the editable `.blend` scene when Blender is available. A static browser page displays the GLB without changing model geometry.

**Tech Stack:** Python 3.12 standard library, `unittest`, Blender Python API (`bpy`, optional execution environment), glTF 2.0/GLB, Wavefront OBJ, HTML/CSS/JavaScript.

**Spec:** `docs/superpowers/specs/2026-08-30-rainforest-hall-3d-design.md`

## Global Constraints

- Interior clear width is exactly 14.80 m.
- Interior clear length is exactly 25.00 m.
- The hall remains a constant-width rectangle for its full length.
- Stage-A wall/eave height is exactly 4.00 m.
- A-lobby glass entrance frame clear width is exactly 4.80 m.
- Double-door full-open clear width is exactly 2.20 m.
- The 13 m, 12 m, 24.5 m and narrowed-middle dimensions are forbidden.
- Preserve placeholders for the pitched roof, principal structure and right-side existing opening.
- Floor finish is sand.
- Ridge height, roof pitch, column grid, brace locations, opening heights, fire systems, MEP and life-tree geometry remain adjustable provisional parameters.
- Stage A must not introduce dining/banquet table arrays, full timber flooring or the rejected fully open left side.
- All generated geometry uses metres and must pass automated dimensional checks.

---

## File Map

- `src/rainforest_hall/parameters.py`: authoritative locked and provisional dimensions.
- `src/rainforest_hall/geometry.py`: dependency-free mesh primitives and scene assembly.
- `src/rainforest_hall/export_obj.py`: deterministic OBJ/MTL exporter.
- `src/rainforest_hall/export_glb.py`: deterministic glTF 2.0 binary exporter.
- `src/blender/build_white_model.py`: Blender adapter, materials, collections, camera and `.blend` save.
- `scripts/build_white_model.py`: command-line build entry point.
- `tests/test_parameters.py`: locked-dimension and rejected-dimension tests.
- `tests/test_geometry.py`: overall bounds, constant width, entrance and opening tests.
- `tests/test_exports.py`: OBJ and GLB structure tests.
- `web-preview/index.html`: local cross-device GLB viewer.
- `models/exports/rainforest-hall-white-v1.obj`: generated portable mesh.
- `models/exports/rainforest-hall-white-v1.mtl`: generated white/sand materials.
- `models/exports/rainforest-hall-white-v1.glb`: generated web preview model.
- `models/source/README.md`: Blender generation instructions and source-model status.
- `docs/dimensions/white-model-v1.json`: machine-readable dimension report.
- `README.md`: Chinese project entry point and build/check commands.

### Task 1: Authoritative Parameters and Dimension Guardrails

**Files:**
- Create: `src/rainforest_hall/__init__.py`
- Create: `src/rainforest_hall/parameters.py`
- Create: `tests/test_parameters.py`

**Interfaces:**
- Produces: `HallParameters` frozen dataclass and `DEFAULT_PARAMETERS: HallParameters`.
- Produces: `validate_parameters(params: HallParameters) -> list[str]`.
- Consumes: no project code.

- [ ] **Step 1: Write the failing parameter tests**

```python
# tests/test_parameters.py
import unittest
from dataclasses import replace
from src.rainforest_hall.parameters import DEFAULT_PARAMETERS, validate_parameters

class ParameterTests(unittest.TestCase):
    def test_locked_dimensions(self):
        p = DEFAULT_PARAMETERS
        self.assertEqual((p.clear_width, p.clear_length, p.eave_height), (14.8, 25.0, 4.0))
        self.assertEqual((p.entrance_frame_width, p.double_door_clear_width), (4.8, 2.2))

    def test_rejects_historic_wrong_dimensions(self):
        for field, value in (("clear_width", 13.0), ("clear_width", 12.0), ("clear_length", 24.5)):
            with self.subTest(field=field, value=value):
                errors = validate_parameters(replace(DEFAULT_PARAMETERS, **{field: value}))
                self.assertTrue(errors)

    def test_provisional_values_are_explicit(self):
        p = DEFAULT_PARAMETERS
        self.assertTrue(p.ridge_height_provisional)
        self.assertTrue(p.structure_grid_provisional)
        self.assertTrue(p.life_tree_provisional)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify the module is missing**

Run: `python3 -m unittest tests.test_parameters -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'src.rainforest_hall'`.

- [ ] **Step 3: Implement the immutable parameter model and validation**

```python
# src/rainforest_hall/parameters.py
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
            errors.append(f"{name} must be {expected:.2f} m, got {actual:.2f} m")
    if params.wall_thickness <= 0 or params.slab_thickness <= 0:
        errors.append("wall_thickness and slab_thickness must be positive")
    if params.roof_rise <= 0:
        errors.append("roof_rise must be positive and remain provisional")
    return errors
```

Create `src/rainforest_hall/__init__.py` exporting `DEFAULT_PARAMETERS`, `HallParameters` and `validate_parameters`.

- [ ] **Step 4: Run parameter tests**

Run: `python3 -m unittest tests.test_parameters -v`

Expected: 3 tests PASS.

- [ ] **Step 5: Commit the parameter baseline**

```bash
git add src/rainforest_hall tests/test_parameters.py
git commit -m "feat: lock rainforest hall dimensions"
```

### Task 2: White-Model Geometry and Spatial Verification

**Files:**
- Create: `src/rainforest_hall/geometry.py`
- Create: `tests/test_geometry.py`

**Interfaces:**
- Consumes: `HallParameters` and `DEFAULT_PARAMETERS`.
- Produces: `Mesh(name: str, vertices: tuple[tuple[float, float, float], ...], faces: tuple[tuple[int, ...], ...], material: str)`.
- Produces: `Scene(meshes: tuple[Mesh, ...], metadata: dict[str, object])`.
- Produces: `build_white_model(params: HallParameters) -> Scene`.
- Produces: `scene_bounds(scene: Scene) -> tuple[tuple[float, float, float], tuple[float, float, float]]`.

- [ ] **Step 1: Write failing geometry tests**

```python
# tests/test_geometry.py
import unittest
from src.rainforest_hall.geometry import build_white_model
from src.rainforest_hall.parameters import DEFAULT_PARAMETERS

class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.scene = build_white_model(DEFAULT_PARAMETERS)

    def test_clear_envelope_is_constant_width(self):
        envelope = self.scene.metadata["clear_envelope"]
        self.assertEqual(envelope["width_samples"], [14.8, 14.8, 14.8])
        self.assertEqual(envelope["length"], 25.0)
        self.assertEqual(envelope["eave_height"], 4.0)

    def test_required_components_exist(self):
        names = {mesh.name for mesh in self.scene.meshes}
        self.assertTrue({
            "sand_floor", "left_lower_operable_placeholder",
            "left_upper_screen", "right_wall_front",
            "right_wall_back", "entrance_frame",
            "roof_left", "roof_right", "ridge"
        }.issubset(names))

    def test_entrance_and_right_opening_metadata(self):
        self.assertEqual(self.scene.metadata["entrance"]["frame_clear_width"], 4.8)
        self.assertEqual(self.scene.metadata["entrance"]["door_clear_width"], 2.2)
        self.assertEqual(self.scene.metadata["right_opening"]["status"], "provisional")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run geometry tests and verify failure**

Run: `python3 -m unittest tests.test_geometry -v`

Expected: FAIL because `src.rainforest_hall/geometry.py` does not exist.

- [ ] **Step 3: Implement focused geometry primitives**

Implement `box_mesh(name, center, size, material)` with eight vertices and six quad faces. Implement `quad_mesh(name, vertices, material)` for roof planes. Keep the internal clear envelope at `x = ±7.40`, `y = 0…25.00`, `z = 0…4.00`. Place wall thickness outside this envelope so structural placeholders never reduce the locked clear dimensions.

```python
@dataclass(frozen=True)
class Mesh:
    name: str
    vertices: tuple[tuple[float, float, float], ...]
    faces: tuple[tuple[int, ...], ...]
    material: str

@dataclass(frozen=True)
class Scene:
    meshes: tuple[Mesh, ...]
    metadata: dict[str, object]

def build_white_model(params: HallParameters = DEFAULT_PARAMETERS) -> Scene:
    errors = validate_parameters(params)
    if errors:
        raise ValueError("; ".join(errors))
    half = params.clear_width / 2
    ridge_z = params.eave_height + params.roof_rise
    # Assemble sand floor, exterior wall/screen placeholders, centered
    # entrance frame, provisional right opening split, two roof planes,
    # ridge and lightweight principal-structure placeholders.
    # All exact coordinates derive from params; no historic dimensions.
    return Scene(meshes=tuple(meshes), metadata={
        "units": "metres",
        "clear_envelope": {
            "width_samples": [params.clear_width] * 3,
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
    })
```

The implementation must replace the explanatory assembly comments above with explicit `box_mesh` and `quad_mesh` calls; no implicit wall or roof dimensions may be introduced.

- [ ] **Step 4: Run geometry and parameter tests**

Run: `python3 -m unittest tests.test_parameters tests.test_geometry -v`

Expected: 6 tests PASS.

- [ ] **Step 5: Commit verified white-model geometry**

```bash
git add src/rainforest_hall/geometry.py tests/test_geometry.py
git commit -m "feat: build dimensioned rainforest hall white model"
```

### Task 3: Deterministic OBJ, GLB and Dimension-Report Exports

**Files:**
- Create: `src/rainforest_hall/export_obj.py`
- Create: `src/rainforest_hall/export_glb.py`
- Create: `scripts/build_white_model.py`
- Create: `tests/test_exports.py`
- Generate: `models/exports/rainforest-hall-white-v1.obj`
- Generate: `models/exports/rainforest-hall-white-v1.mtl`
- Generate: `models/exports/rainforest-hall-white-v1.glb`
- Generate: `docs/dimensions/white-model-v1.json`

**Interfaces:**
- Consumes: `Scene` from Task 2.
- Produces: `write_obj(scene: Scene, obj_path: Path) -> tuple[Path, Path]`.
- Produces: `write_glb(scene: Scene, glb_path: Path) -> Path`.
- Produces: command `python3 scripts/build_white_model.py --output-root .`.

- [ ] **Step 1: Write failing export tests**

```python
# tests/test_exports.py
import json, struct, tempfile, unittest
from pathlib import Path
from src.rainforest_hall.export_glb import write_glb
from src.rainforest_hall.export_obj import write_obj
from src.rainforest_hall.geometry import build_white_model

class ExportTests(unittest.TestCase):
    def test_obj_contains_named_components_and_metre_units(self):
        with tempfile.TemporaryDirectory() as temp:
            obj_path, mtl_path = write_obj(build_white_model(), Path(temp) / "hall.obj")
            text = obj_path.read_text(encoding="utf-8")
            self.assertIn("# units: metres", text)
            self.assertIn("o sand_floor", text)
            self.assertTrue(mtl_path.exists())

    def test_glb_has_valid_header_and_json_chunk(self):
        with tempfile.TemporaryDirectory() as temp:
            path = write_glb(build_white_model(), Path(temp) / "hall.glb")
            data = path.read_bytes()
            magic, version, total = struct.unpack_from("<4sII", data, 0)
            self.assertEqual((magic, version, total), (b"glTF", 2, len(data)))
            json_length, json_type = struct.unpack_from("<I4s", data, 12)
            self.assertEqual(json_type, b"JSON")
            payload = json.loads(data[20:20 + json_length].decode("utf-8").rstrip(" "))
            self.assertEqual(payload["asset"]["version"], "2.0")
            self.assertEqual(payload["asset"]["extras"]["units"], "metres")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run export tests and verify failure**

Run: `python3 -m unittest tests.test_exports -v`

Expected: FAIL because exporter modules do not exist.

- [ ] **Step 3: Implement OBJ/MTL exporter**

Write one `o <mesh.name>` block per mesh, offset face indices correctly, preserve material names, and write `White_Model`, `Sand`, `Structure`, `Screen` materials. Start the file with `# units: metres` and `mtllib <filename>.mtl`. Use UTF-8 and deterministic mesh order.

- [ ] **Step 4: Implement binary glTF 2.0 exporter**

Pack vertex positions as little-endian float32 and triangulated indices as unsigned integers. Align JSON and BIN chunks to four bytes. Create one node and mesh per named component, include min/max accessor bounds, and store locked dimensions in `asset.extras`:

```json
{
  "units": "metres",
  "clear_width": 14.8,
  "clear_length": 25.0,
  "eave_height": 4.0,
  "entrance_frame_width": 4.8,
  "double_door_clear_width": 2.2
}
```

- [ ] **Step 5: Implement the build command and JSON report**

The command creates output directories, validates parameters, builds the scene, writes OBJ/MTL/GLB, and serializes `scene.metadata` to `docs/dimensions/white-model-v1.json` using `ensure_ascii=False`, sorted keys and two-space indentation. It exits non-zero on any validation or export error.

- [ ] **Step 6: Run export tests**

Run: `python3 -m unittest tests.test_exports -v`

Expected: 2 tests PASS.

- [ ] **Step 7: Generate artifacts and inspect dimensions**

Run: `python3 scripts/build_white_model.py --output-root .`

Run: `python3 -c "import json; d=json.load(open('docs/dimensions/white-model-v1.json')); assert d['clear_envelope']=={'eave_height':4.0,'length':25.0,'width_samples':[14.8,14.8,14.8]}"`

Expected: both commands exit 0; OBJ, MTL and GLB files exist.

- [ ] **Step 8: Commit exporters and generated white model**

```bash
git add src/rainforest_hall/export_obj.py src/rainforest_hall/export_glb.py scripts/build_white_model.py tests/test_exports.py models/exports docs/dimensions/white-model-v1.json
git commit -m "feat: export rainforest hall white model"
```

### Task 4: Editable Blender Source Adapter and Browser Preview

**Files:**
- Create: `src/blender/build_white_model.py`
- Create: `models/source/README.md`
- Create: `web-preview/index.html`
- Modify: `README.md`
- Create: `.gitignore`

**Interfaces:**
- Consumes: `DEFAULT_PARAMETERS` and `build_white_model()`.
- Produces: Blender command `blender --background --python src/blender/build_white_model.py`.
- Produces: `models/source/rainforest-hall-white-v1.blend` when run with Blender.
- Produces: local preview entry point `web-preview/index.html`.

- [ ] **Step 1: Add a Blender-script contract test**

Add to `tests/test_exports.py`:

```python
def test_blender_adapter_declares_expected_output(self):
    script = Path("src/blender/build_white_model.py").read_text(encoding="utf-8")
    self.assertIn("rainforest-hall-white-v1.blend", script)
    self.assertIn("bpy.ops.wm.save_as_mainfile", script)
    self.assertNotIn("24.5", script)
    self.assertNotIn("13.0", script)
    self.assertNotIn("12.0", script)
```

- [ ] **Step 2: Run the contract test and verify failure**

Run: `python3 -m unittest tests.test_exports.ExportTests.test_blender_adapter_declares_expected_output -v`

Expected: FAIL with `FileNotFoundError`.

- [ ] **Step 3: Implement the Blender adapter**

The script imports project geometry after adding repository root to `sys.path`, clears the default scene, creates collections named `00_REFERENCE`, `10_ARCHITECTURE`, `20_PROVISIONAL_STRUCTURE`, `30_MATERIALS`, and `90_CAMERAS`, converts each dependency-free `Mesh` to a Blender mesh, applies white/sand/structure/screen materials, sets `scene.unit_settings.system = "METRIC"` and `scale_length = 1.0`, adds a dimension-check camera, stores locked values as scene custom properties, then saves to the absolute path `models/source/rainforest-hall-white-v1.blend`.

- [ ] **Step 4: Add a dependency-free browser preview**

Create `web-preview/index.html` with a full-window `<model-viewer>` element loading `../models/exports/rainforest-hall-white-v1.glb`, orbit controls, neutral lighting, an 14.8 × 25 × 4 m status badge, and a Chinese notice that roof/structure positions are provisional. Load `model-viewer` from `https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js`.

- [ ] **Step 5: Document exact user commands and status**

Replace the one-line README with a Chinese entry point covering:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_white_model.py --output-root .
python3 -m http.server 8000
blender --background --python src/blender/build_white_model.py
```

State explicitly that the committed GLB/OBJ are generated and viewable now, while the `.blend` file is generated only by the final Blender command. `models/source/README.md` repeats the Blender command and identifies all provisional fields.

- [ ] **Step 6: Run the complete verification suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests PASS.

Run: `python3 scripts/build_white_model.py --output-root .`

Expected: exit 0 and deterministic artifacts.

Run: `git diff --exit-code models/exports docs/dimensions/white-model-v1.json`

Expected: exit 0 after regeneration.

- [ ] **Step 7: Commit Blender adapter, preview and documentation**

```bash
git add src/blender/build_white_model.py models/source/README.md web-preview/index.html README.md .gitignore tests/test_exports.py
git commit -m "feat: add editable Blender workflow and GLB preview"
```

## Final Acceptance

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_white_model.py --output-root .
git diff --exit-code
```

Expected:

- Every test passes.
- Generated OBJ/MTL/GLB and dimension JSON are present.
- Dimension report contains width samples `[14.8, 14.8, 14.8]`, length `25.0`, eave height `4.0`, entrance frame `4.8` and double-door opening `2.2`.
- No generated or source file contains the rejected 24.5 m, 13 m or 12 m hall dimensions.
- Repository working tree is clean after deterministic regeneration.
- Blender adapter is ready to create `models/source/rainforest-hall-white-v1.blend` on a Blender-equipped computer.
