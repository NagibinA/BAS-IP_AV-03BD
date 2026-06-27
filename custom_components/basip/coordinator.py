import async_timeout
import hashlib
import aiohttp
import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from .const import *

_LOGGER = logging.getLogger(__name__)

class BASIPCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config):
        self.hass = hass
        self.host = config[CONF_HOST]
        self.port = config[CONF_PORT]
        self.password = config[CONF_PASSWORD]
        self.token = None
        self.token_expiry = None
        self.base_url = f"http://{self.host}:{self.port}"
        self.connected = False
        self._session = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60)  # Обновление каждую минуту
        )

    async def _async_update_data(self):
        """Обновление данных всех датчиков"""
        try:
            async with async_timeout.timeout(10):
                # Проверяем токен перед обновлением
                if not self.token or await self._is_token_expired():
                    await self.async_login()
                return await self.async_fetch_all_data()
        except Exception as error:
            _LOGGER.error(f"Error updating BAS-IP data: {error}")
            raise UpdateFailed(f"Error updating: {error}")

    async def _is_token_expired(self):
        """Проверка истечения срока токена"""
        if not self.token_expiry:
            return True
        # Проверяем, не истек ли токен (с запасом в 5 минут)
        from datetime import datetime, timedelta
        if datetime.now() > self.token_expiry - timedelta(minutes=5):
            return True
        return False

    def _hash_password(self, password):
        """Расчет MD5 хеша пароля"""
        return hashlib.md5(password.encode()).hexdigest()

    async def async_login(self):
        """Авторизация и получение токена с правильным хешированием"""
        try:
            # Вычисляем MD5 хеш пароля
            password_hash = self._hash_password(self.password)
            url = f"{self.base_url}{API_LOGIN}?username=admin&password={password_hash}"
            
            _LOGGER.debug(f"Attempting login to {self.host} with password hash: {password_hash}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('token'):
                            self.token = f"Bearer {data['token']}"
                            # Устанавливаем время истечения токена (обычно 24 часа)
                            from datetime import datetime, timedelta
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
        """Гарантирует, что токен валиден, обновляет если нужно"""
        if not self.token or await self._is_token_expired():
            _LOGGER.debug("Token expired or missing, refreshing...")
            await self.async_login()
        return self.token is not None

    async def async_request(self, endpoint, method="GET", data=None, json_data=None, retry_count=2):
        """Универсальный метод для запросов с авторизацией и автоматическим обновлением токена"""
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
                        # Если токен недействителен (401), обновляем и пробуем снова
                        if resp.status == 401:
                            _LOGGER.warning("Token expired, refreshing and retrying...")
                            await self.async_login()
                            if self.token:
                                headers["Authorization"] = self.token
                                continue  # Повторяем запрос с новым токеном
                            else:
                                _LOGGER.error("Failed to refresh token")
                                return None
                        
                        if resp.status != 200:
                            _LOGGER.error(f"Request failed with status {resp.status}: {await resp.text()}")
                            return None
                            
                        # Обработка ответа в зависимости от типа контента
                        content_type = resp.headers.get("content-type", "")
                        if "application/json" in content_type:
                            return await resp.json()
                        elif "image" in content_type or "application/octet-stream" in content_type:
                            # Для бинарных данных (фото, бэкап)
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
    
    async def async_open_lock(self, lock_id=1):
        """Открыть замок"""
        return await self.async_request(API_LOCK_OPEN, "GET")

    async def async_emergency_open(self, lock_id=1, unlock_time=10000):
        """Аварийное открытие"""
        data = {
            "locks": [{
                "lock_number": lock_id,
                "unlock_time": unlock_time
            }]
        }
        return await self.async_request(API_LOCK_EMERGENCY_OPEN, "POST", json_data=data)

    async def async_emergency_close(self, lock_id=1):
        """Закрыть аварийный режим"""
        data = {"locks": [lock_id]}
        return await self.async_request(API_LOCK_EMERGENCY_CLOSE, "POST", json_data=data)

    async def async_get_photo(self):
        """Сделать снимок с камеры"""
        result = await self.async_request(API_PHOTO, "GET")
        return result

    async def async_reboot(self):
        """Перезагрузка устройства"""
        return await self.async_request(API_REBOOT, "GET")

    async def async_call_start(self, number):
        """Начать вызов"""
        data = {"number": f"sip:{number}@ru.sip.bas-ip.com"}
        return await self.async_request(API_CALL_START, "POST", json_data=data)

    async def async_call_end(self):
        """Завершить вызов"""
        return await self.async_request(API_CALL_END, "POST")

    async def async_set_language(self, language):
        """Установить язык"""
        return await self.async_request(
            f"{API_LANGUAGE}?language={language}", "POST"
        )

    async def async_get_device_info(self):
        """Получить информацию об устройстве"""
        return await self.async_request(API_DEVICE_INFO, "GET")

    async def async_get_network_settings(self):
        """Получить сетевые настройки"""
        return await self.async_request(API_NETWORK, "GET")

    async def async_set_static_ip(self, ip, mask, gateway, dns):
        """Установить статический IP"""
        data = {
            "ip_address": ip,
            "mask": mask,
            "gateway": gateway,
            "dns": dns
        }
        return await self.async_request(
            "/api/v1/network/settings/static", "POST", json_data=data
        )

    async def async_enable_dhcp(self):
        """Включить DHCP"""
        return await self.async_request("/api/v1/network/settings/dhcp", "POST")

    async def async_fetch_all_data(self):
        """Собрать все данные для датчиков"""
        data = {}
        
        try:
            data["device_info"] = await self.async_get_device_info()
        except Exception as e:
            _LOGGER.warning(f"Failed to get device info: {e}")
            
        try:
            data["network"] = await self.async_get_network_settings()
        except Exception as e:
            _LOGGER.warning(f"Failed to get network settings: {e}")
            
        try:
            data["sip_status"] = await self.async_request(API_SIP_STATUS, "GET")
        except Exception as e:
            _LOGGER.warning(f"Failed to get SIP status: {e}")
            
        try:
            data["mac"] = await self.async_request(API_MAC, "GET")
        except Exception as e:
            _LOGGER.warning(f"Failed to get MAC: {e}")
            
        try:
            data["time"] = await self.async_request(API_DEVICE_TIME, "GET")
        except Exception as e:
            _LOGGER.warning(f"Failed to get time: {e}")
            
        try:
            data["mode"] = await self.async_request(API_CURRENT_MODE, "GET")
        except Exception as e:
            _LOGGER.warning(f"Failed to get mode: {e}")
            
        try:
            data["lock_type"] = await self.async_request(API_LOCK_TYPE, "GET")
        except Exception as e:
            _LOGGER.warning(f"Failed to get lock type: {e}")
            
        try:
            data["rtsp"] = await self.async_request(API_RTSP, "GET")
        except Exception as e:
            _LOGGER.warning(f"Failed to get RTSP: {e}")
        
        return data

    async def async_validate_auth(self):
        """Проверка авторизации"""
        try:
            result = await self.async_login()
            self.connected = result
            return result
        except:
            self.connected = False
            return False
