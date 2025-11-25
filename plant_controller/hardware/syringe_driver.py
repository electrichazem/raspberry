from __future__ import annotations

import time
from dataclasses import dataclass

from .gpio import get_gpio


@dataclass
class SyringeConfig:
    step_pin: int
    dir_pin: int
    enable_pin: int
    limit_top: int
    limit_bottom: int
    steps_per_ml: int = 200
    step_delay: float = 0.002


class SyringeDriver:
    def __init__(self, config: SyringeConfig) -> None:
        self.cfg = config
        self.gpio = get_gpio()
        for pin in (config.step_pin, config.dir_pin, config.enable_pin):
            self.gpio.setup(pin, self.gpio.OUT)
        for pin in (config.limit_top, config.limit_bottom):
            self.gpio.setup(pin, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
        self.disable()

    def enable(self) -> None:
        self.gpio.output(self.cfg.enable_pin, False)

    def disable(self) -> None:
        self.gpio.output(self.cfg.enable_pin, True)

    def _limit_triggered(self, top: bool) -> bool:
        pin = self.cfg.limit_top if top else self.cfg.limit_bottom
        return not bool(self.gpio.input(pin))

    def move_steps(self, steps: int, direction_up: bool) -> None:
        self.enable()
        self.gpio.output(self.cfg.dir_pin, direction_up)
        for _ in range(abs(steps)):
            if direction_up and self._limit_triggered(True):
                break
            if not direction_up and self._limit_triggered(False):
                break
            self.gpio.output(self.cfg.step_pin, True)
            time.sleep(self.cfg.step_delay)
            self.gpio.output(self.cfg.step_pin, False)
            time.sleep(self.cfg.step_delay)
        self.disable()

    def dispense_ml(self, ml: float, direction_up: bool = False) -> None:
        steps = int(ml * self.cfg.steps_per_ml)
        self.move_steps(steps, direction_up)

