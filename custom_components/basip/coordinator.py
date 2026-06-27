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
        self.rtsp_password = config.get("rtsp_password", DEFAULT_RTSP_PASSWORD)
        self.token = None
        self.token_expiry = None
        self.base_url = f"http://{self.host}:{self.port}"
        self.connected = False
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=60))

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                if not self.token or await self._is_token_expired():
                    await self.async_login()
                return await self.async_fetch_all_data()
        except Exception as error:
            _LOGGER.error(f"Error updating: {error}")
            raise UpdateFailed(f"Error: {error}")

    async def _is_token_expired(self):
        if not self.token_expiry:
            return True
        return datetime.now() > self.token_expiry - timedelta(minutes=5)

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

    async def _ensure_valid_token(self):
        if not self.token or await self._is_token_expired():
            await self.async_login()
        return self.token is not None

    async def async_request(self, endpoint, method="GET", data=None, json_data=None, retry_count=2):
        if not await self._ensure_valid_token():
            return None
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            for attempt in range(retry_count):
                try:
                    async with session.request(method, url, headers=headers, data=data, json=json_data, timeout=10) as resp:
                        if resp.status == 401:
                            await self.async_login()
                            headers["Authorization"] = self.token
                            continue
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
        try:
            return await self.async_login()
        except:
            return False
