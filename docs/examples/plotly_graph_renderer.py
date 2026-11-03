"""
Interactive Plotly hardware graph
=================================

Component circles, small port circles, net diamonds, outlined bus diamonds, and
coloured power squares describe electrical membership, not signal flow or
physical placement. Hover for details, drag to pan, and use the toolbar to zoom.
Only connected ports are displayed to keep the graph readable.

Kaleido image export requires Chrome; install it with ``plotly_get_chrome`` if
it is not already available.
"""

from pathlib import Path

import plotly.graph_objects as go

from circuitspec.io import load_project
from circuitspec.renderers import render_graph
from circuitspec.validation import require_valid


class DisplayGraph:
    """Provide self-contained HTML to Sphinx Gallery without a CDN."""

    def __init__(self, figure: go.Figure) -> None:
        self.figure = figure

    def _repr_html_(self) -> str:
        return self.figure.to_html(include_plotlyjs=True, full_html=False)


def find_specification() -> Path:
    """Find the YAML in scripts, gallery builds, and downloaded notebooks."""
    starts = [Path.cwd()]
    if "__file__" in globals():
        starts.append(Path(__file__).resolve().parent)
    for start in starts:
        for directory in (start, *start.parents):
            for relative in (
                "turntable_camera_controller.yaml",
                "docs/examples/turntable_camera_controller.yaml",
            ):
                candidate = directory / relative
                if candidate.is_file():
                    return candidate
    raise FileNotFoundError("Could not locate turntable_camera_controller.yaml")


# %%
# Load and validate the specification
# ------------------------------------
# Named signal nets, the three-member UART bus, and power rails all come from
# the YAML alongside this example. Validation happens before rendering.

project = load_project(find_specification())
require_valid(project)
print(f"Validated {project.name}: {len(project.instances)} components")

# %%
# Render and export
# ------------------
# The renderer consumes the project model, not YAML. HTML embeds JavaScript
# and works offline; PNG and SVG are static documentation assets.

figure = render_graph(project)
artifacts = Path("artifacts")
artifacts.mkdir(exist_ok=True)
figure.write_html(artifacts / "project_graph.html", include_plotlyjs=True)
figure.write_image(artifacts / "project_graph.png")
figure.write_image(artifacts / "project_graph.svg")

# %%
# Explore the graph
# ------------------
# No arrows or source/target styling are used: every member of a net is
# electrically connected to the others.

DisplayGraph(figure)
