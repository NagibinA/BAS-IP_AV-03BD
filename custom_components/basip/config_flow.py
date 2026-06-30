"""Config flow for BAS-IP integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback
import logging
import asyncio
import subprocess

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class BASIPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._errors = {}
        self._host = None
        self._password = None
        self._mask = None
        self._gateway = None
        self._dns = None

    async def async_step_user(self, user_input=None):
        """Первоначальная установка."""
        self._errors = {}

        if user_input is not None:
            if not user_input.get(CONF_PASSWORD):
                self._errors["base"] = "password_required"
                return self._show_user_form(user_input)

            if not user_input.get(CONF_HOST):
                self._errors["base"] = "host_required"
                return self._show_user_form(user_input)

            from .coordinator import BASIPCoordinator
            config = {
                CONF_HOST: user_input[CONF_HOST],
                CONF_PASSWORD: user_input[CONF_PASSWORD],
                "call_numbers": ["79020"],
            }
            coordinator = BASIPCoordinator(self.hass, config)
            valid = await coordinator.async_validate_auth()

            if valid:
                self._host = user_input[CONF_HOST]
                self._password = user_input[CONF_PASSWORD]
                self._mask = user_input.get("mask")
                self._gateway = user_input.get("gateway")
                self._dns = user_input.get("dns")
                return await self.async_step_numbers()
            else:
                self._errors["base"] = "cannot_connect"
                return self._show_user_form(user_input)

        return self._show_user_form()

    def _show_user_form(self, user_input=None):
        if user_input is None:
            user_input = {}

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "192.168.1.90")): str,
            vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "123456")): str,
            vol.Required("mask", default=user_input.get("mask", "255.255.255.0")): str,
            vol.Required("gateway", default=user_input.get("gateway", "192.168.1.1")): str,
            vol.Required("dns", default=user_input.get("dns", "8.8.8.8")): str,
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

    async def async_step_numbers(self, user_input=None):
        self._errors = {}

        if user_input is not None:
            numbers = []
            for i in range(1, 6):
                key = f"call_number_{i}"
                if key in user_input and user_input[key] and str(user_input[key]).strip():
                    numbers.append(str(user_input[key]).strip())

            if not numbers:
                numbers = ["79020"]

            return self.async_create_entry(
                title=f"BAS-IP ({self._host})",
                data={
                    CONF_HOST: self._host,
                    CONF_PASSWORD: self._password,
                    "mask": self._mask,
                    "gateway": self._gateway,
                    "dns": self._dns,
                    "call_numbers": numbers,
                }
            )

        return self._show_numbers_form()

    def _show_numbers_form(self, user_input=None):
        if user_input is None:
            user_input = {}

        display_numbers = ["", "", "", "", ""]

        schema = {
            vol.Optional(
                "call_number_1",
                description={"suggested_value": display_numbers[0]}
            ): str,
            vol.Optional(
                "call_number_2",
                description={"suggested_value": display_numbers[1]}
            ): str,
            vol.Optional(
                "call_number_3",
                description={"suggested_value": display_numbers[2]}
            ): str,
            vol.Optional(
                "call_number_4",
                description={"suggested_value": display_numbers[3]}
            ): str,
            vol.Optional(
                "call_number_5",
                description={"suggested_value": display_numbers[4]}
            ): str,
        }

        return self.async_show_form(
            step_id="numbers",
            data_schema=vol.Schema(schema),
            errors=self._errors,
            description_placeholders={
                "numbers_help": "Enter up to 5 phone numbers. Leave empty to skip.",
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
        self._errors = {}

    async def _async_ping_host(self, ip_address: str) -> bool:
        """Проверить, отвечает ли IP-адрес на ping."""
        try:
            process = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "2", ip_address,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await process.wait()
            return process.returncode == 0
        except Exception:
            return False

    async def async_step_init(self, user_input=None):
        """Главное меню опций с красивыми иконками."""
        if user_input is not None:
            selected = user_input.get("section")
            if selected == "change_ip":
                return await self.async_step_change_ip()
            elif selected == "change_password":
                return await self.async_step_change_password()
            elif selected == "general":
                return await self.async_step_general()
            elif selected == "numbers":
                return await self.async_step_numbers()
            return self.async_abort(reason="no_selection")

        schema = vol.Schema({
            vol.Required("section", default="change_ip"): vol.In({
                "change_ip": "📡 Смена IP-адреса",
                "change_password": "🔑 Смена пароля",
                "general": "⚙️ Общие настройки",
                "numbers": "📞 Настройка номеров",
            })
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={
                "menu_help": "📋 **Выберите раздел для настройки:**"
            }
        )

    async def async_step_change_ip(self, user_input=None):
        """Смена IP, маски, шлюза, DNS."""
        if user_input is not None:
            if not user_input.get("ip_address"):
                self._errors["base"] = "ip_required"
                return self._show_change_ip_form(user_input)

            from .coordinator import BASIPCoordinator
            
            data = dict(self._config_entry.data)
            
            new_host = user_input.get("ip_address")
            new_mask = user_input.get("mask")
            new_gateway = user_input.get("gateway")
            new_dns = user_input.get("dns")
            
            old_host = data.get(CONF_HOST)
            old_password = data.get(CONF_PASSWORD)
            
            # Если IP не изменился - просто выходим без изменений
            if new_host == old_host:
                _LOGGER.info("ℹ️ IP address unchanged, exiting without changes")
                return self.async_abort(reason="ip_unchanged")
            
            # Проверяем, свободен ли новый IP
            ip_occupied = await self._async_ping_host(new_host)
            if ip_occupied:
                self._errors["base"] = "ip_occupied"
                return self._show_change_ip_form(user_input)
            
            # Подключаемся со СТАРЫМ IP
            old_config = {
                CONF_HOST: old_host,
                CONF_PASSWORD: old_password,
                "call_numbers": data.get("call_numbers", ["79020"]),
            }
            coordinator = BASIPCoordinator(self.hass, old_config)
            valid = await coordinator.async_validate_auth()

            if not valid:
                self._errors["base"] = "cannot_connect_current"
                return self._show_change_ip_form(user_input)
            
            # Меняем IP на панели
            try:
                await coordinator.async_set_static_ip(
                    new_host, new_mask, new_gateway, new_dns
                )
                _LOGGER.info("✅ IP changed on panel to %s", new_host)
            except Exception as e:
                _LOGGER.error("Failed to change IP: %s", e)
                self._errors["base"] = "ip_change_failed"
                return self._show_change_ip_form(user_input)
            
            # Сохраняем новые сетевые настройки
            data[CONF_HOST] = new_host
            data["mask"] = new_mask
            data["gateway"] = new_gateway
            data["dns"] = new_dns
            
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                title=f"BAS-IP ({new_host})",
                data=data
            )
            
            # Ждем, пока панель перезагрузится после смены IP
            _LOGGER.info("⏳ Waiting for panel to reboot after IP change...")
            await asyncio.sleep(15)
            
            # Проверяем доступность нового IP
            _LOGGER.info("🔍 Checking if new IP %s is reachable...", new_host)
            reachable = await self._async_ping_host(new_host)
            if not reachable:
                _LOGGER.warning("⚠️ New IP %s is not reachable yet, waiting additional 10 seconds...", new_host)
                await asyncio.sleep(10)
                reachable = await self._async_ping_host(new_host)
                if not reachable:
                    _LOGGER.warning("⚠️ New IP %s still not reachable, integration will reload anyway", new_host)
            
            # Перезагружаем интеграцию
            _LOGGER.info("🔄 Reloading integration...")
            await self.hass.config_entries.async_reload(self._config_entry.entry_id)
            
            return self.async_create_entry(title="", data={})

        return self._show_change_ip_form()

    def _show_change_ip_form(self, user_input=None):
        """Показать форму смены IP."""
        if user_input is None:
            user_input = {}

        data = self._config_entry.data
        
        default_ip = data.get(CONF_HOST, "")
        default_mask = data.get("mask", "255.255.255.0")
        default_gateway = data.get("gateway", "192.168.1.1")
        default_dns = data.get("dns", "8.8.8.8")

        schema = vol.Schema({
            vol.Required(
                "ip_address",
                default=user_input.get("ip_address", default_ip)
            ): str,
            vol.Required(
                "mask",
                default=user_input.get("mask", default_mask)
            ): str,
            vol.Required(
                "gateway",
                default=user_input.get("gateway", default_gateway)
            ): str,
            vol.Required(
                "dns",
                default=user_input.get("dns", default_dns)
            ): str,
        })

        return self.async_show_form(
            step_id="change_ip",
            data_schema=schema,
            errors=self._errors,
            description_placeholders={
                "change_ip_help": "📡 **Измените сетевые настройки панели BAS-IP**\n\nIP-адрес, маска подсети, шлюз и DNS-сервер.",
                "warning": "⚠️ После сохранения интеграция будет перезагружена"
            }
        )

    async def async_step_change_password(self, user_input=None):
        """Смена пароля."""
        if user_input is not None:
            if not user_input.get(CONF_PASSWORD):
                self._errors["base"] = "password_required"
                return self._show_change_password_form(user_input)

            from .coordinator import BASIPCoordinator
            
            data = dict(self._config_entry.data)
            
            new_password = user_input.get(CONF_PASSWORD)
            old_password = data.get(CONF_PASSWORD)
            old_host = data.get(CONF_HOST)
            
            # Подключаемся со СТАРЫМ паролем
            old_config = {
                CONF_HOST: old_host,
                CONF_PASSWORD: old_password,
                "call_numbers": data.get("call_numbers", ["79020"]),
            }
            coordinator = BASIPCoordinator(self.hass, old_config)
            valid = await coordinator.async_validate_auth()

            if not valid:
                self._errors["base"] = "cannot_connect_current"
                return self._show_change_password_form(user_input)
            
            # Меняем пароль на панели
            try:
                await coordinator.async_change_password(old_password, new_password)
                _LOGGER.info("✅ Password changed on panel")
            except Exception as e:
                _LOGGER.error("Failed to change password: %s", e)
                self._errors["base"] = "password_change_failed"
                return self._show_change_password_form(user_input)
            
            # Сохраняем новый пароль
            data[CONF_PASSWORD] = new_password
            
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data=data
            )
            
            # Перезагружаем интеграцию
            await self.hass.config_entries.async_reload(self._config_entry.entry_id)
            
            return self.async_create_entry(title="", data={})

        return self._show_change_password_form()

    def _show_change_password_form(self, user_input=None):
        """Показать форму смены пароля."""
        if user_input is None:
            user_input = {}

        data = self._config_entry.data

        schema = vol.Schema({
            vol.Required(
                CONF_PASSWORD,
                default=user_input.get(CONF_PASSWORD, data.get(CONF_PASSWORD, ""))
            ): str,
        })

        return self.async_show_form(
            step_id="change_password",
            data_schema=schema,
            errors=self._errors,
            description_placeholders={
                "change_password_help": "🔑 **Измените пароль администратора панели BAS-IP**\n\nВведите новый пароль для доступа к веб-интерфейсу.",
                "warning": "⚠️ После сохранения интеграция будет перезагружена"
            }
        )

    async def async_step_general(self, user_input=None):
        """Общие настройки."""
        if user_input is not None:
            options = dict(self._config_entry.options)
            options["update_interval"] = user_input.get("update_interval", 60)
            return self.async_create_entry(title="", data=options)

        schema = vol.Schema({
            vol.Optional(
                "update_interval",
                default=self._config_entry.options.get("update_interval", 60)
            ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
        })

        return self.async_show_form(
            step_id="general",
            data_schema=schema,
            description_placeholders={
                "general_help": "⚙️ **Общие настройки интеграции**\n\nИнтервал обновления данных с панели (в секундах)."
            }
        )

    async def async_step_numbers(self, user_input=None):
        """Настройка номеров."""
        if user_input is not None:
            numbers = []
            for i in range(1, 6):
                key = f"call_number_{i}"
                if key in user_input and user_input[key] and str(user_input[key]).strip():
                    numbers.append(str(user_input[key]).strip())

            if not numbers:
                numbers = ["79020"]

            data = dict(self._config_entry.data)
            data["call_numbers"] = numbers
            self.hass.config_entries.async_update_entry(self._config_entry, data=data)

            options = dict(self._config_entry.options)
            options["call_numbers"] = numbers
            return self.async_create_entry(title="", data=options)

        saved_numbers = self._config_entry.data.get("call_numbers", ["79020"])
        if isinstance(saved_numbers, str):
            saved_numbers = [n.strip() for n in saved_numbers.split(",") if n.strip()]
        if not saved_numbers:
            saved_numbers = ["79020"]

        display_numbers = saved_numbers.copy()
        while len(display_numbers) < 5:
            display_numbers.append("")

        schema = {
            vol.Optional(
                "call_number_1",
                description={"suggested_value": display_numbers[0] if len(display_numbers) > 0 else ""}
            ): str,
            vol.Optional(
                "call_number_2",
                description={"suggested_value": display_numbers[1] if len(display_numbers) > 1 else ""}
            ): str,
            vol.Optional(
                "call_number_3",
                description={"suggested_value": display_numbers[2] if len(display_numbers) > 2 else ""}
            ): str,
            vol.Optional(
                "call_number_4",
                description={"suggested_value": display_numbers[3] if len(display_numbers) > 3 else ""}
            ): str,
            vol.Optional(
                "call_number_5",
                description={"suggested_value": display_numbers[4] if len(display_numbers) > 4 else ""}
            ): str,
        }

        return self.async_show_form(
            step_id="numbers",
            data_schema=vol.Schema(schema),
            description_placeholders={
                "numbers_help": "📞 **Настройка номеров для звонков**\n\nВведите до 5 номеров. Оставьте поле пустым для удаления номера."
            }
        )