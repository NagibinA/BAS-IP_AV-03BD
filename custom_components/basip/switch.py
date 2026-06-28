"""Switch platform for BAS-IP."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the BAS-IP switch platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    switches = [
        BASIPEmergencySwitch(coordinator),
    ]

    async_add_entities(switches)


class BASIPEmergencySwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a BAS-IP emergency mode switch."""

    def __init__(self, coordinator):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = "BAS-IP Emergency Mode"
        self._attr_unique_id = f"{coordinator.host}_emergency"
        self._attr_is_on = False
        self._attr_icon = "mdi:alert"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    async def async_turn_on(self, **kwargs):
        """Turn on emergency mode."""
        try:
            await self.coordinator.async_emergency_open()
            self._attr_is_on = True
            _LOGGER.info("Emergency mode activated")
        except Exception as e:
            _LOGGER.error(f"Error activating emergency mode: {e}")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off emergency mode."""
        try:
            await self.coordinator.async_emergency_close()
            self._attr_is_on = False
            _LOGGER.info("Emergency mode deactivated")
        except Exception as e:
            _LOGGER.error(f"Error deactivating emergency mode: {e}")
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.connected
