# CircuitSpec

Hardware specification as code. Define components and typed-port connections in
YAML, validate them, then export a graph or a machine-readable netlist.

## Quick start

```yaml
project:
  name: simple_motion
instances:
  controller:
    component: ESP32_S3_ETH_POE
  driver:
    component: TMC2209
connections:
  - controller.GPIO38 -> driver.STEP
```

Install the package with UV and validate or export the included example:

```bash
uv sync
uv run circuitspec validate examples/dual_tmc2209.yaml
uv run circuitspec render graph examples/dual_tmc2209.yaml
uv run circuitspec render graph examples/dual_tmc2209.yaml --png artifacts/project_graph.png --svg artifacts/project_graph.svg
uv run circuitspec render dot examples/dual_tmc2209.yaml -o circuit.dot
uv run circuitspec render stripboard examples/dual_tmc2209.yaml -o stripboard.svg
uv run circuitspec export netlist examples/dual_tmc2209.yaml -o netlist.json
```

The initial built-in library contains `ESP32_S3_ETH_POE` and `TMC2209`.
Connections, named nets, multi-member buses, and power nets are checked against
the component ports. Graph output is standalone, offline Plotly HTML at
`artifacts/project_graph.html` (override with `--output`). Components, connected
ports, nets, buses, and power rails are visible, with undirected edges and hover
details. This shows logical connectivity, not signal flow or physical placement.
Kaleido exports PNG/SVG and requires Chrome; if needed, run
`uv run plotly_get_chrome` once before exporting images. HTML rendering does not
require Chrome. DOT export remains available with `render dot`; netlists are JSON.
The SVG stripboard view is an illustrative connectivity map, not a manufacturing-ready
layout; verify clearances, cuts, and component footprints before building hardware.

## Documentation

The user guide, glossary, and executable example gallery are available in the
[documentation](docs/index.rst). Gallery scripts and their shared YAML
specifications live together in [`examples/`](examples/). The scripts execute
during the documentation build. Install Graphviz separately and ensure its
`dot` executable is on `PATH` for the legacy DOT example. Chrome must be available
for the Plotly example's image exports and gallery thumbnail; Kaleido uses an
existing installation, or you can run `uv run plotly_get_chrome` if needed.
The interactive gallery figure loads Plotly JavaScript from a CDN; exported HTML
embeds it and works offline. Build the HTML site with:

```bash
uv sync --extra docs
uv run sphinx-build -b html docs docs/_build/html
```
