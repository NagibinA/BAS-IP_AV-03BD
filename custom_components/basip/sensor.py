from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.entity import DeviceInfo
import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
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

class BASIPSensor(SensorEntity):
    def __init__(self, coordinator, sensor_type, name, icon=None):
        self.coordinator = coordinator
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
        data = self.coordinator.data
        if not data:
            return STATE_UNAVAILABLE
            
        value = data.get(self._sensor_type)
        if value is None:
            return STATE_UNKNOWN
            
        if isinstance(value, dict):
            # Извлекаем статус из словаря
            status = value.get("status", value.get("state", "unknown"))
            return str(status)
        return str(value)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        value = data.get(self._sensor_type, {})
        if isinstance(value, dict):
            return value
        return {"value": value}

class BASIPTokenSensor(SensorEntity):
    """Сенсор для отображения статуса токена"""
    
    def __init__(self, coordinator, sensor_type, name, icon=None):
        self.coordinator = coordinator
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
        if not self.coordinator.token:
            return "expired"
        return "valid"

    @property
    def extra_state_attributes(self):
        return {
            "token_preview": self.coordinator.token[:20] + "..." if self.coordinator.token else None,
            "expiry": str(self.coordinator.token_expiry) if self.coordinator.token_expiry else None,
            "connected": self.coordinator.connected,
        }
