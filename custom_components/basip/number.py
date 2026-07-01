"""Number platform for BAS-IP."""
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging
import asyncio

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up BAS-IP number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entry_id = config_entry.entry_id
    async_add_entities([BASIPVolumeNumber(coordinator, entry_id)])


class BASIPVolumeNumber(CoordinatorEntity, NumberEntity):
    """Number entity for BAS-IP volume control."""

    def __init__(self, coordinator, entry_id):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_volume"
        self._attr_has_entity_name = True
        self._attr_translation_key = "volume"
        self._attr_icon = "mdi:volume-high"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 6
        self._attr_native_step = 1
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def native_value(self):
        """Return the current volume level."""
        if not self.coordinator.data:
            return None
        value = self.coordinator.data.get("bas_ip_device_volume")
        if isinstance(value, dict):
            return value.get("volume_level")
        return value

    async def async_set_native_value(self, value: float):
        """Set the volume level."""
        try:
            _LOGGER.info(f"🔊 Setting volume to: {int(value)}")
            
            # 1. Сразу обновляем локальное состояние
            if self.coordinator.data:
                volume_data = self.coordinator.data.get("bas_ip_device_volume", {})
                if isinstance(volume_data, dict):
                    volume_data["volume_level"] = int(value)
                    self.coordinator.data["bas_ip_device_volume"] = volume_data
            
            # 2. Мгновенно обновляем UI
            self.async_write_ha_state()
            
            # 3. Отправляем запрос на устройство
            success = await self.coordinator.async_set_volume(int(value))
            
            if success:
                # 4. БЫСТРЫЙ опрос ТОЛЬКО громкости (не всех сенсоров!)
                await self.coordinator.async_refresh_volume_only()
                _LOGGER.info(f"✅ Volume successfully set to: {int(value)}")
            else:
                _LOGGER.error(f"❌ Failed to set volume to: {int(value)}")
                # Откатываем изменения
                await self.coordinator.async_refresh_volume_only()
                self.async_write_ha_state()
                
        except Exception as e:
            _LOGGER.error(f"❌ Exception while setting volume: {e}")
            raise