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
API_CALL_DROP = "/api/v1/device/call/drop"
API_CALL_DROP_LOCK_OPEN = "/api/v1/device/call/drop/lock-open"
API_RESCUE_SERVICE = "/api/v1/device/feature/rescue-service"
API_DEVICE_TIME = "/api/v1/device/time"
API_DEVICE_LANGUAGE = "/api/v1/device/language"
API_DEVICE_VIDEO = "/api/v1/device/settings/video"
API_DEVICE_RTSP = "/api/v1/device/settings/rtsp"
API_DEVICE_PAYLOAD = "/api/v1/device/settings/payload"
API_DEVICE_VOLUME = "/api/v1/device/settings/volume"
API_SET_VOLUME = "/api/v1/device/settings/volume"
API_DEVICE_RELAY = "/api/v1/device/relay/settings"
API_DEVICE_MODE = "/api/v1/device/mode/current"
API_LOCK_OPEN = "/api/v1/access/general/lock/open/remote/accepted/1"
API_LOCK_EMERGENCY_OPEN = "/api/v1/access/general/lock/open/emergency"
API_LOCK_EMERGENCY_CLOSE = "/api/v1/access/general/lock/close/emergency"
API_LOCK_TYPE = "/api/v1/access/general/lock/type"
API_MASTER_CARD = "/api/v1/access/general/unlock/card/master"
API_INPUT_CODE = "/api/v1/access/general/unlock/input/code"
API_APARTMENT_ITEM = "/api/v1/apartment/item"
API_PHOTO = "/api/v1/photo/file"
API_REBOOT = "/api/v1/system/reboot/run"
API_CALL_START = "/api/v1/system/debug/call/start"
API_CALL_END = "/api/v1/system/debug/call/end"
API_LOGS_ITEMS = "/api/v1/log/items"
API_DOOR_STATUS = "/api/v1/access/door/status"
API_DOOR_SENSOR = "/api/v1/access/door/sensor"
API_EXIT_BUTTON = "/api/v1/access/exit/button/toggle"
API_NETWORK_STATIC = "/api/v1/network/settings/static"
API_NETWORK_DHCP = "/api/v1/network/settings/dhcp"
API_CHANGE_PASSWORD = "/api/v1/security/password/web/admin"

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
LANGUAGES = [
    "English",
    "Russian",
    "Ukrainian",
    "Spanish",
    "Turkish",
    "Deutsch",
    "Italian",
    "French"
]

# Supported platforms
PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CAMERA,
    Platform.LOCK,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

# Sensor types with their API endpoints and display names
SENSOR_TYPES = {
    "bas_ip_info": {
        "endpoint": API_INFO,
        "icon": "mdi:information",
        "translation_key": "bas_ip_info"
    },
    "bas_ip_network_settings": {
        "endpoint": API_NETWORK_SETTINGS,
        "icon": "mdi:network",
        "translation_key": "bas_ip_network_settings"
    },
    "bas_ip_network_mac": {
        "endpoint": API_NETWORK_MAC,
        "icon": "mdi:ethernet",
        "translation_key": "bas_ip_network_mac"
    },
    "bas_ip_network_ntp": {
        "endpoint": API_NETWORK_NTP,
        "icon": "mdi:clock",
        "translation_key": "bas_ip_network_ntp"
    },
    "bas_ip_network_dst": {
        "endpoint": API_NETWORK_DST,
        "icon": "mdi:weather-sunset",
        "translation_key": "bas_ip_network_dst"
    },
    "bas_ip_network_timezone": {
        "endpoint": API_NETWORK_TIMEZONE,
        "icon": "mdi:map-clock",
        "translation_key": "bas_ip_network_timezone"
    },
    "bas_ip_network_management_link": {
        "endpoint": API_NETWORK_MANAGEMENT_LINK,
        "icon": "mdi:link",
        "translation_key": "bas_ip_network_management_link"
    },
    "bas_ip_network_management_server": {
        "endpoint": API_NETWORK_MANAGEMENT_SERVER,
        "icon": "mdi:server",
        "translation_key": "bas_ip_network_management_server"
    },
    "bas_ip_network_management_server_cert": {
        "endpoint": API_NETWORK_MANAGEMENT_SERVER_CERT,
        "icon": "mdi:certificate",
        "translation_key": "bas_ip_network_management_server_cert"
    },
    "bas_ip_sip_status": {
        "endpoint": API_SIP_STATUS,
        "icon": "mdi:phone",
        "translation_key": "bas_ip_sip_status"
    },
    "bas_ip_sip_settings": {
        "endpoint": API_SIP_SETTINGS,
        "icon": "mdi:phone-settings",
        "translation_key": "bas_ip_sip_settings"
    },
    "bas_ip_sip_enable": {
        "endpoint": API_SIP_ENABLE,
        "icon": "mdi:phone-check",
        "translation_key": "bas_ip_sip_enable"
    },
    "bas_ip_sip_reregister": {
        "endpoint": API_SIP_REREGISTER,
        "icon": "mdi:phone-refresh",
        "translation_key": "bas_ip_sip_reregister"
    },
    "bas_ip_call_auto_answer": {
        "endpoint": API_CALL_AUTO_ANSWER,
        "icon": "mdi:phone-in-talk",
        "translation_key": "bas_ip_call_auto_answer"
    },
    "bas_ip_call_drop": {
        "endpoint": API_CALL_DROP,
        "icon": "mdi:phone-hangup",
        "translation_key": "bas_ip_call_drop"
    },
    "bas_ip_call_drop_lock_open": {
        "endpoint": API_CALL_DROP_LOCK_OPEN,
        "icon": "mdi:lock-open-variant",
        "translation_key": "bas_ip_call_drop_lock_open"
    },
    "bas_ip_rescue_service": {
        "endpoint": API_RESCUE_SERVICE,
        "icon": "mdi:lifebuoy",
        "translation_key": "bas_ip_rescue_service"
    },
    "bas_ip_device_time": {
        "endpoint": API_DEVICE_TIME,
        "icon": "mdi:clock",
        "translation_key": "bas_ip_device_time"
    },
    "bas_ip_device_language": {
        "endpoint": API_DEVICE_LANGUAGE,
        "icon": "mdi:translate",
        "translation_key": "bas_ip_device_language"
    },
    "bas_ip_device_video": {
        "endpoint": API_DEVICE_VIDEO,
        "icon": "mdi:video",
        "translation_key": "bas_ip_device_video"
    },
    "bas_ip_device_rtsp": {
        "endpoint": API_DEVICE_RTSP,
        "icon": "mdi:video-input-antenna",
        "translation_key": "bas_ip_device_rtsp"
    },
    "bas_ip_device_payload": {
        "endpoint": API_DEVICE_PAYLOAD,
        "icon": "mdi:code-json",
        "translation_key": "bas_ip_device_payload"
    },
    "bas_ip_device_volume": {
        "endpoint": API_DEVICE_VOLUME,
        "icon": "mdi:volume-high",
        "translation_key": "bas_ip_device_volume"
    },
    "bas_ip_device_relay": {
        "endpoint": API_DEVICE_RELAY,
        "icon": "mdi:relay",
        "translation_key": "bas_ip_device_relay"
    },
    "bas_ip_device_mode": {
        "endpoint": API_DEVICE_MODE,
        "icon": "mdi:cog",
        "translation_key": "bas_ip_device_mode"
    },
    "bas_ip_lock_type": {
        "endpoint": API_LOCK_TYPE,
        "icon": "mdi:lock",
        "translation_key": "bas_ip_lock_type"
    },
    "bas_ip_master_card": {
        "endpoint": API_MASTER_CARD,
        "icon": "mdi:credit-card",
        "translation_key": "bas_ip_master_card"
    },
    "bas_ip_input_code": {
        "endpoint": API_INPUT_CODE,
        "icon": "mdi:keyboard",
        "translation_key": "bas_ip_input_code"
    },
    "bas_ip_door_sensor_settings": {
        "endpoint": API_DOOR_SENSOR,
        "icon": "mdi:door-sensor",
        "translation_key": "bas_ip_door_sensor_settings"
    },
    "bas_ip_exit_button_status": {
        "endpoint": API_EXIT_BUTTON,
        "icon": "mdi:exit-run",
        "translation_key": "bas_ip_exit_button_status"
    },
}

# Translation keys for binary sensors
BINARY_SENSOR_TRANSLATION_KEYS = {
    "doorbell": "doorbell",
    "exit_button": "exit_button",
    "door_sensor": "door_sensor",
    "door_open_too_long": "door_open_too_long",
    "exit_button_status": "exit_button_status",
}

# Configuration flow constants
CONF_CALL_NUMBERS = "call_numbers"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_IP_ADDRESS = "ip_address"
CONF_MASK = "mask"
CONF_GATEWAY = "gateway"
CONF_DNS = "dns"

# Default configuration values
DEFAULT_CALL_NUMBERS = ["79020"]
DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_MASK = "255.255.255.0"
DEFAULT_GATEWAY = "192.168.1.1"
DEFAULT_DNS = "8.8.8.8"

# Volume settings
MIN_VOLUME_LEVEL = 1
MAX_VOLUME_LEVEL = 6

# Service names
SERVICE_OPEN_LOCK = "open_lock"
SERVICE_EMERGENCY_OPEN = "emergency_open"
SERVICE_EMERGENCY_CLOSE = "emergency_close"
SERVICE_REBOOT = "reboot"
SERVICE_TAKE_PHOTO = "take_photo"
SERVICE_CALL_START = "call_start"
SERVICE_CALL_END = "call_end"
SERVICE_SET_LANGUAGE = "set_language"
SERVICE_SET_STATIC_IP = "set_static_ip"
SERVICE_ENABLE_DHCP = "enable_dhcp"
SERVICE_SET_VOLUME = "set_volume"

# Service field names
SERVICE_FIELD_LOCK_NUMBER = "lock_number"
SERVICE_FIELD_UNLOCK_TIME = "unlock_time"
SERVICE_FIELD_NUMBER = "number"
SERVICE_FIELD_LANGUAGE = "language"
SERVICE_FIELD_IP_ADDRESS = "ip_address"
SERVICE_FIELD_MASK = "mask"
SERVICE_FIELD_GATEWAY = "gateway"
SERVICE_FIELD_DNS = "dns"
SERVICE_FIELD_VOLUME = "volume"

# Maximum values
MAX_CALL_NUMBERS = 5
MAX_VOLUME_LEVEL = 6
MIN_VOLUME_LEVEL = 1
MAX_UNLOCK_TIME = 60000
DEFAULT_UNLOCK_TIME = 10000

# Lock numbers
LOCK_NUMBERS = [1, 2, 3, 4]

# Event types
EVENT_DOORBELL = "basip_doorbell"
EVENT_EXIT_BUTTON = "basip_exit_button"
EVENT_DOOR_OPEN = "basip_door_open"
EVENT_DOOR_CLOSED = "basip_door_closed"
EVENT_DOOR_OPEN_TOO_LONG = "basip_door_open_too_long"

# Log event keys
LOG_EVENT_OUTGOING_CALL = "outgoing_call"
LOG_EVENT_LOCK_OPENED_BY_EXIT_BTN = "lock_was_opened_by_exit_btn"
LOG_EVENT_LOCK_OPENED = "lock_was_opened"
LOG_EVENT_LOCK_CLOSED = "lock_was_closed"
LOG_EVENT_DOOR_OPEN = "door_is_open"
LOG_EVENT_DOOR_CLOSED = "door_is_closed"
LOG_EVENT_TIMEOUT_EXCEED = "timeout_is_exceed"

# Device attributes
ATTR_LAST_EVENT_TIMESTAMP = "last_event_timestamp"
ATTR_EXIT_BUTTON_ENABLED = "exit_button_enabled"
ATTR_UPDATE_INTERVAL = "update_interval"
ATTR_LAST_UPDATE = "last_update"
ATTR_VALUE = "value"

# Error messages
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_CANNOT_CONNECT_CURRENT = "cannot_connect_current"
ERROR_PASSWORD_REQUIRED = "password_required"
ERROR_HOST_REQUIRED = "host_required"
ERROR_IP_REQUIRED = "ip_required"
ERROR_IP_OCCUPIED = "ip_occupied"
ERROR_IP_CHANGE_FAILED = "ip_change_failed"
ERROR_PASSWORD_CHANGE_FAILED = "password_change_failed"
ERROR_IP_UNCHANGED = "ip_unchanged"
ERROR_UNKNOWN = "unknown"