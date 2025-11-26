#!/usr/bin/env python3
"""
TB6600 Stepper Motor Test: Rotate one revolution forward, then one revolution backward.

Hardware:
  - TB6600 stepper driver module
  - Step pin: GPIO12
  - Direction pin: GPIO24
  - Typical stepper: 200 steps/revolution (1.8° per step)

Requirements:
    pip install RPi.GPIO

Usage:
    python3 sensor_tests/tb6600_stepper_test.py
"""

import time
import RPi.GPIO as GPIO

# GPIO pins
STEP_PIN = 12
DIR_PIN = 24

# Stepper motor settings
STEPS_PER_REVOLUTION = 200  # Most common stepper motors (1.8° per step)
# If your motor is 400 steps/rev (0.9° per step), change this to 400

STEP_DELAY = 0.001  # Delay between steps in seconds (1ms = 1000 steps/sec max)
# Adjust STEP_DELAY to control speed:
# - 0.001s = 1000 steps/sec = 5 rev/sec (fast)
# - 0.002s = 500 steps/sec = 2.5 rev/sec (medium)
# - 0.005s = 200 steps/sec = 1 rev/sec (slow)


def setup_gpio():
    """Initialize GPIO pins."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(STEP_PIN, GPIO.OUT)
    GPIO.setup(DIR_PIN, GPIO.OUT)
    
    # Start with both pins LOW
    GPIO.output(STEP_PIN, GPIO.LOW)
    GPIO.output(DIR_PIN, GPIO.LOW)
    print("GPIO initialized:")
    print(f"  Step pin (GPIO{STEP_PIN}): ready")
    print(f"  Direction pin (GPIO{DIR_PIN}): ready")


def rotate_steps(steps, direction_forward=True):
    """
    Rotate the stepper motor a specified number of steps.
    
    Args:
        steps: Number of steps to rotate
        direction_forward: True for forward, False for backward
    """
    # Set direction
    GPIO.output(DIR_PIN, GPIO.HIGH if direction_forward else GPIO.LOW)
    direction_str = "forward" if direction_forward else "backward"
    
    print(f"\nRotating {steps} steps ({direction_str})...")
    
    # Generate step pulses
    for i in range(steps):
        # Step pulse: HIGH then LOW
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY / 2)  # Half delay for HIGH
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY / 2)  # Half delay for LOW
        
        # Progress indicator every 50 steps
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{steps} steps completed")
    
    print(f"✓ Completed {steps} steps ({direction_str})")


def main():
    """Main test sequence."""
    print("=" * 60)
    print("TB6600 STEPPER MOTOR TEST")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Steps per revolution: {STEPS_PER_REVOLUTION}")
    print(f"  Step delay: {STEP_DELAY * 1000:.1f}ms")
    print(f"  Estimated speed: {1.0 / STEP_DELAY / STEPS_PER_REVOLUTION:.1f} rev/sec")
    
    try:
        setup_gpio()
        
        # Small delay to ensure everything is ready
        time.sleep(0.5)
        
        # Rotate one revolution forward
        print("\n" + "-" * 60)
        print("STEP 1: Rotating ONE REVOLUTION FORWARD")
        print("-" * 60)
        rotate_steps(STEPS_PER_REVOLUTION, direction_forward=True)
        
        # Brief pause between rotations
        print("\nPausing 1 second before reverse rotation...")
        time.sleep(1.0)
        
        # Rotate one revolution backward
        print("\n" + "-" * 60)
        print("STEP 2: Rotating ONE REVOLUTION BACKWARD")
        print("-" * 60)
        rotate_steps(STEPS_PER_REVOLUTION, direction_forward=False)
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print("\nMotor should have rotated:")
        print("  1. One full revolution forward")
        print("  2. One full revolution backward")
        print("  (Net rotation: 0)")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
    finally:
        # Cleanup GPIO
        print("\nCleaning up GPIO...")
        GPIO.output(STEP_PIN, GPIO.LOW)
        GPIO.output(DIR_PIN, GPIO.LOW)
        GPIO.cleanup()
        print("GPIO cleanup complete")


if __name__ == "__main__":
    main()

