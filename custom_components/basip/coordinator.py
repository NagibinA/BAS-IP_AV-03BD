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
    """Coordinate data updates for BAS-IP."""

    def __init__(self, hass: HomeAssistant, config):
        """Initialize coordinator."""
        self.hass = hass
        self.host = config.get(CONF_HOST)
        self.port = config.get(CONF_PORT, DEFAULT_PORT)
        self.password = config.get(CONF_PASSWORD)
        self.token = None
        self.token_expiry = None
        self.base_url = f"http://{self.host}:{self.port}"
        self.connected = False
        self._session = None

        # Настройка интервала обновления (60 секунд)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60)
        )

    async def _async_update_data(self):
        """Fetch all data from BAS-IP."""
        try:
            async with async_timeout.timeout(10):
                # Проверяем токен
                if not self.token or await self._is_token_expired():
                    await self.async_login()
                
                # Собираем все данные
                return await self.async_fetch_all_data()
        except Exception as error:
            _LOGGER.error(f"Error updating BAS-IP data: {error}")
            raise UpdateFailed(f"Error updating: {error}")

    async def _is_token_expired(self):
        """Check if token is expired."""
        if not self.token_expiry:
            return True
        return datetime.now() > self.token_expiry - timedelta(minutes=5)

    def _hash_password(self, password):
        """Calculate MD5 hash of password."""
        return hashlib.md5(password.encode()).hexdigest()

    async def async_login(self):
        """Authenticate and get token."""
        try:
            password_hash = self._hash_password(self.password)
            url = f"{self.base_url}{API_LOGIN}?username=admin&password={password_hash}"
            
            _LOGGER.debug(f"Attempting login to {self.host}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('token'):
                            self.token = f"Bearer {data['token']}"
                            self.token_expiry = datetime.now() + timedelta(hours=24)
                            self.connected = True
                            _LOGGER.info(f"Successfully authenticated with BAS-IP at {self.host}")
                            return True
                    else:
                        _LOGGER.error(f"Login failed with status {resp.status}: {await resp.text()}")
                        self.connected = False
                        return False
        except Exception as e:
            _LOGGER.error(f"Login error: {e}")
            self.connected = False
            return False

    async def _ensure_valid_token(self):
        """Ensure token is valid, refresh if needed."""
        if not self.token or await self._is_token_expired():
            _LOGGER.debug("Token expired or missing, refreshing...")
            await self.async_login()
        return self.token is not None

    async def async_request(self, endpoint, method="GET", data=None, json_data=None, retry_count=2):
        """Make authenticated request to BAS-IP API."""
        if not await self._ensure_valid_token():
            _LOGGER.error("No valid token available for request")
            return None

        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        
        _LOGGER.debug(f"Request: {method} {url}")
        
        async with aiohttp.ClientSession() as session:
            for attempt in range(retry_count):
                try:
                    async with session.request(
                        method, url, headers=headers, data=data, json=json_data, timeout=10
                    ) as resp:
                        if resp.status == 401:
                            _LOGGER.warning("Token expired, refreshing...")
                            await self.async_login()
                            if self.token:
                                headers["Authorization"] = self.token
                                continue
                            else:
                                _LOGGER.error("Failed to refresh token")
                                return None

                        if resp.status != 200:
                            _LOGGER.error(f"Request failed with status {resp.status}")
                            return None

                        content_type = resp.headers.get("content-type", "")
                        if "application/json" in content_type:
                            return await resp.json()
                        elif "image" in content_type or "application/octet-stream" in content_type:
                            return await resp.read()
                        else:
                            return await resp.text()

                except aiohttp.ClientError as e:
                    _LOGGER.warning(f"Request attempt {attempt + 1} failed: {e}")
                    if attempt == retry_count - 1:
                        raise
                    await asyncio.sleep(1)

        return None

    # ============= SPECIFIC METHODS =============

    async def async_open_lock(self):
        """Open the door lock."""
        return await self.async_request(API_LOCK_OPEN, "GET")

    async def async_emergency_open(self, lock_id=1, unlock_time=10000):
        """Emergency open lock."""
        data = {
            "locks": [{
                "lock_number": lock_id,
                "unlock_time": unlock_time
            }]
        }
        return await self.async_request(API_LOCK_EMERGENCY_OPEN, "POST", json_data=data)

    async def async_emergency_close(self, lock_id=1):
        """Close emergency mode."""
        data = {"locks": [lock_id]}
        return await self.async_request(API_LOCK_EMERGENCY_CLOSE, "POST", json_data=data)

    async def async_get_photo(self):
        """Take snapshot from camera."""
        return await self.async_request(API_PHOTO, "GET")

    async def async_reboot(self):
        """Reboot the device."""
        return await self.async_request(API_REBOOT, "GET")

    async def async_call_start(self, number):
        """Start outgoing call."""
        data = {"number": f"sip:{number}@ru.sip.bas-ip.com"}
        return await self.async_request(API_CALL_START, "POST", json_data=data)

    async def async_call_end(self):
        """End current call."""
        return await self.async_request(API_CALL_END, "POST")

    async def async_set_language(self, language):
        """Set device language."""
        return await self.async_request(f"{API_LANGUAGE}?language={language}", "POST")

    async def async_set_static_ip(self, ip, mask, gateway, dns):
        """Set static IP configuration."""
        data = {
            "ip_address": ip,
            "mask": mask,
            "gateway": gateway,
            "dns": dns
        }
        return await self.async_request(API_NETWORK_STATIC, "POST", json_data=data)

    async def async_enable_dhcp(self):
        """Enable DHCP."""
        return await self.async_request(API_NETWORK_DHCP, "POST")

    async def async_fetch_all_data(self):
        """Fetch all data for sensors."""
        data = {}
        
        _LOGGER.debug("Fetching all BAS-IP data...")
        
        # Получаем каждый тип данных отдельно
        try:
            data["device_info"] = await self.async_request(API_DEVICE_INFO, "GET")
            _LOGGER.debug("Device info fetched")
        except Exception as e:
            _LOGGER.warning(f"Failed to get device info: {e}")
            data["device_info"] = {"error": str(e)}

        try:
            data["network"] = await self.async_request(API_NETWORK, "GET")
            _LOGGER.debug("Network settings fetched")
        except Exception as e:
            _LOGGER.warning(f"Failed to get network settings: {e}")
            data["network"] = {"error": str(e)}

        try:
            data["sip_status"] = await self.async_request(API_SIP_STATUS, "GET")
            _LOGGER.debug("SIP status fetched")
        except Exception as e:
            _LOGGER.warning(f"Failed to get SIP status: {e}")
            data["sip_status"] = {"error": str(e)}

        try:
            data["mac"] = await self.async_request(API_MAC, "GET")
            _LOGGER.debug("MAC address fetched")
        except Exception as e:
            _LOGGER.warning(f"Failed to get MAC: {e}")
            data["mac"] = {"error": str(e)}

        try:
            data["time"] = await self.async_request(API_DEVICE_TIME, "GET")
            _LOGGER.debug("Device time fetched")
        except Exception as e:
            _LOGGER.warning(f"Failed to get time: {e}")
            data["time"] = {"error": str(e)}

        try:
            data["mode"] = await self.async_request(API_CURRENT_MODE, "GET")
            _LOGGER.debug("Current mode fetched")
        except Exception as e:
            _LOGGER.warning(f"Failed to get mode: {e}")
            data["mode"] = {"error": str(e)}

        try:
            data["lock_type"] = await self.async_request(API_LOCK_TYPE, "GET")
            _LOGGER.debug("Lock type fetched")
        except Exception as e:
            _LOGGER.warning(f"Failed to get lock type: {e}")
            data["lock_type"] = {"error": str(e)}

        try:
            data["rtsp"] = await self.async_request(API_RTSP, "GET")
            _LOGGER.debug("RTSP settings fetched")
        except Exception as e:
            _LOGGER.warning(f"Failed to get RTSP: {e}")
            data["rtsp"] = {"error": str(e)}

        _LOGGER.debug(f"Data fetch complete: {len(data)} items")
        return data

    async def async_validate_auth(self):
        """Validate authentication."""
        try:
            result = await self.async_login()
            self.connected = result
            return result
        except Exception:
            self.connected = False
            return False
