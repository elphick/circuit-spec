"""Built-in component definitions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Port:
    name: str
    direction: str
    kind: str


@dataclass(frozen=True)
class Component:
    name: str
    ports: frozenset[str]


_gpio_ports = {f"GPIO{number}" for number in range(49)}
COMPONENTS = {
    "ESP32_S3_ETH_POE": Component(
        name="ESP32_S3_ETH_POE",
        ports=frozenset(_gpio_ports | {"3V3", "5V", "GND"}),
    ),
    "TMC2209": Component(
        name="TMC2209",
        ports=frozenset({"STEP", "DIR", "EN", "UART", "VM", "VDD", "GND"}),
    ),
}
