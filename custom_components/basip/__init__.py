"""BAS-IP Intercom integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from .const import DOMAIN, PLATFORMS
from .coordinator import BASIPCoordinator

_LOGGER = logging.getLogger(__name__)

# Схемы для сервисов
LOCK_NUMBER_SCHEMA = vol.Schema({
    vol.Optional("lock_number", default=1): cv.positive_int,
})

EMERGENCY_SCHEMA = vol.Schema({
    vol.Optional("lock_number", default=1): cv.positive_int,
    vol.Optional("unlock_time", default=10000): cv.positive_int,
})

CALL_SCHEMA = vol.Schema({
    vol.Required("number"): cv.string,
})

LANGUAGE_SCHEMA = vol.Schema({
    vol.Required("language"): vol.In(["English", "Russian", "Ukrainian", "Spanish", "Turkish"]),
})

IP_CONFIG_SCHEMA = vol.Schema({
    vol.Required("ip_address"): cv.string,
    vol.Required("mask"): cv.string,
    vol.Required("gateway"): cv.string,
    vol.Required("dns"): cv.string,
})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BAS-IP from a config entry."""
    
    _LOGGER.info("Setting up BAS-IP integration for %s", entry.data.get("host", "unknown"))
    
    # Инициализируем координатор
    coordinator = BASIPCoordinator(hass, entry.data)
    
    # Проверяем авторизацию
    valid = await coordinator.async_validate_auth()
    if not valid:
        _LOGGER.error("Failed to authenticate with BAS-IP device")
        return False
    
    _LOGGER.info("Successfully authenticated with BAS-IP")
    
    # Сохраняем координатор в hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Настраиваем платформы
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Регистрируем сервисы
    await async_register_services(hass, coordinator)
    
    return True

async def async_register_services(hass: HomeAssistant, coordinator: BASIPCoordinator):
    """Register services for BAS-IP integration."""
    
    async def handle_open_lock(service_call: ServiceCall):
        """Handle open lock service."""
        await coordinator.async_open_lock()
        _LOGGER.info("Lock opened")
    
    async def handle_emergency_open(service_call: ServiceCall):
        """Handle emergency open service."""
        lock_number = service_call.data.get("lock_number", 1)
        unlock_time = service_call.data.get("unlock_time", 10000)
        await coordinator.async_emergency_open(lock_number, unlock_time)
        _LOGGER.info(f"Emergency open for lock {lock_number} with {unlock_time}ms")
    
    async def handle_emergency_close(service_call: ServiceCall):
        """Handle emergency close service."""
        lock_number = service_call.data.get("lock_number", 1)
        await coordinator.async_emergency_close(lock_number)
        _LOGGER.info(f"Emergency closed lock {lock_number}")
    
    async def handle_reboot(service_call: ServiceCall):
        """Handle reboot service."""
        await coordinator.async_reboot()
        _LOGGER.info("Device reboot initiated")
    
    async def handle_take_photo(service_call: ServiceCall):
        """Handle take photo service."""
        photo = await coordinator.async_get_photo()
        if photo:
            _LOGGER.info("Photo captured successfully")
        else:
            _LOGGER.warning("Failed to capture photo")
    
    async def handle_call_start(service_call: ServiceCall):
        """Handle call start service."""
        number = service_call.data.get("number")
        await coordinator.async_call_start(number)
        _LOGGER.info(f"Call started to {number}")
    
    async def handle_call_end(service_call: ServiceCall):
        """Handle call end service."""
        await coordinator.async_call_end()
        _LOGGER.info("Call ended")
    
    async def handle_set_language(service_call: ServiceCall):
        """Handle set language service."""
        language = service_call.data.get("language")
        await coordinator.async_set_language(language)
        _LOGGER.info(f"Language set to {language}")
    
    async def handle_set_static_ip(service_call: ServiceCall):
        """Handle set static IP service."""
        ip = service_call.data.get("ip_address")
        mask = service_call.data.get("mask")
        gateway = service_call.data.get("gateway")
        dns = service_call.data.get("dns")
        await coordinator.async_set_static_ip(ip, mask, gateway, dns)
        _LOGGER.info(f"Static IP configured: {ip}")
    
    async def handle_enable_dhcp(service_call: ServiceCall):
        """Handle enable DHCP service."""
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
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    # Удаляем сервисы
    services = [
        "open_lock", "emergency_open", "emergency_close",
        "reboot", "take_photo", "call_start", "call_end",
        "set_language", "set_static_ip", "enable_dhcp"
    ]
    for service in services:
        hass.services.async_remove(DOMAIN, service)
    
    return unload_ok
