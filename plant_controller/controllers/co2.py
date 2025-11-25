from __future__ import annotations

from plant_controller.hardware.relay_manager import RelayManager
from plant_controller.hardware.servo_driver import ServoDriver
from plant_controller.utils.datatypes import SystemState

from .base import BaseController


class CO2Controller(BaseController):
    def __init__(
        self,
        relays: RelayManager,
        servos: ServoDriver,
        config: dict,
        servo_positions: tuple[float, float] = (0.0, 0.0),
        vent_position: float = 90.0,
    ) -> None:
        super().__init__("co2", config)
        self.relays = relays
        self.servos = servos
        self.ppm_min = config.get("ppm_min", 900)
        self.ppm_max = config.get("ppm_max", 1200)
        self.closed_positions = servo_positions
        self.vent_position = vent_position
        self._venting = False

    def _set_vent(self, open_: bool) -> None:
        if open_:
            left = right = self.vent_position
        else:
            left, right = self.closed_positions
        self.servos.set_angle("vent_left", left)
        self.servos.set_angle("vent_right", right)
        self.relays.set_state("vent_fans", open_)
        self._venting = open_

    def update(self, state: SystemState) -> None:
        if not self.enabled:
            self._set_vent(False)
            self.relays.set_state("co2_exhaust", False)
            return
        co2_ppm = state.environment.co2_ppm
        humidity = state.environment.humidity
        if co2_ppm is None and humidity is None:
            return
        if co2_ppm is not None and co2_ppm > self.ppm_max:
            self.relays.set_state("co2_exhaust", True)
            self._set_vent(True)
        elif co2_ppm is not None and co2_ppm < self.ppm_min:
            self.relays.set_state("co2_exhaust", False)
            self._set_vent(True)
        elif humidity is not None and humidity > self.config.get("humidity_high", 80):
            self.relays.set_state("co2_exhaust", False)
            self._set_vent(True)
        else:
            self.relays.set_state("co2_exhaust", False)
            if self._venting:
                self._set_vent(False)

