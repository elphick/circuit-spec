"""Export validated CircuitSpec projects as editable KiCad schematics."""

import uuid

from circuitspec.components import COMPONENTS, Component
from circuitspec.models import Project
from circuitspec.validation import validate

_PIN_SPACING = 2.54
_PIN_LENGTH = 5.08
_BODY_HALF_WIDTH = 5.08


class KicadExportError(ValueError):
    """Raised when a project cannot be represented in the KiCad format."""


def _uuid() -> str:
    return str(uuid.uuid4())


def _quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _number(value: float) -> str:
    return f"{value:g}"


def _symbol(component_name: str, component: Component) -> tuple[str, dict[str, tuple[float, float]]]:
    if not component.symbol or ":" not in component.symbol:
        raise KicadExportError(f"component {component_name!r} has an unknown KiCad symbol")
    missing = set(component.ports) - set(component.symbol_pins)
    if missing:
        raise KicadExportError(
            f"component {component_name!r} has no KiCad pin mapping for "
            + ", ".join(sorted(missing))
        )

    ports = list(component.ports.values())
    pin_positions = {
        port.name: (
            -_PIN_LENGTH - _BODY_HALF_WIDTH,
            (len(ports) - 1) * _PIN_SPACING / 2 - index * _PIN_SPACING,
        )
        for index, port in enumerate(ports)
    }
    half_height = max(_BODY_HALF_WIDTH, (len(ports) - 1) * _PIN_SPACING / 2 + _PIN_SPACING)
    internal_name = component.symbol.rsplit(":", 1)[1]
    lines = [
        f"    (symbol {_quote(component.symbol)}",
        "      (pin_names (offset 0.508))",
        f"      (property \"Reference\" \"U\" (at 0 {_number(half_height + 2.54)} 0)",
        "        (effects (font (size 1.27 1.27))))",
        f"      (property \"Value\" {_quote(component_name)} (at 0 {_number(-half_height - 2.54)} 0)",
        "        (effects (font (size 1.27 1.27))))",
        f"      (symbol {_quote(internal_name + '_0_1')}",
        f"        (rectangle (start -{_number(_BODY_HALF_WIDTH)} {_number(half_height)})",
        f"          (end {_number(_BODY_HALF_WIDTH)} -{_number(half_height)})",
        "          (stroke (width 0) (type default)) (fill (type background))))",
        f"      (symbol {_quote(internal_name + '_1_1')}",
    ]
    for port in ports:
        pin_x, pin_y = pin_positions[port.name]
        pin_type = {
            "input": "input",
            "output": "output",
            "bidirectional": "bidirectional",
        }.get(port.direction, "passive")
        lines.extend(
            [
                f"        (pin {pin_type} line (at {_number(pin_x)} {_number(pin_y)} 0)",
                f"          (length {_number(_PIN_LENGTH)})",
                f"          (name {_quote(port.name)} (effects (font (size 1.0 1.0))))",
                f"          (number {_quote(component.symbol_pins[port.name])} "
                "(effects (font (size 1.0 1.0)))))",
            ]
        )
    lines.extend(["      )", "    )"])
    return "\n".join(lines), pin_positions


def to_kicad_sch(project: Project) -> str:
    """Return a self-contained, editable KiCad schematic for a validated project."""
    errors = validate(project)
    if errors:
        raise KicadExportError("project is not valid:\n" + "\n".join(errors))

    root_uuid = _uuid()
    lib_symbols: list[str] = []
    symbol_pins: dict[str, dict[str, tuple[float, float]]] = {}
    for component_name in dict.fromkeys(project.instances.values()):
        component = COMPONENTS.get(component_name)
        if component is None:
            raise KicadExportError(f"unknown component {component_name!r}")
        definition, pin_positions = _symbol(component_name, component)
        lib_symbols.append(definition)
        symbol_pins[component_name] = pin_positions

    lines = [
        "(kicad_sch",
        "  (version 20231120)",
        '  (generator "eeschema")',
        f'  (uuid "{root_uuid}")',
        '  (paper "A4")',
        "  (lib_symbols",
        *lib_symbols,
        "  )",
    ]
    for index, (instance_name, component_name) in enumerate(project.instances.items()):
        component = COMPONENTS[component_name]
        reference = f"U{index + 1}"
        x, y = 50 + index * 90, 105
        symbol_uuid = _uuid()
        lines.extend(
            [
                f"  (symbol (lib_id {_quote(component.symbol)}) (at {x} {y} 0) (unit 1)",
                "    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)",
                f'    (uuid "{symbol_uuid}")',
                f'    (property "Reference" {_quote(reference)} (at {x} {y - 2.54} 0)',
                "      (effects (font (size 1.27 1.27)) (justify left bottom)))",
                f'    (property "Value" {_quote(component_name)} (at {x} {y + 2.54} 0)',
                "      (effects (font (size 1.27 1.27)) (justify left top)))",
            ]
        )
        for port_name in component.ports:
            pin_number = component.symbol_pins[port_name]
            pin_uuid = _uuid()
            lines.append(f'    (pin "{pin_number}" (uuid "{pin_uuid}"))')
        lines.extend(
            [
                f'    (instances (project {_quote(project.name)} (path "/{root_uuid}"',
                f'      (reference {_quote(reference)}) (unit 1))))',
                "  )",
            ]
        )
        connected_ports = {
            endpoint.port: net.name
            for net in project.nets
            for endpoint in net.endpoints
            if endpoint.instance == instance_name
        }
        for port_name, net_name in connected_ports.items():
            pin_x, pin_y = symbol_pins[component_name][port_name]
            label_x = x + pin_x
            label_y = y - pin_y
            lines.extend(
                [
                    f"  (global_label {_quote(net_name)} (shape bidirectional)",
                    f"    (at {_number(label_x)} {_number(label_y)} 0)",
                    "    (effects (font (size 1.27 1.27)) (justify left bottom))",
                    f'    (uuid "{_uuid()}"))',
                ]
            )
    lines.extend(
        [
            "  (sheet_instances (path \"/\" (page \"1\")))",
            ")",
            "",
        ]
    )
    return "\n".join(lines)
