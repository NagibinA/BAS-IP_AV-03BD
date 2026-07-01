"""Switch platform for BAS-IP."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up BAS-IP switches."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    
    entities.append(BASIPEmergencyModeSwitch(coordinator, config_entry))
    entities.append(BASIPAutoAnswerSwitch(coordinator, config_entry))
    entities.append(BASIPCallDropSwitch(coordinator, config_entry))
    entities.append(BASIPCallDropLockOpenSwitch(coordinator, config_entry))
    
    async_add_entities(entities)


class BASIPEmergencyModeSwitch(CoordinatorEntity, SwitchEntity):
    """Emergency mode switch - НЕ ОПРАШИВАЕМ (действие)."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_emergency_mode"
        self._attr_has_entity_name = True
        self._attr_translation_key = "emergency_mode"
        self._attr_icon = "mdi:alert"
        self._attr_entity_category = EntityCategory.CONFIG
        self._emergency_mode = False

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
    def is_on(self) -> bool:
        """Return true if emergency mode is on."""
        return self._emergency_mode

    async def async_turn_on(self, **kwargs):
        """Turn on emergency mode - открыть аварийно."""
        try:
            _LOGGER.info("🚨 Turning on emergency mode...")
            await self.coordinator.async_emergency_open()
            self._emergency_mode = True
            self.async_write_ha_state()
            # НЕ опрашиваем - это действие
            _LOGGER.info("✅ Emergency mode turned on")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to turn on emergency mode: {e}")
            raise

    async def async_turn_off(self, **kwargs):
        """Turn off emergency mode - закрыть аварийный режим."""
        try:
            _LOGGER.info("🚨 Turning off emergency mode...")
            await self.coordinator.async_emergency_close()
            self._emergency_mode = False
            self.async_write_ha_state()
            # НЕ опрашиваем - это действие
            _LOGGER.info("✅ Emergency mode turned off")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to turn off emergency mode: {e}")
            raise

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class BASIPAutoAnswerSwitch(CoordinatorEntity, SwitchEntity):
    """Auto answer switch - ОПРАШИВАЕМ (состояние на устройстве)."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_auto_answer"
        self._attr_has_entity_name = True
        self._attr_translation_key = "auto_answer"
        self._attr_icon = "mdi:phone-in-talk"
        self._attr_entity_category = EntityCategory.CONFIG

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
    def is_on(self) -> bool:
        """Return true if auto answer is on."""
        if not self.coordinator.data:
            return False
        data = self.coordinator.data.get("bas_ip_call_auto_answer", {})
        if isinstance(data, dict):
            return data.get("is_enabled", False)
        return False

    async def async_turn_on(self, **kwargs):
        """Turn on auto answer."""
        try:
            _LOGGER.info("🔄 Turning on auto answer...")
            await self.coordinator.async_set_auto_answer(True)
            
            # Мгновенное обновление UI
            if self.coordinator.data:
                data = self.coordinator.data.get("bas_ip_call_auto_answer", {})
                if isinstance(data, dict):
                    data["is_enabled"] = True
                    self.coordinator.data["bas_ip_call_auto_answer"] = data
            self.async_write_ha_state()
            
            # ОПРАШИВАЕМ - подтверждаем состояние на устройстве
            await asyncio.sleep(0.5)
            await self.coordinator.async_request_refresh()
            _LOGGER.info("✅ Auto answer turned on")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to turn on auto answer: {e}")
            raise

    async def async_turn_off(self, **kwargs):
        """Turn off auto answer."""
        try:
            _LOGGER.info("🔄 Turning off auto answer...")
            await self.coordinator.async_set_auto_answer(False)
            
            # Мгновенное обновление UI
            if self.coordinator.data:
                data = self.coordinator.data.get("bas_ip_call_auto_answer", {})
                if isinstance(data, dict):
                    data["is_enabled"] = False
                    self.coordinator.data["bas_ip_call_auto_answer"] = data
            self.async_write_ha_state()
            
            # ОПРАШИВАЕМ - подтверждаем состояние на устройстве
            await asyncio.sleep(0.5)
            await self.coordinator.async_request_refresh()
            _LOGGER.info("✅ Auto answer turned off")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to turn off auto answer: {e}")
            raise

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class BASIPCallDropSwitch(CoordinatorEntity, SwitchEntity):
    """Call drop by call button switch - ОПРАШИВАЕМ (состояние на устройстве)."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_call_drop"
        self._attr_has_entity_name = True
        self._attr_translation_key = "call_drop"
        self._attr_icon = "mdi:phone-hangup"
        self._attr_entity_category = EntityCategory.CONFIG

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
    def is_on(self) -> bool:
        """Return true if call drop is on."""
        if not self.coordinator.data:
            return False
        data = self.coordinator.data.get("bas_ip_call_drop", {})
        if isinstance(data, dict):
            return data.get("is_enabled", False)
        return False

    async def async_turn_on(self, **kwargs):
        """Turn on call drop."""
        try:
            _LOGGER.info("🔄 Turning on call drop...")
            await self.coordinator.async_set_call_drop(True)
            
            # Мгновенное обновление UI
            if self.coordinator.data:
                data = self.coordinator.data.get("bas_ip_call_drop", {})
                if isinstance(data, dict):
                    data["is_enabled"] = True
                    self.coordinator.data["bas_ip_call_drop"] = data
            self.async_write_ha_state()
            
            # ОПРАШИВАЕМ - подтверждаем состояние на устройстве
            await asyncio.sleep(0.5)
            await self.coordinator.async_request_refresh()
            _LOGGER.info("✅ Call drop turned on")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to turn on call drop: {e}")
            raise

    async def async_turn_off(self, **kwargs):
        """Turn off call drop."""
        try:
            _LOGGER.info("🔄 Turning off call drop...")
            await self.coordinator.async_set_call_drop(False)
            
            # Мгновенное обновление UI
            if self.coordinator.data:
                data = self.coordinator.data.get("bas_ip_call_drop", {})
                if isinstance(data, dict):
                    data["is_enabled"] = False
                    self.coordinator.data["bas_ip_call_drop"] = data
            self.async_write_ha_state()
            
            # ОПРАШИВАЕМ - подтверждаем состояние на устройстве
            await asyncio.sleep(0.5)
            await self.coordinator.async_request_refresh()
            _LOGGER.info("✅ Call drop turned off")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to turn off call drop: {e}")
            raise

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class BASIPCallDropLockOpenSwitch(CoordinatorEntity, SwitchEntity):
    """Call drop on lock open switch - ОПРАШИВАЕМ (состояние на устройстве)."""
    
    def __init__(self, coordinator, config_entry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_call_drop_lock_open"
        self._attr_has_entity_name = True
        self._attr_translation_key = "call_drop_lock_open"
        self._attr_icon = "mdi:lock-open-variant"
        self._attr_entity_category = EntityCategory.CONFIG

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
    def is_on(self) -> bool:
        """Return true if call drop on lock open is on."""
        if not self.coordinator.data:
            return False
        data = self.coordinator.data.get("bas_ip_call_drop_lock_open", {})
        if isinstance(data, dict):
            return data.get("is_enabled", False)
        return False

    async def async_turn_on(self, **kwargs):
        """Turn on call drop on lock open."""
        try:
            _LOGGER.info("🔄 Turning on call drop on lock open...")
            await self.coordinator.async_set_call_drop_lock_open(True)
            
            # Мгновенное обновление UI
            if self.coordinator.data:
                data = self.coordinator.data.get("bas_ip_call_drop_lock_open", {})
                if isinstance(data, dict):
                    data["is_enabled"] = True
                    self.coordinator.data["bas_ip_call_drop_lock_open"] = data
            self.async_write_ha_state()
            
            # ОПРАШИВАЕМ - подтверждаем состояние на устройстве
            await asyncio.sleep(0.5)
            await self.coordinator.async_request_refresh()
            _LOGGER.info("✅ Call drop on lock open turned on")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to turn on call drop on lock open: {e}")
            raise

    async def async_turn_off(self, **kwargs):
        """Turn off call drop on lock open."""
        try:
            _LOGGER.info("🔄 Turning off call drop on lock open...")
            await self.coordinator.async_set_call_drop_lock_open(False)
            
            # Мгновенное обновление UI
            if self.coordinator.data:
                data = self.coordinator.data.get("bas_ip_call_drop_lock_open", {})
                if isinstance(data, dict):
                    data["is_enabled"] = False
                    self.coordinator.data["bas_ip_call_drop_lock_open"] = data
            self.async_write_ha_state()
            
            # ОПРАШИВАЕМ - подтверждаем состояние на устройстве
            await asyncio.sleep(0.5)
            await self.coordinator.async_request_refresh()
            _LOGGER.info("✅ Call drop on lock open turned off")
        except Exception as e:
            _LOGGER.error(f"❌ Failed to turn off call drop on lock open: {e}")
            raise

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success