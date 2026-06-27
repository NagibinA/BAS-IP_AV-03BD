import async_timeout
import hashlib
import aiohttp
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import *

class BASIPCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config):
        self.hass = hass
        self.host = config[CONF_HOST]
        self.port = config[CONF_PORT]
        self.password = config[CONF_PASSWORD]
        self.token = None
        self.base_url = f"http://{self.host}:{self.port}"
        self.connected = False
        
        super().__init__(
            hass,
            logger,
            name=DOMAIN,
            update_interval=timedelta(seconds=30)
        )

    async def _async_update_data(self):
        """Обновление данных всех датчиков"""
        try:
            async with async_timeout.timeout(10):
                return await self.async_fetch_all_data()
        except Exception as error:
            raise UpdateFailed(f"Error updating: {error}")

    async def async_validate_auth(self):
        """Проверка авторизации"""
        try:
            await self.async_login()
            self.connected = True
            return True
        except:
            self.connected = False
            return False

    async def async_login(self):
        """Авторизация и получение токена"""
        password_hash = hashlib.md5(self.password.encode()).hexdigest()
        url = f"{self.base_url}{API_LOGIN}?username=admin&password={password_hash}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.token = f"Bearer {data.get('token')}"
                    return True
                return False

    async def async_request(self, endpoint, method="GET", data=None, json_data=None):
        """Универсальный метод для запросов с авторизацией"""
        if not self.token:
            await self.async_login()
            
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": self.token}
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, data=data, json=json_data
            ) as resp:
                if resp.status == 401:  # Токен истек
                    await self.async_login()
                    headers["Authorization"] = self.token
                    async with session.request(
                        method, url, headers=headers, data=data, json=json_data
                    ) as resp2:
                        return await resp2.text() if resp2.status != 200 else None
                
                if resp.status != 200:
                    return None
                    
                content_type = resp.headers.get("content-type", "")
                if "application/json" in content_type:
                    return await resp.json()
                else:
                    return await resp.text()

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
        if result and isinstance(result, bytes):
            return result
        return None

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
        
        # Основная информация
        data["device_info"] = await self.async_get_device_info()
        data["network"] = await self.async_get_network_settings()
        data["sip_status"] = await self.async_request(API_SIP_STATUS, "GET")
        data["mac"] = await self.async_request(API_MAC, "GET")
        data["time"] = await self.async_request(API_DEVICE_TIME, "GET")
        data["mode"] = await self.async_request(API_CURRENT_MODE, "GET")
        data["lock_type"] = await self.async_request(API_LOCK_TYPE, "GET")
        data["rtsp"] = await self.async_request(API_RTSP, "GET")
        
        return data
