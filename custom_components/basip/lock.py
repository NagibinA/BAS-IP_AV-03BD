"""Platform for BAS-IP lock."""
from homeassistant.components.lock import LockEntity, LockState
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the BAS-IP lock platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([BASIPLock(coordinator)])

class BASIPLock(LockEntity):
    """Representation of a BAS-IP lock."""

    def __init__(self, coordinator):
        """Initialize the lock."""
        self.coordinator = coordinator
        self._attr_name = "BAS-IP Door Lock"
        self._attr_unique_id = f"{coordinator.host}_lock"
        self._attr_is_locked = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    async def async_lock(self, **kwargs):
        """Lock the door."""
        # BAS-IP не имеет API для блокировки, только открытие
        # Поэтому просто оставляем как есть
        self._attr_is_locked = True
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs):
        """Unlock the door."""
        await self.coordinator.async_open_lock()
        self._attr_is_locked = False
        self.async_write_ha_state()

    @property
    def state(self):
        """Return the state of the lock."""
        if self._attr_is_locked:
            return LockState.LOCKED
        return LockState.UNLOCKED
