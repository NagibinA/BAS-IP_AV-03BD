"""Select platform for BAS-IP."""
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([BASIPCallNumberSelect(coordinator)])


class BASIPCallNumberSelect(CoordinatorEntity, SelectEntity):
    """Select для выбора номера для звонка."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "BAS-IP Call Number Select"
        self._attr_unique_id = f"{coordinator.host}_call_number_select"
        self._attr_icon = "mdi:phone"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )

    @property
    def options(self) -> list[str]:
        """Список доступных номеров."""
        return self.coordinator._call_numbers

    @property
    def current_option(self) -> str:
        """Текущий выбранный номер."""
        return self.coordinator._current_call_number

    async def async_select_option(self, option: str):
        """Выбрать номер для звонка."""
        if option in self.coordinator._call_numbers:
            self.coordinator._current_call_number = option
            self.async_write_ha_state()
            _LOGGER.info(f"📞 Call number selected: {option}")