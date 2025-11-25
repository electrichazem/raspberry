from __future__ import annotations

from typing import Dict

from .gpio import get_gpio


class ServoDriver:
    def __init__(self, servo_pins: Dict[str, int], frequency: int = 50) -> None:
        self.gpio = get_gpio()
        self.frequency = frequency
        self._pwm_channels: Dict[str, object] = {}
        for name, pin in servo_pins.items():
            self.gpio.setup(pin, self.gpio.OUT)
            pwm = self.gpio.PWM(pin, self.frequency)
            pwm.start(0.0)
            self._pwm_channels[name] = pwm

    @staticmethod
    def _angle_to_duty(angle: float) -> float:
        angle = max(0.0, min(180.0, angle))
        duty = 2.5 + (angle / 180.0) * 10.0
        return duty

    def set_angle(self, name: str, angle: float) -> None:
        if name not in self._pwm_channels:
            raise KeyError(f"Unknown servo {name}")
        duty_cycle = self._angle_to_duty(angle)
        self._pwm_channels[name].ChangeDutyCycle(duty_cycle)

    def stop_all(self) -> None:
        for pwm in self._pwm_channels.values():
            pwm.stop()

