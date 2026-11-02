"""
Dual TMC2209 motion controller
==============================

Load the same YAML project used by the command-line examples, validate its
typed connections, and inspect its graph and export representations.
"""

from pathlib import Path

from circuitspec.io import load_project
from circuitspec.renderers import to_dot, to_netlist, to_stripboard_svg
from circuitspec.validation import validate


def find_example() -> Path:
    """Find the repository's shared dual-driver YAML example."""
    starts = [Path.cwd()]
    script_file = globals().get("__file__")
    if script_file:
        starts.append(Path(script_file).resolve().parent)
    for start in starts:
        for directory in (start, *start.parents):
            candidate = directory / "examples" / "dual_tmc2209.yaml"
            if candidate.is_file():
                return candidate
    raise FileNotFoundError("Could not locate examples/dual_tmc2209.yaml")


project = load_project(find_example())
errors = validate(project)
if errors:
    raise ValueError("\n".join(errors))

print(f"Validated {project.name}: {len(project.instances)} components")
print("DOT graph:")
print(to_dot(project))

netlist = to_netlist(project)
print(f"Netlist contains {len(netlist['nets'])} nets.")
stripboard_svg = to_stripboard_svg(project)
print(f"Illustrative stripboard SVG contains {stripboard_svg.count('<circle')} pad markers.")
