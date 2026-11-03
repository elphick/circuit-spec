import tempfile
import unittest
from pathlib import Path

from circuitspec.io import SpecError, load_project
from circuitspec.models import Endpoint, Net, Project
from circuitspec.renderers import to_dot, to_netlist, to_stripboard_svg
from circuitspec.validation import validate


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/dual_tmc2209.yaml"


class TestCircuitSpec(unittest.TestCase):
    def test_example_loads_and_validates(self):
        project = load_project(EXAMPLE)

        self.assertEqual(project.name, "dual_tmc2209")
        self.assertEqual(len(project.instances), 3)
        self.assertEqual(validate(project), [])

    def test_unknown_component_and_port_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / "bad.yaml"
            spec.write_text(
                "instances:\n  controller:\n    component: ESP32_S3_ETH_POE\n"
                "  driver:\n    component: TMC2209\n"
                "nets:\n  first: [controller.NOT_A_PIN, driver.STEP]\n"
                "  second: [controller.GPIO1, missing.STEP]\n",
                encoding="utf-8",
            )

            errors = validate(load_project(spec))

        self.assertTrue(any("unknown port controller.NOT_A_PIN" in error for error in errors))
        self.assertTrue(any("unknown instance 'missing'" in error for error in errors))

    def test_duplicate_yaml_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / "duplicate.yaml"
            spec.write_text(
                "instances:\n  controller:\n    component: TMC2209\n"
                "  controller:\n    component: TMC2209\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SpecError, "duplicate key"):
                load_project(spec)

    def test_net_type_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / "mismatch.yaml"
            spec.write_text(
                "instances:\n  controller:\n    component: ESP32_S3_ETH_POE\n"
                "  driver:\n    component: TMC2209\n"
                "nets:\n  mismatch: [controller.3V3, driver.STEP]\n",
                encoding="utf-8",
            )

            errors = validate(load_project(spec))

        self.assertTrue(any("incompatible port types" in error for error in errors))

    def test_duplicate_named_nets_are_reported(self):
        project = Project(
            "duplicate", "0.1",
            {"controller": "ESP32_S3_ETH_POE", "driver": "TMC2209"},
            [
                Net("shared", [Endpoint("controller", "GPIO40"), Endpoint("driver", "UART")]),
                Net("shared", [Endpoint("controller", "3V3"), Endpoint("driver", "VDD")]),
            ],
        )

        self.assertIn("duplicate net name: shared", validate(project))

    def test_renderers_include_nets(self):
        project = load_project(EXAMPLE)

        self.assertIn('"controller" -- "turntable"', to_dot(project))
        self.assertIn("style=dashed", to_dot(project))
        self.assertIn("color=red", to_dot(project))
        netlist = to_netlist(project)
        self.assertIn("24V", netlist["nets"])
        layout = to_stripboard_svg(project)
        self.assertIn("Illustrative layout", layout)
        self.assertIn("controller", layout)
        self.assertIn("GPIO38", layout)
        self.assertEqual(netlist["nets"]["A_STEP"], ["controller.GPIO38", "turntable.STEP"])

    def test_empty_and_duplicate_endpoint_nets_are_rejected(self):
        project = Project(
            "invalid", "0.1", {},
            [Net("empty", []), Net("duplicate", [
                Endpoint("missing", "PIN"), Endpoint("missing", "PIN"),
            ])],
        )
        errors = validate(project)
        self.assertTrue(any("empty: must contain" in error for error in errors))
        self.assertTrue(any("duplicate endpoint" in error for error in errors))
