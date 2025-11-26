#!/usr/bin/env python3
"""
Simple Bluetooth serial link test between Raspberry Pi and Arduino TFT board.

On the Arduino side:
  - `arduino/tft_dashboard/tft_dashboard.ino` uses a HC-05/HC-06 on pins 10 (RX) and 11 (TX)
  - It marks BT as OK on the TFT once it receives any line of text.

On the Pi side (this script):
  1. Pair and bind your HC-05/HC-06 to a serial port, e.g. /dev/rfcomm0
  2. Install pyserial in your venv:
       pip install pyserial
  3. Run:
       python3 sensor_tests/bt_link_test.py
"""

import time

import serial

PORT = "/dev/rfcomm0"  # adjust to your BT serial device (e.g. /dev/ttyUSB0, /dev/ttyAMA0)
BAUD = 9600


def main() -> None:
    print(f"Opening Bluetooth serial on {PORT} @ {BAUD}...")
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        print("Connected. Sending heartbeat lines to Arduino.")
        print("Press Ctrl+C to stop.\n")
        counter = 0
        try:
            while True:
                msg = f"HELLO_FROM_PI {counter}\n"
                ser.write(msg.encode("utf-8"))
                print(f"TX: {msg.strip()}")

                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    print(f"RX: {line}")
                time.sleep(1.0)
                counter += 1
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()


