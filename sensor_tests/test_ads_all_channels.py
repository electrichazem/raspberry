#!/usr/bin/env python3
"""
Comprehensive ADS1115 Analog-to-Digital Converter Test Script
Based on the old working code pattern (ph.py, tds.py)

This script tests all channels on all configured ADS1115 boards.
It uses the same proven pattern from the old working codes:
- AnalogIn wrapper for easy channel access
- Multiple samples with averaging for accuracy
- Direct voltage readings

SETUP (using virtual environment - recommended):
    
    WINDOWS (PowerShell):
    1. Create virtual environment:
       python -m venv venv
    
    2. Activate it:
       .\venv\Scripts\Activate.ps1
       (If you get execution policy error, run first:
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser)
    
    3. Install dependencies:
       pip install adafruit-circuitpython-ads1x15 adafruit-blinka
    
    4. Run the script:
       python sensor_tests/test_ads_all_channels.py
    
    RASPBERRY PI (Linux):
    1. Create virtual environment:
       python3 -m venv venv
    
    2. Activate it:
       source venv/bin/activate
    
    3. Install dependencies:
       pip install adafruit-circuitpython-ads1x15 adafruit-blinka
    
    4. Run the script:
       python3 sensor_tests/test_ads_all_channels.py
    
    Alternative (system-wide, requires sudo on Pi):
       sudo pip3 install adafruit-circuitpython-ads1x15 adafruit-blinka

Configuration:
    Edit the ADS_BOARDS list below to match your hardware setup.
    Default matches config.yaml: 0x48 and 0x49 addresses.
"""

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# ===== CONFIGURATION =====
# List of ADS1115 board addresses to test
ADS_BOARDS = [
    0x48,  # First ADS1115 (default address)
    0x49,  # Second ADS1115 (ADDR pin to VIN)
]

# Number of samples to average per reading (same as old code)
SAMPLES = 10

# Delay between individual sample reads (seconds)
DELAY_BETWEEN_READS = 0.05

# Delay between channel readings (seconds)
DELAY_BETWEEN_CHANNELS = 0.1

# Main loop delay (seconds)
MAIN_LOOP_DELAY = 1.0
# ==========================

def test_ads_board(address, channel):
    """
    Test a single channel on an ADS1115 board.
    Uses the same pattern as old working code (ph.py, tds.py).
    
    Args:
        address: I2C address of the ADS1115 board
        channel: Channel number (0, 1, 2, or 3)
    
    Returns:
        tuple: (avg_voltage, raw_readings_list) or (None, None) if error
    """
    try:
        # Initialize I2C and ADS1115 (same as old code)
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c, address=address)
        
        # Create AnalogIn channel (same as old code: AnalogIn(ads, 0))
        chan = AnalogIn(ads, channel)
        
        # Read multiple samples and average (same pattern as old code)
        voltages = []
        for _ in range(SAMPLES):
            voltages.append(chan.voltage)
            time.sleep(DELAY_BETWEEN_READS)
        
        # Calculate average (same as old code)
        avg_voltage = sum(voltages) / len(voltages)
        
        return avg_voltage, voltages
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None, None


def main():
    """Main test loop - tests all channels on all boards."""
    print("=" * 70)
    print("ADS1115 Analog-to-Digital Converter Test")
    print("Based on old working code pattern (ph.py, tds.py)")
    print("=" * 70)
    print(f"\nTesting {len(ADS_BOARDS)} ADS1115 board(s):")
    for addr in ADS_BOARDS:
        print(f"  - Address 0x{addr:02X}")
    print(f"\nConfiguration:")
    print(f"  - Samples per reading: {SAMPLES}")
    print(f"  - Delay between reads: {DELAY_BETWEEN_READS}s")
    print(f"  - Channels per board: 4 (0-3)")
    print("\nPress Ctrl+C to stop\n")
    print("-" * 70)
    
    # Initialize I2C once for all boards
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
    except Exception as e:
        print(f"ERROR: Failed to initialize I2C bus: {e}")
        print("\nPlease check:")
        print("  1. I2C is enabled on Raspberry Pi (raspi-config)")
        print("  2. ADS1115 is properly connected to SCL/SDA pins")
        print("  3. Required libraries are installed")
        return
    
    # Create ADS1115 objects for each board
    ads_boards = {}
    for address in ADS_BOARDS:
        try:
            ads = ADS.ADS1115(i2c, address=address)
            ads_boards[address] = ads
            print(f"✓ Successfully initialized ADS1115 at address 0x{address:02X}")
        except Exception as e:
            print(f"✗ Failed to initialize ADS1115 at address 0x{address:02X}: {e}")
            print(f"  (This board will be skipped)")
    
    if not ads_boards:
        print("\nERROR: No ADS1115 boards could be initialized!")
        return
    
    print(f"\nTesting {len(ads_boards)} board(s)...\n")
    print("-" * 70)
    
    try:
        while True:
            # Test each board
            for address in sorted(ads_boards.keys()):
                ads = ads_boards[address]
                print(f"\nBoard 0x{address:02X}:")
                
                # Test each channel (0-3)
                for channel in range(4):
                    try:
                        # Create AnalogIn channel (same as old code)
                        chan = AnalogIn(ads, channel)
                        
                        # Read multiple samples and average (same pattern as old code)
                        voltages = []
                        for _ in range(SAMPLES):
                            voltages.append(chan.voltage)
                            time.sleep(DELAY_BETWEEN_READS)
                        
                        # Calculate average (same as old code)
                        avg_voltage = sum(voltages) / len(voltages)
                        
                        # Calculate min/max for reference
                        min_voltage = min(voltages)
                        max_voltage = max(voltages)
                        voltage_range = max_voltage - min_voltage
                        
                        # Display results
                        print(f"  Channel {channel}: {avg_voltage:.4f} V "
                              f"(min: {min_voltage:.4f}, max: {max_voltage:.4f}, "
                              f"range: {voltage_range:.4f})")
                        
                        time.sleep(DELAY_BETWEEN_CHANNELS)
                        
                    except Exception as e:
                        print(f"  Channel {channel}: ERROR - {e}")
                        time.sleep(DELAY_BETWEEN_CHANNELS)
            
            print("-" * 70)
            time.sleep(MAIN_LOOP_DELAY)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

