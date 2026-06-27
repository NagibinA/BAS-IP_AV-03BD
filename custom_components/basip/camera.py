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
    async_add_entities([BASIPCamera(coordinator)])


class BASIPCamera(CoordinatorEntity, Camera):
    """Representation of a BAS-IP camera with photo + RTSP."""

    def __init__(self, coordinator):
        """Initialize the camera."""
        super().__init__(coordinator)
        self._attr_name = "BAS-IP Camera"
        self._attr_unique_id = f"{coordinator.host}_camera"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="BAS-IP Intercom",
            manufacturer="BAS-IP",
            model="Intercom Panel",
        )
        self._image = None
        self._rtsp_url = None
        self._rtsp_username = None

    async def async_added_to_hass(self):
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        
        rtsp_data = await self.coordinator.async_request(API_DEVICE_RTSP, "GET")
        if rtsp_data and isinstance(rtsp_data, dict):
            self._rtsp_username = rtsp_data.get("username", "user")
        else:
            self._rtsp_username = "user"
            _LOGGER.warning("Could not get RTSP username, using default: user")
        
        rtsp_password = self.coordinator.rtsp_password
        self._rtsp_url = f"rtsp://{self._rtsp_username}:{rtsp_password}@{self.coordinator.host}:8554/ch01"
        _LOGGER.info(f"RTSP URL configured: rtsp://{self._rtsp_username}:****@{self.coordinator.host}:8554/ch01")

    @property
    def is_streaming(self) -> bool:
        return True

    async def stream_source(self):
        return self._rtsp_url

    async def async_camera_image(self, width=None, height=None):
        try:
            self._image = await self.coordinator.async_get_photo()
            if self._image:
                _LOGGER.debug("Snapshot taken successfully")
            return self._image
        except Exception as e:
            _LOGGER.error(f"Error taking snapshot: {e}")
            return None

    @property
    def extra_state_attributes(self):
        return {
            "rtsp_url": self._rtsp_url,
            "is_streaming": self.is_streaming,
            "snapshot_source": "API /api/v1/photo/file",
            "stream_source": "RTSP",
        }
