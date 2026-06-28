"""BAS-IP Intercom integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from .const import DOMAIN
from .coordinator import BASIPCoordinator

_LOGGER = logging.getLogger(__name__)

# Импортируем PLATFORMS из const
from .const import PLATFORMS

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
    """Set up BAS-IP from a config entry."""
    _LOGGER.info("Setting up BAS-IP for %s", entry.data.get("host"))
    
    # Инициализируем координатор
    coordinator = BASIPCoordinator(hass, entry.data)
    
    # Проверяем авторизацию
    valid = await coordinator.async_validate_auth()
    if not valid:
        _LOGGER.error("Failed to authenticate with BAS-IP")
        return False
    
    # Сохраняем координатор
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Регистрируем платформы
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Регистрируем сервисы
    await async_register_services(hass, coordinator)
    
    _LOGGER.info("BAS-IP integration setup complete")
    return True

async def async_register_services(hass: HomeAssistant, coordinator: BASIPCoordinator):
    """Register services for BAS-IP integration."""
    
    async def handle_open_lock(call: ServiceCall):
        await coordinator.async_open_lock()
        _LOGGER.info("Lock opened")
    
    async def handle_emergency_open(call: ServiceCall):
        await coordinator.async_emergency_open(
            call.data.get("lock_number", 1),
            call.data.get("unlock_time", 10000)
        )
        _LOGGER.info("Emergency open activated")
    
    async def handle_emergency_close(call: ServiceCall):
        await coordinator.async_emergency_close(call.data.get("lock_number", 1))
        _LOGGER.info("Emergency mode closed")
    
    async def handle_reboot(call: ServiceCall):
        await coordinator.async_reboot()
        _LOGGER.info("Device reboot initiated")
    
    async def handle_take_photo(call: ServiceCall):
        await coordinator.async_get_photo()
        _LOGGER.info("Photo taken")
    
    async def handle_call_start(call: ServiceCall):
        await coordinator.async_call_start(call.data.get("number"))
        _LOGGER.info("Call started")
    
    async def handle_call_end(call: ServiceCall):
        await coordinator.async_call_end()
        _LOGGER.info("Call ended")
    
    async def handle_set_language(call: ServiceCall):
        await coordinator.async_set_language(call.data.get("language"))
        _LOGGER.info("Language set")
    
    async def handle_set_static_ip(call: ServiceCall):
        await coordinator.async_set_static_ip(
            call.data.get("ip_address"),
            call.data.get("mask"),
            call.data.get("gateway"),
            call.data.get("dns")
        )
        _LOGGER.info("Static IP configured")
    
    async def handle_enable_dhcp(call: ServiceCall):
        await coordinator.async_enable_dhcp()
        _LOGGER.info("DHCP enabled")

    # Регистрируем все сервисы
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
    """Unload a config entry."""
    _LOGGER.info("Unloading BAS-IP integration")
    
    # Удаляем сервисы
    services = [
        "open_lock", "emergency_open", "emergency_close",
        "reboot", "take_photo", "call_start", "call_end",
        "set_language", "set_static_ip", "enable_dhcp"
    ]
    for service in services:
        hass.services.async_remove(DOMAIN, service)
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok