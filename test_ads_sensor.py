#!/usr/bin/env python3
"""
Standalone test script for a single ADS1115 sensor channel.
No config needed - just edit the channel number and address below.
"""

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# ===== CONFIGURATION - Edit these =====
CHANNEL = 0          # ADS1115 channel (0, 1, 2, or 3)
ADDRESS = 0x48       # I2C address (0x48 or 0x49)
SAMPLES = 10         # Number of samples to average
DELAY = 0.05        # Delay between samples (seconds)
# ======================================

# Initialize I2C and ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=ADDRESS)
chan = AnalogIn(ads, CHANNEL)

print(f"Testing ADS1115 channel {CHANNEL} at address 0x{ADDRESS:02X}")
print("Press Ctrl+C to stop\n")

try:
    while True:
        # Average multiple samples
        voltages = [chan.voltage for _ in range(SAMPLES)]
        avg_voltage = sum(voltages) / len(voltages)
        
        # Display raw voltage
        print(f"Channel {CHANNEL}: {avg_voltage:.4f} V")
        
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nStopped by user.")

