from __future__ import annotations

import time

from plant_controller.hardware.relay_manager import RelayManager
from plant_controller.hardware.syringe_driver import SyringeDriver
from plant_controller.utils.datatypes import SystemState

from .base import BaseController


class SoilController(BaseController):
    def __init__(self, relays: RelayManager, syringe: SyringeDriver, config: dict) -> None:
        super().__init__("soil", config)
        self.relays = relays
        self.syringe = syringe
        self.moisture_min = config.get("moisture_min", 0.35)
        self.pulse_ml = config.get("pulse_ml", 0.5)
        self._next_check = 0.0

    def update(self, state: SystemState) -> None:
        if not self.enabled:
            self.relays.set_state("plant_output", False)
            return
        now = time.time()
        if now < self._next_check:
            return
        soil_moisture = state.soil.moisture
        if soil_moisture is None or soil_moisture >= self.moisture_min:
            self.relays.set_state("plant_output", False)
            self._next_check = now + 10
            return
        self.relays.set_state("plant_output", True)
        self.syringe.dispense_ml(self.pulse_ml, direction_up=False)
        self.relays.set_state("plant_output", False)
        self._next_check = now + self.config.get("settle_time_seconds", 60)

