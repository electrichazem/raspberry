from __future__ import annotations

from plant_controller.hardware.pwm_channel import PWMChannel
from plant_controller.utils.datatypes import SystemState
from plant_controller.utils.pid import PID

from .base import BaseController


class AirPIDController(BaseController):
    def __init__(self, pwm: PWMChannel, config: dict) -> None:
        super().__init__("air_pid", config)
        self.pwm = pwm
        self.pid = PID(
            config.get("kp", 10.0),
            config.get("ki", 0.5),
            config.get("kd", 1.0),
        )
        self.target = config.get("target_c", 24.0)

    def update(self, state: SystemState) -> None:
        if not self.enabled:
            self.pwm.set_output(0.0)
            return
        temp = state.environment.air_temp_c
        if temp is None:
            return
        output = self.pid.compute(self.target, temp)
        forward = temp > self.target
        self.pwm.set_output(abs(output), forward=forward)

