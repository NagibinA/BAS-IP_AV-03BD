"""Sensor platform for BAS-IP."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up BAS-IP sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    sensors = [
        BASIPSensor(coordinator, "sip_status", "SIP Status", "mdi:phone"),
        BASIPSensor(coordinator, "mac", "MAC Address", "mdi:ethernet"),
        BASIPSensor(coordinator, "device_info", "Device Info", "mdi:information"),
        BASIPSensor(coordinator, "time", "Device Time", "mdi:clock"),
        BASIPSensor(coordinator, "mode", "Mode", "mdi:cog"),
        BASIPSensor(coordinator, "lock_type", "Lock Type", "mdi:lock"),
        BASIPTokenSensor(coordinator, "token_status", "Token Status", "mdi:key"),
    ]
    
    async_add_entities(sensors)

class BASIPSensor(CoordinatorEntity, SensorEntity):
    """Representation of a BAS-IP sensor."""

    def __init__(self, coordinator, sensor_type, name, icon=None):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"BAS-IP {name}"
        self._attr_unique_id = f"{coordinator.host}_{sensor_type}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def state(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return STATE_UNAVAILABLE
            
        value = self.coordinator.data.get(self._sensor_type)
        if value is None:
            return STATE_UNKNOWN
            
        if isinstance(value, dict):
            # Извлекаем статус из словаря
            status = value.get("status", value.get("state", "unknown"))
            if isinstance(status, (dict, list)):
                return str(status)
            return str(status) if status is not None else STATE_UNKNOWN
            
        return str(value)

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}
            
        value = self.coordinator.data.get(self._sensor_type)
        if isinstance(value, dict):
            return value
        return {"value": value}

class BASIPTokenSensor(CoordinatorEntity, SensorEntity):
    """Sensor for token status."""

    def __init__(self, coordinator, sensor_type, name, icon=None):
        """Initialize the token sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"BAS-IP {name}"
        self._attr_unique_id = f"{coordinator.host}_{sensor_type}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def state(self):
        """Return token status."""
        if not self.coordinator.token:
            return "expired"
        return "valid"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "connected": self.coordinator.connected,
            "token_preview": self.coordinator.token[:20] + "..." if self.coordinator.token else None,
            "host": self.coordinator.host,
        }
