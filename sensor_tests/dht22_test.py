#!/usr/bin/env python3
"""
Standalone DHT22 test (matches the old script style).

Usage:
    source venv/bin/activate   # optional virtual env
    pip install adafruit-circuitpython-dht RPi.GPIO
    python3 sensor_tests/dht22_test.py

Wiring:
    - Data pin -> GPIO4 (physical pin 7) by default
    - Power -> 3.3 V, GND -> GND
    - 10 kΩ pull-up resistor between DATA and 3.3 V
"""

import time

import board
import adafruit_dht

DHT_PIN = board.D4  # change if you wired to another GPIO


def main() -> None:
    sensor = adafruit_dht.DHT22(DHT_PIN, use_pulseio=False)
    print("Reading DHT22... Press Ctrl+C to stop.\n")
    try:
        while True:
            try:
                temperature_c = sensor.temperature
                humidity = sensor.humidity
                if temperature_c is not None and humidity is not None:
                    temperature_f = temperature_c * 9.0 / 5.0 + 32.0
                    print(
                        f"Temp: {temperature_c:5.1f} °C | {temperature_f:5.1f} °F  "
                        f"Humidity: {humidity:5.1f} %"
                    )
                else:
                    print("Sensor returned None values")
            except RuntimeError as err:
                # DHT sensors are finicky; just retry
                print(f"RuntimeError: {err.args[0]}")
            except Exception as err:
                print(f"Other error: {err}")
                sensor.exit()
                raise
            time.sleep(2.0)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        sensor.exit()


if __name__ == "__main__":
    main()

