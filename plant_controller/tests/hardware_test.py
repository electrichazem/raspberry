from __future__ import annotations

import argparse
import time
from typing import Callable, Dict, Iterable, List

from plant_controller.hardware.pwm_channel import PWMChannel
from plant_controller.hardware.relay_manager import RelayManager
from plant_controller.hardware.servo_driver import ServoDriver
from plant_controller.hardware.syringe_driver import SyringeConfig, SyringeDriver
from plant_controller.sensors.hub import SensorHub
from plant_controller.utils.config import load_config
from plant_controller.utils.datatypes import SystemState


def build_relay_manager(config: dict) -> RelayManager:
    relay_cfg = config.get("relays", {})
    return RelayManager(
        expander_pins=relay_cfg.get("expander", {}),
        direct_pins=relay_cfg.get("direct", {}),
        expander_address=relay_cfg.get("expander_address"),
    )


def test_sensors(config: dict) -> None:
    print("=== Sensor Test ===")
    hub = SensorHub(config)
    state = SystemState()
    hub.refresh(state)
    print(f"Air temp: {state.environment.air_temp_c} °C")
    print(f"Humidity: {state.environment.humidity} %")
    print(f"CO2: {state.environment.co2_ppm} ppm")
    print(f"Water temp: {state.reservoir.water_temp_c} °C")
    print(f"pH: {state.reservoir.ph}")
    print(f"TDS/EC: {state.reservoir.tds}")
    print(f"Soil moisture: {state.soil.moisture}")


def test_servos(config: dict) -> None:
    print("=== Servo Test ===")
    servo_cfg = config.get("servos", {})
    driver = ServoDriver(servo_cfg)
    for name in servo_cfg.keys():
        print(f"Moving servo {name} +10°")
        driver.set_angle(name, 10.0)
        time.sleep(1.0)
        print(f"Returning servo {name} to 0°")
        driver.set_angle(name, 0.0)
        time.sleep(1.0)
    driver.stop_all()


def _relay_sequence(manager: RelayManager, names: Iterable[str], dwell: float) -> None:
    for name in names:
        print(f"Energizing relay {name}")
        manager.set_state(name, True)
        time.sleep(dwell)
        print(f"De-energizing relay {name}")
        manager.set_state(name, False)
        time.sleep(1.0)


def test_expander_relays(config: dict) -> None:
    print("=== Expander Relay Test ===")
    manager = build_relay_manager(config)
    expander_names: List[str] = list(config.get("relays", {}).get("expander", {}).keys())
    _relay_sequence(manager, expander_names, 5.0)


def test_direct_relays(config: dict) -> None:
    print("=== Direct Relay Test ===")
    manager = build_relay_manager(config)
    direct_names: List[str] = list(config.get("relays", {}).get("direct", {}).keys())
    _relay_sequence(manager, direct_names, 2.0)


def _test_peltier(channel_cfg: dict, label: str) -> None:
    if not channel_cfg:
        print(f"No config for {label}, skipping")
        return
    pwm = PWMChannel(**channel_cfg)
    print(f"{label}: Cooling direction for 3 minutes")
    pwm.set_output(80.0, forward=True)
    for remaining in range(3, 0, -1):
        print(f"  Cooling... {remaining} minute(s) left")
        time.sleep(60)
    print(f"{label}: Heating direction for 3 minutes")
    pwm.set_output(80.0, forward=False)
    for remaining in range(3, 0, -1):
        print(f"  Heating... {remaining} minute(s) left")
        time.sleep(60)
    pwm.set_output(0.0)
    pwm.stop()


def test_peltiers(config: dict) -> None:
    print("=== Peltier Test ===")
    pwm_cfg = config.get("pwm", {})
    _test_peltier(pwm_cfg.get("air_peltier", {}), "Air Peltier")
    _test_peltier(pwm_cfg.get("water_peltier", {}), "Water Peltier")


def test_stepper(config: dict) -> None:
    print("=== Stepper (Syringe) Test ===")
    syringe_cfg = config.get("syringe")
    if not syringe_cfg:
        print("No syringe config found")
        return
    driver = SyringeDriver(SyringeConfig(**syringe_cfg))
    steps_per_rev = syringe_cfg.get("steps_per_ml", 200)
    print("Moving +1 revolution")
    driver.move_steps(steps_per_rev, direction_up=True)
    time.sleep(1.0)
    print("Moving -1 revolution")
    driver.move_steps(steps_per_rev, direction_up=False)


TESTS: Dict[str, Callable[[dict], None]] = {
    "sensors": test_sensors,
    "servos": test_servos,
    "relays_expander": test_expander_relays,
    "relays_direct": test_direct_relays,
    "peltiers": test_peltiers,
    "stepper": test_stepper,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Hardware bring-up helper")
    parser.add_argument(
        "--tests",
        nargs="+",
        choices=TESTS.keys(),
        default=list(TESTS.keys()),
        help="Specific tests to run (defaults to all)",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Repeat the selected tests indefinitely",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds to wait between loops when --loop is set",
    )
    args = parser.parse_args()
    config = load_config(args.config)
    interval = max(args.interval, 0.0)

    def run_selected_tests() -> None:
        for name in args.tests:
            try:
                TESTS[name](config)
            except Exception as exc:  # pragma: no cover
                print(f"Test '{name}' failed: {exc}")

    while True:
        run_selected_tests()
        if not args.loop:
            break
        print(f"Loop complete, sleeping for {interval} second(s)")
        time.sleep(interval)


if __name__ == "__main__":
    main()

