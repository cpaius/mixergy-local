"""Tests for the Mixergy Local coordinator."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
import pytest

from custom_components.mixergy_local.coordinator import MixergyLocalCoordinator
from tests.conftest import MOCK_STATUS, TEST_HOST, mock_aiohttp_get


async def test_coordinator_update_success(hass: HomeAssistant) -> None:
    """Test coordinator fetches status data."""
    coordinator = MixergyLocalCoordinator(hass, TEST_HOST)

    with patch(
        "custom_components.mixergy_local.coordinator.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(MOCK_STATUS),
    ):
        data = await coordinator._async_update_data()

    assert data == MOCK_STATUS


async def test_coordinator_update_bad_status(hass: HomeAssistant) -> None:
    """Test coordinator raises when the API returns a non-200 status."""
    coordinator = MixergyLocalCoordinator(hass, TEST_HOST)

    with patch(
        "custom_components.mixergy_local.coordinator.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(None, status=500),
    ):
        with pytest.raises(UpdateFailed, match="Bad status 500"):
            await coordinator._async_update_data()
