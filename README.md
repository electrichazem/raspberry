# Plant Controller

Python control stack for the Raspberry Pi 4 grow system. It manages humidity, CO₂, lighting, air and water temperature, nutrient dosing, and soil moisture while exposing telemetry and manual overrides through a BLE/UART bridge to an Arduino console.

## Features
- Modular drivers for relays (PCF8574 + GPIO), PWM peltiers, vent servos, and syringe pump
- Sensor hub that polls DHT22, DS18B20, and multiple ADS1115 analog channels (soil moisture, pH, TDS/EC, MG811 CO₂). ADS1115 readings use averaged samples for accuracy, with proper TDS/EC polynomial formulas and temperature compensation matching the original working code.
- Controllers for humidity, CO₂/venting, lighting schedules, PID temperature loops, nutrient mixing/dosing, and soil moisture pulses
- BLE gateway publishing JSON telemetry packets and accepting manual override commands
- Config-driven pinout, PID gains, schedules, and subsystem enable flags via `config.yaml`

## Getting Started
1. Enable I²C, SPI, 1-Wire, and UART on the Pi.
2. Install dependencies: `sudo pip install -r requirements.txt` (list to be finalized).
3. Update `config.yaml` with your actual pin mappings, ADS channel assignments, and controller targets.
4. Run the service: `python -m plant_controller.main`.

## Hardware Bring-Up Tests
Use the helper script to exercise individual subsystems before running the full controller:
```
python -m plant_controller.tests.hardware_test --tests sensors servos
```
Available test names: `sensors`, `servos`, `relays_expander`, `relays_direct`, `peltiers`, `stepper`. The script loads pins and addresses from `config.yaml`, reports actions to the console, and applies short movements (e.g., 10° servo jogs, 1 revolution syringe moves) so you can verify hardware safely.
Add `--loop` to keep rerunning the selected tests and `--interval <seconds>` (default 5) to control the pause between passes. The `hardware_test_commands.txt` file in the repo root lists sample invocations for every test combination.

### TFT Dashboard (Arduino)
- Located at `arduino/tft_dashboard/tft_dashboard.ino`
- Uses MCUFRIEND + TouchScreen libraries; on-screen “Prev/Next” buttons handle pagination, and telemetry auto-refreshes every 5 s so you don’t need a manual refresh control
- If your controller uses different touch pin assignments or raw ADC ranges, edit the `XP/YP/XM/YM` defines and the `map()` calibration values accordingly

### Sensor Test Utilities
- `sensor_tests/test_ads_all_channels.py`, `sensor_tests/test_ads_sensor.py` help sanity-check ADS1115 channels without the full controller.
- `sensor_tests/ds18b20_test.py` reads the DS18B20 via the `/sys/bus/w1/devices` interface (enable 1-Wire, then run `python3 sensor_tests/ds18b20_test.py`).
- `sensor_tests/dht22_test.py` mirrors the old DHT22 script (`pip install adafruit-circuitpython-dht RPi.GPIO`, then run `python3 sensor_tests/dht22_test.py`).
- `sensor_tests/pcf8574_relay_test.py` walks each relay on the PCF8574 expander for 5 seconds (`pip install adafruit-circuitpython-pcf8574`, then run `python3 sensor_tests/pcf8574_relay_test.py`).
- `sensor_tests/system_step1_relay7.py` runs only relay P7 on the PCF8574 for 5 seconds (first step of full-system sequence).
- `sensor_tests/system_step2_peltiers_relay4.py` runs peltiers on PCA9685 channels 0 & 1 and turns on relay P4, keeping relay P7 ON from step 1 (second step of full-system sequence).
- `sensor_tests/system_step3_servos_relay6.py` moves servos from 0° to 90° and turns on relay P5 and relay P6, keeping all previous outputs ON (third step of full-system sequence).
- `sensor_tests/system_step4_relay4_relay7.py` ensures relay P4 + relay P7 are ON, keeping all previous outputs ON (fourth step of full-system sequence).
- `sensor_tests/system_step5_relay3.py` turns on relay P3, keeping all previous outputs ON (fifth and final step of full-system sequence).
- `sensor_tests/system_full_sequence.py` runs all 5 steps sequentially in a single script with 5-second delays between each step (recommended for full system testing).
- `sensor_tests/servo_pwm_test.py` sweeps a servo on GPIO20 using pigpio (`sudo apt install pigpio`, `pip install pigpio`, ensure `pigpiod` is running, then `python3 sensor_tests/servo_pwm_test.py`).
- `sensor_tests/servo_driver_test.py` drives a PCA9685 servo/PWM board (needs `pip install adafruit-circuitpython-pca9685`; run `python3 sensor_tests/servo_driver_test.py`).
- `sensor_tests/bt_link_test.py` sends heartbeat lines over a Bluetooth serial link to the Arduino TFT board (`pip install pyserial`, bind HC-05/HC-06 to `/dev/rfcomm0`, then `python3 sensor_tests/bt_link_test.py`).
- `sensor_tests/VIRTUAL_ENV_SETUP.md` documents the recommended virtual environment workflow when running standalone scripts on the Pi.

## Troubleshooting
- **`SyntaxError: from __future__ imports must occur at the beginning of the file`** when running hardware tests: pull the latest code so `plant_controller/utils/datatypes.py` contains a single set of dataclass definitions and the `from __future__ import annotations` line stays at the very top.

## BLE Command Examples
Send newline-delimited JSON over the BLE UART link:
```json
{"target":"relay","name":"lights","state":1}
{"target":"controller","name":"humidity","enabled":false}
{"target":"dose","channel":"nutrient_a","amount":1.0}
```

## Repository Layout
- `plant_controller/` – main Python package
  - `hardware/` – relay, PWM, servo, syringe drivers
  - `sensors/` – DHT22, DS18B20, ADS1115 readers and sensor hub
  - `controllers/` – logic modules per subsystem
  - `comms/` – BLE/serial gateway
  - `utils/` – config loader, datatypes, PID helper
- `config.yaml` – hardware pins and controller tuning
- `arduino/tft_dashboard/tft_dashboard.ino` – Uno sketch for the TFT telemetry display mock data UI
- `hardware_test_commands.txt` – copy/paste command reference for hardware tests
- `README.md`, `DOCUMENTATION.md` – keep both updated with behavior changes

