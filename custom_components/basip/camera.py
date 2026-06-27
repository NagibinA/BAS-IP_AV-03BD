"""Camera platform for BAS-IP."""
from homeassistant.components.camera import Camera
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

from .const import DOMAIN, API_DEVICE_RTSP, DEFAULT_RTSP_PASSWORD

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the BAS-IP camera platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Получаем RTSP пароль из настроек интеграции
    rtsp_password = config_entry.data.get("rtsp_password", DEFAULT_RTSP_PASSWORD)
    
    # Получаем RTSP настройки с устройства (логин читаем из панели)
    rtsp_data = await coordinator.async_request(API_DEVICE_RTSP, "GET")
    
    if rtsp_data and isinstance(rtsp_data, dict):
        username = rtsp_data.get("username", "user")
        _LOGGER.debug(f"RTSP username from device: {username}")
    else:
        username = "user"
        _LOGGER.warning("Could not get RTSP username from device, using default: user")
    
    # Формируем RTSP URL
    rtsp_url = f"rtsp://{username}:{rtsp_password}@{coordinator.host}:8554/ch01"
    
    _LOGGER.info(f"RTSP URL configured: rtsp://{username}:****@{coordinator.host}:8554/ch01")
    
    async_add_entities([BASIPCamera(coordinator, rtsp_url)])


class BASIPCamera(CoordinatorEntity, Camera):
    """Representation of a BAS-IP camera."""

    def __init__(self, coordinator, rtsp_url: str):
        """Initialize the camera."""
        super().__init__(coordinator)
        self._rtsp_url = rtsp_url
        self._attr_name = "BAS-IP Camera"
        self._attr_unique_id = f"{coordinator.host}_camera"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )
        self._image = None

    @property
    def is_streaming(self) -> bool:
        """Return True if the camera supports streaming."""
        return True

    async def stream_source(self):
        """Return the RTSP stream source."""
        return self._rtsp_url

    async def async_camera_image(self, width=None, height=None):
        """Take a snapshot from the camera."""
        try:
            self._image = await self.coordinator.async_get_photo()
            return self._image
        except Exception as e:
            _LOGGER.error(f"Error taking snapshot: {e}")
            return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "rtsp_url": self._rtsp_url,
            "is_streaming": self.is_streaming,
        }
