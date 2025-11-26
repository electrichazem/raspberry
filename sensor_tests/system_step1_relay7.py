#!/usr/bin/env python3
"""
System step 1 test: drive ONLY relay 7 (P7) on the PCF8574 expander.

Behavior:
  - All outputs are forced to OFF (high) at start.
  - Relay P7 is then energised (active-low) and LEFT ON.
  - The script waits 5 seconds (gap before the next manual step) and exits,
    leaving relay P7 energised so you can chain the next action.

Requirements (inside your venv):
    pip install adafruit-circuitpython-pcf8574

Usage:
    python3 sensor_tests/system_step1_relay7.py
"""
 
import time

import board
import busio
from adafruit_pcf8574 import PCF8574

I2C_ADDRESS = 0x27  # PCF8574 address from your i2cdetect output
RELAY_INDEX = 7     # last pin on the module (P7)
GAP_SECONDS = 5.0


def main() -> None:
    i2c = busio.I2C(board.SCL, board.SDA)
    pcf = PCF8574(i2c, address=I2C_ADDRESS)

    pins = [pcf.get_pin(n) for n in range(8)]
    # Ensure all relays are OFF (assuming active-low board: HIGH = off)
    for pin in pins:
        pin.switch_to_output(value=False)

    print("Step 1: ONLY relay P7 should energise and stay ON.\n")
    print(f"Energising relay P{RELAY_INDEX} (will remain ON after {GAP_SECONDS:.0f}s gap)")
    pins[RELAY_INDEX].value = True  # active-low: LOW = ON
    time.sleep(GAP_SECONDS)
    print("Gap elapsed. Relay P7 is still ON. You can now run the next step script.")


if __name__ == "__main__":
    main()


