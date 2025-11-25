from __future__ import annotations

from typing import Dict

from plant_controller.utils.datatypes import SystemState

from .ads_reader import ADSReader
from .dht22_service import DHT22Service
from .ds18b20_service import DS18B20Service


class SensorHub:
    def __init__(self, config: dict) -> None:
        sensors = config.get("sensors", {})
        self.dht = DHT22Service(sensors.get("dht22_gpio", 17))
        self.ds18b20 = DS18B20Service(sensors.get("ds18b20_bus"))
        ads_configs: Dict[int, Dict[str, int]] = {}
        for adc in sensors.get("ads1115", []):
            ads_configs[adc["address"]] = adc.get("channels", {})
        self.ads = ADSReader(ads_configs)

    def refresh(self, state: SystemState) -> None:
        air_temp, humidity = self.dht.read()
        if air_temp is not None:
            state.environment.air_temp_c = air_temp
        if humidity is not None:
            state.environment.humidity = humidity
        water_temp = self.ds18b20.read()
        if water_temp is not None:
            state.reservoir.water_temp_c = water_temp
        soil_v = self.ads.read_voltage("soil_moisture")
        if soil_v is not None:
            state.soil.moisture = min(max(soil_v / 3.3, 0.0), 1.0)
        ph_v = self.ads.read_voltage("ph")
        if ph_v is not None:
            state.reservoir.ph = ph_v * 3.0
        tds_v = self.ads.read_voltage("tds")
        if tds_v is not None:
            state.reservoir.tds = tds_v * 2.0
            state.reservoir.ec = state.reservoir.tds
        co2_v = self.ads.read_voltage("co2")
        if co2_v is not None:
            state.environment.co2_ppm = 200 * co2_v

