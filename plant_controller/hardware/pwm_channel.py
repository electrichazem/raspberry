from __future__ import annotations

from typing import Optional

from .gpio import get_gpio


class PWMChannel:
    def __init__(self, pwm_pin: int, dir_pin: Optional[int] = None, frequency: int = 1000):
        self.gpio = get_gpio()
        self.pwm_pin = pwm_pin
        self.dir_pin = dir_pin
        self.frequency = frequency
        self.gpio.setup(self.pwm_pin, self.gpio.OUT)
        if self.dir_pin is not None:
            self.gpio.setup(self.dir_pin, self.gpio.OUT)
        self._pwm = self.gpio.PWM(self.pwm_pin, self.frequency)
        self._pwm.start(0.0)

    def set_output(self, duty_cycle: float, forward: bool = True) -> None:
        duty_cycle = max(0.0, min(100.0, duty_cycle))
        if self.dir_pin is not None:
            self.gpio.output(self.dir_pin, bool(forward))
        self._pwm.ChangeDutyCycle(duty_cycle)

    def stop(self) -> None:
        self._pwm.stop()
        if self.dir_pin is not None:
            self.gpio.output(self.dir_pin, False)

