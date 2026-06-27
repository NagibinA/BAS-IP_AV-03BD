"""BAS-IP Intercom integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from .const import DOMAIN, PLATFORMS
from .coordinator import BASIPCoordinator

_LOGGER = logging.getLogger(__name__)

LOCK_NUMBER_SCHEMA = vol.Schema({vol.Optional("lock_number", default=1): cv.positive_int})
EMERGENCY_SCHEMA = vol.Schema({
    vol.Optional("lock_number", default=1): cv.positive_int,
    vol.Optional("unlock_time", default=10000): cv.positive_int,
})
CALL_SCHEMA = vol.Schema({vol.Required("number"): cv.string})
LANGUAGE_SCHEMA = vol.Schema({
    vol.Required("language"): vol.In(["English", "Russian", "Ukrainian", "Spanish", "Turkish", "Deutsch", "Italian", "French"])
})
IP_CONFIG_SCHEMA = vol.Schema({
    vol.Required("ip_address"): cv.string,
    vol.Required("mask"): cv.string,
    vol.Required("gateway"): cv.string,
    vol.Required("dns"): cv.string,
})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Setting up BAS-IP for %s", entry.data.get("host"))
    coordinator = BASIPCoordinator(hass, entry.data)
    valid = await coordinator.async_validate_auth()
    if not valid:
        _LOGGER.error("Failed to authenticate with BAS-IP")
        return False
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_register_services(hass, coordinator)
    return True

async def async_register_services(hass: HomeAssistant, coordinator: BASIPCoordinator):
    async def handle_open_lock(call: ServiceCall):
        await coordinator.async_open_lock()
    async def handle_emergency_open(call: ServiceCall):
        await coordinator.async_emergency_open(call.data.get("lock_number", 1), call.data.get("unlock_time", 10000))
    async def handle_emergency_close(call: ServiceCall):
        await coordinator.async_emergency_close(call.data.get("lock_number", 1))
    async def handle_reboot(call: ServiceCall):
        await coordinator.async_reboot()
    async def handle_take_photo(call: ServiceCall):
        await coordinator.async_get_photo()
    async def handle_call_start(call: ServiceCall):
        await coordinator.async_call_start(call.data.get("number"))
    async def handle_call_end(call: ServiceCall):
        await coordinator.async_call_end()
    async def handle_set_language(call: ServiceCall):
        await coordinator.async_set_language(call.data.get("language"))
    async def handle_set_static_ip(call: ServiceCall):
        await coordinator.async_set_static_ip(
            call.data.get("ip_address"), call.data.get("mask"),
            call.data.get("gateway"), call.data.get("dns")
        )
    async def handle_enable_dhcp(call: ServiceCall):
        await coordinator.async_enable_dhcp()

    hass.services.async_register(DOMAIN, "open_lock", handle_open_lock)
    hass.services.async_register(DOMAIN, "emergency_open", handle_emergency_open, schema=EMERGENCY_SCHEMA)
    hass.services.async_register(DOMAIN, "emergency_close", handle_emergency_close, schema=LOCK_NUMBER_SCHEMA)
    hass.services.async_register(DOMAIN, "reboot", handle_reboot)
    hass.services.async_register(DOMAIN, "take_photo", handle_take_photo)
    hass.services.async_register(DOMAIN, "call_start", handle_call_start, schema=CALL_SCHEMA)
    hass.services.async_register(DOMAIN, "call_end", handle_call_end)
    hass.services.async_register(DOMAIN, "set_language", handle_set_language, schema=LANGUAGE_SCHEMA)
    hass.services.async_register(DOMAIN, "set_static_ip", handle_set_static_ip, schema=IP_CONFIG_SCHEMA)
    hass.services.async_register(DOMAIN, "enable_dhcp", handle_enable_dhcp)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
