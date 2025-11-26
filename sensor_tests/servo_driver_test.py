#!/usr/bin/env python3
"""
PCA9685-based driver test for:
  - Two servo outputs (channels 0 & 1)
  - Two PWM outputs driving Peltier H-bridges (channels 8 & 9)

Requirements:
    pip install adafruit-circuitpython-pca9685

Usage:
    python3 sensor_tests/servo_driver_test.py

Adjust SERVO_CHANNELS / PWM_CHANNELS / I2C address to match your board.
"""

import time

import board
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

I2C_ADDRESS = 0x40
SERVO_CHANNELS = (0, 1)   # vent_left, vent_right, for example
PWM_CHANNELS = (8, 9)     # air_peltier, water_peltier
PWM_TEST_DUTY = (0x0000, 0x3FFF, 0x7FFF, 0xFFFF)


def main() -> None:
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c, address=I2C_ADDRESS)
    pca.frequency = 50  # good for servos & general PWM

    print("Initializing servos...")
    servos = [servo.Servo(pca.channels[ch], min_pulse=500, max_pulse=2500) for ch in SERVO_CHANNELS]

    print("Sweeping servos (0° → 90° → 180°)")
    try:
        for angle in (0, 90, 180, 90):
            for idx, s in enumerate(servos):
                print(f"Servo channel {SERVO_CHANNELS[idx]} → {angle}°")
                s.angle = angle
            time.sleep(1)

        print("\nTesting PWM outputs for Peltiers:")
        for duty in PWM_TEST_DUTY:
            for ch in PWM_CHANNELS:
                print(f"Channel {ch} PWM duty 0x{duty:04X}")
                pca.channels[ch].duty_cycle = duty
            time.sleep(1)
    finally:
        print("\nResetting outputs.")
        for s in servos:
            s.angle = 90
        for ch in PWM_CHANNELS:
            pca.channels[ch].duty_cycle = 0
        pca.deinit()


if __name__ == "__main__":
    main()

