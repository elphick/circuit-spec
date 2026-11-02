"""Simple machine-readable graph renderers."""

from html import escape

from circuitspec.models import Project


def _connection_nets(project: Project) -> list[tuple[str, list[str]]]:
    nets = [
        (f"NET_{index}", [str(connection.source), str(connection.target)])
        for index, connection in enumerate(project.connections, start=1)
    ]
    nets.extend((name, [str(endpoint) for endpoint in members]) for name, members in project.buses.items())
    nets.extend((name, [str(endpoint) for endpoint in members]) for name, members in project.power.items())
    return nets


def _dot_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def to_dot(project: Project) -> str:
    """Render a project as a Graphviz DOT graph."""
    lines = ["graph circuit {"]
    for name, component in project.instances.items():
        label = f"{name}\n{component}"
        lines.append(f"  {_dot_quote(name)} [label={_dot_quote(label)}];")

    for index, connection in enumerate(project.connections, start=1):
        lines.append(
            f"  {_dot_quote(connection.source.instance)} -- "
            f"{_dot_quote(connection.target.instance)} "
            f"[label={_dot_quote(f'{connection.source.port} - {connection.target.port}')}, "
            f'id="connection{index}"];'
        )
    for bus, members in project.buses.items():
        for endpoint in members[1:]:
            lines.append(
                f"  {_dot_quote(members[0].instance)} -- {_dot_quote(endpoint.instance)} "
                f"[label={_dot_quote(bus)}, style=dashed];"
            )
    for net, members in project.power.items():
        for endpoint in members[1:]:
            lines.append(
                f"  {_dot_quote(members[0].instance)} -- {_dot_quote(endpoint.instance)} "
                f"[label={_dot_quote(net)}, color=red];"
            )
    lines.append("}")
    return "\n".join(lines) + "\n"


def to_stripboard_svg(project: Project) -> str:
    """Render a labeled stripboard-style connection map as SVG."""
    nets = _connection_nets(project)
    width = max(600, len(project.instances) * 190 + 160)
    row_height = 54
    height = max(100, 70 + len(nets) * row_height)
    instance_positions = {
        name: 140 + index * 190 for index, name in enumerate(project.instances)
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        "<title>Illustrative stripboard connection map</title>",
        '<rect width="100%" height="100%" fill="#fffdf5"/>',
        '<text x="20" y="28" font-family="sans-serif" font-size="16" font-weight="bold">'
        "Illustrative layout — verify before manufacture</text>",
    ]
    for name, x in instance_positions.items():
        parts.append(
            f'<text x="{x}" y="55" text-anchor="middle" font-family="sans-serif" '
            f'font-size="13">{escape(name)}</text>'
        )

    for row, (net_name, members) in enumerate(nets):
        y = 82 + row * row_height
        parts.append(f'<line x1="20" y1="{y}" x2="{width - 20}" y2="{y}" stroke="#b65b35" stroke-width="4"/>')
        parts.append(
            f'<text x="20" y="{y - 9}" font-family="sans-serif" font-size="11">'
            f'{escape(net_name)}</text>'
        )
        for member in members:
            instance, port = member.rsplit(".", 1)
            x = instance_positions.get(instance, 20)
            parts.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#243b53"/>')
            parts.append(
                f'<text x="{x + 9}" y="{y + 4}" font-family="sans-serif" '
                f'font-size="10">{escape(port)}</text>'
            )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def to_netlist(project: Project) -> dict:
    """Return a JSON-serializable netlist representation."""
    return {
        "project": {"name": project.name, "version": project.version},
        "components": [
            {"reference": name, "component": component}
            for name, component in project.instances.items()
        ],
        "nets": [
            {"name": name, "members": members}
            for name, members in _connection_nets(project)
        ],
    }
