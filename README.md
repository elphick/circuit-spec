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
uv run circuitspec render graph examples/dual_tmc2209.yaml -o circuit.dot
uv run circuitspec render stripboard examples/dual_tmc2209.yaml -o stripboard.svg
uv run circuitspec export netlist examples/dual_tmc2209.yaml -o netlist.json
```

The initial built-in library contains `ESP32_S3_ETH_POE` and `TMC2209`.
Connections, multi-member buses, and named power nets are checked against the
component ports. Graph output is Graphviz DOT; netlists are JSON.
The SVG stripboard view is an illustrative connectivity map, not a manufacturing-ready
layout; verify clearances, cuts, and component footprints before building hardware.

## Documentation

The user guide, glossary, and executable example gallery are available in the
[documentation](docs/index.rst). Build the HTML site with:

```bash
uv sync --extra docs
uv run sphinx-build -b html docs docs/_build/html
```
