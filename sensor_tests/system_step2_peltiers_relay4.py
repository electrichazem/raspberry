#!/usr/bin/env python3
"""
System step 2 test: run peltiers (PWM channels 0 & 1) + turn on relay 4 (P4).

Assumes relay 7 (P7) is already ON from step 1.

Behavior:
  - Keeps relay 7 ON (from step 1).
  - Runs peltiers on PCA9685 channels 0 and 1 (forward, no reverse).
  - Turns on relay 4 (P4).
  - Waits 5 seconds (gap), then exits leaving everything ON.

Requirements (inside your venv):
    pip install adafruit-circuitpython-pcf8574 adafruit-circuitpython-pca9685

Usage:
    python3 sensor_tests/system_step2_peltiers_relay4.py
"""

import time

import board
import busio
from adafruit_pcf8574 import PCF8574
from adafruit_pca9685 import PCA9685

# PCF8574 relay expander
RELAY_I2C_ADDRESS = 0x27
RELAY_7_INDEX = 7  # keep this ON from step 1
RELAY_4_INDEX = 4  # turn this ON in step 2

# PCA9685 PWM expander for peltiers
PWM_I2C_ADDRESS = 0x40
PELTIER_CHANNELS = (0, 1)  # first two channels
PWM_DUTY = 0x7FFF  # 50% duty cycle (forward, no reverse)

GAP_SECONDS = 5.0


def main() -> None:
    i2c = busio.I2C(board.SCL, board.SDA)
    
    # Initialize relay expander
    pcf = PCF8574(i2c, address=RELAY_I2C_ADDRESS)
    relay_pins = [pcf.get_pin(n) for n in range(8)]
    for pin in relay_pins:
        pin.switch_to_output(value=False)  # all OFF initially
    
    # Initialize PWM expander for peltiers
    pca = PCA9685(i2c, address=PWM_I2C_ADDRESS)
    pca.frequency = 50  # 50 Hz for PWM
    
    print("Step 2: Peltiers (channels 0 & 1) + Relay 4 (P4)\n")
    
    # Keep relay 7 ON (from step 1)
    print(f"Keeping relay P{RELAY_7_INDEX} ON (from step 1)")
    relay_pins[RELAY_7_INDEX].value = True
    
    # Turn on relay 4
    print(f"Turning ON relay P{RELAY_4_INDEX}")
    relay_pins[RELAY_4_INDEX].value = True
    
    # Run peltiers on channels 0 and 1 (forward, no reverse)
    print(f"Running peltiers on PWM channels {PELTIER_CHANNELS[0]} and {PELTIER_CHANNELS[1]} (forward)")
    for ch in PELTIER_CHANNELS:
        pca.channels[ch].duty_cycle = PWM_DUTY
        print(f"  Channel {ch}: PWM duty 0x{PWM_DUTY:04X} (50%)")
    
    print(f"\nAll outputs are ON. Waiting {GAP_SECONDS:.0f}s gap...")
    time.sleep(GAP_SECONDS)
    
    print("Gap elapsed. Everything is still ON:")
    print(f"  - Relay P{RELAY_7_INDEX}: ON")
    print(f"  - Relay P{RELAY_4_INDEX}: ON")
    print(f"  - Peltier channels {PELTIER_CHANNELS[0]} & {PELTIER_CHANNELS[1]}: running")
    print("You can now run the next step script.")


if __name__ == "__main__":
    main()

