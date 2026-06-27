from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNAVAILABLE
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [
        BASIPSensor(coordinator, "sip_status", "SIP Status"),
        BASIPSensor(coordinator, "mac", "MAC Address"),
        BASIPSensor(coordinator, "device_info", "Device Info"),
        BASIPSensor(coordinator, "time", "Device Time"),
        BASIPSensor(coordinator, "mode", "Mode"),
    ]
    async_add_entities(sensors)

class BASIPSensor(SensorEntity):
    def __init__(self, coordinator, sensor_type, name):
        self.coordinator = coordinator
        self._sensor_type = sensor_type
        self._attr_name = f"BAS-IP {name}"
        self._attr_unique_id = f"{coordinator.host}_{sensor_type}"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return STATE_UNAVAILABLE
            
        value = data.get(self._sensor_type)
        if isinstance(value, dict):
            return str(value.get("status", "unknown"))
        return str(value)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return data.get(self._sensor_type, {})
