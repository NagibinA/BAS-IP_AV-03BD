import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from .const import DOMAIN, DEFAULT_PORT

class BASIPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            # Проверяем подключение
            from .coordinator import BASIPCoordinator
            coordinator = BASIPCoordinator(self.hass, user_input)
            await coordinator.async_validate_auth()
            
            if coordinator.connected:
                return self.async_create_entry(
                    title=f"BAS-IP ({user_input[CONF_HOST]})",
                    data=user_input
                )
            else:
                errors["base"] = "cannot_connect"

        # Форма ввода
        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )
