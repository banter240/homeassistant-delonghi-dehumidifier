"""Binary sensors."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ALARM_OK,
    ALARM_TANK,
    ENTITY_KIND_BINARY_SENSOR,
    KNOWN_ALARM_STATES,
)
from .coordinator import DelonghiCoordinator
from .entity import DelonghiEntity, async_setup_platform_entities
from .helpers import properties as props

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[DelonghiCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    def build(coordinator: DelonghiCoordinator) -> list[TankFullBinarySensor]:
        return [TankFullBinarySensor(coordinator)]

    await async_setup_platform_entities(config_entry, async_add_entities, build)


class TankFullBinarySensor(DelonghiEntity, BinarySensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "water_tank"

    def __init__(self, coordinator: DelonghiCoordinator) -> None:
        super().__init__(
            coordinator,
            translation_key="water_tank",
            object_id="water_tank",
            kind=ENTITY_KIND_BINARY_SENSOR,
        )
        self._alarm_state = ALARM_OK
        self._apply_data()

    @property
    def extra_state_attributes(self) -> dict[str, int]:
        return {"alarm_state": self._alarm_state}

    @callback
    def _handle_coordinator_update(self) -> None:
        self._apply_data()
        self.async_write_ha_state()

    def _apply_data(self) -> None:
        raw = props.alarm_state(self.props)
        self._alarm_state = ALARM_OK if raw is None else raw
        self._attr_is_on = self._alarm_state == ALARM_TANK
        if self._alarm_state not in KNOWN_ALARM_STATES:
            _LOGGER.warning(
                "Unknown alarm_state=%s (expected %s)",
                self._alarm_state,
                sorted(KNOWN_ALARM_STATES),
            )
