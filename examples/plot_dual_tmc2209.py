"""
Dual TMC2209 motion controller
==============================

Load the same YAML project used by the command-line examples, validate its
typed connections, and inspect its graph and export representations.
"""

import json
from pathlib import Path

import yaml
from graphviz import Source

from circuitspec.io import load_project
from circuitspec.renderers import to_dot, to_netlist, to_stripboard_svg
from circuitspec.validation import validate


class DisplaySVG:
    """Expose SVG output to Sphinx Gallery's HTML capture."""

    def __init__(self, svg: str) -> None:
        self.svg = svg

    def _repr_html_(self) -> str:
        return self.svg


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


# %%
# Load and inspect the specification
# ----------------------------------
# Load the shared YAML into a typed project, then pretty-print the source
# specification, including metadata such as the drivers' UART addresses.

example_path = find_example()
project = load_project(example_path)
specification = yaml.safe_load(example_path.read_text(encoding="utf-8"))
print(yaml.safe_dump(specification, sort_keys=False), end="")

# %%
# Validate the connections
# ------------------------
# Check the component ports and net connections before generating outputs.

errors = validate(project)
if errors:
    raise ValueError("\n".join(errors))

print(f"Validated {project.name}: {len(project.instances)} components")

# %%
# Export a DOT graph
# ------------------
# The graph describes the components and their connections in Graphviz format.
# Solid edges show port-to-port connections, dashed edges show the UART bus,
# and red edges show shared power nets.

dot = to_dot(project)
print(dot)

# %%
# Display the graph
# -----------------
# Render the same DOT source as SVG using Graphviz's ``dot`` executable.
# The Python ``graphviz`` package is included in the documentation dependencies;
# Graphviz itself must be installed separately, with ``dot`` on ``PATH``.

DisplaySVG(Source(dot).pipe(format="svg", encoding="utf-8"))

# %%
# Export a netlist
# ----------------
# The machine-readable netlist groups the endpoints into electrical nets.
# Each net is a set of ports that should be electrically connected, rather than
# a physical routing plan:
#
# * ``project`` contains the project name and version.
# * ``components`` maps each instance's ``reference`` to its component type.
# * ``nets`` lists each net's ``name`` and ``members`` in ``instance.port`` form.
#
# ``NET_1`` through ``NET_4`` come from the explicit port-to-port connections.
# ``uart`` comes from the shared bus; ``3V3``, ``24V``, and ``GND`` come from
# the power definitions. The three components and all eight nets are shown
# below. UART addresses remain in the YAML; they are not exported in this
# connectivity-only netlist.

netlist = to_netlist(project)
print(f"Netlist contains {len(netlist['nets'])} nets.")
print(json.dumps(netlist, indent=2))

# %%
# Generate an illustrative stripboard map
# ---------------------------------------
# This SVG is a connectivity illustration, not a manufacturing-ready layout.
# Rows represent nets, with labeled pads showing their member ports.

stripboard_svg = to_stripboard_svg(project)
print(f"Illustrative stripboard SVG contains {stripboard_svg.count('<circle')} pad markers.")
DisplaySVG(stripboard_svg)
