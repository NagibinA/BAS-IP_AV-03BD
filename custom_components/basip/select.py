"""Select platform for BAS-IP."""
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up BAS-IP selects."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    
    entities.append(BASIPCallNumberSelect(coordinator, config_entry))
    
    async_add_entities(entities)


class BASIPCallNumberSelect(SelectEntity):
    """Call number select."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the select."""
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_call_number"
        self._attr_has_entity_name = True
        self._attr_translation_key = "call_number_select"
        self._attr_icon = "mdi:phone"
        # Убираем EntityCategory.CONFIG - селект должен быть в управлении

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
    def options(self) -> list[str]:
        """Return the list of available options."""
        if hasattr(self.coordinator, '_call_numbers'):
            return self.coordinator._call_numbers
        return ["79020"]

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if hasattr(self.coordinator, '_current_call_number'):
            return self.coordinator._current_call_number
        return None

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        if hasattr(self.coordinator, '_current_call_number'):
            self.coordinator._current_call_number = option
            self.async_write_ha_state()
            _LOGGER.info(f"📞 Call number selected: {option}")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()