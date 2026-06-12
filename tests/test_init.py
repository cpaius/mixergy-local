"""Tests for Mixergy Local sensors and binary sensors."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.conftest import MOCK_STATUS, TEST_HOST, mock_aiohttp_get


async def test_setup_creates_entities(
    hass: HomeAssistant, enable_custom_integrations, mock_config_entry
) -> None:
    """Test integration setup creates expected entities."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.mixergy_local.coordinator.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(MOCK_STATUS),
    ):
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

    system_on_entity = registry.async_get_entity_id(
        "binary_sensor",
        "mixergy_local",
        f"{mock_config_entry.entry_id}_system_on",
    )
    assert system_on_entity is not None
    assert hass.states.get(system_on_entity).state == "on"


async def test_unload_removes_entities(
    hass: HomeAssistant, enable_custom_integrations, mock_config_entry
) -> None:
    """Test unloading the integration removes entity states."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.mixergy_local.coordinator.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(MOCK_STATUS),
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    registry = er.async_get(hass)
    charge_entity = registry.async_get_entity_id(
        "sensor", "mixergy_local", f"{mock_config_entry.entry_id}_charge"
    )
    assert hass.states.get(charge_entity) is not None

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert hass.states.get(charge_entity).state == "unavailable"
