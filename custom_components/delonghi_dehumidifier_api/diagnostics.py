"""Diagnostics support."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from . import DeLonghiDehumidifierConfigEntry
from .coordinator import DelonghiCoordinator

REDACT_KEYS = {CONF_EMAIL, CONF_PASSWORD}


def _coordinator_snapshot(coordinator: DelonghiCoordinator) -> dict[str, Any]:
    """Return the raw device property snapshot used by all entities."""
    return {
        "device_dsn": coordinator.device_dsn,
        "properties": dict(coordinator.data or {}),
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: DeLonghiDehumidifierConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry, with credentials redacted."""
    coordinator = entry.runtime_data
    return {
        "entry": {
            "data": async_redact_data(dict(entry.data), REDACT_KEYS),
            "options": dict(entry.options),
        },
        **_coordinator_snapshot(coordinator),
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: DeLonghiDehumidifierConfigEntry,
    device: DeviceEntry,
) -> dict[str, Any]:
    """Return device-level diagnostics."""
    return _coordinator_snapshot(entry.runtime_data)
