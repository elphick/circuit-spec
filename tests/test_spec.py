import json

import pytest

from circuitspec.io import SpecError, load_project
from circuitspec.renderers import to_dot, to_netlist
from circuitspec.validation import validate


EXAMPLE = "examples/dual_tmc2209.yaml"


def test_example_loads_and_validates():
    project = load_project(EXAMPLE)

    assert project.name == "dual_tmc2209"
    assert len(project.instances) == 3
    assert validate(project) == []


def test_unknown_component_and_port_are_reported(tmp_path):
    spec = tmp_path / "bad.yaml"
    spec.write_text(
        "instances:\n  controller:\n    component: ESP32_S3_ETH_POE\n"
        "  driver:\n    component: TMC2209\n"
        "connections:\n  - controller.NOT_A_PIN -> driver.STEP\n"
        "  - controller.GPIO1 -> missing.STEP\n",
        encoding="utf-8",
    )

    errors = validate(load_project(spec))

    assert any("unknown port controller.NOT_A_PIN" in error for error in errors)
    assert any("unknown instance 'missing'" in error for error in errors)


def test_duplicate_yaml_keys_are_rejected(tmp_path):
    spec = tmp_path / "duplicate.yaml"
    spec.write_text(
        "instances:\n  controller:\n    component: TMC2209\n"
        "  controller:\n    component: TMC2209\n",
        encoding="utf-8",
    )

    with pytest.raises(SpecError, match="duplicate key"):
        load_project(spec)


def test_renderers_include_connections_and_power_nets():
    project = load_project(EXAMPLE)

    assert '"controller" -- "turntable"' in to_dot(project)
    netlist = to_netlist(project)
    assert any(net["name"] == "24V" for net in netlist["nets"])
    assert json.loads(json.dumps(netlist))["components"][0]["reference"] == "controller"
