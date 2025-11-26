#!/usr/bin/env python3
"""
Standalone test script for a single ADS1115 sensor channel.
No config needed - just edit the channel number and address below.

SETUP (using virtual environment - recommended):
    1. Create virtual environment:
       python3 -m venv venv
    
    2. Activate it:
       source venv/bin/activate
    
    3. Install dependencies:
       pip install RPi.GPIO adafruit-circuitpython-ads1x15 adafruit-blinka
    
    4. Run the script:
       python3 test_ads_sensor.py

Alternative (system-wide, requires sudo):
    sudo pip3 install RPi.GPIO adafruit-circuitpython-ads1x15 adafruit-blinka
"""

import time

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.ads1x15 import P0, P1, P2, P3
except ImportError as e:
    print("ERROR: Missing required libraries!")
    print("\nUsing virtual environment (recommended):")
    print("  python3 -m venv venv")
    print("  source venv/bin/activate")
    print("  pip install RPi.GPIO adafruit-circuitpython-ads1x15 adafruit-blinka")
    print("\nOr system-wide (requires sudo):")
    print("  sudo pip3 install RPi.GPIO adafruit-circuitpython-ads1x15 adafruit-blinka")
    print(f"\nOriginal error: {e}")
    exit(1)

# ===== CONFIGURATION - Edit these =====
CHANNEL = 0          # ADS1115 channel (0, 1, 2, or 3)
ADDRESS = 0x48       # I2C address (0x48 or 0x49)
SAMPLES = 10         # Number of samples to average
# ======================================

# Channel mapping
CHANNEL_MAP = {0: P0, 1: P1, 2: P2, 3: P3}

# Initialize I2C and ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=ADDRESS)

print(f"Testing ADS1115 channel {CHANNEL} at address 0x{ADDRESS:02X}")
print("Press Ctrl+C to stop\n")

try:
    while True:
        # Average multiple samples - read raw value and convert to voltage
        raw_values = []
        for _ in range(SAMPLES):
            raw = ads.read(CHANNEL_MAP[CHANNEL])
            # Convert 16-bit signed value to voltage (ADS1115 is +/- 4.096V)
            voltage = (raw / 32767.0) * 4.096
            raw_values.append(voltage)
        
        avg_voltage = sum(raw_values) / len(raw_values)
        
        # Display raw voltage
        print(f"Channel {CHANNEL}: {avg_voltage:.4f} V")
        
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nStopped by user.")

