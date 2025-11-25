from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class EnvironmentReading:
    air_temp_c: Optional[float] = None
    humidity: Optional[float] = None
    co2_ppm: Optional[float] = None


@dataclass
class ReservoirReading:
    water_temp_c: Optional[float] = None
    ph: Optional[float] = None
    ec: Optional[float] = None
    tds: Optional[float] = None


@dataclass
class SoilReading:
    moisture: Optional[float] = None


@dataclass
class NutrientState:
    last_dose_ml: float = 0.0
    pending_recipe: Optional[str] = None


@dataclass
class ActuatorState:
    relays: Dict[str, bool] = field(default_factory=dict)
    pwm_outputs: Dict[str, float] = field(default_factory=dict)
    servos: Dict[str, float] = field(default_factory=dict)


@dataclass
class SystemState:
    environment: EnvironmentReading = field(default_factory=EnvironmentReading)
    reservoir: ReservoirReading = field(default_factory=ReservoirReading)
    soil: SoilReading = field(default_factory=SoilReading)
    nutrients: NutrientState = field(default_factory=NutrientState)
    actuators: ActuatorState = field(default_factory=ActuatorState)
    timestamp: float = 0.0


@dataclass
class ManualCommand:
    target: str
    action: str
    value: Optional[float] = None
