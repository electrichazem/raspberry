from __future__ import annotations

from typing import Dict, Optional


try:
    from adafruit_ads1x15.analog_in import AnalogIn  # type: ignore
    from adafruit_ads1x15.ads1115 import ADS1115  # type: ignore
    from adafruit_ads1x15.ads1x15 import ADS1x15 as ADS  # type: ignore
    import board  # type: ignore
    import busio  # type: ignore
except ImportError:  # pragma: no cover
    AnalogIn = None  # type: ignore
    ADS1115 = None  # type: ignore
    ADS = None  # type: ignore
    board = None  # type: ignore
    busio = None  # type: ignore


class ADSReader:
    def __init__(self, configs: Dict[int, Dict[str, int]]) -> None:
        self.channels: Dict[str, object] = {}
        if ADS1115 and board and busio and ADS:
            i2c = busio.I2C(board.SCL, board.SDA)
            for address, channel_map in configs.items():
                ads = ADS1115(i2c, address=address)
                for name, ch in channel_map.items():
                    ads_channel = getattr(ADS, f"P{ch}")
                    self.channels[name] = AnalogIn(ads, ads_channel)
        self._fallback: Dict[str, float] = {
            name: 0.0 for channel_map in configs.values() for name in channel_map.keys()
        }

    def read_voltage(self, name: str) -> Optional[float]:
        channel = self.channels.get(name)
        if channel:
            return float(channel.voltage)
        return self._fallback.get(name)

