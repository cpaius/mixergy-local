# Mixergy Local

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/cpaius/mixergy-local/actions/workflows/validate.yml/badge.svg)](https://github.com/cpaius/mixergy-local/actions/workflows/validate.yml)

Local Home Assistant integration for [Mixergy](https://mixergy.co.uk/) smart hot water tanks, polling the on-tank controller API directly on your LAN.

## Installation

### HACS (recommended)

1. Open **HACS** → **Integrations** → **⋮** → **Custom repositories**
2. Add `https://github.com/cpaius/mixergy-local` as category **Integration**
3. Search for **Mixergy Local**, install, and restart Home Assistant
4. Add the integration via **Settings** → **Devices & services** → **Add integration**

### Manual

Copy `custom_components/mixergy_local` into your Home Assistant `config/custom_components/` directory and restart.

## Configuration

During setup, enter the IP address of your Mixergy Pi controller (for example `192.168.1.100`). The integration validates connectivity by calling `http://<host>/status`.

## Entities

### Status (polled every 30 s)

| Entity | Description |
| --- | --- |
| `sensor.*_tank_charge` | Tank charge level (%) |
| `sensor.*_heat_source` | Configured heat source |
| `sensor.*_system_state` | System on/off state |
| `sensor.*_current_heat_source` | Active heat source |
| `sensor.*_immersion` | Immersion heater state |
| `binary_sensor.*_immersion_active` | Whether immersion is heating |
| `binary_sensor.*_indirect_active` | Whether indirect heating is active |

### Measurements (real-time stream)

| Entity | Description |
| --- | --- |
| `sensor.*_current_power` | Whole-house power draw (W) |
| `sensor.*_discharge_power` | Discharge power (W) |
| `sensor.*_frequency` | Grid frequency (Hz) |
| `sensor.*_charge_rt` | Tank charge — realtime (%) |
| `sensor.*_top_temp` | Top of tank temperature (°C) |
| `sensor.*_flow_temp` | Flow temperature (°C) |
| `sensor.*_bottom_temp` | Bottom of tank temperature (°C) |
| `sensor.*_voltage` | Supply voltage (V) |
| `sensor.*_current` | Supply current (A) |
| `binary_sensor.*_operating` | Tank actively heating |
| `binary_sensor.*_direct_relay` | Direct relay output state |
| `binary_sensor.*_indirect_relay` | Indirect relay output state |
| `binary_sensor.*_pump` | Pump running |

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt
pytest
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
