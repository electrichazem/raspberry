#!/usr/bin/env python3
"""
Quick DS18B20 temperature reader.

Usage:
    source venv/bin/activate  # optional virtual env
    pip install w1thermsensor
    python3 sensor_tests/ds18b20_test.py

Ensure 1-Wire is enabled (raspi-config) and kernel modules are loaded:
    sudo modprobe w1-gpio
    sudo modprobe w1-therm
"""

import time

try:
    from w1thermsensor import W1ThermSensor
except ImportError:
    print("Missing w1thermsensor. Install with:")
    print("  pip install w1thermsensor")
    raise


def main() -> None:
    sensor = W1ThermSensor()  # auto-detect first DS18B20
    print(f"Found sensor: {sensor.id}")
    print("Press Ctrl+C to stop\n")
    try:
        while True:
            temp_c = sensor.get_temperature()  # Celsius
            temp_f = sensor.get_temperature(W1ThermSensor.DEGREES_F)
            print(f"{temp_c:6.2f} °C  |  {temp_f:6.2f} °F")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

