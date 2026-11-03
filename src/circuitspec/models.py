"""Data structures for a CircuitSpec project."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Endpoint:
    instance: str
    port: str

    def __str__(self) -> str:
        return f"{self.instance}.{self.port}"


@dataclass
class Net:
    name: str
    endpoints: list[Endpoint]


@dataclass
class Project:
    name: str
    version: str
    instances: dict[str, str]
    nets: list[Net] = field(default_factory=list)
