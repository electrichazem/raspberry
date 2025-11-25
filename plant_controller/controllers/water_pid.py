from __future__ import annotations

from plant_controller.hardware.pwm_channel import PWMChannel
from plant_controller.hardware.relay_manager import RelayManager
from plant_controller.utils.datatypes import SystemState
from plant_controller.utils.pid import PID

from .base import BaseController


class WaterPIDController(BaseController):
    def __init__(self, pwm: PWMChannel, relays: RelayManager, config: dict) -> None:
        super().__init__("water_pid", config)
        self.pwm = pwm
        self.relays = relays
        self.pid = PID(
            config.get("kp", 8.0),
            config.get("ki", 0.4),
            config.get("kd", 1.2),
        )
        self.target = config.get("target_c", 19.0)

    def update(self, state: SystemState) -> None:
        if not self.enabled:
            self.pwm.set_output(0.0)
            self.relays.set_state("water_pump", False)
            return
        water_temp = state.reservoir.water_temp_c
        if water_temp is None:
            return
        output = self.pid.compute(self.target, water_temp)
        forward = water_temp > self.target
        self.pwm.set_output(abs(output), forward=forward)
        self.relays.set_state("water_pump", output > 5.0)

