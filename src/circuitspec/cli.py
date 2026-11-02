"""Command-line interface for CircuitSpec."""

import argparse
import json
import sys
from pathlib import Path

from circuitspec.io import SpecError, load_project
from circuitspec.renderers import to_dot, to_netlist, to_stripboard_svg
from circuitspec.validation import validate


def _write(output: str | None, content: str) -> None:
    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        sys.stdout.write(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="circuitspec")
    commands = parser.add_subparsers(dest="command", required=True)
    validate_command = commands.add_parser("validate", help="validate a YAML project")
    validate_command.add_argument("project")
    graph_command = commands.add_parser("render", help="render a project")
    graph_command.add_argument("format", choices=["graph", "stripboard"])
    graph_command.add_argument("project")
    graph_command.add_argument("-o", "--output")
    export_command = commands.add_parser("export", help="export a project")
    export_command.add_argument("format", choices=["netlist"])
    export_command.add_argument("project")
    export_command.add_argument("-o", "--output")
    args = parser.parse_args(argv)

    try:
        project = load_project(args.project)
        errors = validate(project)
        if errors:
            print("\n".join(f"Error: {error}" for error in errors), file=sys.stderr)
            return 1
        if args.command == "validate":
            print(f"Valid: {project.name} ({len(project.instances)} components)")
        elif args.command == "render":
            renderers = {"graph": to_dot, "stripboard": to_stripboard_svg}
            _write(args.output, renderers[args.format](project))
        else:
            _write(args.output, json.dumps(to_netlist(project), indent=2) + "\n")
    except (OSError, SpecError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
