"""Lock platform for BAS-IP."""
from homeassistant.components.lock import LockEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up BAS-IP lock."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    
    entities.append(BASIPDoorLock(coordinator, config_entry))
    
    async_add_entities(entities)


class BASIPDoorLock(LockEntity):
    """Door lock entity."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the lock."""
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_door_lock"
        self._attr_has_entity_name = True
        self._attr_translation_key = "door_lock"
        self._attr_icon = "mdi:lock"

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
    def is_locked(self) -> bool:
        """Return true if lock is locked."""
        # Если дверь закрыта (door_state = False) - замок заперт
        return not self.coordinator.door_state

    @property
    def is_locking(self) -> bool:
        """Return true if lock is locking."""
        return False

    @property
    def is_unlocking(self) -> bool:
        """Return true if lock is unlocking."""
        return False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_lock(self, **kwargs):
        """Lock the door."""
        try:
            _LOGGER.info("🔒 Locking door...")
            await self.coordinator.async_emergency_close()
            await self.coordinator.async_request_refresh()
            _LOGGER.info("✅ Door locked successfully")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to lock door: {e}")
            raise

    async def async_unlock(self, **kwargs):
        """Unlock the door."""
        try:
            _LOGGER.info("🔓 Unlocking door...")
            await self.coordinator.async_open_lock()
            await self.coordinator.async_request_refresh()
            _LOGGER.info("✅ Door unlocked successfully")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to unlock door: {e}")
            raise

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()