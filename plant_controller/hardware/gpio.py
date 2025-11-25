from __future__ import annotations

from typing import Any


def get_gpio() -> Any:
    try:
        import RPi.GPIO as GPIO  # type: ignore

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        return GPIO
    except ImportError:

        class _MockGPIO:
            BOARD = "BOARD"
            BCM = "BCM"
            OUT = "OUT"
            IN = "IN"
            PUD_UP = "PUD_UP"

            def __init__(self) -> None:
                self._pins: dict[int, bool] = {}

            def setmode(self, *_args, **_kwargs) -> None:
                return

            def setwarnings(self, *_args, **_kwargs) -> None:
                return

            def setup(self, pin: int, *_args, **_kwargs) -> None:
                self._pins.setdefault(pin, False)

            def output(self, pin: int, value: bool) -> None:
                self._pins[pin] = bool(value)

            def input(self, pin: int) -> bool:
                return self._pins.get(pin, False)

            def cleanup(self) -> None:
                self._pins.clear()

            class PWM:
                def __init__(self, pin: int, frequency: int) -> None:
                    self.pin = pin
                    self.frequency = frequency
                    self._duty_cycle = 0.0

                def start(self, duty_cycle: float) -> None:
                    self._duty_cycle = duty_cycle

                def ChangeDutyCycle(self, duty_cycle: float) -> None:
                    self._duty_cycle = duty_cycle

                def stop(self) -> None:
                    self._duty_cycle = 0.0

        gpio = _MockGPIO()
        gpio.setmode(gpio.BCM)
        gpio.setwarnings(False)
        return gpio

