"""Mixergy Local - Sensors."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import MixergyLocalCoordinator

@dataclass
class MixergyLocalSensorDescription(SensorEntityDescription):
    value_fn: Any = None

SENSOR_DESCRIPTIONS = (
    MixergyLocalSensorDescription(key="charge", name="Tank Charge", native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("charge"), icon="mdi:water-boiler"),
    MixergyLocalSensorDescription(key="heat_source", name="Heat Source", value_fn=lambda d: d.get("state", {}).get("heat_source"), icon="mdi:heat-wave"),
    MixergyLocalSensorDescription(key="system_state", name="System State", value_fn=lambda d: d.get("state", {}).get("system"), icon="mdi:power"),
    MixergyLocalSensorDescription(key="current_heat_source", name="Current Heat Source", value_fn=lambda d: d.get("state", {}).get("current", {}).get("heat_source"), icon="mdi:fire"),
    MixergyLocalSensorDescription(key="immersion", name="Immersion State", value_fn=lambda d: d.get("state", {}).get("current", {}).get("immersion"), icon="mdi:lightning-bolt"),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(MixergyLocalSensor(coordinator, desc, entry) for desc in SENSOR_DESCRIPTIONS)

class MixergyLocalSensor(CoordinatorEntity, SensorEntity):
    entity_description: MixergyLocalSensorDescription

    def __init__(self, coordinator, description, entry):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name=f"Mixergy Tank ({coordinator.host})", manufacturer="Mixergy", model="Smart Hot Water Tank", configuration_url=f"http://{coordinator.host}")

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
