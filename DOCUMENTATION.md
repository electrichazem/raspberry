# Documentation

## Hardware Mapping
- **Relays via PCF8574 (I²C)**: heater, humidity fan, CO₂ exhaust, vent fans, lights, water pump, nutrient A/B.
- **Direct GPIO relays**: main water feed (`GPIO22`), mix tank solenoid (`GPIO5`), plant output (`GPIO7`).
- **Servos**: vent left/right on `GPIO20`/`GPIO21` using 50 Hz PWM.
- **PWM channels**: air peltier (`GPIO19` PWM + `GPIO26` DIR), water peltier (`GPIO17` PWM + `GPIO27` DIR).
- **Syringe driver**: `STEP12`, `DIR25`, `ENABLE6`, limit switches on `GPIO23`/`GPIO24`.
- **Sensors**:
  - DHT22 (`GPIO16`)
  - DS18B20 (1-Wire bus on `GPIO4`)
  - Two ADS1115 boards for soil moisture, reservoir humidity probe, pH, TDS/EC, MG811 CO₂, and spare analog channels.

Update `config.yaml` if your wiring differs.

## Software Architecture
1. **Hardware drivers** in `plant_controller/hardware/` abstract relays, PWM, servos, and syringe movement so controllers only toggle named outputs.
2. **Sensor hub** (`sensors/hub.py`) polls DHT22, DS18B20, and ADS1115 inputs, converts them to engineering values, and populates the shared `SystemState`. ADS1115 readings use averaged samples (10 samples by default) for improved accuracy. TDS/EC calculations use polynomial formulas with temperature compensation, and pH uses a calibrated linear formula matching the original working code.
3. **Controllers** (`controllers/*.py`) implement individual subsystems:
   - `humidity` cycles heater + fan with cooldown windows.
   - `co2` vents via servos/fans, runs exhaust fans when ppm high.
   - `lighting` enforces on/off schedule.
   - `air_pid` and `water_pid` use PID to drive peltiers and circulation pump.
   - `nutrient` doses Nutrient A/B or dilutes with water when EC out of band.
   - `soil` pulses nutrient output solenoid and syringe when dish moisture low.
4. **BLE gateway** streams telemetry JSON and accepts manual commands for relays, controller enable flags, or ad-hoc doses.
5. **System manager** (`system_manager.py`) loads config, instantiates hardware + controllers, runs the main control loop, and coordinates BLE comms.

## Control Loop
1. Refresh sensors → update `SystemState`.
2. Sequentially run controllers; each decides whether to act based on current readings and guard timers.
3. Publish telemetry via BLE.
4. Consume any manual command overrides (relays, controllers, dosing).
5. Sleep to maintain the configured loop frequency (`loop_hz`).

## Hardware Test Utility
`plant_controller/tests/hardware_test.py` lets you validate peripherals individually. Invoke it with:
```
python -m plant_controller.tests.hardware_test --tests sensors servos --loop --interval 2
```
Tests read all pin assignments from `config.yaml`. Highlights:
- `sensors`: Poll DHT22, DS18B20, ADS1115 channels and print readings.
- `servos`: Jog each vent servo +10° and back.
- `relays_expander` / `relays_direct`: Sequentially energize each relay for a few seconds.
- `peltiers`: Drive each PWM channel forward (cool) and reverse (heat) for three minutes while logging progress.
- `stepper`: Move the syringe one revolution up and one down using the configured STEP/DIR pins and limit switches.
Use `--loop` to repeat the selected tests automatically, and `--interval <seconds>` (defaults to 5 s) to control the pause between iterations. See `hardware_test_commands.txt` for ready-made command lines that cover the common combinations.

## Arduino TFT Dashboard
- `arduino/tft_dashboard/tft_dashboard.ino` drives the 3.5″ MCUFRIEND TFT on an Arduino Uno/Mega with resistive touch.
- Displays three pages (environment, reservoir, system) with mock JSON data. A Bluetooth HC-05/HC-06 module on pins 10/11 marks the link as OK on the TFT header (`BT OK`) whenever it receives a line of text from the Pi; real JSON streaming will replace the static payload later.
- On-screen touch buttons (Prev / Next) replace physical switches. Telemetry refreshes automatically every few seconds, so no manual refresh button is needed. Adjust the `XP/YP/XM/YM` pin defines and `map()` ranges if your shield uses different wiring.
- Requires the `MCUFRIEND_kbv`, `Adafruit_GFX`, `TouchScreen`, and `ArduinoJson` libraries.

## Sensor Test Scripts
- `sensor_tests/test_ads_sensor.py` / `sensor_tests/test_ads_all_channels.py`: standalone ADS1115 voltage readers (configure the channel/address inside the script).
- `sensor_tests/ds18b20_test.py`: quick DS18B20 reader using the `/sys/bus/w1/devices` interface (enable 1-Wire, then `python3 sensor_tests/ds18b20_test.py`).
- `sensor_tests/dht22_test.py`: simple DHT22 loop using `adafruit-circuitpython-dht` (`pip install adafruit-circuitpython-dht RPi.GPIO`, then `python3 sensor_tests/dht22_test.py`).
- `sensor_tests/pcf8574_relay_test.py`: sequentially toggles each relay on the PCF8574 expander for verification (`pip install adafruit-circuitpython-pcf8574`, then `python3 sensor_tests/pcf8574_relay_test.py`).
- `sensor_tests/system_step1_relay7.py`: first full-system step, energising only relay P7 on the PCF8574 for 5 seconds to verify wiring and default OFF states.
- `sensor_tests/system_step2_peltiers_relay4.py`: second full-system step, running peltiers on PCA9685 channels 0 & 1 and turning on relay P4, keeping relay P7 ON from step 1.
- `sensor_tests/system_step3_servos_relay6.py`: third full-system step, moving servos from 0° to 90° and turning on relay P5 and relay P6, keeping all previous outputs ON.
- `sensor_tests/system_step4_relay4_relay7.py`: fourth full-system step, ensuring relay P4 + relay P7 are ON, keeping all previous outputs ON.
- `sensor_tests/system_step5_relay3.py`: fifth and final full-system step, turning on relay P3, keeping all previous outputs ON.
- `sensor_tests/system_full_sequence.py`: combined script that runs all 5 steps sequentially in a single execution with 5-second delays between each step (recommended for full system testing).
- `sensor_tests/servo_pwm_test.py`: demonstrates servo control on GPIO20 using pigpio (`sudo apt install pigpio`, `pip install pigpio`, start `pigpiod`, then `python3 sensor_tests/servo_pwm_test.py`).
- `sensor_tests/servo_driver_test.py`: exercises the PCA9685 servo/PWM board for dual servos + dual peltiers (`pip install adafruit-circuitpython-pca9685`, then `python3 sensor_tests/servo_driver_test.py`).
- `sensor_tests/bt_link_test.py`: sanity-checks the Bluetooth serial link to the Arduino TFT using `pyserial` (bind HC-05/HC-06 to `/dev/rfcomm0`, then `python3 sensor_tests/bt_link_test.py`).
- `sensor_tests/VIRTUAL_ENV_SETUP.md`: step-by-step virtual environment guide for running sensor tests on the Pi.

## Troubleshooting
- **SyntaxError mentioning `from __future__ import annotations` inside `plant_controller/utils/datatypes.py`**: This stemmed from a duplicated block of dataclass definitions that placed a second `from __future__` import mid-file. Update to the latest code so the file only defines each dataclass once, with the import correctly at the top.

## Configuration
- `loop_hz`: main loop frequency.
- `ble`: port, baudrate, enable flag.
- `sensors`: pin selections and ADS channel mapping.
- `controllers`: thresholds, PID gains, schedule info, enable toggles.
- `relays`, `servos`, `pwm`, `syringe`: hardware pinouts.

All new features or behavior changes must be reflected both here and in the `README.md`.

