from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .gpio import get_gpio


try:
    from smbus2 import SMBus  # type: ignore
except ImportError:  # pragma: no cover
    SMBus = None  # type: ignore


@dataclass
class PCF8574Config:
    address: int
    bus: int = 1


class PCF8574Driver:
    def __init__(self, config: PCF8574Config) -> None:
        self.config = config
        self._state = 0xFF
        self._bus: Optional[SMBus] = SMBus(config.bus) if SMBus else None
        if self._bus:
            self._bus.write_byte(self.config.address, self._state)

    def write_pin(self, pin: int, value: bool) -> None:
        if value:
            self._state |= 1 << pin
        else:
            self._state &= ~(1 << pin)
        if self._bus:
            self._bus.write_byte(self.config.address, self._state)


class RelayManager:
    def __init__(
        self,
        expander_pins: Dict[str, int],
        direct_pins: Dict[str, int],
        expander_address: Optional[int] = None,
    ) -> None:
        self.gpio = get_gpio()
        self.direct_map = direct_pins
        self.expander_map = expander_pins
        self.expander = (
            PCF8574Driver(PCF8574Config(expander_address)) if expander_address else None
        )
        for name, pin in self.direct_map.items():
            self.gpio.setup(pin, self.gpio.OUT)
            self.gpio.output(pin, False)
        self._states: Dict[str, bool] = {name: False for name in self.names}

    @property
    def names(self) -> Dict[str, int]:
        return {**self.expander_map, **self.direct_map}

    def set_state(self, name: str, enabled: bool) -> None:
        self._states[name] = enabled
        if name in self.expander_map and self.expander:
            self.expander.write_pin(self.expander_map[name], not enabled)
        elif name in self.direct_map:
            self.gpio.output(self.direct_map[name], enabled)

    def get_state(self, name: str) -> bool:
        return self._states.get(name, False)

    def all_states(self) -> Dict[str, bool]:
        return dict(self._states)

