"""Number platform for BAS-IP."""
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([BASIPVolumeNumber(coordinator)])


class BASIPVolumeNumber(CoordinatorEntity, NumberEntity):
    """Number entity for BAS-IP volume control."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "BAS-IP Volume"
        self._attr_unique_id = f"{coordinator.host}_volume"
        self._attr_icon = "mdi:volume-high"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 6
        self._attr_native_step = 1
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        value = self.coordinator.data.get("device_volume")
        if isinstance(value, dict):
            return value.get("volume_level")
        return value

    async def async_set_native_value(self, value: float):
        await self.coordinator.async_set_volume(int(value))
        await self.coordinator.async_request_refresh()