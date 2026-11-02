"""Simple machine-readable graph renderers."""

from circuitspec.models import Project


def to_dot(project: Project) -> str:
    """Render a project as a Graphviz DOT graph."""
    lines = ["graph circuit {"]
    for name, component in project.instances.items():
        lines.append(f'  "{name}" [label="{name}\\n{component}"];')

    for index, connection in enumerate(project.connections, start=1):
        lines.append(
            f'  "{connection.source.instance}" -- "{connection.target.instance}" '
            f'[label="{connection.source.port} - {connection.target.port}", id="connection{index}"];'
        )
    for bus, members in project.buses.items():
        for endpoint in members[1:]:
            lines.append(
                f'  "{members[0].instance}" -- "{endpoint.instance}" '
                f'[label="{bus}", style=dashed];'
            )
    for net, members in project.power.items():
        for endpoint in members[1:]:
            lines.append(
                f'  "{members[0].instance}" -- "{endpoint.instance}" '
                f'[label="{net}", color=red];'
            )
    lines.append("}")
    return "\n".join(lines) + "\n"


def to_netlist(project: Project) -> dict:
    """Return a JSON-serializable netlist representation."""
    nets = []
    for index, connection in enumerate(project.connections, start=1):
        nets.append({"name": f"NET_{index}", "members": [str(connection.source), str(connection.target)]})
    nets.extend(
        {"name": name, "members": [str(endpoint) for endpoint in members]}
        for name, members in project.buses.items()
    )
    nets.extend(
        {"name": name, "members": [str(endpoint) for endpoint in members]}
        for name, members in project.power.items()
    )
    return {
        "project": {"name": project.name, "version": project.version},
        "components": [
            {"reference": name, "component": component}
            for name, component in project.instances.items()
        ],
        "nets": nets,
    }
