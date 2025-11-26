#!/usr/bin/env python3
"""
PCF8574/PCF8574A relay expander test.

It toggles each relay output (P0-P7) for 5 seconds with console messages so
you can see what’s energised.

Usage:
    source venv/bin/activate                     # optional virtual env
    pip install adafruit-circuitpython-pcf8574   # install dependency
    python3 sensor_tests/pcf8574_relay_test.py

Update I2C_ADDRESS if your expander isn’t at 0x20.
"""

import time

import board
import busio

from adafruit_pcf8574 import PCF8574

I2C_ADDRESS = 0x27        # change if your expander uses another address


def main() -> None:
    i2c = busio.I2C(board.SCL, board.SDA)
    pcf = PCF8574(i2c, address=I2C_ADDRESS)

    pins = [pcf.get_pin(n) for n in range(8)]
    for pin in pins:
        pin.switch_to_output(value=True)  # default off for active-low relays

    print("Manual relay test:")
    print("  - P0 on for 10 seconds, then off for 3 seconds")
    print("  - P7 on for 10 seconds, then off")
    print()

    def pulse(pin_idx: int, on_seconds: float, off_seconds: float) -> None:
        print(f"Energising relay P{pin_idx} for {on_seconds:.0f} seconds")
        pins[pin_idx].value = False
        time.sleep(on_seconds)
        print(f"Releasing relay P{pin_idx} for {off_seconds:.0f} seconds")
        pins[pin_idx].value = True
        time.sleep(max(off_seconds, 0))

    try:
        pulse(0, 10.0, 3.0)
        pulse(7, 10.0, 0.0)
        print("\nSequence complete.")
    finally:
        for pin in pins:
            pin.value = True


if __name__ == "__main__":
    main()

