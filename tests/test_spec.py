import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from circuitspec.components import COMPONENTS
from circuitspec.cli import main
from circuitspec.io import SpecError, load_project
from circuitspec.models import Endpoint, Net, Project
from circuitspec.renderers import (
    KicadExportError,
    to_dot,
    to_kicad_sch,
    to_netlist,
    to_stripboard_svg,
)
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

    def test_kicad_export_contains_symbols_and_named_net_labels(self):
        project = load_project(ROOT / "examples/turntable_camera_controller.yaml")

        schematic = to_kicad_sch(project)

        self.assertIn("(version 20231120)", schematic)
        self.assertIn('"RF_Module:ESP32"', schematic)
        self.assertIn('"Driver_Motor:TMC2209"', schematic)
        self.assertIn('(global_label "A_STEP"', schematic)
        self.assertIn('(global_label "UART"', schematic)
        self.assertIn('(reference "U1")', schematic)
        self.assertIn('(reference "U3")', schematic)

    def test_kicad_export_rejects_missing_component_port_mapping(self):
        project = load_project(EXAMPLE)
        component = COMPONENTS["TMC2209"]
        incomplete = replace(component, symbol_pins={})

        with patch.dict(COMPONENTS, {"TMC2209": incomplete}):
            with self.assertRaisesRegex(KicadExportError, "no KiCad pin mapping"):
                to_kicad_sch(project)

    def test_kicad_export_rejects_unknown_symbol(self):
        project = load_project(EXAMPLE)
        component = COMPONENTS["TMC2209"]
        unsupported = replace(component, symbol="")

        with patch.dict(COMPONENTS, {"TMC2209": unsupported}):
            with self.assertRaisesRegex(KicadExportError, "unknown KiCad symbol"):
                to_kicad_sch(project)

    def test_kicad_export_cli_writes_turntable_schematic(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "turntable.kicad_sch"

            result = main([
                "export",
                "kicad",
                str(ROOT / "examples/turntable_camera_controller.yaml"),
                "-o",
                str(output),
            ])

            self.assertEqual(result, 0)
            self.assertIn("(kicad_sch", output.read_text(encoding="utf-8"))

    def test_kicad_export_cli_uses_default_artifact_path(self):
        original_directory = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                result = main([
                    "export",
                    "kicad",
                    str(ROOT / "examples/turntable_camera_controller.yaml"),
                ])
            finally:
                os.chdir(original_directory)

            output = Path(directory) / "artifacts" / "project.kicad_sch"
            self.assertEqual(result, 0)
            self.assertTrue(output.is_file())

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
