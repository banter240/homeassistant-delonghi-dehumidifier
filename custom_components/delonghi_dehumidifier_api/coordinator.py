"""Data update coordinator."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import APIClient
from .const import DOMAIN, SCAN_INTERVAL
from .helpers.device import build_device_info
from .helpers.properties import props_from_list

_LOGGER = logging.getLogger(__name__)


class DelonghiCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: APIClient,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client
        self.device_dsn: str = ""
        self.device_info: DeviceInfo | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            self.device_dsn = await self.client.get_first_device()
            raw = await self.client.fetch_properties()
            data = props_from_list(raw)
            self.device_info = build_device_info(self.device_dsn, data)
            return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching DeLonghi data: {err}") from err
