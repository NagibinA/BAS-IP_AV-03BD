"""Config flow for BAS-IP integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from homeassistant.core import HomeAssistant, callback
import logging

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_RTSP_PASSWORD

_LOGGER = logging.getLogger(__name__)

class BASIPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BAS-IP Intercom."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        self._errors = {}

        if user_input is not None:
            # Проверяем, что пароль не пустой
            if not user_input.get(CONF_PASSWORD):
                self._errors["base"] = "password_required"
                return self._show_form(user_input)

            # Проверяем, что IP адрес не пустой
            if not user_input.get(CONF_HOST):
                self._errors["base"] = "host_required"
                return self._show_form(user_input)

            # Пытаемся подключиться к устройству
            from .coordinator import BASIPCoordinator

            coordinator = BASIPCoordinator(self.hass, user_input)
            valid = await coordinator.async_validate_auth()

            if valid:
                # Создаем запись с уникальным ID
                return self.async_create_entry(
                    title=f"BAS-IP ({user_input[CONF_HOST]})",
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT),
                        "rtsp_password": user_input.get("rtsp_password", DEFAULT_RTSP_PASSWORD),
                    }
                )
            else:
                self._errors["base"] = "cannot_connect"
                return self._show_form(user_input)

        # Показываем форму для ввода данных
        return self._show_form()

    def _show_form(self, user_input=None):
        """Show the configuration form."""
        if user_input is None:
            user_input = {}

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "")): str,
            vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "")): str,
            vol.Optional(CONF_PORT, default=user_input.get(CONF_PORT, DEFAULT_PORT)): int,
            vol.Optional("rtsp_password", default=user_input.get("rtsp_password", DEFAULT_RTSP_PASSWORD)): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=self._errors,
            description_placeholders={
                "host_help": "Example: 192.168.1.90",
                "password_help": "Default password is usually 123456",
                "rtsp_help": "RTSP password for camera stream (default: 1234)",
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return BASIPOptionsFlow(config_entry)


class BASIPOptionsFlow(config_entries.OptionsFlow):
    """Handle BAS-IP options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = vol.Schema({
            vol.Optional(
                "update_interval",
                default=self.config_entry.options.get("update_interval", 60)
            ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
            vol.Optional(
                "rtsp_password",
                default=self.config_entry.options.get("rtsp_password", 
                    self.config_entry.data.get("rtsp_password", DEFAULT_RTSP_PASSWORD))
            ): str,
        })

        return self.async_show_form(step_id="init", data_schema=options)
