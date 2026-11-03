"""
Dual TMC2209 motion controller
==============================

Load the same YAML project used by the command-line examples, validate its
typed nets, and inspect its graph and export representations.
"""

from pathlib import Path

import yaml
from graphviz import Source

from circuitspec.io import load_project
from circuitspec.renderers import to_dot, to_kicad_sch, to_netlist, to_stripboard_svg
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
# Validate the netlist
# ------------------------
# Check the component ports and net endpoints before generating outputs.

errors = validate(project)
if errors:
    raise ValueError("\n".join(errors))

print(f"Validated {project.name}: {len(project.instances)} components")

# %%
# Export a DOT graph
# ------------------
# The graph describes the components and their connections in Graphviz format.
# Edges show undirected connectivity between component instances.

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
# * ``nets`` maps each net name to its ``instance.port`` endpoint references.
#
# Each named net in the source YAML remains intact in the exported netlist.
# The three components and all eight nets are shown
# below. UART addresses remain in the YAML; they are not exported in this
# connectivity-only netlist.

netlist = to_netlist(project)
print(f"Netlist contains {len(netlist['nets'])} nets.")
print(yaml.safe_dump(netlist, sort_keys=False), end="")

# %%
# Generate an illustrative stripboard map
# ---------------------------------------
# This SVG is a connectivity illustration, not a manufacturing-ready layout.
# Rows represent nets, with labeled pads showing their member ports.

stripboard_svg = to_stripboard_svg(project)
print(f"Illustrative stripboard SVG contains {stripboard_svg.count('<circle')} pad markers.")
DisplaySVG(stripboard_svg)

# %%
# Generate a KiCad schematic
# --------------------------
# The same validated connectivity can be exported as a self-contained
# schematic. The CLI writes this content to ``artifacts/project.kicad_sch``;
# the Python API returns it as text.

kicad_schematic = to_kicad_sch(project)
print(
    f"KiCad schematic: {len(project.instances)} components, "
    f"{len(project.nets)} named nets, {len(kicad_schematic)} characters."
)
print("\n".join(line.strip() for line in kicad_schematic.splitlines() if "(global_label " in line))
