"""Validation for typed CircuitSpec port graphs."""

from circuitspec.components import COMPONENTS
from circuitspec.io import SpecError
from circuitspec.models import Endpoint, Project


def validate(project: Project) -> list[str]:
    """Return all validation errors found in a project."""
    errors = []
    for name, component in project.instances.items():
        if component not in COMPONENTS:
            errors.append(f"instance {name}: unknown component {component!r}")

    def check_endpoint(endpoint: Endpoint, context: str) -> None:
        component_name = project.instances.get(endpoint.instance)
        if component_name is None:
            errors.append(f"{context}: unknown instance {endpoint.instance!r}")
        elif component_name in COMPONENTS and endpoint.port not in COMPONENTS[component_name].ports:
            errors.append(f"{context}: unknown port {endpoint}")

    seen_connections = set()
    for connection in project.connections:
        check_endpoint(connection.source, "connection")
        check_endpoint(connection.target, "connection")
        edge = frozenset((connection.source, connection.target))
        if len(edge) < 2:
            errors.append(f"connection: cannot connect {connection.source} to itself")
        elif edge in seen_connections:
            errors.append(f"duplicate connection: {connection.source} -> {connection.target}")
        seen_connections.add(edge)

    for bus_name, members in project.buses.items():
        if len(members) < 2:
            errors.append(f"bus {bus_name}: must contain at least two endpoints")
        if len(set(members)) != len(members):
            errors.append(f"bus {bus_name}: duplicate endpoint")
        for endpoint in members:
            check_endpoint(endpoint, f"bus {bus_name}")

    for net_name, members in project.power.items():
        if len(members) < 2:
            errors.append(f"power net {net_name}: must contain at least two endpoints")
        if len(set(members)) != len(members):
            errors.append(f"power net {net_name}: duplicate endpoint")
        for endpoint in members:
            check_endpoint(endpoint, f"power net {net_name}")
    return errors


def require_valid(project: Project) -> None:
    """Raise SpecError when project validation fails."""
    errors = validate(project)
    if errors:
        raise SpecError("\n".join(errors))
