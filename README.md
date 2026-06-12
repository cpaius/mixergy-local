# Mixergy Local

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Validate with hassfest](https://github.com/cpaius/mixergy-local/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/cpaius/mixergy-local/actions/workflows/hassfest.yaml)
[![Validate with HACS](https://github.com/cpaius/mixergy-local/actions/workflows/hacs.yml/badge.svg)](https://github.com/cpaius/mixergy-local/actions/workflows/hacs.yml)
[![Run tests](https://github.com/cpaius/mixergy-local/actions/workflows/pytest.yml/badge.svg)](https://github.com/cpaius/mixergy-local/actions/workflows/pytest.yml)

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

| Entity | Description |
| --- | --- |
| `sensor.*_tank_charge` | Tank charge level (%) |
| `sensor.*_heat_source` | Configured heat source |
| `sensor.*_system_state` | System on/off state |
| `sensor.*_current_heat_source` | Active heat source |
| `sensor.*_immersion` | Immersion heater state |
| `binary_sensor.*_immersion_active` | Whether immersion is heating |
| `binary_sensor.*_indirect_active` | Whether indirect heating is active |
| `binary_sensor.*_system_on` | Whether the system is on |

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt
pytest
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
