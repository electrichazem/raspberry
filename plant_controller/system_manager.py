from __future__ import annotations

import time
from typing import Dict, List

from plant_controller.comms.ble_gateway import BLEGateway
from plant_controller.controllers.air_pid import AirPIDController
from plant_controller.controllers.co2 import CO2Controller
from plant_controller.controllers.humidity import HumidityController
from plant_controller.controllers.lighting import LightingController
from plant_controller.controllers.nutrient import NutrientController
from plant_controller.controllers.soil import SoilController
from plant_controller.controllers.water_pid import WaterPIDController
from plant_controller.hardware.pwm_channel import PWMChannel
from plant_controller.hardware.relay_manager import RelayManager
from plant_controller.hardware.servo_driver import ServoDriver
from plant_controller.hardware.syringe_driver import SyringeConfig, SyringeDriver
from plant_controller.sensors.hub import SensorHub
from plant_controller.utils.config import load_config
from plant_controller.utils.datatypes import SystemState


class NullServos:
    def set_angle(self, *_args, **_kwargs) -> None:
        return


class NullPWM:
    def set_output(self, *_args, **_kwargs) -> None:
        return

    def stop(self) -> None:
        return


class SystemManager:
    def __init__(self, config_path: str = "config.yaml") -> None:
        self.config = load_config(config_path)
        self.state = SystemState()
        self.sensor_hub = SensorHub(self.config)
        relays_cfg = self.config.get("relays", {})
        self.relays = RelayManager(
            expander_pins=relays_cfg.get("expander", {}),
            direct_pins=relays_cfg.get("direct", {}),
            expander_address=relays_cfg.get("expander_address"),
        )
        servo_cfg = self.config.get("servos", {})
        self.servos = ServoDriver(servo_cfg) if servo_cfg else NullServos()
        pwm_cfg = self.config.get("pwm", {})
        air_cfg = pwm_cfg.get("air_peltier")
        water_cfg = pwm_cfg.get("water_peltier")
        self.air_pwm = PWMChannel(**air_cfg) if air_cfg else NullPWM()
        self.water_pwm = PWMChannel(**water_cfg) if water_cfg else NullPWM()
        syringe_cfg_data = self.config.get("syringe")
        if not syringe_cfg_data:
            raise ValueError("Syringe configuration missing in config.yaml")
        syringe_cfg = SyringeConfig(**syringe_cfg_data)
        self.syringe = SyringeDriver(syringe_cfg)
        controllers_cfg = self.config.get("controllers", {})
        self.controllers = self._build_controllers(controllers_cfg)
        ble_cfg = self.config.get("ble", {})
        self.ble = BLEGateway(
            ble_cfg.get("port", "/dev/ttyS0"),
            ble_cfg.get("baudrate", 115200),
            ble_cfg.get("enabled", True),
        )

    def _build_controllers(self, cfg: dict) -> List:
        controllers = []
        controllers.append(HumidityController(self.relays, cfg.get("humidity", {})))
        controllers.append(
            CO2Controller(self.relays, self.servos, cfg.get("co2", {}), (0.0, 0.0), 90.0)
        )
        controllers.append(LightingController(self.relays, cfg.get("lighting", {})))
        controllers.append(AirPIDController(self.air_pwm, cfg.get("air_pid", {})))
        controllers.append(WaterPIDController(self.water_pwm, self.relays, cfg.get("water_pid", {})))
        controllers.append(NutrientController(self.relays, self.syringe, cfg.get("nutrient", {})))
        controllers.append(SoilController(self.relays, self.syringe, cfg.get("soil", {})))
        return controllers

    def _handle_command(self, command: Dict) -> None:
        target = command.get("target")
        if target == "relay":
            name = command.get("name")
            state = bool(command.get("state", False))
            self.relays.set_state(name, state)
        elif target == "controller":
            name = command.get("name")
            enabled = bool(command.get("enabled", True))
            for ctrl in self.controllers:
                if ctrl.name == name:
                    ctrl.enabled = enabled
        elif target == "dose":
            channel = command.get("channel", "nutrient_a")
            amount = float(command.get("amount", 1.0))
            if channel in ("nutrient_a", "nutrient_b"):
                self.relays.set_state(channel, True)
                self.syringe.dispense_ml(amount, direction_up=False)
                self.relays.set_state(channel, False)

    def run_once(self) -> None:
        self.sensor_hub.refresh(self.state)
        self.state.timestamp = time.time()
        for controller in self.controllers:
            controller.update(self.state)
        payload = {
            "timestamp": self.state.timestamp,
            "environment": self.state.environment.__dict__,
            "reservoir": self.state.reservoir.__dict__,
            "soil": self.state.soil.__dict__,
            "relays": self.relays.all_states(),
        }
        self.ble.publish_state(payload)
        command = self.ble.poll_command()
        if command:
            self._handle_command(command)

    def run_forever(self) -> None:
        loop_hz = self.config.get("loop_hz", 1)
        delay = 1.0 / max(loop_hz, 1)
        while True:
            start = time.time()
            self.run_once()
            elapsed = time.time() - start
            if elapsed < delay:
                time.sleep(delay - elapsed)

