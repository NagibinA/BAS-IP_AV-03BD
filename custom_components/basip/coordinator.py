"""Coordinator for BAS-IP integration."""
import async_timeout
import hashlib
import aiohttp
import asyncio
import logging
from datetime import timedelta, datetime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from .const import *

_LOGGER = logging.getLogger(__name__)

class BASIPCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config):
        self.hass = hass
        self.host = config.get(CONF_HOST)
        self.port = config.get(CONF_PORT, DEFAULT_PORT)
        self.password = config.get(CONF_PASSWORD)
        self.token = None
        self.token_expiry = None
        self.base_url = f"http://{self.host}:{self.port}"
        self.connected = False
        
        self._doorbell_state = False
        self._exit_button_state = False
        self._door_state = False
        self._door_open_too_long = False
        
        self._last_doorbell_timestamp = None
        self._last_exit_timestamp = None
        self._last_door_timestamp = None
        self._last_door_open_too_long_timestamp = None
        
        self._button_task = None
        self._button_stop = False
        
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=60))

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

    async def async_init_door_open_too_long(self):
        """При старте проверить, есть ли событие lock_is_opened_to_long в логах."""
        try:
            logs = await self.async_get_logs(limit=10)
            if not logs or not isinstance(logs, dict):
                return
            
            items = logs.get("list_items", [])
            if not items:
                return
            
            for item in items:
                name_key = item.get("name", {}).get("key", "")
                if name_key == "lock_is_opened_to_long":
                    self._door_open_too_long = True
                    self._last_door_open_too_long_timestamp = item.get("timestamp")
                    self.async_update_listeners()
                    _LOGGER.info("🔵 Initial door_open_too_long set to: True")
                    return
            
            self._door_open_too_long = False
            self.async_update_listeners()
            _LOGGER.info("🔵 Initial door_open_too_long set to: False")
            
        except Exception as e:
            _LOGGER.warning(f"Failed to initialize door_open_too_long: {e}")

    async def async_check_events(self) -> tuple:
        doorbell = False
        exit_button = False
        door_open = self._door_state
        door_open_too_long = self._door_open_too_long
        
        _LOGGER.debug(f"Checking events... Current door_open_too_long: {door_open_too_long}")
        
        try:
            logs = await self.async_get_logs(limit=10)
            if not logs or not isinstance(logs, dict):
                _LOGGER.debug("No logs received or invalid format")
                return doorbell, exit_button, door_open, door_open_too_long
            
            items = logs.get("list_items", [])
            if not items:
                _LOGGER.debug("No items in logs")
                return doorbell, exit_button, door_open, door_open_too_long
            
            _LOGGER.debug(f"Processing {len(items)} log items")
            
            for item in items:
                name_key = item.get("name", {}).get("key", "")
                timestamp_ms = item.get("timestamp")
                if not timestamp_ms:
                    continue
                
                if name_key == "lock_is_opened_to_long":
                    door_open_too_long = True
                    self._last_door_open_too_long_timestamp = timestamp_ms
                    _LOGGER.info("🔴 DOOR OPEN TOO LONG DETECTED!")
                    continue
                
                timestamp_sec = timestamp_ms / 1000
                event_time = datetime.fromtimestamp(timestamp_sec)
                if datetime.now() - event_time > timedelta(seconds=3):
                    continue
                
                if name_key == "outgoing_call":
                    doorbell = True
                    self._last_doorbell_timestamp = timestamp_ms
                    _LOGGER.debug("Doorbell event detected")
                elif name_key == "lock_was_opened_by_exit_btn":
                    exit_button = True
                    self._last_exit_timestamp = timestamp_ms
                    _LOGGER.debug("Exit button event detected")
                elif name_key == "door_was_opened":
                    door_open = True
                    self._last_door_timestamp = timestamp_ms
                    _LOGGER.debug("Door opened event detected")
                elif name_key == "door_was_closed":
                    door_open = False
                    self._last_door_timestamp = timestamp_ms
                    if self._door_open_too_long:
                        door_open_too_long = False
                        self._last_door_open_too_long_timestamp = None
                        _LOGGER.info("🔵 Door open too long reset (door closed)")
            
            _LOGGER.debug(f"Final states: doorbell={doorbell}, exit_button={exit_button}, door_open={door_open}, door_open_too_long={door_open_too_long}")
            return doorbell, exit_button, door_open, door_open_too_long
        except Exception as e:
            _LOGGER.warning(f"Failed to check events: {e}")
            return doorbell, exit_button, door_open, door_open_too_long

    async def _async_button_updater(self):
        _LOGGER.info("🔄 Button updater started")
        
        await self.async_init_door_open_too_long()
        
        while not self._button_stop:
            try:
                if not self.token:
                    await self.async_login()
                    if not self.token:
                        await asyncio.sleep(5)
                        continue
                
                doorbell, exit_button, door_open, door_open_too_long = await self.async_check_events()
                
                if doorbell != self._doorbell_state:
                    self._doorbell_state = doorbell
                    self.async_update_listeners()
                    _LOGGER.info(f"📢 Doorbell state changed to: {doorbell}")
                
                if exit_button != self._exit_button_state:
                    self._exit_button_state = exit_button
                    self.async_update_listeners()
                    _LOGGER.info(f"🚪 Exit button state changed to: {exit_button}")
                
                if door_open != self._door_state:
                    self._door_state = door_open
                    self.async_update_listeners()
                    _LOGGER.info(f"🚪 Door state changed to: {door_open}")
                
                if door_open_too_long != self._door_open_too_long:
                    self._door_open_too_long = door_open_too_long
                    self.async_update_listeners()
                    _LOGGER.info(f"⏰ Door open too long changed to: {door_open_too_long}")
                
                await asyncio.sleep(3)
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

    async def async_set_static_ip(self, ip, mask, gateway, dns):
        data = {"ip_address": ip, "mask": mask, "gateway": gateway, "dns": dns}
        return await self.async_request(API_NETWORK_STATIC, "POST", json_data=data)

    async def async_enable_dhcp(self):
        return await self.async_request(API_NETWORK_DHCP, "POST")

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