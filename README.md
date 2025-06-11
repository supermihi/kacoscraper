# kacoscraper – simple access to solar inverter live data

Tiny Python tool to query live data (power, voltage etc.) of Kaco NX3
(and probably other similar decives) solar inverters.

Includes an optional [Prometheus](https://prometheus.io/docs/instrumenting/exporters/) exporter.

## Installation
The package is not on _PyPI_ yet. Clone repository and install [`uv`](https://docs.astral.sh/uv/). Then:
```
uv sync
# or: with prometheus
uv sync --extra prometheus
# or: with development dependencies
uv sync --dev
```
## Run
Print current values to stdout:
```
uv run kacoscraper --host kaco.example.com live 
```
Run Prometheus exporter:
```
uv run kacoscraper --host kaco.example.com serve --port 8007
```
## How it works
This tool queries the inverter using the (undocumented) simple HTTP/JSON API used by their "KACO Tool" installation app.

This supports only a limited set of values:
```
{'ac_power_watts': 16854,
 'current_dc_amps': [12.67, 14.94],
 'energy_day_kwh': 67.9,
 'energy_total_kwh': 2242.1,
 'error_code': 0,
 'operating_time': datetime.timedelta(days=12, seconds=72000),
 'power_factor': 1.0,
 'serial': '20.0NX312078172',
 'temperature_celsius': 46.5,
 'time': datetime.datetime(2025, 6, 28, 13, 23, 46),
 'voltage_ac_volts': [236.2, 235.6, 231.8],
 'voltage_dc_volts': [607.1, 659.5]}
```