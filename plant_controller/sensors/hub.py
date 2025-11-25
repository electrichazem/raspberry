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
        
        # Use averaged readings for better accuracy
        soil_v = self.ads.read_voltage_averaged("soil_moisture")
        if soil_v is not None:
            state.soil.moisture = min(max(soil_v / 3.3, 0.0), 1.0)
        
        ph_v = self.ads.read_voltage_averaged("ph")
        if ph_v is not None:
            # pH formula from old code: -5.70 * voltage + calibration_value
            # Using calibration value 16.83 from old code
            state.reservoir.ph = -5.70 * ph_v + 16.83
        
        tds_v = self.ads.read_voltage_averaged("tds")
        if tds_v is not None:
            # TDS/EC calculation from old code
            temp = state.reservoir.water_temp_c if state.reservoir.water_temp_c is not None else 25.0
            calibration_factor = 0.885  # From old code
            
            # EC calculation: polynomial formula
            ec_value = (133.42 * tds_v**3 - 255.86 * tds_v**2 + 857.39 * tds_v) / 1000.0
            # Temperature compensation to 25°C
            ec25 = ec_value / (1 + 0.02 * (temp - 25.0))
            # TDS = EC * 500
            tds_value = ec25 * 500.0
            # Apply calibration factor
            tds_value *= calibration_factor
            
            state.reservoir.ec = ec25
            state.reservoir.tds = tds_value
        
        co2_v = self.ads.read_voltage_averaged("co2")
        if co2_v is not None:
            state.environment.co2_ppm = 200 * co2_v

