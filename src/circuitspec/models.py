"""Data structures for a CircuitSpec project."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Endpoint:
    instance: str
    port: str

    def __str__(self) -> str:
        return f"{self.instance}.{self.port}"


@dataclass(frozen=True)
class Connection:
    source: Endpoint
    target: Endpoint


@dataclass
class Project:
    name: str
    version: str
    instances: dict[str, str]
    connections: list[Connection] = field(default_factory=list)
    buses: dict[str, list[Endpoint]] = field(default_factory=dict)
    power: dict[str, list[Endpoint]] = field(default_factory=dict)
