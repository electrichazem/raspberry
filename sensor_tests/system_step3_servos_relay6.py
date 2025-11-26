#!/usr/bin/env python3
"""
System step 3 test: move servos (0° → 90°) + turn on relay 6 (P6).

Assumes:
  - Relay 7 (P7) is ON from step 1
  - Relay 4 (P4) is ON from step 2
  - Peltiers on PCA9685 channels 0 & 1 are running from step 2

Behavior:
  - Keeps all previous outputs ON (relay 7, relay 4, peltiers).
  - Moves servos from 0° to 90° on PCA9685 servo channels.
  - Turns on relay 6 (P6).
  - Waits 5 seconds (gap), then exits leaving everything ON.

Requirements (inside your venv):
    pip install adafruit-circuitpython-pcf8574 adafruit-circuitpython-pca9685 adafruit-circuitpython-motor

Usage:
    python3 sensor_tests/system_step3_servos_relay6.py
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
RELAY_6_INDEX = 6  # turn ON in step 3

# PCA9685 PWM expander
PWM_I2C_ADDRESS = 0x40
PELTIER_CHANNELS = (0, 1)  # keep running from step 2
SERVO_CHANNELS = (2, 3)     # servos on channels 2 & 3 (adjust if different)
PWM_DUTY = 0x7FFF  # 50% duty for peltiers (keep from step 2)

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
    
    print("Step 3: Servos (0° → 90°) + Relay 6 (P6)\n")
    
    # Keep relay 7 ON (from step 1)
    print(f"Keeping relay P{RELAY_7_INDEX} ON (from step 1)")
    relay_pins[RELAY_7_INDEX].value = True
    
    # Keep relay 4 ON (from step 2)
    print(f"Keeping relay P{RELAY_4_INDEX} ON (from step 2)")
    relay_pins[RELAY_4_INDEX].value = True
    
    # Keep peltiers running (from step 2)
    print(f"Keeping peltiers running on channels {PELTIER_CHANNELS[0]} & {PELTIER_CHANNELS[1]}")
    for ch in PELTIER_CHANNELS:
        pca.channels[ch].duty_cycle = PWM_DUTY
    
    # Initialize servos
    servos = [
        servo.Servo(pca.channels[ch], min_pulse=500, max_pulse=2500)
        for ch in SERVO_CHANNELS
    ]
    
    # Move servos from 0° to 90°
    print(f"Moving servos on channels {SERVO_CHANNELS[0]} & {SERVO_CHANNELS[1]} from 0° to 90°")
    for idx, s in enumerate(servos):
        print(f"  Servo channel {SERVO_CHANNELS[idx]}: 0° → 90°")
        s.angle = 0
        time.sleep(0.5)  # brief pause
        s.angle = 90
    
    # Turn on relay 6
    print(f"Turning ON relay P{RELAY_6_INDEX}")
    relay_pins[RELAY_6_INDEX].value = True
    
    print(f"\nAll outputs are ON. Waiting {GAP_SECONDS:.0f}s gap...")
    time.sleep(GAP_SECONDS)
    
    print("Gap elapsed. Everything is still ON:")
    print(f"  - Relay P{RELAY_7_INDEX}: ON")
    print(f"  - Relay P{RELAY_4_INDEX}: ON")
    print(f"  - Relay P{RELAY_6_INDEX}: ON")
    print(f"  - Peltier channels {PELTIER_CHANNELS[0]} & {PELTIER_CHANNELS[1]}: running")
    print(f"  - Servo channels {SERVO_CHANNELS[0]} & {SERVO_CHANNELS[1]}: at 90°")
    print("You can now run the next step script.")


if __name__ == "__main__":
    main()

