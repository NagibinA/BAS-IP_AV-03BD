"""Coordinator for BAS-IP integration."""
import async_timeout
import hashlib
import aiohttp
import asyncio
import logging
from datetime import timedelta, datetime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from .const import *

_LOGGER = logging.getLogger(__name__)

class BASIPCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config):
        self.hass = hass
        self.host = config.get(CONF_HOST)
        self.password = config.get(CONF_PASSWORD)
        self.token = None
        self.token_expiry = None
        self.base_url = f"http://{self.host}:{DEFAULT_PORT}"
        self.connected = False
        self._entry_id = None
        
        self._doorbell_state = False
        self._exit_button_state = False
        self._door_state = False
        self._door_open_too_long = False
        self._exit_button_enabled = False
        
        self._call_numbers = self._extract_numbers(config)
        self._current_call_number = self._call_numbers[0] if self._call_numbers else "79020"
        
        self._last_doorbell_timestamp = None
        self._last_exit_timestamp = None
        self._last_door_timestamp = None
        self._last_door_open_too_long_timestamp = None
        
        self._button_task = None
        self._button_stop = False
        
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=60))

    def _extract_numbers(self, config):
        """Извлечь список номеров из конфига."""
        numbers = []
        
        if "call_numbers" in config:
            val = config["call_numbers"]
            if isinstance(val, list):
                numbers = [str(n).strip() for n in val if n and str(n).strip()]
            elif isinstance(val, str):
                numbers = [n.strip() for n in val.split(",") if n.strip()]
        
        if not numbers and "options" in config:
            options = config["options"]
            if "call_numbers" in options:
                val = options["call_numbers"]
                if isinstance(val, list):
                    numbers = [str(n).strip() for n in val if n and str(n).strip()]
                elif isinstance(val, str):
                    numbers = [n.strip() for n in val.split(",") if n.strip()]
        
        seen = set()
        unique_numbers = []
        for n in numbers:
            if n not in seen:
                seen.add(n)
                unique_numbers.append(n)
        
        return unique_numbers if unique_numbers else ["79020"]

    def update_call_numbers(self, options):
        new_numbers = self._extract_numbers({"options": options})
        self._call_numbers = new_numbers
        if self._current_call_number not in self._call_numbers:
            self._current_call_number = self._call_numbers[0] if self._call_numbers else "79020"
        self.async_update_listeners()
        _LOGGER.info(f"📞 Call numbers updated: {self._call_numbers}")

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                if not self.token:
                    await self.async_login()
                return await self.async_fetch_all_data()
        except Exception as error:
            _LOGGER.error(f"Error updating: {error}")
            raise UpdateFailed(f"Error: {error}")

    def _hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    async def async_login(self):
        try:
            password_hash = self._hash_password(self.password)
            url = f"{self.base_url}{API_LOGIN}?username=admin&password={password_hash}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("token"):
                            self.token = f"Bearer {data['token']}"
                            self.token_expiry = datetime.now() + timedelta(hours=24)
                            self.connected = True
                            _LOGGER.info("Authenticated with BAS-IP")
                            return True
                    _LOGGER.error(f"Login failed: {resp.status}")
                    self.connected = False
                    return False
        except Exception as e:
            _LOGGER.error(f"Login error: {e}")
            self.connected = False
            return False

    async def async_request(self, endpoint, method="GET", data=None, json_data=None, retry_count=2):
        if not self.token:
            await self.async_login()
            if not self.token:
                return None
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            for attempt in range(retry_count):
                try:
                    async with session.request(method, url, headers=headers, data=data, json=json_data, timeout=10) as resp:
                        if resp.status == 401:
                            _LOGGER.warning("Token expired, re-authenticating...")
                            await self.async_login()
                            if self.token:
                                headers["Authorization"] = self.token
                                continue
                            else:
                                _LOGGER.error("Re-authentication failed")
                                return None
                        
                        if resp.status != 200:
                            return None
                        
                        content_type = resp.headers.get("content-type", "")
                        if "application/json" in content_type:
                            return await resp.json()
                        elif "image" in content_type or "application/octet-stream" in content_type:
                            return await resp.read()
                        return await resp.text()
                except aiohttp.ClientError as e:
                    if attempt == retry_count - 1:
                        raise
                    await asyncio.sleep(1)
        return None

    async def async_get_logs(self, limit: int = 10, page_number: int = 1):
        try:
            url = f"{API_LOGS_ITEMS}?limit={limit}&page_number={page_number}"
            result = await self.async_request(url, "GET")
            _LOGGER.debug(f"Logs response received: {result is not None}")
            return result
        except Exception as e:
            _LOGGER.warning(f"Failed to get logs: {e}")
            return None

    async def async_get_door_status(self):
        try:
            return await self.async_request(API_DOOR_STATUS, "GET")
        except Exception as e:
            _LOGGER.warning(f"Failed to get door status: {e}")
            return None

    async def async_check_door_open_too_long(self) -> bool:
        status = await self.async_get_door_status()
        if not status or not isinstance(status, dict):
            return False
        
        if status.get("is_timeout_exceed"):
            self._last_door_open_too_long_timestamp = int(datetime.now().timestamp() * 1000)
        else:
            self._last_door_open_too_long_timestamp = None
        
        return status.get("is_timeout_exceed", False)

    async def async_check_door_state(self) -> bool:
        status = await self.async_get_door_status()
        if not status or not isinstance(status, dict):
            return self._door_state
        
        is_open = status.get("status") == "open"
        if is_open:
            self._last_door_timestamp = int(datetime.now().timestamp() * 1000)
        return is_open

    async def async_check_exit_button_enabled(self) -> bool:
        try:
            result = await self.async_request(API_EXIT_BUTTON, "GET")
            if result and isinstance(result, dict):
                return result.get("enable", False)
            return False
        except Exception as e:
            _LOGGER.warning(f"Failed to get exit button status: {e}")
            return False

    async def async_change_password(self, old_password: str, new_password: str):
        """Сменить пароль администратора на панели."""
        url = f"{API_CHANGE_PASSWORD}?oldPassword={old_password}&newPassword={new_password}"
        return await self.async_request(url, "POST")

    async def async_set_static_ip(self, ip: str, mask: str, gateway: str, dns: str):
        """Установить статический IP на панели."""
        _LOGGER.info(f"🔄 Setting static IP: {ip}, Mask: {mask}, Gateway: {gateway}, DNS: {dns}")
        
        data = {
            "ip_address": ip,
            "mask": mask,
            "gateway": gateway,
            "dns": dns,
        }
        
        _LOGGER.debug(f"📤 Request data: {data}")
        
        try:
            result = await self.async_request(API_NETWORK_STATIC, "POST", json_data=data)
            
            if result is None:
                raise Exception("Request returned None - check authentication or connection")
                
            _LOGGER.info(f"✅ Static IP set successfully")
            return result
        except Exception as e:
            _LOGGER.error(f"❌ Failed to set static IP: {e}")
            raise

    async def async_get_network_settings(self):
        """Получить текущие сетевые настройки."""
        return await self.async_request(API_NETWORK_SETTINGS, "GET")

    async def async_check_events(self) -> tuple:
        doorbell = False
        exit_button = False
        door_open_too_long = await self.async_check_door_open_too_long()
        door_state = await self.async_check_door_state()
        exit_button_enabled = await self.async_check_exit_button_enabled()
        
        try:
            logs = await self.async_get_logs(limit=10)
            if logs and isinstance(logs, dict):
                items = logs.get("list_items", [])
                now = datetime.now()
                for item in items:
                    name_key = item.get("name", {}).get("key", "")
                    timestamp_ms = item.get("timestamp")
                    if not timestamp_ms:
                        continue
                    
                    timestamp_sec = timestamp_ms / 1000
                    event_time = datetime.fromtimestamp(timestamp_sec)
                    if now - event_time > timedelta(seconds=3):
                        continue
                    
                    if name_key == "outgoing_call":
                        doorbell = True
                        self._last_doorbell_timestamp = timestamp_ms
                    elif name_key == "lock_was_opened_by_exit_btn":
                        exit_button = True
                        self._last_exit_timestamp = timestamp_ms
            
            return doorbell, exit_button, door_open_too_long, door_state, exit_button_enabled
        except Exception as e:
            _LOGGER.warning(f"Failed to check events: {e}")
            return doorbell, exit_button, door_open_too_long, door_state, exit_button_enabled

    async def async_open_lock(self):
        return await self.async_request(API_LOCK_OPEN, "GET")

    async def async_emergency_open(self, lock_id=1, unlock_time=10000):
        data = {"locks": [{"lock_number": lock_id, "unlock_time": unlock_time}]}
        return await self.async_request(API_LOCK_EMERGENCY_OPEN, "POST", json_data=data)

    async def async_emergency_close(self, lock_id=1):
        data = {"locks": [lock_id]}
        return await self.async_request(API_LOCK_EMERGENCY_CLOSE, "POST", json_data=data)

    async def async_get_photo(self):
        return await self.async_request(API_PHOTO, "GET")

    async def async_reboot(self):
        return await self.async_request(API_REBOOT, "GET")

    async def async_call_start(self, number):
        data = {"number": f"sip:{number}@ru.sip.bas-ip.com"}
        return await self.async_request(API_CALL_START, "POST", json_data=data)

    async def async_call_end(self):
        return await self.async_request(API_CALL_END, "POST")

    async def async_set_language(self, language):
        return await self.async_request(f"{API_DEVICE_LANGUAGE}?language={language}", "POST")

    async def async_enable_dhcp(self):
        return await self.async_request(API_NETWORK_DHCP, "POST")

    async def async_set_volume(self, level: int):
        data = {"volume_level": level}
        return await self.async_request(API_SET_VOLUME, "POST", json_data=data)

    async def _async_button_updater(self):
        _LOGGER.info("🔄 Button updater started (interval: 1s)")
        
        while not self._button_stop:
            try:
                if not self.token:
                    await self.async_login()
                    if not self.token:
                        await asyncio.sleep(5)
                        continue
                
                doorbell, exit_button, door_open_too_long, door_state, exit_button_enabled = await self.async_check_events()
                
                if doorbell != self._doorbell_state:
                    self._doorbell_state = doorbell
                    self.async_update_listeners()
                    _LOGGER.info(f"📢 Doorbell state changed to: {doorbell}")
                
                if exit_button != self._exit_button_state:
                    self._exit_button_state = exit_button
                    self.async_update_listeners()
                    _LOGGER.info(f"🚪 Exit button pressed changed to: {exit_button}")
                
                if door_state != self._door_state:
                    self._door_state = door_state
                    self.async_update_listeners()
                    _LOGGER.info(f"🚪 Door state changed to: {door_state}")
                
                if door_open_too_long != self._door_open_too_long:
                    self._door_open_too_long = door_open_too_long
                    self.async_update_listeners()
                    _LOGGER.info(f"⏰ Door open too long changed to: {door_open_too_long}")
                
                if exit_button_enabled != self._exit_button_enabled:
                    self._exit_button_enabled = exit_button_enabled
                    self.async_update_listeners()
                    _LOGGER.info(f"🔘 Exit button enabled changed to: {exit_button_enabled}")
                
                await asyncio.sleep(1)
            except Exception as e:
                _LOGGER.error(f"Button updater error: {e}")
                await asyncio.sleep(5)

    def start_button_updater(self):
        if self._button_task is None or self._button_task.done():
            self._button_stop = False
            self._button_task = asyncio.create_task(self._async_button_updater())
            _LOGGER.info("Button updater task created")

    async def async_stop_button_updater(self):
        self._button_stop = True
        if self._button_task and not self._button_task.done():
            self._button_task.cancel()
            try:
                await self._button_task
            except asyncio.CancelledError:
                pass
            self._button_task = None
            _LOGGER.info("Button updater stopped")

    async def async_fetch_all_data(self):
        data = {}
        for sensor_key, sensor_info in SENSOR_TYPES.items():
            try:
                endpoint = sensor_info["endpoint"]
                if "{lockNumber}" in endpoint:
                    for lock_num in [1, 2]:
                        key = f"{sensor_key}_{lock_num}"
                        data[key] = await self.async_request(endpoint.replace("{lockNumber}", str(lock_num)), "GET")
                elif ":apartmentUid" in endpoint:
                    continue
                else:
                    data[sensor_key] = await self.async_request(endpoint, "GET")
                _LOGGER.debug(f"Fetched {sensor_key}")
            except Exception as e:
                _LOGGER.warning(f"Failed {sensor_key}: {e}")
                data[sensor_key] = {"error": str(e)}
        return data

    async def async_validate_auth(self):
        return await self.async_login()