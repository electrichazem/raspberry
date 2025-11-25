from __future__ import annotations

import datetime as dt

from plant_controller.hardware.relay_manager import RelayManager

from .base import BaseController


class LightingController(BaseController):
    def __init__(self, relays: RelayManager, config: dict) -> None:
        super().__init__("lighting", config)
        self.relays = relays
        schedule = config.get("schedule", {})
        self.on_hour = schedule.get("on_hour", 6)
        self.off_hour = schedule.get("off_hour", 24)

    def update(self, *_args) -> None:
        if not self.enabled:
            self.relays.set_state("lights", False)
            return
        now = dt.datetime.now().hour
        lights_on = False
        if self.on_hour < self.off_hour:
            lights_on = self.on_hour <= now < self.off_hour
        else:
            lights_on = now >= self.on_hour or now < self.off_hour
        self.relays.set_state("lights", lights_on)

