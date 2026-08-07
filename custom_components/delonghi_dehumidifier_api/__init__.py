"""DeLonghi dehumidifier integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_LANGUAGE, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .client import APIClient
from .const import PLATFORMS
from .coordinator import DelonghiCoordinator

type DeLonghiDehumidifierConfigEntry = ConfigEntry[DelonghiCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: DeLonghiDehumidifierConfigEntry
) -> bool:
    session = aiohttp_client.async_get_clientsession(hass)
    client = APIClient(
        session,
        entry.data[CONF_LANGUAGE],
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
    )
    coordinator = DelonghiCoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: DeLonghiDehumidifierConfigEntry
) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
