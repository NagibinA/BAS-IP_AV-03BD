"""Constants for BAS-IP Intercom integration."""
from homeassistant.const import Platform

DOMAIN = "basip"
MANUFACTURER = "BAS-IP"
MODEL = "Intercom Panel"

# API Endpoints
API_LOGIN = "/api/v1/login"
API_LOGOUT = "/api/v1/logout"
API_LANGUAGE = "/api/v1/device/language"
API_SIP_STATUS = "/api/v1/sip/status"
API_NETWORK = "/api/v1/network/settings"
API_MAC = "/api/v1/network/mac"
API_DEVICE_INFO = "/api/info"
API_DEVICE_TIME = "/api/v1/device/time"
API_CURRENT_MODE = "/api/v1/device/mode/current"
API_LOCK_OPEN = "/api/v1/access/general/lock/open/remote/accepted/1"
API_LOCK_EMERGENCY_OPEN = "/api/v1/access/general/lock/open/emergency"
API_LOCK_EMERGENCY_CLOSE = "/api/v1/access/general/lock/close/emergency"
API_LOCK_TYPE = "/api/v1/access/general/lock/type"
API_MASTER_CARD = "/api/v1/access/general/unlock/card/master"
API_CODE_UNLOCK = "/api/v1/access/general/unlock/input/code"
API_PHOTO = "/api/v1/photo/file"
API_REBOOT = "/api/v1/system/reboot/run"
API_BACKUP = "/api/v1/system/settings/backup/all"
API_FIRMWARE_CHECK = "/api/v1/system/firmware/check/status"
API_RTSP = "/api/v1/device/settings/rtsp"
API_VIDEO_RESOLUTION = "/api/v1/device/settings/video"
API_CALL_START = "/api/v1/system/debug/call/start"
API_CALL_END = "/api/v1/system/debug/call/end"
API_IDENTIFIERS = "/api/v1/access/identifier/items"

# Network settings
API_NETWORK_STATIC = "/api/v1/network/settings/static"
API_NETWORK_DHCP = "/api/v1/network/settings/dhcp"

# Default settings
DEFAULT_PASSWORD = "123456"
DEFAULT_PORT = 80
TIMEOUT = 10

# Token settings
TOKEN_EXPIRY_HOURS = 24
TOKEN_RENEWAL_MINUTES = 5

# Update intervals
DEFAULT_UPDATE_INTERVAL = 60  # seconds

# Supported languages
LANGUAGES = [
    "English",
    "Russian",
    "Ukrainian",
    "Spanish",
    "Turkish",
]

# Supported platforms (using Platform enum for HA 2026.x compatibility)
PLATFORMS = [
    Platform.CAMERA,
    Platform.LOCK,
    Platform.SWITCH,
    Platform.SENSOR,
]
