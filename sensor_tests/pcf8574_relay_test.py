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
HOLD_SECONDS = 5.0        # how long to hold each relay closed


def main() -> None:
    i2c = busio.I2C(board.SCL, board.SDA)
    pcf = PCF8574(i2c, address=I2C_ADDRESS)

    pins = [pcf.get_pin(n) for n in range(8)]
    for pin in pins:
        pin.switch_to_output(value=True)  # default off for active-low relays

    print("Starting relay walk test (Ctrl+C to stop)\n")

    try:
        while True:
            for idx, pin in enumerate(pins):
                print(f"Energising relay P{idx}")
                pin.value = False  # active-low
                time.sleep(HOLD_SECONDS)
                print(f"Releasing relay P{idx}")
                pin.value = True
                time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping – returning all relays to off state.")
    finally:
        for pin in pins:
            pin.value = True


if __name__ == "__main__":
    main()

