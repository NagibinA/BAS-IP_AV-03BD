"""BAS-IP Intercom integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN, PLATFORMS, DEFAULT_UPDATE_INTERVAL, MANUFACTURER, MODEL
from .coordinator import BASIPCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BAS-IP from a config entry."""
    config = {**entry.data}
    
    # Добавляем опции
    if entry.options:
        config.update(entry.options)
    
    # Создаем координатор
    coordinator = BASIPCoordinator(hass, config)
    
    # Выполняем первое обновление
    await coordinator.async_config_entry_first_refresh()
    
    # Сохраняем координатор в hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Запускаем обновление кнопок (для событий звонка, кнопки выхода, двери)
    coordinator.start_button_updater()
    
    # Настраиваем все платформы
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Обновляем опции при изменении
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    # Регистрируем устройство в device registry
    device_registry = dr.async_get(hass)
    
    # Получаем версию ПО из данных координатора
    sw_version = "Unknown"
    if coordinator.data and isinstance(coordinator.data, dict):
        info = coordinator.data.get("bas_ip_info", {})
        if isinstance(info, dict):
            sw_version = info.get("firmware_version", "Unknown")
            _LOGGER.debug(f"📱 Device firmware version: {sw_version}")
    
    # Получаем модель устройства
    device_model = MODEL
    if coordinator.data and isinstance(coordinator.data, dict):
        info = coordinator.data.get("bas_ip_info", {})
        if isinstance(info, dict):
            model = info.get("device_model", "")
            if model:
                device_model = model.upper()
    
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=f"BAS-IP {device_model}",
        manufacturer=MANUFACTURER,
        model=device_model,
        sw_version=sw_version,
        configuration_url=f"http://{coordinator.host}",
    )
    
    _LOGGER.info(f"✅ BAS-IP integration setup completed for {coordinator.host} (FW: {sw_version})")
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Обновляем интервал обновления
    if "update_interval" in entry.options:
        coordinator.update_interval = entry.options.get(
            "update_interval", DEFAULT_UPDATE_INTERVAL
        )
    
    # Обновляем номера для звонков
    if "call_numbers" in entry.options:
        coordinator.update_call_numbers(entry.options)
    
    _LOGGER.info(f"🔄 BAS-IP options updated for {coordinator.host}")

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Останавливаем обновление кнопок
    await coordinator.async_stop_button_updater()
    
    # Выгружаем платформы
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info(f"✅ BAS-IP integration unloaded for {coordinator.host}")
    
    return unload_ok

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove a config entry."""
    _LOGGER.info(f"🗑️ Removing BAS-IP entry for {entry.data.get(CONF_HOST)}")
    
    # Очищаем данные
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        coordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_stop_button_updater()
        hass.data[DOMAIN].pop(entry.entry_id)
    
    # Удаляем устройство из device registry
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    if device:
        device_registry.async_remove_device(device.id)
        _LOGGER.info(f"🗑️ Device removed from registry")

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.info(f"🔄 Migrating BAS-IP entry from version {config_entry.version}")
    
    if config_entry.version == 1:
        new_data = {**config_entry.data}
        
        if "mask" not in new_data:
            new_data["mask"] = "255.255.255.0"
        if "gateway" not in new_data:
            new_data["gateway"] = "192.168.1.1"
        if "dns" not in new_data:
            new_data["dns"] = "8.8.8.8"
        if "port" not in new_data:
            new_data["port"] = 80
        
        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new_data)
        _LOGGER.info("✅ BAS-IP entry migrated to version 2")
    
    return True

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the BAS-IP component."""
    hass.data.setdefault(DOMAIN, {})
    return True