"""Command-line interface for CircuitSpec."""

import argparse
import sys
from pathlib import Path

import yaml

from circuitspec.io import SpecError, load_project
from circuitspec.models import Project
from circuitspec.renderers import (
    render_graph,
    to_dot,
    to_kicad_sch,
    to_netlist,
    to_stripboard_svg,
)
from circuitspec.validation import validate


def _write(output: str | None, content: str) -> None:
    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        sys.stdout.write(content)


def _render_graph(project: Project, args: argparse.Namespace) -> None:
    figure = render_graph(project)
    output = Path(args.output) if args.output else Path("artifacts/project_graph.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(output, include_plotlyjs=True, full_html=True)
    for image_path, image_format in ((args.png, "png"), (args.svg, "svg")):
        if image_path:
            path = Path(image_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            figure.write_image(path, format=image_format)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="circuitspec")
    commands = parser.add_subparsers(dest="command", required=True)
    validate_command = commands.add_parser("validate", help="validate a YAML project")
    validate_command.add_argument("project")
    graph_command = commands.add_parser("render", help="render a project")
    graph_command.add_argument("format", choices=["graph", "dot", "stripboard"])
    graph_command.add_argument("project")
    graph_command.add_argument("-o", "--output")
    graph_command.add_argument("--png", help="also export a graph PNG using Kaleido")
    graph_command.add_argument("--svg", help="also export a graph SVG using Kaleido")
    export_command = commands.add_parser("export", help="export a project")
    export_command.add_argument("format", choices=["netlist", "kicad"])
    export_command.add_argument("project")
    export_command.add_argument("-o", "--output")
    args = parser.parse_args(argv)
    if args.command == "render" and args.format != "graph" and (args.png or args.svg):
        parser.error("--png and --svg are only supported by render graph")

    try:
        project = load_project(args.project)
        errors = validate(project)
        if errors:
            print("\n".join(f"Error: {error}" for error in errors), file=sys.stderr)
            return 1
        if args.command == "validate":
            print(f"Valid: {project.name} ({len(project.instances)} components)")
        elif args.command == "render":
            if args.format == "graph":
                _render_graph(project, args)
            else:
                renderers = {"dot": to_dot, "stripboard": to_stripboard_svg}
                _write(args.output, renderers[args.format](project))
        elif args.format == "netlist":
            _write(args.output, yaml.safe_dump(to_netlist(project), sort_keys=False))
        else:
            output = Path(args.output) if args.output else Path("artifacts/project.kicad_sch")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(to_kicad_sch(project), encoding="utf-8")
    except (OSError, SpecError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
