"""Button platform for BAS-IP."""
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the BAS-IP button platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    buttons = [
        BASIPRebootButton(coordinator),
    ]

    async_add_entities(buttons)


class BASIPRebootButton(CoordinatorEntity, ButtonEntity):
    """Representation of a BAS-IP reboot button."""

    def __init__(self, coordinator):
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_name = "BAS-IP Reboot"
        self._attr_unique_id = f"{coordinator.host}_reboot"
        self._attr_icon = "mdi:restart"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    async def async_press(self, **kwargs):
        """Press the button (reboot the device)."""
        try:
            await self.coordinator.async_reboot()
            _LOGGER.info("Device reboot initiated")
        except Exception as e:
            _LOGGER.error(f"Error rebooting device: {e}")
