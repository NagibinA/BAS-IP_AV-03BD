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

    # Проверяем, поддерживается ли замок
    # Показываем один замок, но можно добавить поддержку нескольких
    locks = [
        BASIPLock(coordinator, lock_id=1, name="BAS-IP Door Lock"),
    ]

    async_add_entities(locks)


class BASIPLock(CoordinatorEntity, LockEntity):
    """Representation of a BAS-IP lock."""

    def __init__(self, coordinator, lock_id: int, name: str):
        """Initialize the lock."""
        super().__init__(coordinator)
        self._lock_id = lock_id
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.host}_lock_{lock_id}"
        self._attr_is_locked = True  # По умолчанию считаем, что замок закрыт
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
            sw_version="1.0.0",
        )

    async def async_lock(self, **kwargs):
        """Lock the door."""
        # BAS-IP не имеет API для блокировки, только открытие
        # Поэтому просто устанавливаем состояние как закрытое
        self._attr_is_locked = True
        self.async_write_ha_state()
        _LOGGER.debug(f"Lock {self._lock_id} set to locked state (no actual API call)")

    async def async_unlock(self, **kwargs):
        """Unlock the door."""
        try:
            # Отправляем команду на открытие замка
            result = await self.coordinator.async_open_lock()

            if result is not None:
                # Если команда успешно отправлена, считаем, что замок открыт
                self._attr_is_locked = False
                _LOGGER.info(f"Lock {self._lock_id} unlocked successfully")
            else:
                _LOGGER.error(f"Failed to unlock lock {self._lock_id}")

        except Exception as e:
            _LOGGER.error(f"Error unlocking lock {self._lock_id}: {e}")
            # В случае ошибки не меняем состояние

        self.async_write_ha_state()

    @property
    def state(self):
        """Return the state of the lock."""
        if self._attr_is_locked:
            return LockState.LOCKED
        return LockState.UNLOCKED

    @property
    def is_locked(self):
        """Return true if the lock is locked."""
        return self._attr_is_locked

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.connected and self.coordinator.data is not None
