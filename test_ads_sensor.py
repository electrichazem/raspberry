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
            # Use the channel number directly (0, 1, 2, or 3)
            raw = ads.read(CHANNEL)
            # Convert 16-bit signed value to voltage (ADS1115 is +/- 4.096V)
            # ADS1115 returns values from -32768 to +32767 for +/- 4.096V range
            voltage = (raw / 32767.0) * 4.096
            raw_values.append(voltage)
        
        avg_voltage = sum(raw_values) / len(raw_values)
        
        # Display raw voltage
        print(f"Channel {CHANNEL}: {avg_voltage:.4f} V (raw: {raw_values[0]:.0f})")
        
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nStopped by user.")
except Exception as e:
    print(f"\nError: {e}")
    print("\nTrying alternative method...")
    # Fallback: try using the old-style AnalogIn if available
    try:
        from adafruit_ads1x15.analog_in import AnalogIn
        chan = AnalogIn(ads, CHANNEL)
        print("Using AnalogIn wrapper...")
        while True:
            voltages = [chan.voltage for _ in range(SAMPLES)]
            avg_voltage = sum(voltages) / len(voltages)
            print(f"Channel {CHANNEL}: {avg_voltage:.4f} V")
            time.sleep(1)
    except Exception as e2:
        print(f"Alternative method also failed: {e2}")
        print("\nPlease check your library version and wiring.")

