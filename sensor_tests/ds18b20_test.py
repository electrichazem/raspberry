#!/usr/bin/env python3
"""
DS18B20 reader using the raw /sys/bus/w1/devices interface (old code style).

Ensure 1-Wire is enabled (raspi-config) and the kernel modules are loaded:
    sudo modprobe w1-gpio
    sudo modprobe w1-therm
"""

import glob
import time
from pathlib import Path

BASE_DIR = Path("/sys/bus/w1/devices/")


def find_sensor_device() -> Path:
    """Return the first DS18B20 device folder."""
    matches = list(BASE_DIR.glob("28*"))
    if not matches:
        raise FileNotFoundError("No DS18B20 device found under /sys/bus/w1/devices/")
    return matches[0] / "w1_slave"


def read_temperature_c(device_file: Path) -> float | None:
    """Read temperature in °C from the w1_slave file."""
    with device_file.open("r") as f:
        lines = f.readlines()
    if not lines or not lines[0].strip().endswith("YES"):
        return None
    equals_pos = lines[1].find("t=")
    if equals_pos == -1:
        return None
    temp_c = float(lines[1][equals_pos + 2 :]) / 1000.0
    return temp_c


def main() -> None:
    try:
        device_file = find_sensor_device()
    except FileNotFoundError as exc:
        print(exc)
        print("Check wiring and dtoverlay=w1-gpio in /boot/config.txt")
        return

    print(f"Reading DS18B20 at {device_file.parent.name}")
    print("Press Ctrl+C to stop\n")
    try:
        while True:
            temp_c = read_temperature_c(device_file)
            if temp_c is not None:
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                print(f"{temp_c:6.2f} °C  |  {temp_f:6.2f} °F")
            else:
                print("Reading failed (CRC error)")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

