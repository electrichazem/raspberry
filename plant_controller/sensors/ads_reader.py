from __future__ import annotations

import time
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
    def __init__(self, configs: Dict[int, Dict[str, int]], samples: int = 10, delay_between_reads: float = 0.05) -> None:
        self.channels: Dict[str, object] = {}
        self.samples = samples
        self.delay_between_reads = delay_between_reads
        self._fallback: Dict[str, float] = {}
        
        if ADS1115 and board and busio:
            i2c = busio.I2C(board.SCL, board.SDA)
            for address, channel_map in configs.items():
                ads = ADS1115(i2c, address=address)
                for name, ch in channel_map.items():
                    # Use channel number directly like old code: AnalogIn(ads, 0)
                    self.channels[name] = AnalogIn(ads, ch)
                    self._fallback[name] = 0.0
        else:
            # Fallback when libraries not available
            for channel_map in configs.values():
                for name in channel_map.keys():
                    self._fallback[name] = 0.0

    def read_voltage_averaged(self, name: str) -> Optional[float]:
        """Read and average multiple samples exactly like the old working code."""
        channel = self.channels.get(name)
        if not channel:
            return self._fallback.get(name)
        
        # Take multiple samples and average them - exactly like old code
        voltages = [channel.voltage for _ in range(self.samples)]
        avg_voltage = sum(voltages) / len(voltages)
        return float(avg_voltage)
    
    def read_voltage(self, name: str) -> Optional[float]:
        """Read a single voltage sample (backward compatibility)."""
        channel = self.channels.get(name)
        if channel:
            return float(channel.voltage)
        return self._fallback.get(name)

