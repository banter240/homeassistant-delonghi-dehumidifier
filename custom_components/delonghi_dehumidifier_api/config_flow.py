"""Config flow."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_EMAIL, CONF_LANGUAGE, CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .client import APIClient
from .const import (
    CONF_POLL_INTERVAL,
    CONFIG_FLOW_VERSION,
    DEFAULT_LANGUAGE,
    DEFAULT_POLL_INTERVAL_SECONDS,
    DOMAIN,
    MAX_POLL_INTERVAL_SECONDS,
    MIN_POLL_INTERVAL_SECONDS,
)
from .coordinator import poll_interval_seconds
from .helpers.auth import AuthError

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


def _options_schema(
    language: str = DEFAULT_LANGUAGE,
    email: str = "",
    password: str = "",
    poll_interval: int = DEFAULT_POLL_INTERVAL_SECONDS,
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_LANGUAGE, default=language): str,
            vol.Required(CONF_EMAIL, default=email): str,
            vol.Required(CONF_PASSWORD, default=password): str,
            vol.Required(CONF_POLL_INTERVAL, default=poll_interval): vol.All(
                vol.Coerce(int),
                vol.Range(
                    min=MIN_POLL_INTERVAL_SECONDS,
                    max=MAX_POLL_INTERVAL_SECONDS,
                ),
            ),
        }
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    session = aiohttp_client.async_get_clientsession(hass)
    client = APIClient(
        session, data[CONF_LANGUAGE], data[CONF_EMAIL], data[CONF_PASSWORD]
    )
    try:
        if not await client.authenticate():
            raise InvalidAuth
        title = await client.get_product_name()
    except AuthError as err:
        raise InvalidAuth from err
    return {"title": title}


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


class DeLonghiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg, unused-ignore]
    VERSION = CONFIG_FLOW_VERSION

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            info, errors = await _auth_step(self.hass, user_input)
            if info is not None:
                await self.async_set_unique_id(user_input[CONF_EMAIL].lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                    options={CONF_POLL_INTERVAL: DEFAULT_POLL_INTERVAL_SECONDS},
                )

        return self.async_show_form(
            step_id="user", data_schema=_user_schema(), errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Start reauthentication after the coordinator reported failed credentials."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for fresh credentials and update the existing entry."""
        errors: dict[str, str] = {}
        if user_input is not None:
            info, errors = await _auth_step(self.hass, user_input)
            if info is not None:
                entry = self._get_reauth_entry()
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={**entry.data, **user_input},
                    title=info["title"],
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        entry = self._get_reauth_entry()
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=_user_schema(
                language=entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
                email=entry.data.get(CONF_EMAIL, ""),
                password="",
            ),
            errors=errors,
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
            poll = int(user_input[CONF_POLL_INTERVAL])
            auth_data = {
                CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                CONF_EMAIL: user_input[CONF_EMAIL],
                CONF_PASSWORD: user_input[CONF_PASSWORD],
            }
            info, errors = await _auth_step(self.hass, auth_data)
            if info is not None:
                options = {CONF_POLL_INTERVAL: poll}
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=auth_data,
                    options=options,
                    title=info["title"],
                )
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                return self.async_create_entry(title="", data=options)

        data = self.config_entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(
                language=data[CONF_LANGUAGE],
                email=data[CONF_EMAIL],
                password=data[CONF_PASSWORD],
                poll_interval=poll_interval_seconds(self.config_entry),
            ),
            errors=errors,
        )


class InvalidAuth(HomeAssistantError):
    """Raised when authentication fails."""
