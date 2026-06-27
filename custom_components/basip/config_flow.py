import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from homeassistant.core import HomeAssistant, callback
import hashlib
from .const import DOMAIN, DEFAULT_PORT

class BASIPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        self._errors = {}

    async def async_step_user(self, user_input=None):
        self._errors = {}
        
        if user_input is not None:
            # Валидируем введенные данные
            host = user_input.get(CONF_HOST)
            password = user_input.get(CONF_PASSWORD)
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            
            # Проверяем формат пароля (не пустой)
            if not password or len(password) < 1:
                self._errors["base"] = "password_required"
            
            # Проверяем IP адрес (простая валидация)
            if not host:
                self._errors["base"] = "host_required"
            
            if not self._errors:
                # Проверяем подключение
                from .coordinator import BASIPCoordinator
                coordinator = BASIPCoordinator(self.hass, user_input)
                valid = await coordinator.async_validate_auth()
                
                if valid:
                    # Создаем запись с уникальным ID
                    return self.async_create_entry(
                        title=f"BAS-IP ({host})",
                        data={
                            CONF_HOST: host,
                            CONF_PASSWORD: password,
                            CONF_PORT: port
                        }
                    )
                else:
                    self._errors["base"] = "cannot_connect"
        
        # Показываем форму ввода
        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=""): str,
            vol.Required(CONF_PASSWORD, default=""): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=self._errors,
            description_placeholders={
                "host_help": "Example: 192.168.1.90",
                "password_help": "Default password is usually 123456"
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BASIPOptionsFlow(config_entry)

class BASIPOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = vol.Schema({
            vol.Optional(
                "update_interval",
                default=self.config_entry.options.get("update_interval", 60)
            ): int,
        })

        return self.async_show_form(step_id="init", data_schema=options)
