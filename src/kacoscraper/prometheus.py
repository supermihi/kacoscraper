from collections.abc import Iterable
from dataclasses import dataclass
from datetime import timedelta
import logging
import time
from typing import Final, Literal

from prometheus_client import Gauge
import prometheus_client

from kacoscraper.livedata import InverterDataProvider
from kacoscraper.model import InverterDetails


@dataclass(slots=True, frozen=True)
class MultiValueSpec:
    label: str
    index: int


@dataclass(slots=True, frozen=True)
class MetricSpec:
    name: str
    description: str
    type: Literal["enum", "gauge"]
    multi: MultiValueSpec | None = None


operating_time_spec = MetricSpec(
    "operating_time_seconds", "time since restart (or installation?)", type="gauge"
)
ac_power_spec = MetricSpec(
    "AC_power_total",
    description="Current AC power (in Watts)",
    type="gauge",
)
dc_current_specs = [
    MetricSpec(
        "DC_current",
        description="DC current (in Amperes) per input",
        type="gauge",
        multi=MultiValueSpec("input", i),
    )
    for i in range(1, 4)
]
dc_voltage_specs = [
    MetricSpec(
        "DC_voltage",
        description="DC voltage (in Volts) per input",
        type="gauge",
        multi=MultiValueSpec("input", i),
    )
    for i in range(1, 4)
]
ac_voltage_specs = [
    MetricSpec(
        "AC_voltage",
        description="AC voltage (in Volts) per phase",
        type="gauge",
        multi=MultiValueSpec("phase", i),
    )
    for i in range(1, 4)
]
energy_total_spec = MetricSpec(
    "AC_energy_total",
    description="total AC energy since installation (in kWh)",
    type="gauge",
)

temperature_spec = MetricSpec(
    "temperature", description="device temperature (in °C)", type="gauge"
)
power_factor_spec = MetricSpec("power_factor", description="power factor", type="gauge")


def get_metric_values(
    details: InverterDetails,
) -> Iterable[tuple[MetricSpec, float | int]]:
    yield operating_time_spec, details.operating_time.total_seconds()
    yield ac_power_spec, details.ac_power_watts
    for dc_current_spec, dc_current in zip(dc_current_specs, details.current_dc_amps):
        yield dc_current_spec, dc_current
    for dc_voltage_spec, dc_voltage in zip(dc_voltage_specs, details.voltage_dc_volts):
        yield dc_voltage_spec, dc_voltage
    for ac_voltage_spec, ac_voltage in zip(ac_voltage_specs, details.voltage_ac_volts):
        yield ac_voltage_spec, ac_voltage
    yield energy_total_spec, details.energy_total_kwh
    yield temperature_spec, details.temperature_celsius
    yield power_factor_spec, details.power_factor


DEVICE_NAME_LABEL: Final[str] = "name"
SERIAL_LABEL: Final[str] = "serial"


def create_metric(spec: MetricSpec):
    label_names = [DEVICE_NAME_LABEL, SERIAL_LABEL]
    if spec.multi is not None:
        label_names.append(spec.multi.label)
    return Gauge(spec.name, spec.description, label_names)


class InverterMetrics:
    def __init__(self, inverters: list[InverterDataProvider]):
        self.metrics: dict[str, Gauge] = {}
        self.inverters = inverters

    def poll(self):
        for inverter in self.inverters:
            self.update_inverter(inverter)

    def get_metric(self, spec: MetricSpec, name: str, serial: str) -> Gauge:
        if spec.name in self.metrics:
            metric = self.metrics[spec.name]
        else:
            metric = create_metric(spec)
            self.metrics[spec.name] = metric
        labels = [name, serial]
        if spec.multi:
            labels.append(str(spec.multi.index))
        return metric.labels(*labels)

    def update_inverter(self, inverter: InverterDataProvider) -> None:
        results = inverter.get_details()
        for metric_spec, value in get_metric_values(results):
            metric = self.get_metric(metric_spec, inverter.name, results.serial)
            metric.set(value)


def poll(
    inverters: list[InverterDataProvider],
    port: int,
    poll_interval: timedelta = timedelta(seconds=5),
):
    metrics = InverterMetrics(inverters)

    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
    logging.info(f"starting Prometheus exporter on port {port}")
    prometheus_client.start_http_server(port)
    logging.info(f"polling every {poll_interval.total_seconds()}s ...")
    while True:
        logging.debug("polling ...")
        try:
            metrics.poll()
        except Exception:
            logging.exception("Exception polling data")
        time.sleep(poll_interval.total_seconds())
