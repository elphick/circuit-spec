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

Install the package and validate or export the included example:

```bash
python -m pip install -e .
circuitspec validate examples/dual_tmc2209.yaml
circuitspec render graph examples/dual_tmc2209.yaml -o circuit.dot
circuitspec export netlist examples/dual_tmc2209.yaml -o netlist.json
```

The initial built-in library contains `ESP32_S3_ETH_POE` and `TMC2209`.
Connections, multi-member buses, and named power nets are checked against the
component ports. Graph output is Graphviz DOT; netlists are JSON.
