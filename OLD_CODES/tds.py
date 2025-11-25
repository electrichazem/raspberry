import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


TEMPERATURE = 25.0            
CALIBRATION_FACTOR = .885      # adjust after calibration
SAMPLES = 10                  # readings per measurement
DELAY_BETWEEN_READS = 0.05    # seconds


i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, 0)       # A0 channel for TDS signal



while True:
    try:
        # Step 1: average a few samples
        voltages = [chan.voltage for _ in range(SAMPLES)]
        avg_voltage = sum(voltages) / len(voltages)

        ec_value = (133.42 * avg_voltage**3
                    - 255.86 * avg_voltage**2
                    + 857.39 * avg_voltage) / 1000.0


        ec25 = ec_value / (1 + 0.02 * (TEMPERATURE - 25.0))

     
        tds_value = ec25 * 500.0

        # Step 5: apply calibration factor
        tds_value *= CALIBRATION_FACTOR

        print(f"Voltage: {avg_voltage:.3f} V  TDS: {tds_value:.1f} ppm")
        time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped by user.")
        break

