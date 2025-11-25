from __future__ import annotations

import time
from typing import Optional, Tuple


try:
    import board  # type: ignore
    import adafruit_dht  # type: ignore
except ImportError:  # pragma: no cover
    board = None  # type: ignore
    adafruit_dht = None  # type: ignore


class DHT22Service:
    def __init__(self, gpio_pin: int) -> None:
        if board and adafruit_dht:
            pin = getattr(board, f"D{gpio_pin}")
            self._sensor = adafruit_dht.DHT22(pin)
        else:
            self._sensor = None
        self._last_read: Tuple[Optional[float], Optional[float]] = (None, None)
        self._last_ts = 0.0

    def read(self) -> Tuple[Optional[float], Optional[float]]:
        now = time.time()
        if now - self._last_ts < 2.0:
            return self._last_read
        if not self._sensor:
            return self._last_read
        try:
            temp_c = self._sensor.temperature
            humidity = self._sensor.humidity
            if temp_c is not None and humidity is not None:
                self._last_read = (float(temp_c), float(humidity))
        except RuntimeError:
            pass
        finally:
            self._last_ts = now
        return self._last_read

