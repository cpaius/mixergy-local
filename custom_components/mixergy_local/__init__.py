"""The Mixergy Local integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import MixergyLocalCoordinator, MixergyMeasurementsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


@dataclass
class MixergyEntryData:
    coordinator: MixergyLocalCoordinator
    measurements: MixergyMeasurementsCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mixergy Local from a config entry."""
    host = entry.data[CONF_HOST]

    coordinator = MixergyLocalCoordinator(hass, host)
    await coordinator.async_config_entry_first_refresh()

    measurements = MixergyMeasurementsCoordinator(hass, host)
    await measurements.async_start_stream()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = MixergyEntryData(
        coordinator=coordinator,
        measurements=measurements,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    entry_data: MixergyEntryData = hass.data[DOMAIN][entry.entry_id]
    await entry_data.measurements.async_stop_stream()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
