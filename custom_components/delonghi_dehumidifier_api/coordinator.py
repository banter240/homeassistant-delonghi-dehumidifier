"""Data update coordinator."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import APIClient
from .const import (
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL_SECONDS,
    DOMAIN,
    MAX_POLL_INTERVAL_SECONDS,
    MIN_POLL_INTERVAL_SECONDS,
)
from .helpers.auth import AuthError
from .helpers.device import build_device_info
from .helpers.properties import props_from_list

_LOGGER = logging.getLogger(__name__)


def poll_interval_seconds(entry: ConfigEntry) -> int:
    """Resolve poll interval from options (then data), clamped to allowed range."""
    raw = entry.options.get(
        CONF_POLL_INTERVAL,
        entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL_SECONDS),
    )
    try:
        seconds = int(raw)
    except TypeError, ValueError:
        seconds = DEFAULT_POLL_INTERVAL_SECONDS
    return max(MIN_POLL_INTERVAL_SECONDS, min(MAX_POLL_INTERVAL_SECONDS, seconds))


class DelonghiCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: APIClient,
        entry: ConfigEntry,
    ) -> None:
        interval = timedelta(seconds=poll_interval_seconds(entry))
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=interval,
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
        except AuthError as err:
            raise ConfigEntryAuthFailed(
                f"DeLonghi authentication failed: {err}"
            ) from err
        except Exception as err:
            raise UpdateFailed(f"Error fetching DeLonghi data: {err}") from err
