"""Button platform for BAS-IP."""
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entry_id = config_entry.entry_id
    buttons = [
        BASIPRebootButton(coordinator, entry_id),
        BASIPCallStartButton(coordinator, entry_id),
        BASIPCallEndButton(coordinator, entry_id),
    ]
    async_add_entities(buttons)


class BASIPRebootButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "BAS-IP Reboot"
        self._attr_unique_id = f"{entry_id}_reboot"
        self._attr_icon = "mdi:restart"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    async def async_press(self, **kwargs):
        try:
            await self.coordinator.async_reboot()
            _LOGGER.info("Device reboot initiated")
        except Exception as e:
            _LOGGER.error(f"Error rebooting device: {e}")


class BASIPCallStartButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "BAS-IP Call"
        self._attr_unique_id = f"{entry_id}_call"
        self._attr_icon = "mdi:phone"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    async def async_press(self, **kwargs):
        try:
            number = self.coordinator._current_call_number
            if not number:
                _LOGGER.warning("No call number configured")
                return
            await self.coordinator.async_call_start(number)
            _LOGGER.info(f"📞 Call started to {number}")
        except Exception as e:
            _LOGGER.error(f"Error starting call: {e}")


class BASIPCallEndButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_name = "BAS-IP Call End"
        self._attr_unique_id = f"{entry_id}_call_end"
        self._attr_icon = "mdi:phone-hangup"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    async def async_press(self, **kwargs):
        try:
            await self.coordinator.async_call_end()
            _LOGGER.info("Call ended")
        except Exception as e:
            _LOGGER.error(f"Error ending call: {e}")