"""Mixergy Local - Sensors."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfFrequency, UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import MixergyLocalCoordinator, MixergyMeasurementsCoordinator

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

MEASUREMENT_SENSOR_DESCRIPTIONS = (
    MixergyLocalSensorDescription(key="immersion_power", name="Immersion Power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("dp"), icon="mdi:heating-coil"),
    MixergyLocalSensorDescription(key="frequency", name="Grid Frequency", native_unit_of_measurement=UnitOfFrequency.HERTZ, device_class=SensorDeviceClass.FREQUENCY, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("f"), icon="mdi:sine-wave"),
    MixergyLocalSensorDescription(key="top_temp", name="Top Temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("tt"), icon="mdi:thermometer"),
    MixergyLocalSensorDescription(key="flow_temp", name="Flow Temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("ft"), icon="mdi:thermometer"),
    MixergyLocalSensorDescription(key="bottom_temp", name="Bottom Temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("bt"), icon="mdi:thermometer-low"),
    MixergyLocalSensorDescription(key="voltage", name="Voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("v"), icon="mdi:flash"),
    MixergyLocalSensorDescription(key="immersion_current", name="Immersion Current", native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, value_fn=lambda d: d.get("i"), icon="mdi:current-ac"),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    from .__init__ import MixergyEntryData
    entry_data: MixergyEntryData = hass.data[DOMAIN][entry.entry_id]
    entities: list = [MixergyLocalSensor(entry_data.coordinator, desc, entry) for desc in SENSOR_DESCRIPTIONS]
    entities += [MixergyLocalSensor(entry_data.measurements, desc, entry) for desc in MEASUREMENT_SENSOR_DESCRIPTIONS]
    async_add_entities(entities)

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
