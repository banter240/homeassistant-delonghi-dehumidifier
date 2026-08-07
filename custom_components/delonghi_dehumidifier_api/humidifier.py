"""Humidifier platform."""

from typing import Any

from homeassistant.components.humidifier import HumidifierDeviceClass, HumidifierEntity
from homeassistant.components.humidifier.const import HumidifierEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ENTITY_KIND_DEHUMIDIFIER,
    HUMIDIFIER_MODES,
    HUMIDIFIER_UNIQUE_ID_SUFFIX,
    HUMIDITY_MAX,
    HUMIDITY_MIN,
    MODE_BY_KEY,
    Mode,
    Status,
)
from .coordinator import DelonghiCoordinator
from .entity import DelonghiEntity, async_setup_platform_entities
from .helpers import properties as props
from .helpers.device import humidifier_unique_id


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[DelonghiCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    def build(coordinator: DelonghiCoordinator) -> list[DehumidifierEntity]:
        return [DehumidifierEntity(coordinator)]

    await async_setup_platform_entities(config_entry, async_add_entities, build)


class DehumidifierEntity(DelonghiEntity, HumidifierEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = HumidifierDeviceClass.DEHUMIDIFIER
    _attr_translation_key = "unit"
    _attr_max_humidity = HUMIDITY_MAX
    _attr_min_humidity = HUMIDITY_MIN
    _attr_supported_features = HumidifierEntityFeature.MODES
    _attr_available_modes = list(HUMIDIFIER_MODES)

    def __init__(self, coordinator: DelonghiCoordinator) -> None:
        super().__init__(
            coordinator,
            translation_key="unit",
            object_id="unit",
            kind=ENTITY_KIND_DEHUMIDIFIER,
        )
        self._attr_unique_id = humidifier_unique_id(
            coordinator.device_dsn, HUMIDIFIER_UNIQUE_ID_SUFFIX
        )
        self._cloud_status = Status.OFF.value
        self._apply_data()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._apply_data()
        self.async_write_ha_state()

    def _apply_data(self) -> None:
        data = self.props
        status = props.device_status(data)
        mode = props.device_mode(data)
        self._attr_mode = mode.name.lower()
        self._attr_current_humidity = props.current_humidity(data)
        self._attr_is_on = status is Status.ON
        self._cloud_status = status.value
        if mode is Mode.REAL_FEEL:
            self._attr_target_humidity = None
        else:
            self._attr_target_humidity = props.humidity_setpoint(data)

    @property
    def extra_state_attributes(self) -> dict[str, int]:
        return {"cloud_status": self._cloud_status}

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.client.set_status(Status.ON)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.client.set_status(Status.OFF)
        await self.coordinator.async_request_refresh()

    async def async_set_mode(self, mode: str) -> None:
        mapped = MODE_BY_KEY.get(mode.lower())
        if mapped is None:
            return
        await self.client.set_mode(mapped)
        await self.coordinator.async_request_refresh()

    async def async_set_humidity(self, humidity: int) -> None:
        if props.device_mode(self.props) is Mode.REAL_FEEL:
            raise ServiceValidationError(
                "Humidity setpoint is not available in Real Feel mode"
            )
        await self.client.set_humidity(humidity)
        await self.coordinator.async_request_refresh()
