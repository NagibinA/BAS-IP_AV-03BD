"""Binary sensor platform for BAS-IP."""
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up BAS-IP binary sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    
    # Бинарные сенсоры
    entities.append(BASIPDoorbellSensor(coordinator, config_entry))
    entities.append(BASIPExitButtonSensor(coordinator, config_entry))
    entities.append(BASIPDoorSensor(coordinator, config_entry))
    entities.append(BASIPDoorOpenTooLongSensor(coordinator, config_entry))
    entities.append(BASIPExitButtonStatusSensor(coordinator, config_entry))
    
    async_add_entities(entities)


class BASIPDoorbellSensor(BinarySensorEntity):
    """Doorbell sensor entity."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_doorbell"
        self._attr_device_class = None
        self._attr_icon = "mdi:doorbell"
        self._attr_has_entity_name = True
        self._attr_translation_key = "doorbell"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def is_on(self) -> bool:
        """Return true if doorbell was pressed."""
        return self.coordinator.doorbell_state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        attrs = {}
        if self.coordinator.last_doorbell_timestamp:
            attrs["last_event_timestamp"] = self.coordinator.last_doorbell_timestamp
        return attrs

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()


class BASIPExitButtonSensor(BinarySensorEntity):
    """Exit button sensor entity."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_exit_button"
        self._attr_device_class = None
        self._attr_icon = "mdi:exit-run"
        self._attr_has_entity_name = True
        self._attr_translation_key = "exit_button"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def is_on(self) -> bool:
        """Return true if exit button was pressed."""
        if not self.coordinator.exit_button_enabled:
            return None
        return self.coordinator.exit_button_state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.exit_button_enabled

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        return {
            "exit_button_enabled": self.coordinator.exit_button_enabled,
        }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()


class BASIPDoorSensor(BinarySensorEntity):
    """Door sensor entity."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_door"
        self._attr_device_class = BinarySensorDeviceClass.DOOR
        self._attr_icon = "mdi:door-closed"
        self._attr_has_entity_name = True
        self._attr_translation_key = "door_sensor"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def is_on(self) -> bool:
        """Return true if the door is open."""
        return self.coordinator.door_state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        attrs = {}
        if self.coordinator.last_door_timestamp:
            attrs["last_event_timestamp"] = self.coordinator.last_door_timestamp
        return attrs

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()


class BASIPDoorOpenTooLongSensor(BinarySensorEntity):
    """Door open too long sensor entity."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_door_open_too_long"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = "mdi:clock-alert"
        self._attr_has_entity_name = True
        self._attr_translation_key = "door_open_too_long"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def is_on(self) -> bool:
        """Return true if door is open too long."""
        return self.coordinator.door_open_too_long

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        attrs = {}
        if self.coordinator.last_door_open_too_long_timestamp:
            attrs["last_event_timestamp"] = self.coordinator.last_door_open_too_long_timestamp
        return attrs

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()


class BASIPExitButtonStatusSensor(BinarySensorEntity):
    """Exit button status (enabled/disabled) sensor entity."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_exit_button_enabled"
        self._attr_device_class = None
        self._attr_icon = "mdi:exit-run"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_has_entity_name = True
        self._attr_translation_key = "exit_button_status"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def is_on(self) -> bool:
        """Return true if exit button is enabled."""
        return self.coordinator.exit_button_enabled

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