"""Lock platform for BAS-IP Intercom."""
from homeassistant.components.lock import LockEntity, LockState
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the BAS-IP lock platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entry_id = config_entry.entry_id

    locks = [
        BASIPLock(coordinator, entry_id, lock_id=1, name="BAS-IP Door Lock"),
    ]

    async_add_entities(locks)


class BASIPLock(CoordinatorEntity, LockEntity):
    """Representation of a BAS-IP lock."""

    def __init__(self, coordinator, entry_id, lock_id: int, name: str):
        """Initialize the lock."""
        super().__init__(coordinator)
        self._lock_id = lock_id
        self._entry_id = entry_id
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_lock_{lock_id}"
        self._attr_is_locked = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )
        self._attr_translation_key = "door_lock"

    async def async_lock(self, **kwargs):
        """Lock the door."""
        self._attr_is_locked = True
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs):
        """Open the door."""
        try:
            result = await self.coordinator.async_open_lock()
            if result is not None:
                _LOGGER.info("Door opened successfully")
                self._attr_is_locked = True
            else:
                _LOGGER.error("Failed to open door")
        except Exception as e:
            _LOGGER.error(f"Error opening door: {e}")

        self.async_write_ha_state()

    @property
    def state(self):
        """Return the state of the lock."""
        return LockState.LOCKED

    @property
    def is_locked(self):
        """Return true if the lock is locked."""
        return True

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.connected