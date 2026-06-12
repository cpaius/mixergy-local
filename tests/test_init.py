"""Tests for Mixergy Local sensors and binary sensors."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.conftest import MOCK_MEASUREMENTS, MOCK_STATUS, TEST_HOST, mock_aiohttp_get


def _patch_stream(measurements: dict):
    """Patch the measurements coordinator stream so it immediately sets data."""

    async def _fake_start_stream(self):
        self.async_set_updated_data(measurements)

    return patch(
        "custom_components.mixergy_local.coordinator.MixergyMeasurementsCoordinator.async_start_stream",
        _fake_start_stream,
    )


async def test_setup_creates_entities(
    hass: HomeAssistant, enable_custom_integrations, mock_config_entry
) -> None:
    """Test integration setup creates expected entities."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.mixergy_local.coordinator.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(MOCK_STATUS),
    ), _patch_stream(MOCK_MEASUREMENTS):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    registry = er.async_get(hass)

    charge_entity = registry.async_get_entity_id(
        "sensor", "mixergy_local", f"{mock_config_entry.entry_id}_charge"
    )
    assert charge_entity is not None
    assert hass.states.get(charge_entity).state == "75"

    immersion_entity = registry.async_get_entity_id(
        "binary_sensor",
        "mixergy_local",
        f"{mock_config_entry.entry_id}_immersion_active",
    )
    assert immersion_entity is not None
    assert hass.states.get(immersion_entity).state == "off"

    top_temp_entity = registry.async_get_entity_id(
        "sensor", "mixergy_local", f"{mock_config_entry.entry_id}_top_temp"
    )
    assert top_temp_entity is not None
    assert hass.states.get(top_temp_entity).state == "55.0"

    pump_entity = registry.async_get_entity_id(
        "binary_sensor", "mixergy_local", f"{mock_config_entry.entry_id}_pump"
    )
    assert pump_entity is not None
    assert hass.states.get(pump_entity).state == "off"


async def test_unload_removes_entities(
    hass: HomeAssistant, enable_custom_integrations, mock_config_entry
) -> None:
    """Test unloading the integration removes entity states."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.mixergy_local.coordinator.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(MOCK_STATUS),
    ), _patch_stream(MOCK_MEASUREMENTS):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    registry = er.async_get(hass)
    charge_entity = registry.async_get_entity_id(
        "sensor", "mixergy_local", f"{mock_config_entry.entry_id}_charge"
    )
    assert hass.states.get(charge_entity) is not None

    with patch(
        "custom_components.mixergy_local.coordinator.MixergyMeasurementsCoordinator.async_stop_stream",
        new_callable=AsyncMock,
    ):
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert hass.states.get(charge_entity).state == "unavailable"
