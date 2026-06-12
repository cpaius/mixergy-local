"""Mixergy Local - Binary Sensors."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import MixergyLocalCoordinator

@dataclass
class MixergyLocalBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Any = None

BINARY_SENSOR_DESCRIPTIONS = (
    MixergyLocalBinarySensorDescription(key="immersion_active", name="Immersion Active", device_class=BinarySensorDeviceClass.HEAT, value_fn=lambda d: d.get("state", {}).get("current", {}).get("immersion", "Off") != "Off", icon="mdi:lightning-bolt"),
    MixergyLocalBinarySensorDescription(key="indirect_active", name="Indirect Heating Active", device_class=BinarySensorDeviceClass.HEAT, value_fn=lambda d: d.get("state", {}).get("relay", {}).get("heat_source", "Off") == "Indirect", icon="mdi:radiator"),
    MixergyLocalBinarySensorDescription(key="system_on", name="System On", device_class=BinarySensorDeviceClass.POWER, value_fn=lambda d: d.get("state", {}).get("system", "Off") == "On", icon="mdi:power"),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MixergyLocalBinarySensor(coordinator, desc, entry) for desc in BINARY_SENSOR_DESCRIPTIONS)

class MixergyLocalBinarySensor(CoordinatorEntity, BinarySensorEntity):
    entity_description: MixergyLocalBinarySensorDescription

    def __init__(self, coordinator, description, entry):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name=f"Mixergy Tank ({coordinator.host})", manufacturer="Mixergy", model="Smart Hot Water Tank", configuration_url=f"http://{coordinator.host}")

    @property
    def is_on(self):
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
