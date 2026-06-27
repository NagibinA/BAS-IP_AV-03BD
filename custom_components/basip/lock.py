from homeassistant.components.lock import LockEntity
from homeassistant.const import STATE_LOCKED, STATE_UNLOCKED
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([BASIPLock(coordinator)])

class BASIPLock(LockEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "BAS-IP Door Lock"
        self._attr_unique_id = f"{coordinator.host}_lock"
        self._attr_is_locked = True

    async def async_lock(self):
        # BAS-IP не имеет API для блокировки, только открытие
        await self.coordinator.async_open_lock()
        self._attr_is_locked = True
        self.async_write_ha_state()

    async def async_unlock(self):
        await self.coordinator.async_open_lock()
        self._attr_is_locked = False
        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.host)},
            "name": "BAS-IP Intercom",
            "manufacturer": "BAS-IP",
            "model": "Intercom Panel",
            "sw_version": "1.0",
        }
