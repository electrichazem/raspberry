from __future__ import annotations

import glob
from pathlib import Path
from typing import Optional


class DS18B20Service:
    def __init__(self, device_id: str | None = None) -> None:
        base_dir = Path("/sys/bus/w1/devices")
        if device_id:
            self.device_file = base_dir / device_id / "w1_slave"
        else:
            matches = glob.glob(str(base_dir / "28*"))
            self.device_file = Path(matches[0]) / "w1_slave" if matches else None

    def read(self) -> Optional[float]:
        if not self.device_file or not self.device_file.exists():
            return None
        with self.device_file.open("r", encoding="utf-8") as handle:
            lines = handle.readlines()
        if not lines or not lines[0].strip().endswith("YES"):
            return None
        equals = lines[1].find("t=")
        if equals != -1:
            temp_c = float(lines[1][equals + 2 :]) / 1000.0
            return temp_c
        return None

