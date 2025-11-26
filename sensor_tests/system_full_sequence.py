#!/usr/bin/env python3
"""
Full system connection test sequence: all 5 steps in one script with stepper motor.

This script runs the complete system test sequence:
  Initialization: Return servos to 0°, close all relays, wait for Enter key
  Step 1: Turn on relay P7
  Step 2: Run peltiers + turn on relay P4 (keeps P7 ON)
  Step 3: Move servos to 90° + turn on relay P5 and P6 (keeps all previous ON)
  Step 4: Ensure relay P4 + P7 are ON (keeps all previous ON)
  Step 5: Turn on relay P3, run syringe pump (stepper), turn on ALL 8 relays

Each step waits 5 seconds before proceeding to the next.

Requirements (inside your venv):
    pip install adafruit-circuitpython-pcf8574 adafruit-circuitpython-pca9685 adafruit-circuitpython-motor RPi.GPIO

Usage:
    python3 sensor_tests/system_full_sequence.py
"""

import time
import sys

import board
import busio
import RPi.GPIO as GPIO
from adafruit_motor import servo
from adafruit_pcf8574 import PCF8574
from adafruit_pca9685 import PCA9685

# PCF8574 relay expander
RELAY_I2C_ADDRESS = 0x27
RELAY_7_INDEX = 7
RELAY_4_INDEX = 4
RELAY_5_INDEX = 5
RELAY_6_INDEX = 6
RELAY_3_INDEX = 3

# PCA9685 PWM expander
PWM_I2C_ADDRESS = 0x40
PELTIER_CHANNELS = (0, 1)
SERVO_CHANNELS = (2, 3)
PWM_DUTY = 0x7FFF  # 50% duty for peltiers
SERVO_ANGLE = 90
SERVO_INITIAL_ANGLE = 0  # Initial position for servos

# TB6600 Stepper Motor (Syringe Pump)
STEP_PIN = 12
DIR_PIN = 25
CW = 1
CCW = 0
STEPS_PER_REVOLUTION = 200  # Adjust based on your motor
STEP_DELAY = 0.005  # 5ms delay

GAP_SECONDS = 5.0


def setup_stepper_gpio():
    """Initialize GPIO pins for stepper motor."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(STEP_PIN, GPIO.OUT)
    GPIO.setup(DIR_PIN, GPIO.OUT)
    GPIO.output(STEP_PIN, GPIO.LOW)
    GPIO.output(DIR_PIN, CCW)


def run_syringe_pump():
    """Run syringe pump: one revolution forward, then one backward."""
    print("\nRunning syringe pump (stepper motor)...")
    print(f"  Step pin: GPIO{STEP_PIN}")
    print(f"  Direction pin: GPIO{DIR_PIN}")
    
    # Forward rotation
    print(f"  Rotating {STEPS_PER_REVOLUTION} steps forward...")
    GPIO.output(DIR_PIN, CW)
    time.sleep(0.1)  # Direction settle time
    
    for i in range(STEPS_PER_REVOLUTION):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY)
    
    print(f"  ✓ Completed {STEPS_PER_REVOLUTION} steps forward")
    
    # Brief pause before reverse
    time.sleep(0.5)
    
    # Backward rotation
    print(f"  Rotating {STEPS_PER_REVOLUTION} steps backward...")
    GPIO.output(DIR_PIN, CCW)
    time.sleep(0.1)  # Direction settle time
    
    for i in range(STEPS_PER_REVOLUTION):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY)
    
    print(f"  ✓ Completed {STEPS_PER_REVOLUTION} steps backward")
    print("  ✓ Syringe pump cycle complete")


def wait_for_enter():
    """Wait for user to press Enter key."""
    print("\n" + "=" * 60)
    print("READY TO START")
    print("=" * 60)
    print("\nAll systems initialized:")
    print("  ✓ Servos returned to 0°")
    print("  ✓ All relays turned OFF")
    print("\nPress ENTER to start the test sequence...")
    try:
        input()  # Wait for Enter key
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")
        sys.exit(0)


def main() -> None:
    print("=" * 60)
    print("FULL SYSTEM CONNECTION TEST SEQUENCE")
    print("=" * 60)
    print()
    
    # Initialize I2C and hardware
    i2c = busio.I2C(board.SCL, board.SDA)
    
    # Initialize relay expander
    pcf = PCF8574(i2c, address=RELAY_I2C_ADDRESS)
    relay_pins = [pcf.get_pin(n) for n in range(8)]
    
    # Initialize PWM expander
    pca = PCA9685(i2c, address=PWM_I2C_ADDRESS)
    pca.frequency = 50  # 50 Hz for servos & PWM
    
    # Initialize servos
    servos = [
        servo.Servo(pca.channels[ch], min_pulse=500, max_pulse=2500)
        for ch in SERVO_CHANNELS
    ]
    
    # Initialize stepper motor GPIO
    setup_stepper_gpio()
    
    # ========== INITIALIZATION: Return servos to 0° and close all relays ==========
    print("INITIALIZATION: Resetting system to safe state")
    print("-" * 60)
    
    # Close all relays (turn OFF)
    print("Closing all relays (turning OFF)...")
    for idx, pin in enumerate(relay_pins):
        pin.switch_to_output(value=False)  # OFF
        print(f"  ✓ Relay P{idx}: OFF")
    
    # Return servos to 0°
    print(f"\nReturning servos to {SERVO_INITIAL_ANGLE}°...")
    for idx, s in enumerate(servos):
        s.angle = SERVO_INITIAL_ANGLE
        print(f"  ✓ Servo channel {SERVO_CHANNELS[idx]}: {SERVO_INITIAL_ANGLE}°")
    
    print("\n✓ Initialization complete")
    
    # Wait for user to press Enter
    try:
        wait_for_enter()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        GPIO.cleanup()
        sys.exit(0)
    
    try:
        # ========== STEP 1: Relay P7 ==========
        print("STEP 1: Turning ON relay P7")
        print("-" * 60)
        relay_pins[RELAY_7_INDEX].value = True
        print(f"✓ Relay P{RELAY_7_INDEX}: ON")
        print(f"\nWaiting {GAP_SECONDS:.0f}s before next step...\n")
        time.sleep(GAP_SECONDS)
        
        # ========== STEP 2: Peltiers + Relay P4 ==========
        print("STEP 2: Running peltiers + turning ON relay P4")
        print("-" * 60)
        print(f"✓ Keeping relay P{RELAY_7_INDEX} ON (from step 1)")
        relay_pins[RELAY_7_INDEX].value = True
        
        print(f"✓ Turning ON relay P{RELAY_4_INDEX}")
        relay_pins[RELAY_4_INDEX].value = True
        
        print(f"✓ Running peltiers on channels {PELTIER_CHANNELS[0]} & {PELTIER_CHANNELS[1]}")
        for ch in PELTIER_CHANNELS:
            pca.channels[ch].duty_cycle = PWM_DUTY
            print(f"  Channel {ch}: PWM duty 0x{PWM_DUTY:04X} (50%)")
        
        print(f"\nWaiting {GAP_SECONDS:.0f}s before next step...\n")
        time.sleep(GAP_SECONDS)
        
        # ========== STEP 3: Servos + Relay P5 + Relay P6 ==========
        print("STEP 3: Moving servos to 90° + turning ON relay P5 and P6")
        print("-" * 60)
        print(f"✓ Keeping relay P{RELAY_7_INDEX} ON (from step 1)")
        relay_pins[RELAY_7_INDEX].value = True
        
        print(f"✓ Keeping relay P{RELAY_4_INDEX} ON (from step 2)")
        relay_pins[RELAY_4_INDEX].value = True
        
        print(f"✓ Keeping peltiers running on channels {PELTIER_CHANNELS[0]} & {PELTIER_CHANNELS[1]}")
        for ch in PELTIER_CHANNELS:
            pca.channels[ch].duty_cycle = PWM_DUTY
        
        print(f"✓ Moving servos on channels {SERVO_CHANNELS[0]} & {SERVO_CHANNELS[1]} from 0° to 90°")
        for idx, s in enumerate(servos):
            print(f"  Servo channel {SERVO_CHANNELS[idx]}: 0° → 90°")
            s.angle = 0
            time.sleep(0.5)  # brief pause
            s.angle = SERVO_ANGLE
        
        print(f"✓ Turning ON relay P{RELAY_5_INDEX}")
        relay_pins[RELAY_5_INDEX].value = True
        
        print(f"✓ Turning ON relay P{RELAY_6_INDEX}")
        relay_pins[RELAY_6_INDEX].value = True
        
        print(f"\nWaiting {GAP_SECONDS:.0f}s before next step...\n")
        time.sleep(GAP_SECONDS)
        
        # ========== STEP 4: Ensure Relay P4 + P7 ==========
        print("STEP 4: Ensuring relay P4 + P7 are ON")
        print("-" * 60)
        print(f"✓ Ensuring relay P{RELAY_7_INDEX} is ON (from step 1)")
        relay_pins[RELAY_7_INDEX].value = True
        
        print(f"✓ Ensuring relay P{RELAY_4_INDEX} is ON (from step 2)")
        relay_pins[RELAY_4_INDEX].value = True
        
        print(f"✓ Keeping relay P{RELAY_5_INDEX} ON (from step 3)")
        relay_pins[RELAY_5_INDEX].value = True
        
        print(f"✓ Keeping relay P{RELAY_6_INDEX} ON (from step 3)")
        relay_pins[RELAY_6_INDEX].value = True
        
        print(f"✓ Keeping peltiers running on channels {PELTIER_CHANNELS[0]} & {PELTIER_CHANNELS[1]}")
        for ch in PELTIER_CHANNELS:
            pca.channels[ch].duty_cycle = PWM_DUTY
        
        print(f"✓ Keeping servos on channels {SERVO_CHANNELS[0]} & {SERVO_CHANNELS[1]} at {SERVO_ANGLE}°")
        for s in servos:
            s.angle = SERVO_ANGLE
        
        print(f"\nWaiting {GAP_SECONDS:.0f}s before next step...\n")
        time.sleep(GAP_SECONDS)
        
        # ========== STEP 5: Relay P3 + Syringe Pump + All Relays ==========
        print("STEP 5: Turning ON relay P3 + Running syringe pump + Turning ON ALL relays")
        print("-" * 60)
        print(f"✓ Keeping relay P{RELAY_7_INDEX} ON (from step 1)")
        relay_pins[RELAY_7_INDEX].value = True
        
        print(f"✓ Keeping relay P{RELAY_4_INDEX} ON (from step 2)")
        relay_pins[RELAY_4_INDEX].value = True
        
        print(f"✓ Keeping relay P{RELAY_5_INDEX} ON (from step 3)")
        relay_pins[RELAY_5_INDEX].value = True
        
        print(f"✓ Keeping relay P{RELAY_6_INDEX} ON (from step 3)")
        relay_pins[RELAY_6_INDEX].value = True
        
        print(f"✓ Turning ON relay P{RELAY_3_INDEX}")
        relay_pins[RELAY_3_INDEX].value = True
        
        print(f"✓ Keeping peltiers running on channels {PELTIER_CHANNELS[0]} & {PELTIER_CHANNELS[1]}")
        for ch in PELTIER_CHANNELS:
            pca.channels[ch].duty_cycle = PWM_DUTY
        
        print(f"✓ Keeping servos on channels {SERVO_CHANNELS[0]} & {SERVO_CHANNELS[1]} at {SERVO_ANGLE}°")
        for s in servos:
            s.angle = SERVO_ANGLE
        
        # Run syringe pump (stepper motor)
        run_syringe_pump()
        
        # Turn on ALL 8 relays
        print("\nTurning ON ALL 8 relays...")
        for idx, pin in enumerate(relay_pins):
            pin.value = True  # Turn ON
            print(f"  ✓ Relay P{idx}: ON")
        
        print(f"\nWaiting {GAP_SECONDS:.0f}s before final status...\n")
        time.sleep(GAP_SECONDS)
        
        # ========== FINAL STATUS ==========
        print("=" * 60)
        print("FULL SYSTEM SEQUENCE COMPLETE")
        print("=" * 60)
        print("\nFinal status - All outputs are ON:")
        print("  ✓ All 8 relays: ON")
        for idx in range(8):
            print(f"    - Relay P{idx}: ON")
        print(f"  ✓ Peltier channels {PELTIER_CHANNELS[0]} & {PELTIER_CHANNELS[1]}: running")
        print(f"  ✓ Servo channels {SERVO_CHANNELS[0]} & {SERVO_CHANNELS[1]}: at {SERVO_ANGLE}°")
        print("  ✓ Syringe pump: completed one full cycle (forward + backward)")
        print("\nAll hardware connections verified successfully!")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup GPIO
        try:
            GPIO.cleanup()
            print("\nGPIO cleaned up successfully")
        except:
            pass


if __name__ == "__main__":
    main()

