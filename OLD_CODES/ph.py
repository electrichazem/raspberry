import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import statistics

# === Configuration ===
CALIBRATION_VALUE = 16.83   # From your Arduino setup
SAMPLES = 10                # Number of samples to average
DELAY_BETWEEN_READS = 0.03  # 30 ms between reads

# === Initialize I2C and ADC ===
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, 0)     # A0 channel (ADS.P0 also works on newer libs)

# === Main loop ===
print("Reading pH sensor... Press Ctrl+C to stop.")
while True:
    try:
        readings = []
        for _ in range(SAMPLES):
            readings.append(chan.voltage)
            time.sleep(DELAY_BETWEEN_READS)

        # Sort readings and remove outliers (like Arduino code)
        readings.sort()
        filtered = readings[2:-2]  # discard 2 lowest and 2 highest
        avg_voltage = statistics.mean(filtered)

        # Apply same calibration formula as your Arduino code
        ph_value = -5.70 * avg_voltage + CALIBRATION_VALUE

        print(f"Voltage: {avg_voltage:.3f} V | pH: {ph_value:.2f}")
        time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped by user.")
        break

