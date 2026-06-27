"""Sensor platform for BAS-IP."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, SENSOR_TYPES

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensors = []
    for sensor_key, sensor_info in SENSOR_TYPES.items():
        sensors.append(BASIPSensor(coordinator, sensor_key, sensor_info))
    async_add_entities(sensors)

class BASIPSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sensor_key, sensor_info):
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = f"BAS-IP {sensor_info['name']}"
        self._attr_unique_id = f"{coordinator.host}_{sensor_key}"
        self._attr_icon = sensor_info.get("icon", "mdi:information")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def state(self):
        if not self.coordinator.data:
            return STATE_UNAVAILABLE
        value = self.coordinator.data.get(self._sensor_key)
        if value is None:
            return STATE_UNKNOWN
        if isinstance(value, dict):
            if self._sensor_key == "sip_status":
                return value.get("sip_status", STATE_UNKNOWN)
            elif self._sensor_key == "network_mac":
                return value.get("mac_address", STATE_UNKNOWN)
            elif self._sensor_key == "device_time":
                return value.get("device_timezone", STATE_UNKNOWN)
            elif self._sensor_key == "device_language":
                return value.get("current_language", STATE_UNKNOWN)
            elif self._sensor_key == "device_video":
                return value.get("video_resolution", STATE_UNKNOWN)
            elif self._sensor_key == "device_rtsp":
                return value.get("username", STATE_UNKNOWN)
            elif self._sensor_key == "device_payload":
                return value.get("payload_codec_h264", STATE_UNKNOWN)
            elif self._sensor_key == "device_volume":
                return value.get("volume_level", STATE_UNKNOWN)
            elif self._sensor_key == "device_relay":
                pos = value.get("position_settings", {})
                return pos.get("position", STATE_UNKNOWN)
            elif self._sensor_key == "device_mode":
                return value.get("current_panel_mode", STATE_UNKNOWN)
            elif self._sensor_key == "lock_type":
                locks = value.get("locks", [])
                if locks:
                    return locks[0].get("type", STATE_UNKNOWN)
                return STATE_UNKNOWN
            elif self._sensor_key == "master_card":
                return value.get("master_card", STATE_UNKNOWN)
            elif self._sensor_key == "input_code":
                return value.get("input_code_number", STATE_UNKNOWN)
            elif "lock_timeout" in self._sensor_key:
                return value.get("lock_timeout", STATE_UNKNOWN)
            elif self._sensor_key == "network_ntp":
                return value.get("custom_server", STATE_UNKNOWN)
            elif self._sensor_key == "network_dst":
                return "Enabled" if value.get("is_enabled") else "Disabled"
            elif self._sensor_key == "network_timezone":
                return value.get("current_timezone", STATE_UNKNOWN)
            elif self._sensor_key == "network_management_link":
                return "Enabled" if value.get("link_enable") else "Disabled"
            elif self._sensor_key == "network_management_server":
                return value.get("protocol", STATE_UNKNOWN)
            elif self._sensor_key == "network_management_server_cert":
                return "Valid" if value.get("uploaded") else "Not uploaded"
            elif self._sensor_key == "sip_settings":
                return value.get("user", STATE_UNKNOWN)
            elif self._sensor_key == "sip_enable":
                return "Enabled" if value.get("sip_enable") else "Disabled"
            elif self._sensor_key == "sip_reregister":
                return "Enabled" if value.get("is_reregister") else "Disabled"
            elif self._sensor_key == "call_auto_answer":
                return "Enabled" if value.get("is_enabled") else "Disabled"
            elif self._sensor_key == "rescue_service":
                return "Enabled" if value.get("is_enabled") else "Disabled"
            elif self._sensor_key == "network_settings":
                return value.get("ip_address", STATE_UNKNOWN)
            elif self._sensor_key == "info":
                return value.get("device_name", STATE_UNKNOWN)
            return str(value)
        return str(value)

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        value = self.coordinator.data.get(self._sensor_key)
        if isinstance(value, dict):
            return value
        return {"value": value}
