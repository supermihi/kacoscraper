from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class InverterDetails:
    serial: str
    operating_time: timedelta
    ac_power_watts: float
    voltage_ac_volts: list[float]
    voltage_dc_volts: list[float]
    current_dc_amps: list[float]
    energy_day_kwh: float
    energy_total_kwh: float
    power_factor: float
    temperature_celsius: float
    error_code: int
    time: datetime

    @staticmethod
    def from_json(serial: str, data: dict[str, Any]) -> InverterDetails:
        return InverterDetails(
            serial=serial,
            operating_time=timedelta(hours=data["hto"]),
            ac_power_watts=data["pac"],
            voltage_ac_volts=[v / 10 for v in data["vac"]],
            voltage_dc_volts=[v / 10 for v in data["vpv"]],
            current_dc_amps=[a / 100 for a in data["ipv"]],
            energy_day_kwh=data["etd"] / 10,
            energy_total_kwh=data["eto"] / 10,
            power_factor=data["pf"] / 100,
            temperature_celsius=data["tmp"] / 10,
            error_code=data["err"],
            time=datetime.strptime(data["tim"], "%Y%m%d%H%M%S"),
        )
