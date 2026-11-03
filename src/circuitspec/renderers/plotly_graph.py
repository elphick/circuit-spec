"""Interactive, undirected views of validated electrical connectivity."""

from html import escape

import networkx as nx
import plotly.graph_objects as go

from circuitspec.components import COMPONENTS
from circuitspec.models import Endpoint, Project


_POWER_COLORS = {
    "24V": "#d62728",
    "5V": "#ff7f0e",
    "3V3": "#2ca02c",
    "GND": "#000000",
}


def _net_kind(project: Project, members: list[Endpoint]) -> str:
    kinds = set()
    for endpoint in members:
        component = COMPONENTS.get(project.instances.get(endpoint.instance, ""))
        port = component.ports.get(endpoint.port) if component else None
        if port:
            kinds.add(port.kind)
    if kinds == {"power"}:
        return "power"
    if "bus" in kinds:
        return "bus"
    return "net"


def render_graph(project: Project) -> go.Figure:
    """Return a logical connectivity figure for an already validated project.

    Only connected ports are shown; unconnected component instances remain
    visible. Layout is deterministic and carries no physical or flow semantics.
    Save offline HTML with ``fig.write_html(path, include_plotlyjs=True)`` and
    PNG/SVG with ``fig.write_image(path)`` (Kaleido requires Chrome).
    """
    graph = nx.Graph()
    for name, component in project.instances.items():
        graph.add_node(
            ("instance", name),
            kind="instance",
            label=f"{escape(name)}<br>({escape(component)})",
            hover=f"Instance: {escape(name)}<br>Component: {escape(component)}",
        )

    nets = [
        (_net_kind(project, net.endpoints), net.name, net.endpoints)
        for net in project.nets
    ]
    titles = {"net": "Net", "bus": "Bus", "power": "Power Net"}
    for index, (kind, name, members) in enumerate(nets):
        net_id = (kind, index)
        graph.add_node(
            net_id,
            kind=kind,
            label=escape(name),
            hover=(
                f"{titles[kind]}: {escape(name)}<br>Members: {len(members)}<br>"
                + "<br>".join(escape(str(member)) for member in members)
            ),
            color=_POWER_COLORS.get(name.upper(), "#9467bd"),
        )
        for endpoint in members:
            port_id = ("port", endpoint.instance, endpoint.port)
            graph.add_node(
                port_id,
                kind="port",
                label=escape(endpoint.port),
                hover=f"Instance: {escape(endpoint.instance)}<br>Port: {escape(endpoint.port)}",
            )
            graph.add_edge(("instance", endpoint.instance), port_id)
            graph.add_edge(port_id, net_id)

    positions = nx.spring_layout(graph, seed=42, iterations=100)
    edge_x, edge_y = [], []
    for left, right in graph.edges:
        edge_x.extend([float(positions[left][0]), float(positions[right][0]), None])
        edge_y.extend([float(positions[left][1]), float(positions[right][1]), None])

    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line={"color": "#a0aab4", "width": 1.5},
        hoverinfo="skip", showlegend=False,
        meta={"kind": "edges"},
    ))
    styles = {
        "instance": ("Components", "circle", 36, "#3366aa", 2),
        "port": ("Connected ports", "circle", 10, "#66788a", 1),
        "net": ("Nets", "diamond", 20, "#17a2a4", 1),
        "bus": ("Buses", "diamond", 26, "#ab63fa", 4),
        "power": ("Power nets", "square", 22, None, 2),
    }
    for kind, (title, symbol, size, color, outline) in styles.items():
        nodes = [(node, data) for node, data in graph.nodes(data=True) if data["kind"] == kind]
        if not nodes:
            continue
        figure.add_trace(go.Scatter(
            x=[float(positions[node][0]) for node, _ in nodes],
            y=[float(positions[node][1]) for node, _ in nodes],
            ids=[str(node) for node, _ in nodes],
            text=[data["label"] for _, data in nodes],
            hovertext=[data["hover"] for _, data in nodes],
            hovertemplate="%{hovertext}<extra></extra>",
            mode="markers+text", textposition="top center",
            textfont={"size": 11 if kind == "port" else 13},
            marker={
                "symbol": symbol, "size": size,
                "color": color if color else [data["color"] for _, data in nodes],
                "line": {"color": "#263445", "width": outline},
            },
            name=title, meta={"kind": kind},
        ))

    figure.update_layout(
        title={"text": f"{escape(project.name)} - logical connectivity"},
        template="plotly_white", width=1100, height=800,
        margin={"l": 60, "r": 60, "t": 90, "b": 60},
        hovermode="closest", dragmode="pan",
        xaxis={"visible": False},
        yaxis={"visible": False, "scaleanchor": "x", "scaleratio": 1},
        legend={"orientation": "h", "y": 1.05},
    )
    return figure
