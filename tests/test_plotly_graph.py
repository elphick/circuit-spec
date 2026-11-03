import contextlib
import io
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

import plotly.graph_objects as go
import yaml

from circuitspec.cli import main
from circuitspec.io import SpecError, load_project
from circuitspec.models import Connection, Endpoint, Project
from circuitspec.renderers import render_graph, to_dot, to_netlist, to_stripboard_svg
from circuitspec.validation import require_valid, validate


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs/examples/turntable_camera_controller.yaml"


class ScriptSources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.sources.extend(value for key, value in attrs if key == "src")


class TestPlotlyGraph(unittest.TestCase):
    def setUp(self):
        self.project = load_project(EXAMPLE)
        require_valid(self.project)

    def test_project_loads_named_nets_bus_and_power(self):
        self.assertIsInstance(self.project, Project)
        self.assertEqual(self.project.nets["A_STEP"], [
            Endpoint("controller", "GPIO38"), Endpoint("turntable", "STEP"),
        ])
        self.assertEqual(len(self.project.buses["UART"]), 3)
        self.assertEqual(validate(self.project), [])

    def test_nets_only_yaml_is_supported(self):
        raw = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
        raw["nets"]["UART"] = raw.pop("buses")["UART"]["members"]
        raw["nets"].update(raw.pop("power"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "project.yaml"
            path.write_text(yaml.safe_dump(raw), encoding="utf-8")
            project = load_project(path)
        require_valid(project)
        figure = render_graph(project)
        traces = {trace.meta["kind"]: trace for trace in figure.data}
        self.assertIn("UART", traces["bus"].text)
        self.assertTrue(any("Bus: UART<br>Members: 3" in text
                            for text in traces["bus"].hovertext))
        self.assertIn("24V", traces["power"].text)
        self.assertIn("GND", traces["power"].text)

    def test_visible_nodes_hover_and_distinct_styles(self):
        figure = render_graph(self.project)
        self.assertIsInstance(figure, go.Figure)
        traces = {trace.meta["kind"]: trace for trace in figure.data}
        self.assertEqual(len(traces["instance"].x), 3)
        self.assertIn("turntable<br>(TMC2209)", traces["instance"].text)
        self.assertIn("Instance: turntable<br>Component: TMC2209",
                      traces["instance"].hovertext)
        self.assertIn("STEP", traces["port"].text)
        self.assertIn("Instance: turntable<br>Port: STEP", traces["port"].hovertext)
        self.assertIn("A_STEP", traces["net"].text)
        self.assertIn("UART", traces["bus"].text)
        self.assertIn("Bus: UART<br>Members: 3", traces["bus"].hovertext[0])
        for endpoint in self.project.buses["UART"]:
            self.assertIn(str(endpoint), traces["bus"].hovertext[0])
        self.assertGreater(traces["bus"].marker.line.width, traces["net"].marker.line.width)
        self.assertNotEqual(traces["power"].marker.symbol, traces["net"].marker.symbol)
        colors = dict(zip(traces["power"].text, traces["power"].marker.color))
        self.assertEqual(colors["24V"], "#d62728")
        self.assertEqual(colors["GND"], "#000000")
        self.assertEqual(colors["3V3"], "#2ca02c")
        self.assertTrue(any("Power Net: GND<br>Members: 3" in text
                            for text in traces["power"].hovertext))

    def test_edges_are_undirected_component_port_net_links(self):
        figure = render_graph(self.project)
        positions = {}
        for trace in figure.data[1:]:
            for x, y in zip(trace.x, trace.y):
                positions[(x, y)] = trace.meta["kind"]
        edge_trace = figure.data[0]
        kinds = []
        for index in range(0, len(edge_trace.x), 3):
            left = (edge_trace.x[index], edge_trace.y[index])
            right = (edge_trace.x[index + 1], edge_trace.y[index + 1])
            pair = {positions[left], positions[right]}
            kinds.append(pair)
            self.assertIsNone(edge_trace.x[index + 2])
            self.assertIn("port", pair)
            self.assertEqual(len(pair), 2)
        endpoints = [
            endpoint
            for groups in (self.project.nets, self.project.buses, self.project.power)
            for members in groups.values()
            for endpoint in members
        ]
        self.assertEqual(len(kinds), 2 * len(endpoints))
        self.assertEqual(
            sum(pair == {"instance", "port"} for pair in kinds),
            len(set(endpoints)),
        )
        self.assertEqual(edge_trace.mode, "lines")
        self.assertFalse(figure.layout.annotations)
        self.assertFalse(figure.layout.shapes)

    def test_layout_is_deterministic(self):
        self.assertEqual(render_graph(self.project).to_json(), render_graph(self.project).to_json())

    def test_legacy_connections_reuse_ports(self):
        self.project.nets.clear()
        shared = Endpoint("controller", "GPIO38")
        self.project.connections = [
            Connection(shared, Endpoint("turntable", "STEP")),
            Connection(Endpoint("camera_slide", "STEP"), shared),
        ]
        require_valid(self.project)
        traces = {trace.meta["kind"]: trace for trace in render_graph(self.project).data}
        self.assertEqual(list(traces["port"].text).count("GPIO38"), 1)
        self.assertEqual(list(traces["net"].text), ["NET_1", "NET_2"])

    def test_empty_and_unconnected_projects_render(self):
        for instances in ({}, {"idle": "TMC2209"}):
            with self.subTest(instances=instances):
                project = Project("empty", "0.1", instances)
                require_valid(project)
                figure = render_graph(project)
                self.assertIsInstance(figure, go.Figure)
                self.assertEqual(sum(len(trace.x) for trace in figure.data), len(instances))

    def test_html_export_is_standalone(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "graph.html"
            render_graph(self.project).write_html(path, include_plotlyjs=True)
            html = path.read_text(encoding="utf-8")
        scripts = ScriptSources()
        scripts.feed(html)
        self.assertEqual(scripts.sources, [])
        self.assertIn("<html>", html)
        self.assertIn("Plotly.newPlot", html)
        for name in ("controller", "turntable", "camera_slide", "UART", "24V", "GND"):
            self.assertIn(name, html)

    def test_named_nets_appear_in_existing_exports(self):
        self.assertIn("A_STEP", to_dot(self.project))
        self.assertIn("A_STEP", to_stripboard_svg(self.project))
        nets = {net["name"]: net["members"] for net in to_netlist(self.project)["nets"]}
        self.assertEqual(nets["A_STEP"], ["controller.GPIO38", "turntable.STEP"])

    def test_cli_default_and_custom_html_outputs(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.chdir(directory):
            self.assertEqual(main(["render", "graph", str(EXAMPLE)]), 0)
            self.assertTrue(Path("artifacts/project_graph.html").is_file())
            self.assertEqual(main([
                "render", "graph", str(EXAMPLE), "--output", "nested/custom.html",
            ]), 0)
            self.assertTrue(Path("nested/custom.html").is_file())

    def test_cli_real_kaleido_png_and_svg_export(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.chdir(directory):
            self.assertEqual(main([
                "render", "graph", str(EXAMPLE), "--png", "images/graph.png",
                "--svg", "images/graph.svg",
            ]), 0)
            self.assertEqual(Path("images/graph.png").read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            svg = ElementTree.parse("images/graph.svg").getroot()
            self.assertEqual(svg.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertIn("UART", "".join(svg.itertext()))
            self.assertTrue(Path("artifacts/project_graph.html").is_file())

    def test_cli_does_not_render_invalid_project(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.chdir(directory):
            Path("bad.yaml").write_text(
                "instances:\n  bad:\n    component: unknown\n", encoding="utf-8"
            )
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                self.assertEqual(main(["render", "graph", "bad.yaml"]), 1)
            self.assertIn("unknown component", stderr.getvalue())
            self.assertFalse(Path("artifacts").exists())

    def test_cli_reports_image_export_errors(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.chdir(directory):
            with patch.object(go.Figure, "write_image", side_effect=RuntimeError("Chrome required")):
                with contextlib.redirect_stderr(io.StringIO()) as stderr:
                    result = main(["render", "graph", str(EXAMPLE), "--png", "graph.png"])
            self.assertEqual(result, 1)
            self.assertIn("Chrome required", stderr.getvalue())

    def test_cli_retains_dot_and_stripboard(self):
        for output_format, expected in (("dot", "graph circuit"), ("stripboard", "<svg")):
            with self.subTest(output_format=output_format):
                with contextlib.redirect_stdout(io.StringIO()) as stdout:
                    self.assertEqual(main(["render", output_format, str(EXAMPLE)]), 0)
                self.assertIn(expected, stdout.getvalue())

    def test_named_net_validation(self):
        cases = [
            ({"bad": [Endpoint("missing", "STEP"), Endpoint("turntable", "STEP")]}, "unknown instance"),
            ({"bad": [Endpoint("controller", "NO_PIN"), Endpoint("turntable", "STEP")]}, "unknown port"),
            ({"bad": [Endpoint("turntable", "STEP")]}, "at least two"),
            ({"bad": [Endpoint("turntable", "STEP")] * 2}, "duplicate endpoint"),
            ({"bad": [Endpoint("controller", "3V3"), Endpoint("turntable", "STEP")]}, "incompatible port types"),
            ({"UART": self.project.buses["UART"]}, "duplicate net name: UART"),
            ({"GND": self.project.power["GND"]}, "duplicate net name: GND"),
        ]
        for nets, expected in cases:
            with self.subTest(expected=expected, nets=nets):
                self.project.nets = nets
                self.assertTrue(any(expected in error for error in validate(self.project)))

    def test_named_net_reassignment_is_reported(self):
        self.project.nets["second"] = self.project.nets["A_STEP"]
        self.assertTrue(any(
            "assigned to multiple nets" in error for error in validate(self.project)
        ))

    def test_malformed_nets_are_rejected(self):
        for nets in ([], {"bad": "controller.GPIO38"}, {"": []}, {"bad": ["bad-endpoint"]}):
            with self.subTest(nets=nets), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bad.yaml"
                path.write_text(yaml.safe_dump({"instances": {}, "nets": nets}), encoding="utf-8")
                with self.assertRaises(SpecError):
                    load_project(path)


if __name__ == "__main__":
    unittest.main()
