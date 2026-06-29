"""Config flow for BAS-IP integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from homeassistant.core import HomeAssistant, callback
import logging

from .const import DOMAIN, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

class BASIPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._errors = {}

    async def async_step_user(self, user_input=None):
        self._errors = {}

        if user_input is not None:
            if not user_input.get(CONF_PASSWORD):
                self._errors["base"] = "password_required"
                return self._show_form(user_input)

            if not user_input.get(CONF_HOST):
                self._errors["base"] = "host_required"
                return self._show_form(user_input)

            from .coordinator import BASIPCoordinator

            coordinator = BASIPCoordinator(self.hass, user_input)
            valid = await coordinator.async_validate_auth()

            if valid:
                return self.async_create_entry(
                    title=f"BAS-IP ({user_input[CONF_HOST]})",
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT),
                    }
                )
            else:
                self._errors["base"] = "cannot_connect"
                return self._show_form(user_input)

        return self._show_form()

    def _show_form(self, user_input=None):
        if user_input is None:
            user_input = {}

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "")): str,
            vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "")): str,
            vol.Optional(CONF_PORT, default=user_input.get(CONF_PORT, DEFAULT_PORT)): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=self._errors,
            description_placeholders={
                "host_help": "Example: 192.168.1.90",
                "password_help": "Default password is usually 123456",
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BASIPOptionsFlow(config_entry)


class BASIPOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Собираем только непустые номера
            numbers = []
            for i in range(1, 6):
                key = f"call_number_{i}"
                if key in user_input and user_input[key] and str(user_input[key]).strip():
                    numbers.append(str(user_input[key]).strip())

            user_input["call_numbers"] = numbers if numbers else ["79020"]

            for i in range(1, 6):
                user_input.pop(f"call_number_{i}", None)

            return self.async_create_entry(title="", data=user_input)

        current_numbers = self._config_entry.options.get("call_numbers", ["79020"])
        if isinstance(current_numbers, str):
            current_numbers = [n.strip() for n in current_numbers.split(",") if n.strip()]
        if not current_numbers:
            current_numbers = ["79020"]

        while len(current_numbers) < 5:
            current_numbers.append("")

        schema = {
            vol.Optional(
                "update_interval",
                default=self._config_entry.options.get("update_interval", 60)
            ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
        }

        for i in range(1, 6):
            # Используем suggested_value вместо default
            schema[vol.Optional(
                f"call_number_{i}",
                description={"suggested_value": current_numbers[i-1]}
            )] = str

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
            description_placeholders={
                "call_numbers_help": "Enter up to 5 phone numbers. Leave empty to remove."
            }
        )