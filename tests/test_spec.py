import json
import tempfile
import unittest
from pathlib import Path

from circuitspec.io import SpecError, load_project
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
                "connections:\n  - controller.NOT_A_PIN -> driver.STEP\n"
                "  - controller.GPIO1 -> missing.STEP\n",
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

    def test_connection_type_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / "mismatch.yaml"
            spec.write_text(
                "instances:\n  controller:\n    component: ESP32_S3_ETH_POE\n"
                "  driver:\n    component: TMC2209\n"
                "connections:\n  - controller.3V3 -> driver.STEP\n",
                encoding="utf-8",
            )

            errors = validate(load_project(spec))

        self.assertTrue(any("incompatible port types" in error for error in errors))

    def test_duplicate_named_nets_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / "duplicate-nets.yaml"
            spec.write_text(
                "instances:\n  controller:\n    component: ESP32_S3_ETH_POE\n"
                "  driver:\n    component: TMC2209\n"
                "buses:\n  shared:\n    members: [controller.GPIO40, driver.UART]\n"
                "power:\n  shared: [controller.3V3, driver.VDD]\n",
                encoding="utf-8",
            )

            errors = validate(load_project(spec))

        self.assertIn("duplicate net name: shared", errors)

    def test_renderers_include_connections_and_power_nets(self):
        project = load_project(EXAMPLE)

        self.assertIn('"controller" -- "turntable"', to_dot(project))
        netlist = to_netlist(project)
        self.assertTrue(any(net["name"] == "24V" for net in netlist["nets"]))
        layout = to_stripboard_svg(project)
        self.assertIn("Illustrative layout", layout)
        self.assertIn("controller", layout)
        self.assertIn("GPIO38", layout)
        self.assertEqual(
            json.loads(json.dumps(netlist))["components"][0]["reference"],
            "controller",
        )
