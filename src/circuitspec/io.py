"""YAML loading for CircuitSpec projects."""

import re
from pathlib import Path
from typing import Any

import yaml

from circuitspec.models import Endpoint, Net, Project


class SpecError(ValueError):
    """Raised when a specification is malformed."""


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise SpecError(f"duplicate key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
_ENDPOINT = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\.([A-Za-z0-9_][A-Za-z0-9_-]*)$")
def _mapping(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise SpecError(f"{label} must be a mapping")
    return value


def _endpoint(value: Any) -> Endpoint:
    if not isinstance(value, str):
        raise SpecError("endpoints must be strings in instance.port format")
    match = _ENDPOINT.fullmatch(value.strip())
    if not match:
        raise SpecError(f"invalid endpoint: {value!r}; expected instance.port")
    return Endpoint(*match.groups())


def _members(value: Any, label: str) -> list[Endpoint]:
    if not isinstance(value, list):
        raise SpecError(f"{label} members must be a list")
    return [_endpoint(member) for member in value]


def load_project(path: str | Path) -> Project:
    """Load a project YAML file and convert it to typed model objects."""
    try:
        raw = yaml.load(Path(path).read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise SpecError(f"invalid YAML: {exc}") from exc
    raw = _mapping(raw, "project document")

    metadata = _mapping(raw.get("project", {}), "project")
    instances_raw = _mapping(raw.get("instances"), "instances")
    instances = {}
    for name, definition in instances_raw.items():
        if not isinstance(name, str) or not _IDENTIFIER.fullmatch(name):
            raise SpecError(f"invalid instance name: {name!r}")
        definition = _mapping(definition, f"instance {name}")
        component = definition.get("component")
        if not isinstance(component, str) or not component:
            raise SpecError(f"instance {name} must specify a component")
        instances[name] = component

    nets_raw = _mapping(raw.get("nets", {}), "nets")
    nets = []
    for name, members in nets_raw.items():
        if not isinstance(name, str) or not name:
            raise SpecError("net names must be non-empty strings")
        nets.append(Net(name, _members(members, f"net {name}")))

    return Project(
        name=str(metadata.get("name", Path(path).stem)),
        version=str(metadata.get("version", "0.1.0")),
        instances=instances,
        nets=nets,
    )
