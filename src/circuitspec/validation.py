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
        elif (
            component_name in COMPONENTS
            and endpoint.port not in COMPONENTS[component_name].ports
        ):
            errors.append(f"{context}: unknown port {endpoint}")

    net_names = set()
    assigned_endpoints = {}
    for net in project.nets:
        if not net.name:
            errors.append("net names must be non-empty")
        if net.name in net_names:
            errors.append(f"duplicate net name: {net.name}")
        net_names.add(net.name)
        members = net.endpoints
        if not members:
            errors.append(f"net {net.name}: must contain at least one endpoint")
        if len(members) < 2:
            errors.append(f"net {net.name}: must contain at least two endpoints")
        if len(set(members)) != len(members):
            errors.append(f"net {net.name}: duplicate endpoint")
        kinds = set()
        for endpoint in members:
            check_endpoint(endpoint, f"net {net.name}")
            previous_net = assigned_endpoints.get(endpoint)
            if previous_net is not None and previous_net != net.name:
                errors.append(
                    f"{endpoint} is assigned to multiple nets: {previous_net}, {net.name}"
                )
            assigned_endpoints[endpoint] = net.name
            component = COMPONENTS.get(project.instances.get(endpoint.instance, ""))
            port = component.ports.get(endpoint.port) if component else None
            if port:
                kinds.add("signal" if port.kind == "bus" else port.kind)
        if len(kinds) > 1:
            errors.append(f"net {net.name}: incompatible port types")
    return errors


def require_valid(project: Project) -> None:
    """Raise SpecError when project validation fails."""
    errors = validate(project)
    if errors:
        raise SpecError("\n".join(errors))
