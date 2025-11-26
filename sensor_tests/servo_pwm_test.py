
#!/usr/bin/env python3
"""
Simple servo test using pigpio hardware PWM on GPIO20.

Requirements:
    1. Install pigpio and start the daemon:
         sudo apt install pigpio
         sudo systemctl enable pigpiod
         sudo systemctl start pigpiod
       (or run `sudo pigpiod` manually)

    2. Install the Python client inside your venv:
         pip install pigpio

    3. Run the script:
         python3 sensor_tests/servo_pwm_test.py

The script sweeps between 0° / 90° / 180° with 1-second pauses.
"""

import time

import pigpio

SERVO_GPIO = 20
MIN_US = 500      # adjust for your servo (typical 500-2500 µs)
MID_US = 1500
MAX_US = 2500


def main() -> None:
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("pigpio daemon not running. Start with `sudo pigpiod`.")

    print("Sweeping servo on GPIO20...")
    try:
        while True:
            for pulse in (MIN_US, MID_US, MAX_US, MID_US):
                print(f"Setting pulse width to {pulse} µs")
                pi.set_servo_pulsewidth(SERVO_GPIO, pulse)
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        pi.set_servo_pulsewidth(SERVO_GPIO, 0)  # disable pulses
        pi.stop()


if __name__ == "__main__":
    main()

