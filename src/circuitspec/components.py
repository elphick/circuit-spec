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
    ports: dict[str, Port]
    symbol: str
    symbol_pins: dict[str, str]


def _ports(names: set[str], direction: str, kind: str) -> dict[str, Port]:
    return {name: Port(name, direction, kind) for name in sorted(names)}


_gpio_ports = {f"GPIO{number}" for number in range(49)}
COMPONENTS = {
    "ESP32_S3_ETH_POE": Component(
        name="ESP32_S3_ETH_POE",
        ports={
            **_ports(_gpio_ports, "bidirectional", "signal"),
            **_ports({"3V3", "5V"}, "output", "power"),
            **_ports({"GND"}, "bidirectional", "power"),
        },
        symbol="RF_Module:ESP32",
        symbol_pins={
            **{f"GPIO{number}": str(number + 1) for number in range(49)},
            "3V3": "50",
            "5V": "51",
            "GND": "52",
        },
    ),
    "TMC2209": Component(
        name="TMC2209",
        ports={
            **_ports({"STEP", "DIR", "EN"}, "input", "signal"),
            **_ports({"UART"}, "bidirectional", "bus"),
            **_ports({"VM", "VDD", "GND"}, "input", "power"),
        },
        symbol="Driver_Motor:TMC2209",
        symbol_pins={
            "STEP": "1",
            "DIR": "2",
            "EN": "3",
            "UART": "4",
            "VM": "5",
            "VDD": "6",
            "GND": "7",
        },
    ),
}
