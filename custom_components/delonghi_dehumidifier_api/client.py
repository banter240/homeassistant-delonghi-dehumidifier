"""Ayla API client."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import (
    FIRST_DEVICE_INDEX,
    HTTP_CLIENT_ERROR,
    PROP_ACTIVATE_REALFEEL,
    PROP_DEVICE_MODE,
    PROP_HUMIDITY_SETPOINT,
    PROP_PRODUCT_NAME,
    PROP_SET_ECO,
    PROP_SET_STATUS,
    PROP_SWING,
    REAL_FEEL_ACTIVATION_PAYLOAD,
    REAL_FEEL_IDLE_PAYLOAD,
    Mode,
    OffOnStatus,
    Status,
)
from .helpers.auth import AylaAuth
from .helpers.headers import api_headers
from .helpers.paths import ads_url, path_datapoint, path_devices, path_properties
from .helpers.properties import props_from_list

_LOGGER = logging.getLogger(__name__)


class APIClient:
    def __init__(
        self, session: aiohttp.ClientSession, language: str, email: str, password: str
    ) -> None:
        self.session = session
        self._auth = AylaAuth(session, language, email, password)
        self.device_dsn: str | None = None

    async def authenticate(self) -> bool:
        return bool(await self._auth.get_access_token())

    async def get_product_name(self) -> str:
        props = props_from_list(await self.fetch_properties())
        value = props.get(PROP_PRODUCT_NAME)
        return "" if value is None else str(value)

    async def set_status(self, status: Status) -> Any:
        return await self.set_datapoint(PROP_SET_STATUS, status.value)

    async def set_humidity(self, value: int) -> Any:
        return await self.set_datapoint(PROP_HUMIDITY_SETPOINT, value)

    async def set_mode(self, mode: Mode) -> Any:
        if mode == Mode.REAL_FEEL:
            return await self.set_datapoint(
                PROP_ACTIVATE_REALFEEL, REAL_FEEL_ACTIVATION_PAYLOAD
            )
        await self.set_datapoint(PROP_ACTIVATE_REALFEEL, REAL_FEEL_IDLE_PAYLOAD)
        return await self.set_datapoint(PROP_DEVICE_MODE, mode.value)

    async def set_swing(self, status: OffOnStatus) -> Any:
        return await self.set_datapoint(PROP_SWING, status.value)

    async def set_eco(self, status: OffOnStatus) -> Any:
        return await self.set_datapoint(PROP_SET_ECO, status.value)

    async def set_datapoint(self, property_name: str, value: Any) -> Any:
        device_dsn = await self.get_first_device()
        return await self.post_request(
            path_datapoint(device_dsn, property_name),
            {"datapoint": {"value": value}},
        )

    async def get_request(self, path: str) -> Any:
        access_token = await self._auth.get_access_token()
        response = await self.session.get(
            ads_url(path), headers=api_headers(access_token or "")
        )
        status = response.status
        payload = await response.json()
        if status >= HTTP_CLIENT_ERROR:
            _LOGGER.error("Ayla GET %s failed HTTP %s: %s", path, status, payload)
        return payload

    async def post_request(self, path: str, body: dict[str, Any]) -> Any:
        access_token = await self._auth.get_access_token()
        response = await self.session.post(
            ads_url(path),
            headers=api_headers(access_token or "", json_body=True),
            json=body,
        )
        status = response.status
        payload = await response.json()
        if status >= HTTP_CLIENT_ERROR:
            _LOGGER.error("Ayla POST %s failed HTTP %s: %s", path, status, payload)
        return payload

    async def get_first_device(self) -> str:
        if self.device_dsn:
            return self.device_dsn
        devices = await self.get_request(path_devices())
        self.device_dsn = str(devices[FIRST_DEVICE_INDEX]["device"]["dsn"])
        return self.device_dsn

    async def fetch_properties(self) -> list[Any]:
        device_dsn = await self.get_first_device()
        device_properties = await self.get_request(path_properties(device_dsn))
        return [
            device_property.get("property") for device_property in device_properties
        ]
