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

    seen_connections = set()
    for connection in project.connections:
        check_endpoint(connection.source, "connection")
        check_endpoint(connection.target, "connection")
        source_component = COMPONENTS.get(
            project.instances.get(connection.source.instance, "")
        )
        target_component = COMPONENTS.get(
            project.instances.get(connection.target.instance, "")
        )
        if (
            source_component
            and target_component
            and connection.source.port in source_component.ports
            and connection.target.port in target_component.ports
        ):
            source_port = source_component.ports[connection.source.port]
            target_port = target_component.ports[connection.target.port]
            if source_port.kind != target_port.kind:
                errors.append(
                    f"connection: incompatible port types {source_port.kind} and {target_port.kind}"
                )
            elif source_port.direction == target_port.direction in {"input", "output"}:
                errors.append(
                    f"connection: incompatible directions "
                    f"({connection.source}, {connection.target})"
                )
        edge = frozenset((connection.source, connection.target))
        if len(edge) < 2:
            errors.append(f"connection: cannot connect {connection.source} to itself")
        elif edge in seen_connections:
            errors.append(f"duplicate connection: {connection.source} -> {connection.target}")
        seen_connections.add(edge)

    named_nets = dict(project.nets)
    for bus_name, members in project.buses.items():
        if bus_name in named_nets:
            errors.append(f"duplicate net name: {bus_name}")
        named_nets[bus_name] = members
    for net_name, members in project.power.items():
        if net_name in named_nets:
            errors.append(f"duplicate net name: {net_name}")
        named_nets[net_name] = members

    assigned_endpoints = {}
    for net_name, members in named_nets.items():
        for endpoint in members:
            previous_net = assigned_endpoints.get(endpoint)
            if previous_net is not None and previous_net != net_name:
                errors.append(
                    f"{endpoint} is assigned to multiple nets: {previous_net}, {net_name}"
                )
            assigned_endpoints[endpoint] = net_name

    for net_name, members in project.nets.items():
        if len(members) < 2:
            errors.append(f"net {net_name}: must contain at least two endpoints")
        if len(set(members)) != len(members):
            errors.append(f"net {net_name}: duplicate endpoint")
        kinds = set()
        for endpoint in members:
            check_endpoint(endpoint, f"net {net_name}")
            component = COMPONENTS.get(project.instances.get(endpoint.instance, ""))
            port = component.ports.get(endpoint.port) if component else None
            if port:
                kinds.add("signal" if port.kind == "bus" else port.kind)
        if len(kinds) > 1:
            errors.append(f"net {net_name}: incompatible port types")

    for bus_name, members in project.buses.items():
        if len(members) < 2:
            errors.append(f"bus {bus_name}: must contain at least two endpoints")
        if len(set(members)) != len(members):
            errors.append(f"bus {bus_name}: duplicate endpoint")
        for endpoint in members:
            check_endpoint(endpoint, f"bus {bus_name}")
            component_name = project.instances.get(endpoint.instance)
            component = COMPONENTS.get(component_name or "")
            port = component.ports.get(endpoint.port) if component else None
            if port and port.kind not in {"signal", "bus"}:
                errors.append(f"bus {bus_name}: {endpoint} is not a signal or bus port")

    for net_name, members in project.power.items():
        if len(members) < 2:
            errors.append(f"power net {net_name}: must contain at least two endpoints")
        if len(set(members)) != len(members):
            errors.append(f"power net {net_name}: duplicate endpoint")
        for endpoint in members:
            check_endpoint(endpoint, f"power net {net_name}")
            component_name = project.instances.get(endpoint.instance)
            component = COMPONENTS.get(component_name or "")
            port = component.ports.get(endpoint.port) if component else None
            if port and port.kind != "power":
                errors.append(f"power net {net_name}: {endpoint} is not a power port")
    return errors


def require_valid(project: Project) -> None:
    """Raise SpecError when project validation fails."""
    errors = validate(project)
    if errors:
        raise SpecError("\n".join(errors))
