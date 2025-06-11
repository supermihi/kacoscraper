from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
from typing import Any, cast
import requests

from kacoscraper.model import InverterDetails


@dataclass
class InverterData:
    serial: str
    energy_day_kwh: float
    energy_total_kwh: float
    power_ac_watts: float

    @staticmethod
    def from_json(data: dict[str, Any]) -> InverterData:
        return InverterData(
            serial=data["isn"],
            energy_day_kwh=data["etd"] / 10,
            energy_total_kwh=data["eto"] / 10,
            power_ac_watts=data["pac"],
        )


def call_kaco(host: str, path: str) -> dict[str, Any]:
    response = requests.get(f"http://{host}:8484/{path}")
    return cast(dict[str, Any], response.json())


def get_inverters(host: str) -> list[InverterData]:
    response = call_kaco(host, "getdev.cgi?device=2")
    inverters = response.get("inv", [])
    logging.info(f"found {len(inverters)} inverters")
    return [InverterData.from_json(j) for j in inverters]


def get_inverter_details(host: str, serial: str) -> InverterDetails:
    result = call_kaco(host, f"getdevdata.cgi?device=2&sn={serial}")
    return InverterDetails.from_json(serial, result)


class InverterDataProvider(ABC):
    @abstractmethod
    def get_details(self) -> InverterDetails:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class KacoNX3InverterDataProvider(InverterDataProvider):
    def __init__(self, host: str, serial: str) -> None:
        self.host = host
        self.serial = serial

    def get_details(self):
        return get_inverter_details(self.host, self.serial)

    @property
    def name(self):
        return self.host.split(".")[0]
