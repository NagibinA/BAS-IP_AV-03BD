import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS
from .coordinator import BASIPCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BAS-IP from a config entry."""
    
    coordinator = BASIPCoordinator(hass, entry.data)
    await coordinator.async_validate_auth()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, [
        "camera", "lock", "switch", "sensor"
    ])
    
    # Register services
    async def handle_service(service_call):
        """Handle services."""
        service = service_call.service
        data = service_call.data
        
        if service == "open_lock":
            await coordinator.async_open_lock()
        elif service == "emergency_open":
            await coordinator.async_emergency_open(
                data.get("lock_number", 1),
                data.get("unlock_time", 10000)
            )
        elif service == "emergency_close":
            await coordinator.async_emergency_close(data.get("lock_number", 1))
        elif service == "reboot":
            await coordinator.async_reboot()
        elif service == "take_photo":
            await coordinator.async_get_photo()
        elif service == "call_start":
            await coordinator.async_call_start(data.get("number"))
        elif service == "call_end":
            await coordinator.async_call_end()
        elif service == "set_language":
            await coordinator.async_set_language(data.get("language"))
        elif service == "set_static_ip":
            await coordinator.async_set_static_ip(
                data.get("ip_address"),
                data.get("mask"),
                data.get("gateway"),
                data.get("dns")
            )
        elif service == "enable_dhcp":
            await coordinator.async_enable_dhcp()
    
    # Register all services
    hass.services.async_register(DOMAIN, "open_lock", handle_service)
    hass.services.async_register(DOMAIN, "emergency_open", handle_service)
    hass.services.async_register(DOMAIN, "emergency_close", handle_service)
    hass.services.async_register(DOMAIN, "reboot", handle_service)
    hass.services.async_register(DOMAIN, "take_photo", handle_service)
    hass.services.async_register(DOMAIN, "call_start", handle_service)
    hass.services.async_register(DOMAIN, "call_end", handle_service)
    hass.services.async_register(DOMAIN, "set_language", handle_service)
    hass.services.async_register(DOMAIN, "set_static_ip", handle_service)
    hass.services.async_register(DOMAIN, "enable_dhcp", handle_service)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
