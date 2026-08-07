"""Config flow."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_EMAIL, CONF_LANGUAGE, CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .client import APIClient
from .const import CONFIG_FLOW_VERSION, DEFAULT_LANGUAGE, DOMAIN

_LOGGER = logging.getLogger(__name__)


def _user_schema(
    language: str = DEFAULT_LANGUAGE,
    email: str = "",
    password: str = "",
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_LANGUAGE, default=language): str,
            vol.Required(CONF_EMAIL, default=email): str,
            vol.Required(CONF_PASSWORD, default=password): str,
        }
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    session = aiohttp_client.async_get_clientsession(hass)
    client = APIClient(
        session, data[CONF_LANGUAGE], data[CONF_EMAIL], data[CONF_PASSWORD]
    )
    if not await client.authenticate():
        raise InvalidAuth
    return {"title": await client.get_product_name()}


async def _auth_step(
    hass: HomeAssistant, user_input: dict[str, Any]
) -> tuple[dict[str, Any] | None, dict[str, str]]:
    try:
        return await validate_input(hass, user_input), {}
    except InvalidAuth:
        return None, {"base": "invalid_auth"}
    except Exception:
        _LOGGER.exception("Unexpected exception")
        return None, {"base": "unknown"}


class DeLonghiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = CONFIG_FLOW_VERSION

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            info, errors = await _auth_step(self.hass, user_input)
            if info is not None:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=_user_schema(), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return DeLonghiOptionsFlow()


class DeLonghiOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            info, errors = await _auth_step(self.hass, user_input)
            if info is not None:
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=user_input, title=info["title"]
                )
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                return self.async_create_entry(title="", data={})

        data = self.config_entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=_user_schema(
                language=data[CONF_LANGUAGE],
                email=data[CONF_EMAIL],
                password=data[CONF_PASSWORD],
            ),
            errors=errors,
        )


class InvalidAuth(HomeAssistantError):
    pass
