"""Camera platform for BAS-IP."""
from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.components.stream import Stream
from homeassistant.helpers.entity import DeviceInfo
import logging
import base64
import secrets

from .const import DOMAIN, API_DEVICE_RTSP, API_PHOTO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the BAS-IP camera platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([BASIPCamera(coordinator)])


class BASIPCamera(Camera):
    """BAS-IP Camera with RTSP streaming and snapshot."""

    def __init__(self, coordinator):
        """Initialize the camera."""
        super().__init__()
        
        self.coordinator = coordinator
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
        self._rtsp_configured = False
        self._stream = None
        self.access_tokens = [secrets.token_hex(32)]
        self._attr_supported_features = CameraEntityFeature.STREAM

    async def async_added_to_hass(self):
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        
        try:
            rtsp_data = await self.coordinator.async_request(API_DEVICE_RTSP, "GET")
            if rtsp_data and isinstance(rtsp_data, dict):
                self._rtsp_username = rtsp_data.get("username", "user")
            else:
                self._rtsp_username = "user"
                _LOGGER.warning("Could not get RTSP username, using default: user")
            
            rtsp_password = self.coordinator.rtsp_password
            self._rtsp_url = f"rtsp://{self._rtsp_username}:{rtsp_password}@{self.coordinator.host}:8554/ch01"
            self._rtsp_configured = True
            _LOGGER.info(f"RTSP URL configured")
            
            if self.hass and self._rtsp_url:
                self._stream = Stream(
                    self.hass,
                    self._rtsp_url,
                    options={
                        "rtsp_transport": "tcp",
                        "segment_duration": 2,           # Минимальная задержка
                        "part_duration": 0.5,            # LL-HLS
                        "analyzeduration": 1000000,      # Уменьшен для скорости
                        "probesize": 1000000,            # Уменьшен для скорости
                        "buffer_size": 512000,           # 512 КБ — меньше задержка
                        "max_delay": 300000,             # 0.3 секунды
                        "reorder_queue_size": 512,       # Меньше очередь
                        "flags": "low_delay",
                    }
                )
                await self._stream.async_setup()
                _LOGGER.info("RTSP stream registered with low-latency settings")
            
        except Exception as e:
            _LOGGER.error(f"Error setting up RTSP: {e}")

    @property
    def is_streaming(self) -> bool:
        """Return True if the camera supports streaming."""
        return self._rtsp_configured

    async def stream_source(self):
        """Return the RTSP stream source."""
        return self._rtsp_url

    async def async_camera_image(self, width=None, height=None):
        """Take a snapshot."""
        try:
            result = await self.coordinator.async_request(API_PHOTO, "GET")

            if result is None:
                _LOGGER.warning("No image data received")
                return None

            if isinstance(result, str):
                try:
                    self._image = base64.b64decode(result)
                    _LOGGER.debug("Snapshot taken (Base64)")
                except Exception:
                    self._image = result.encode()
                    _LOGGER.debug("Snapshot taken (raw)")
            else:
                self._image = result
                _LOGGER.debug("Snapshot taken (bytes)")

            return self._image

        except Exception as e:
            _LOGGER.error(f"Error taking snapshot: {e}")
            return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        attrs = {
            "is_streaming": self.is_streaming,
            "stream_source": "RTSP",
        }
        if self._rtsp_url:
            attrs["rtsp_url"] = self._rtsp_url
        return attrs