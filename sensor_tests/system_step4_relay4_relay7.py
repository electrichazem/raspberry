#!/usr/bin/env python3
"""
System step 4 test: ensure relay 4 + relay 7 are ON (keeping all previous outputs).

Assumes:
  - Relay 7 (P7) is ON from step 1
  - Relay 4 (P4) is ON from step 2
  - Relay 6 (P6) is ON from step 3
  - Peltiers on PCA9685 channels 0 & 1 are running from step 2
  - Servos on PCA9685 channels 2 & 3 are at 90° from step 3

Behavior:
  - Keeps all previous outputs ON (relay 7, relay 4, relay 6, peltiers, servos).
  - Explicitly ensures relay 4 + relay 7 are ON.
  - Waits 5 seconds (gap), then exits leaving everything ON.

Requirements (inside your venv):
    pip install adafruit-circuitpython-pcf8574 adafruit-circuitpython-pca9685 adafruit-circuitpython-motor

Usage:
    python3 sensor_tests/system_step4_relay4_relay7.py
"""

import time

import board
import busio
from adafruit_motor import servo
from adafruit_pcf8574 import PCF8574
from adafruit_pca9685 import PCA9685

# PCF8574 relay expander
RELAY_I2C_ADDRESS = 0x27
RELAY_7_INDEX = 7  # keep ON from step 1
RELAY_4_INDEX = 4  # keep ON from step 2
RELAY_6_INDEX = 5  # keep ON from step 3

# PCA9685 PWM expander
PWM_I2C_ADDRESS = 0x40
PELTIER_CHANNELS = (0, 1)  # keep running from step 2
SERVO_CHANNELS = (2, 3)     # servos on channels 2 & 3 (keep at 90° from step 3)
PWM_DUTY = 0x7FFF  # 50% duty for peltiers (keep from step 2)
SERVO_ANGLE = 90   # keep servos at 90° from step 3

GAP_SECONDS = 5.0


def main() -> None:
    i2c = busio.I2C(board.SCL, board.SDA)
    
    # Initialize relay expander
    pcf = PCF8574(i2c, address=RELAY_I2C_ADDRESS)
    relay_pins = [pcf.get_pin(n) for n in range(8)]
    for pin in relay_pins:
        pin.switch_to_output(value=False)  # all OFF initially
    
    # Initialize PWM expander
    pca = PCA9685(i2c, address=PWM_I2C_ADDRESS)
    pca.frequency = 50  # 50 Hz for servos & PWM
    
    print("Step 4: Ensure Relay 4 + Relay 7 are ON (keeping all previous outputs)\n")
    
    # Keep relay 7 ON (from step 1)
    print(f"Ensuring relay P{RELAY_7_INDEX} is ON (from step 1)")
    relay_pins[RELAY_7_INDEX].value = True
    
    # Keep relay 4 ON (from step 2)
    print(f"Ensuring relay P{RELAY_4_INDEX} is ON (from step 2)")
    relay_pins[RELAY_4_INDEX].value = True
    
    # Keep relay 6 ON (from step 3)
    print(f"Keeping relay P{RELAY_6_INDEX} ON (from step 3)")
    relay_pins[RELAY_6_INDEX].value = True
    
    # Keep peltiers running (from step 2)
    print(f"Keeping peltiers running on channels {PELTIER_CHANNELS[0]} & {PELTIER_CHANNELS[1]}")
    for ch in PELTIER_CHANNELS:
        pca.channels[ch].duty_cycle = PWM_DUTY
    
    # Keep servos at 90° (from step 3)
    servos = [
        servo.Servo(pca.channels[ch], min_pulse=500, max_pulse=2500)
        for ch in SERVO_CHANNELS
    ]
    print(f"Keeping servos on channels {SERVO_CHANNELS[0]} & {SERVO_CHANNELS[1]} at {SERVO_ANGLE}°")
    for s in servos:
        s.angle = SERVO_ANGLE
    
    print(f"\nAll outputs are ON. Waiting {GAP_SECONDS:.0f}s gap...")
    time.sleep(GAP_SECONDS)
    
    print("Gap elapsed. Everything is still ON:")
    print(f"  - Relay P{RELAY_7_INDEX}: ON")
    print(f"  - Relay P{RELAY_4_INDEX}: ON")
    print(f"  - Relay P{RELAY_6_INDEX}: ON")
    print(f"  - Peltier channels {PELTIER_CHANNELS[0]} & {PELTIER_CHANNELS[1]}: running")
    print(f"  - Servo channels {SERVO_CHANNELS[0]} & {SERVO_CHANNELS[1]}: at {SERVO_ANGLE}°")
    print("You can now run the next step script.")


if __name__ == "__main__":
    main()

