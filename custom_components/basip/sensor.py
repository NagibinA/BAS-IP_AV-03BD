"""Sensor platform for BAS-IP."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, SENSOR_TYPES
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entry_id = config_entry.entry_id
    sensors = []
    for sensor_key, sensor_info in SENSOR_TYPES.items():
        sensors.append(BASIPSensor(coordinator, entry_id, sensor_key, sensor_info))
    sensors.append(BASIPDoorbellSensor(coordinator, entry_id))
    sensors.append(BASIPExitButtonSensor(coordinator, entry_id))
    sensors.append(BASIPDoorSensor(coordinator, entry_id))
    sensors.append(BASIPDoorOpenTooLongSensor(coordinator, entry_id))
    sensors.append(BASIPExitButtonStatusSensor(coordinator, entry_id))
    async_add_entities(sensors)


class BASIPSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry_id, sensor_key, sensor_info):
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._entry_id = entry_id
        self._attr_name = f"BAS-IP {sensor_info['name']}"
        self._attr_unique_id = f"{entry_id}_{sensor_key}"
        self._attr_icon = sensor_info.get("icon", "mdi:information")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
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
            elif self._sensor_key == "door_sensor_settings":
                return f"Delay: {value.get('opening_delay', 'N/A')}s"
            elif self._sensor_key == "exit_button_status":
                return "Enabled" if value.get("enable") else "Disabled"
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


class BASIPDoorbellSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "BAS-IP Doorbell"
        self._attr_unique_id = f"{entry_id}_doorbell"
        self._attr_icon = "mdi:doorbell"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator._doorbell_state

    @property
    def available(self) -> bool:
        return self.coordinator.connected

    @property
    def extra_state_attributes(self):
        return {
            "last_event_timestamp": self.coordinator._last_doorbell_timestamp,
        }


class BASIPExitButtonSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "BAS-IP Exit Button Pressed"
        self._attr_unique_id = f"{entry_id}_exit_button"
        self._attr_icon = "mdi:exit-run"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def is_on(self) -> bool:
        if not self.coordinator._exit_button_enabled:
            return None
        return self.coordinator._exit_button_state

    @property
    def available(self) -> bool:
        return self.coordinator.connected and self.coordinator._exit_button_enabled

    @property
    def extra_state_attributes(self):
        return {
            "last_event_timestamp": self.coordinator._last_exit_timestamp,
            "exit_button_enabled": self.coordinator._exit_button_enabled,
        }


class BASIPDoorSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "BAS-IP Door"
        self._attr_unique_id = f"{entry_id}_door"
        self._attr_icon = "mdi:door"
        self._attr_is_on = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator._door_state

    @property
    def available(self) -> bool:
        return self.coordinator.connected

    @property
    def extra_state_attributes(self):
        return {
            "last_event_timestamp": self.coordinator._last_door_timestamp,
        }


class BASIPDoorOpenTooLongSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "BAS-IP Door Open Too Long"
        self._attr_unique_id = f"{entry_id}_door_open_too_long"
        self._attr_icon = "mdi:clock-alert"
        self._attr_is_on = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator._door_open_too_long

    @property
    def available(self) -> bool:
        return self.coordinator.connected

    @property
    def extra_state_attributes(self):
        return {
            "last_event_timestamp": self.coordinator._last_door_open_too_long_timestamp,
        }


class BASIPExitButtonStatusSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "BAS-IP Exit Button Enabled"
        self._attr_unique_id = f"{entry_id}_exit_button_enabled"
        self._attr_icon = "mdi:exit-run"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_is_on = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator._exit_button_enabled

    @property
    def available(self) -> bool:
        return self.coordinator.connected

    @property
    def extra_state_attributes(self):
        return {}