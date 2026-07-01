"""Sensor platform for BAS-IP."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from .const import DOMAIN, SENSOR_TYPES
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up BAS-IP sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entry_id = config_entry.entry_id
    entities = []
    
    # Обычные сенсоры
    for sensor_key, sensor_info in SENSOR_TYPES.items():
        entities.append(BASIPSensor(coordinator, entry_id, sensor_key, sensor_info))
    
    async_add_entities(entities)


class BASIPSensor(SensorEntity):
    """Sensor entity for BAS-IP device parameters."""
    
    def __init__(self, coordinator, entry_id, sensor_key, sensor_info):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._entry_id = entry_id
        self._sensor_key = sensor_key
        self._attr_translation_key = sensor_key
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry_id}_{sensor_key}"
        self._attr_icon = sensor_info.get("icon", "mdi:information")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return STATE_UNAVAILABLE
        
        value = self.coordinator.data.get(self._sensor_key)
        if value is None:
            return STATE_UNKNOWN
        
        if isinstance(value, dict):
            # Обработка bas_ip_info
            if self._sensor_key == "bas_ip_info":
                # Показываем модель и имя
                device_name = value.get("device_name", "")
                device_model = value.get("device_model", "")
                firmware = value.get("firmware_version", "")
                if device_name and device_model:
                    return f"{device_name} ({device_model.upper()})"
                elif device_name:
                    return device_name
                elif device_model:
                    return device_model.upper()
                return "BAS-IP Intercom"
            
            elif self._sensor_key == "bas_ip_sip_status":
                return value.get("sip_status", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_network_mac":
                return value.get("mac_address", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_device_time":
                return value.get("device_timezone", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_device_language":
                return value.get("current_language", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_device_video":
                return value.get("video_resolution", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_device_rtsp":
                return value.get("username", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_device_payload":
                return value.get("payload_codec_h264", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_device_volume":
                return value.get("volume_level", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_device_relay":
                pos = value.get("position_settings", {})
                return pos.get("position", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_device_mode":
                return value.get("current_panel_mode", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_lock_type":
                locks = value.get("locks", [])
                if locks:
                    return locks[0].get("type", STATE_UNKNOWN)
                return STATE_UNKNOWN
            elif self._sensor_key == "bas_ip_master_card":
                return value.get("master_card", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_input_code":
                return value.get("input_code_number", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_network_ntp":
                return value.get("custom_server", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_network_dst":
                return "Enabled" if value.get("is_enabled") else "Disabled"
            elif self._sensor_key == "bas_ip_network_timezone":
                return value.get("current_timezone", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_network_management_link":
                return "Enabled" if value.get("link_enable") else "Disabled"
            elif self._sensor_key == "bas_ip_network_management_server":
                return value.get("protocol", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_network_management_server_cert":
                return "Valid" if value.get("uploaded") else "Not uploaded"
            elif self._sensor_key == "bas_ip_sip_settings":
                return value.get("user", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_sip_enable":
                return "Enabled" if value.get("sip_enable") else "Disabled"
            elif self._sensor_key == "bas_ip_sip_reregister":
                return "Enabled" if value.get("is_reregister") else "Disabled"
            elif self._sensor_key == "bas_ip_call_auto_answer":
                return "Enabled" if value.get("is_enabled") else "Disabled"
            elif self._sensor_key == "bas_ip_call_drop":
                return "Enabled" if value.get("is_enabled") else "Disabled"
            elif self._sensor_key == "bas_ip_call_drop_lock_open":
                return "Enabled" if value.get("is_enabled") else "Disabled"
            elif self._sensor_key == "bas_ip_rescue_service":
                return "Enabled" if value.get("is_enabled") else "Disabled"
            elif self._sensor_key == "bas_ip_network_settings":
                return value.get("ip_address", STATE_UNKNOWN)
            elif self._sensor_key == "bas_ip_door_sensor_settings":
                return f"Delay: {value.get('opening_delay', 'N/A')}s"
            elif self._sensor_key == "bas_ip_exit_button_status":
                return "Enabled" if value.get("enable") else "Disabled"
            return str(value)
        
        return str(value)

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        value = self.coordinator.data.get(self._sensor_key)
        if isinstance(value, dict):
            # Для bas_ip_info показываем все поля
            if self._sensor_key == "bas_ip_info":
                return {
                    "firmware_version": value.get("firmware_version", ""),
                    "framework_version": value.get("framework_version", ""),
                    "api_version": value.get("api_version", ""),
                    "device_serial_number": value.get("device_serial_number", ""),
                    "device_model": value.get("device_model", ""),
                    "device_type": value.get("device_type", ""),
                    "commit": value.get("commit", ""),
                }
            return value
        
        return {"value": value}

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()