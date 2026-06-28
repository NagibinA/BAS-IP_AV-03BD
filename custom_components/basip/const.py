"""Constants for BAS-IP Intercom integration."""
from homeassistant.const import Platform

DOMAIN = "basip"
MANUFACTURER = "BAS-IP"
MODEL = "Intercom Panel"

# API Endpoints
API_LOGIN = "/api/v1/login"
API_LOGOUT = "/api/v1/logout"
API_INFO = "/api/info"
API_NETWORK_SETTINGS = "/api/v1/network/settings"
API_NETWORK_MAC = "/api/v1/network/mac"
API_NETWORK_NTP = "/api/v1/network/ntp"
API_NETWORK_DST = "/api/v1/network/dst"
API_NETWORK_TIMEZONE = "/api/v1/network/timezone"
API_NETWORK_MANAGEMENT_LINK = "/api/v1/network/management/link"
API_NETWORK_MANAGEMENT_SERVER = "/api/v1/network/management/server"
API_NETWORK_MANAGEMENT_SERVER_CERT = "/api/v1/network/management/server/certificate"
API_SIP_STATUS = "/api/v1/sip/status"
API_SIP_SETTINGS = "/api/v1/device/sip/settings"
API_SIP_ENABLE = "/api/v1/device/sip/enable"
API_SIP_REREGISTER = "/api/v1/device/sip/reregister"
API_CALL_AUTO_ANSWER = "/api/v1/device/call/auto_answer"
API_RESCUE_SERVICE = "/api/v1/device/feature/rescue-service"
API_DEVICE_TIME = "/api/v1/device/time"
API_DEVICE_LANGUAGE = "/api/v1/device/language"
API_DEVICE_VIDEO = "/api/v1/device/settings/video"
API_DEVICE_RTSP = "/api/v1/device/settings/rtsp"
API_DEVICE_PAYLOAD = "/api/v1/device/settings/payload"
API_DEVICE_VOLUME = "/api/v1/device/settings/volume"
API_DEVICE_RELAY = "/api/v1/device/relay/settings"
API_DEVICE_MODE = "/api/v1/device/mode/current"
API_LOCK_OPEN = "/api/v1/access/general/lock/open/remote/accepted/1"
API_LOCK_EMERGENCY_OPEN = "/api/v1/access/general/lock/open/emergency"
API_LOCK_EMERGENCY_CLOSE = "/api/v1/access/general/lock/close/emergency"
API_LOCK_TYPE = "/api/v1/access/general/lock/type"
API_LOCK_TIMEOUT = "/api/v1/access/general/lock/timeout"
API_MASTER_CARD = "/api/v1/access/general/unlock/card/master"
API_INPUT_CODE = "/api/v1/access/general/unlock/input/code"
API_APARTMENT_ITEM = "/api/v1/apartment/item"
API_PHOTO = "/api/v1/photo/file"
API_REBOOT = "/api/v1/system/reboot/run"
API_CALL_START = "/api/v1/system/debug/call/start"
API_CALL_END = "/api/v1/system/debug/call/end"
API_LOGS_ITEMS = "/api/v1/log/items"

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
DEFAULT_UPDATE_INTERVAL = 60

# Supported languages
LANGUAGES = ["English", "Russian", "Ukrainian", "Spanish", "Turkish", "Deutsch", "Italian", "French"]

# Supported platforms
PLATFORMS = [Platform.CAMERA, Platform.LOCK, Platform.SWITCH, Platform.SENSOR, Platform.BUTTON]

# Sensor types with their API endpoints and display names
SENSOR_TYPES = {
    "info": {"endpoint": API_INFO, "name": "Device Info", "icon": "mdi:information"},
    "network_settings": {"endpoint": API_NETWORK_SETTINGS, "name": "Network Settings", "icon": "mdi:network"},
    "network_mac": {"endpoint": API_NETWORK_MAC, "name": "MAC Address", "icon": "mdi:ethernet"},
    "network_ntp": {"endpoint": API_NETWORK_NTP, "name": "NTP Server", "icon": "mdi:clock"},
    "network_dst": {"endpoint": API_NETWORK_DST, "name": "DST Settings", "icon": "mdi:weather-sunset"},
    "network_timezone": {"endpoint": API_NETWORK_TIMEZONE, "name": "Timezone", "icon": "mdi:map-clock"},
    "network_management_link": {"endpoint": API_NETWORK_MANAGEMENT_LINK, "name": "Link Settings", "icon": "mdi:link"},
    "network_management_server": {"endpoint": API_NETWORK_MANAGEMENT_SERVER, "name": "Management Server", "icon": "mdi:server"},
    "network_management_server_cert": {"endpoint": API_NETWORK_MANAGEMENT_SERVER_CERT, "name": "Server Certificate", "icon": "mdi:certificate"},
    "sip_status": {"endpoint": API_SIP_STATUS, "name": "SIP Status", "icon": "mdi:phone"},
    "sip_settings": {"endpoint": API_SIP_SETTINGS, "name": "SIP Settings", "icon": "mdi:phone-settings"},
    "sip_enable": {"endpoint": API_SIP_ENABLE, "name": "SIP Enabled", "icon": "mdi:phone-check"},
    "sip_reregister": {"endpoint": API_SIP_REREGISTER, "name": "SIP Reregister", "icon": "mdi:phone-refresh"},
    "call_auto_answer": {"endpoint": API_CALL_AUTO_ANSWER, "name": "Auto Answer", "icon": "mdi:phone-in-talk"},
    "rescue_service": {"endpoint": API_RESCUE_SERVICE, "name": "Rescue Service", "icon": "mdi:lifebuoy"},
    "device_time": {"endpoint": API_DEVICE_TIME, "name": "Device Time", "icon": "mdi:clock"},
    "device_language": {"endpoint": API_DEVICE_LANGUAGE, "name": "Language", "icon": "mdi:translate"},
    "device_video": {"endpoint": API_DEVICE_VIDEO, "name": "Video Resolution", "icon": "mdi:video"},
    "device_rtsp": {"endpoint": API_DEVICE_RTSP, "name": "RTSP Settings", "icon": "mdi:video-input-antenna"},
    "device_payload": {"endpoint": API_DEVICE_PAYLOAD, "name": "Payload Codec", "icon": "mdi:code-json"},
    "device_volume": {"endpoint": API_DEVICE_VOLUME, "name": "Volume", "icon": "mdi:volume-high"},
    "device_relay": {"endpoint": API_DEVICE_RELAY, "name": "Relay Settings", "icon": "mdi:relay"},
    "device_mode": {"endpoint": API_DEVICE_MODE, "name": "Mode", "icon": "mdi:cog"},
    "lock_type": {"endpoint": API_LOCK_TYPE, "name": "Lock Type", "icon": "mdi:lock"},
    "lock_timeout": {"endpoint": API_LOCK_TIMEOUT, "name": "Lock Timeout", "icon": "mdi:lock-clock"},
    "master_card": {"endpoint": API_MASTER_CARD, "name": "Master Card", "icon": "mdi:credit-card"},
    "input_code": {"endpoint": API_INPUT_CODE, "name": "Access Code", "icon": "mdi:keyboard"},
}
