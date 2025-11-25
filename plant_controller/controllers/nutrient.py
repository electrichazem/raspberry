from __future__ import annotations

import time
from typing import Optional

from plant_controller.hardware.relay_manager import RelayManager
from plant_controller.hardware.syringe_driver import SyringeDriver
from plant_controller.utils.datatypes import SystemState

from .base import BaseController


class NutrientController(BaseController):
    def __init__(self, relays: RelayManager, syringe: SyringeDriver, config: dict) -> None:
        super().__init__("nutrient", config)
        self.relays = relays
        self.syringe = syringe
        self.ec_min = config.get("ec_min", 1.6)
        self.ec_max = config.get("ec_max", 2.0)
        self.dose_ml = config.get("dose_ml", 1.0)
        self._cooldown_until = 0.0

    def _select_channel(self, name: str) -> None:
        for relay in ("nutrient_a", "nutrient_b", "main_water", "mix_tank"):
            self.relays.set_state(relay, relay == name)

    def _dose(self, channel: str, ml: float) -> None:
        self._select_channel(channel)
        self.syringe.dispense_ml(ml, direction_up=False)
        self._select_channel("")

    def update(self, state: SystemState) -> None:
        if not self.enabled:
            for relay in ("nutrient_a", "nutrient_b", "main_water", "mix_tank"):
                self.relays.set_state(relay, False)
            return
        now = time.time()
        if now < self._cooldown_until:
            return
        ec = state.reservoir.ec or state.reservoir.tds
        if ec is None:
            return
        if ec < self.ec_min:
            self._dose("nutrient_a", self.dose_ml)
            self._dose("nutrient_b", self.dose_ml)
            self._cooldown_until = now + self.config.get("cooldown_seconds", 300)
        elif ec > self.ec_max:
            self._select_channel("main_water")
            self.syringe.dispense_ml(self.dose_ml, direction_up=False)
            self._select_channel("")
            self._cooldown_until = now + self.config.get("cooldown_seconds", 300)

