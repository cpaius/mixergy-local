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

@dataclass
class MixergyLocalBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Any = None

BINARY_SENSOR_DESCRIPTIONS = (
    MixergyLocalBinarySensorDescription(key="immersion_active", name="Immersion Active", device_class=BinarySensorDeviceClass.HEAT, value_fn=lambda d: d.get("state", {}).get("current", {}).get("immersion", "Off") != "Off", icon="mdi:lightning-bolt"),
    MixergyLocalBinarySensorDescription(key="indirect_active", name="Indirect Heating Active", device_class=BinarySensorDeviceClass.HEAT, value_fn=lambda d: d.get("state", {}).get("relay", {}).get("heat_source", "Off") == "Indirect", icon="mdi:radiator"),
)

MEASUREMENT_BINARY_SENSOR_DESCRIPTIONS = (
    MixergyLocalBinarySensorDescription(key="operating", name="Operating", device_class=BinarySensorDeviceClass.RUNNING, value_fn=lambda d: bool(d.get("op", False)), icon="mdi:water-boiler"),
    MixergyLocalBinarySensorDescription(key="direct_relay", name="Direct Relay", device_class=BinarySensorDeviceClass.POWER, value_fn=lambda d: bool(d.get("dro", False)), icon="mdi:electric-switch"),
    MixergyLocalBinarySensorDescription(key="indirect_relay", name="Indirect Relay", device_class=BinarySensorDeviceClass.HEAT, value_fn=lambda d: bool(d.get("iro", False)), icon="mdi:radiator"),
    MixergyLocalBinarySensorDescription(key="pump", name="Pump", device_class=BinarySensorDeviceClass.RUNNING, value_fn=lambda d: bool(d.get("po", False)), icon="mdi:pump"),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    from .__init__ import MixergyEntryData
    entry_data: MixergyEntryData = hass.data[DOMAIN][entry.entry_id]
    entities: list = [MixergyLocalBinarySensor(entry_data.coordinator, desc, entry) for desc in BINARY_SENSOR_DESCRIPTIONS]
    entities += [MixergyLocalBinarySensor(entry_data.measurements, desc, entry) for desc in MEASUREMENT_BINARY_SENSOR_DESCRIPTIONS]
    async_add_entities(entities)

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
