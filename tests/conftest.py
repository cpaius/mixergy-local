"""Shared fixtures for Mixergy Local tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mixergy_local.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"

REPO_ROOT = Path(__file__).parent.parent
TEST_HOST = "192.168.1.100"

MOCK_STATUS = {
    "charge": 75,
    "state": {
        "heat_source": "Indirect",
        "system": "On",
        "current": {
            "heat_source": "Indirect",
            "immersion": "Off",
        },
        "relay": {
            "heat_source": "Indirect",
        },
    },
}

MOCK_MEASUREMENTS = {
    "cp": 2360.0,
    "dp": 0.0,
    "f": 50.1034,
    "soc": 78.7,
    "tt": 55.0,
    "ft": 54.7,
    "bt": 22.0,
    "op": False,
    "v": 243.64,
    "i": 0.0,
    "dro": False,
    "iro": False,
    "po": False,
    "ts": 401,
}


@pytest.fixture
def hass_config_dir() -> str:
    """Point Home Assistant at the repository root for custom component loading."""
    return str(REPO_ROOT)


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mocked config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: TEST_HOST},
        unique_id=f"mixergy_local_{TEST_HOST}",
        title=f"Mixergy Tank ({TEST_HOST})",
    )


def mock_aiohttp_get(response_data: dict | None, status: int = 200) -> MagicMock:
    """Build a mock aiohttp ClientSession context manager."""
    mock_response = AsyncMock()
    mock_response.status = status
    mock_response.json = AsyncMock(return_value=response_data)

    mock_get_context = AsyncMock()
    mock_get_context.__aenter__.return_value = mock_response

    mock_session = MagicMock()
    mock_session.get.return_value = mock_get_context

    mock_session_context = AsyncMock()
    mock_session_context.__aenter__.return_value = mock_session

    return mock_session_context
