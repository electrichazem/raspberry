from __future__ import annotations

import time

from plant_controller.hardware.relay_manager import RelayManager
from plant_controller.utils.datatypes import SystemState

from .base import BaseController


class HumidityController(BaseController):
    def __init__(self, relays: RelayManager, config: dict) -> None:
        super().__init__("humidity", config)
        self.relays = relays
        self.rh_min = config.get("rh_min", 50)
        self.rh_max = config.get("rh_max", 60)
        self.heater_cycle = config.get("heater_cycle_seconds", 60)
        self.heater_rest = config.get("heater_rest_seconds", 30)
        self._next_allowed_start = 0.0
        self._heater_on_since = 0.0

    def update(self, state: SystemState) -> None:
        if not self.enabled:
            self.relays.set_state("heater", False)
            self.relays.set_state("humidity_fan", False)
            return
        humidity = state.environment.humidity
        if humidity is None:
            return
        now = time.time()
        heater_active = self.relays.get_state("heater")
        if humidity < self.rh_min and now >= self._next_allowed_start:
            if not heater_active:
                self.relays.set_state("heater", True)
                self.relays.set_state("humidity_fan", True)
                self._heater_on_since = now
        if heater_active and (humidity >= self.rh_max or now - self._heater_on_since > self.heater_cycle):
            self.relays.set_state("heater", False)
            self.relays.set_state("humidity_fan", False)
            self._next_allowed_start = now + self.heater_rest
        if humidity >= self.rh_max:
            self.relays.set_state("heater", False)
            self.relays.set_state("humidity_fan", False)

