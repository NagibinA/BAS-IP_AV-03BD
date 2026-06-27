from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        BASIPRebootSwitch(coordinator),
        BASIPEmergencySwitch(coordinator),
    ])

class BASIPRebootSwitch(SwitchEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "BAS-IP Reboot"
        self._attr_unique_id = f"{coordinator.host}_reboot"
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_reboot()
        self._attr_is_on = True
        self.async_write_ha_state()
        await asyncio.sleep(5)
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._attr_is_on = False
        self.async_write_ha_state()

class BASIPEmergencySwitch(SwitchEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "BAS-IP Emergency Mode"
        self._attr_unique_id = f"{coordinator.host}_emergency"
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_emergency_open()
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_emergency_close()
        self._attr_is_on = False
        self.async_write_ha_state()
