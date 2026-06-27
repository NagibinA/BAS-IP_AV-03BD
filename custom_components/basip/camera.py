import io
import aiohttp
from homeassistant.components.camera import Camera
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([BASIPCamera(coordinator)])

class BASIPCamera(Camera):
    def __init__(self, coordinator):
        super().__init__()
        self.coordinator = coordinator
        self._attr_name = "BAS-IP Camera"
        self._attr_unique_id = f"{coordinator.host}_camera"
        self._image = None

    async def async_camera_image(self, width=None, height=None):
        """Получить снимок с камеры"""
        try:
            self._image = await self.coordinator.async_get_photo()
            return self._image
        except Exception:
            return None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.host)},
            "name": "BAS-IP Intercom",
            "manufacturer": "BAS-IP",
        }
