"""Button platform for BAS-IP."""
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up BAS-IP buttons."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    
    entities.append(BASIPRebootButton(coordinator, config_entry))
    entities.append(BASIPCallButton(coordinator, config_entry))
    entities.append(BASIPCallEndButton(coordinator, config_entry))
    
    async_add_entities(entities)


class BASIPRebootButton(ButtonEntity):
    """Reboot button."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the button."""
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_reboot"
        self._attr_has_entity_name = True
        self._attr_translation_key = "reboot"
        self._attr_icon = "mdi:restart"
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_reboot()
        _LOGGER.info("🔄 Reboot command sent to BAS-IP")

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


class BASIPCallButton(ButtonEntity):
    """Call button."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the button."""
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_call"
        self._attr_has_entity_name = True
        self._attr_translation_key = "call"
        self._attr_icon = "mdi:phone"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    async def async_press(self) -> None:
        """Press the button."""
        if hasattr(self.coordinator, '_current_call_number'):
            number = self.coordinator._current_call_number
            await self.coordinator.async_call_start(number)
            _LOGGER.info(f"📞 Call started to {number}")

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


class BASIPCallEndButton(ButtonEntity):
    """End call button."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the button."""
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_call_end"
        self._attr_has_entity_name = True
        self._attr_translation_key = "call_end"
        self._attr_icon = "mdi:phone-hangup"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_call_end()
        _LOGGER.info("📞 Call end command sent")

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