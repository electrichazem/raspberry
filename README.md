# Plant Controller

Python control stack for the Raspberry Pi 4 grow system. It manages humidity, CO₂, lighting, air and water temperature, nutrient dosing, and soil moisture while exposing telemetry and manual overrides through a BLE/UART bridge to an Arduino console.

## Features
- Modular drivers for relays (PCF8574 + GPIO), PWM peltiers, vent servos, and syringe pump
- Sensor hub that polls DHT22, DS18B20, and multiple ADS1115 analog channels (soil moisture, pH, TDS/EC, MG811 CO₂)
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
- `README.md`, `DOCUMENTATION.md` – keep both updated with behavior changes

