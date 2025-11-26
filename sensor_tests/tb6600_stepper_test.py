#!/usr/bin/env python3
"""
TB6600 Stepper Motor Test: Rotate one revolution forward, then one revolution backward.

Hardware:
  - TB6600 stepper driver module
  - Step pin: GPIO12
  - Direction pin: GPIO25
  - Typical stepper: 200 steps/revolution (1.8° per step) or 6400 with microstepping

Requirements:
    pip install RPi.GPIO

Usage:
    python3 sensor_tests/tb6600_stepper_test.py
"""

import RPi.GPIO as GPIO
from time import sleep

# Direction pin from controller
DIR = 25
# Step pin from controller
STEP = 12
# 0/1 used to signify clockwise or counterclockwise.
CW = 1
CCW = 0

# Steps per revolution (adjust based on your motor and microstepping)
STEPS_PER_REVOLUTION = 200  # Start with 200 for full step, adjust if needed
# Common values:
# - 200 steps/rev for full step (1.8° per step)
# - 400 steps/rev for half step
# - 6400 steps/rev for 32x microstepping

# Step delay in seconds (0.005 = 5ms, adjust for speed)
STEP_DELAY = 0.005  # Dictates how fast stepper motor will run
# - 0.001s = very fast (may skip steps)
# - 0.005s = medium speed (recommended)
# - 0.01s = slow

# Setup pin layout on PI
GPIO.setmode(GPIO.BCM)  # Using BCM mode (GPIO numbers)

# Establish Pins in software
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

# Initialize pins
GPIO.output(DIR, CCW)
GPIO.output(STEP, GPIO.LOW)

print("=" * 60)
print("TB6600 STEPPER MOTOR TEST")
print("=" * 60)
print(f"Step pin (STEP) = GPIO{STEP}")
print(f"Direction pin (DIR) = GPIO{DIR}")
print(f"Steps per revolution: {STEPS_PER_REVOLUTION}")
print(f"Step delay: {STEP_DELAY * 1000:.1f}ms")
print("=" * 60)

try:
    # Rotate one revolution forward
    print("\nSTEP 1: Rotating ONE REVOLUTION FORWARD")
    print("-" * 60)
    
    """Change Direction: Changing direction requires time to switch. The
    time is dictated by the stepper motor and controller."""
    sleep(1.0)
    # Establish the direction you want to go
    GPIO.output(DIR, CW)
    
    # Run for STEPS_PER_REVOLUTION steps
    print(f"Rotating {STEPS_PER_REVOLUTION} steps forward...")
    for x in range(STEPS_PER_REVOLUTION):
        # Set one coil winding to high
        GPIO.output(STEP, GPIO.HIGH)
        # Allow it to get there.
        sleep(STEP_DELAY)  # Dictates how fast stepper motor will run
        # Set coil winding to low
        GPIO.output(STEP, GPIO.LOW)
        sleep(STEP_DELAY)  # Dictates how fast stepper motor will run
    
    print(f"✓ Completed {STEPS_PER_REVOLUTION} steps forward")
    
    # Rotate one revolution backward
    print("\nSTEP 2: Rotating ONE REVOLUTION BACKWARD")
    print("-" * 60)
    
    """Change Direction: Changing direction requires time to switch. The
    time is dictated by the stepper motor and controller."""
    sleep(1.0)
    GPIO.output(DIR, CCW)
    
    print(f"Rotating {STEPS_PER_REVOLUTION} steps backward...")
    for x in range(STEPS_PER_REVOLUTION):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(STEP_DELAY)
        GPIO.output(STEP, GPIO.LOW)
        sleep(STEP_DELAY)
    
    print(f"✓ Completed {STEPS_PER_REVOLUTION} steps backward")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nMotor should have rotated:")
    print("  1. One full revolution forward")
    print("  2. One full revolution backward")
    print("  (Net rotation: 0)")

# Once finished clean everything up
except KeyboardInterrupt:
    print("\n\nTest interrupted by user")
except Exception as e:
    print(f"\n\nError: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\nCleaning up GPIO...")
    GPIO.cleanup()
    print("GPIO cleanup complete")