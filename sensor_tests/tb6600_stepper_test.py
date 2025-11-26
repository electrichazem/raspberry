#!/usr/bin/env python3
"""
TB6600 Stepper Motor Test: Rotate one revolution forward, then one revolution backward.

Hardware:
  - TB6600 stepper driver module
  - Step pin: GPIO12 (PUL)
  - Direction pin: GPIO24 (DIR)
  - Enable pin: Optional (not used in this code, but can be added if needed)
  - Typical stepper: 200 steps/revolution (1.8° per step) or 6400 with microstepping

Requirements:
    pip install RPi.GPIO

Usage:
    python3 sensor_tests/tb6600_stepper_test.py
"""

import time
import RPi.GPIO as GPIO
import atexit

# GPIO pins
PUL = 12   # Stepper Drive Pulses (Step pin)
DIR = 25   # Controller Direction Bit (HIGH = one direction, LOW = other direction)

# Stepper motor settings
STEPS_PER_REVOLUTION = 6400  # Adjust based on your motor and microstepping settings
# Common values:
# - 200 steps/rev for full step (1.8° per step)
# - 400 steps/rev for half step
# - 6400 steps/rev for 32x microstepping

STEP_DELAY = 0.0005  # Delay between step pulses in seconds (0.5ms = 2000 steps/sec max)
# Adjust STEP_DELAY to control speed:
# - 0.0001s = 10000 steps/sec (very fast, may skip steps)
# - 0.0005s = 2000 steps/sec (fast)
# - 0.001s = 1000 steps/sec (medium)
# - 0.002s = 500 steps/sec (slow)

# Cleanup function to ensure GPIO is reset on exit
def cleanup_gpio():
    """Clean up GPIO pins on exit."""
    try:
        GPIO.output(PUL, GPIO.LOW)
        GPIO.output(DIR, GPIO.LOW)
        GPIO.cleanup()
        print("\nGPIO cleaned up successfully")
    except:
        pass

atexit.register(cleanup_gpio)

def setup_gpio():
    """Initialize GPIO pins."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PUL, GPIO.OUT)
    GPIO.setup(DIR, GPIO.OUT)
    
    # Start with both pins LOW
    GPIO.output(PUL, GPIO.LOW)
    GPIO.output(DIR, GPIO.LOW)
    
    print("GPIO initialized:")
    print(f"  Step pin (PUL) = GPIO{PUL}")
    print(f"  Direction pin (DIR) = GPIO{DIR}")

def rotate_forward(steps):
    """Rotate stepper motor forward."""
    print(f"\nRotating {steps} steps FORWARD...")
    GPIO.output(DIR, GPIO.LOW)  # Set direction (LOW = forward)
    time.sleep(0.01)  # Small delay for direction to settle
    
    for i in range(steps):
        GPIO.output(PUL, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(PUL, GPIO.LOW)
        time.sleep(STEP_DELAY)
        
        # Progress indicator every 1000 steps
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{steps} steps completed")
    
    print(f"✓ Completed {steps} steps forward")

def rotate_backward(steps):
    """Rotate stepper motor backward."""
    print(f"\nRotating {steps} steps BACKWARD...")
    GPIO.output(DIR, GPIO.HIGH)  # Set direction (HIGH = backward)
    time.sleep(0.01)  # Small delay for direction to settle
    
    for i in range(steps):
        GPIO.output(PUL, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(PUL, GPIO.LOW)
        time.sleep(STEP_DELAY)
        
        # Progress indicator every 1000 steps
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{steps} steps completed")
    
    print(f"✓ Completed {steps} steps backward")

def main():
    """Main test sequence."""
    print("=" * 60)
    print("TB6600 STEPPER MOTOR TEST")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Steps per revolution: {STEPS_PER_REVOLUTION}")
    print(f"  Step delay: {STEP_DELAY * 1000:.2f}ms")
    print(f"  Estimated speed: {1.0 / (STEP_DELAY * 2) / STEPS_PER_REVOLUTION:.2f} rev/sec")
    
    try:
        setup_gpio()
        time.sleep(0.5)  # Brief pause after initialization
        
        # Rotate one revolution forward
        print("\n" + "-" * 60)
        print("STEP 1: Rotating ONE REVOLUTION FORWARD")
        print("-" * 60)
        rotate_forward(STEPS_PER_REVOLUTION)
        
        # Brief pause between rotations
        print("\nPausing 1 second before reverse rotation...")
        time.sleep(1.0)
        
        # Rotate one revolution backward
        print("\n" + "-" * 60)
        print("STEP 2: Rotating ONE REVOLUTION BACKWARD")
        print("-" * 60)
        rotate_backward(STEPS_PER_REVOLUTION)
        
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
        import traceback
        traceback.print_exc()
    finally:
        cleanup_gpio()

if __name__ == "__main__":
    main()