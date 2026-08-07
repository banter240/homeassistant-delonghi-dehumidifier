"""Sensor platform."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ALARM_LABELS, ENTITY_KIND_SENSOR, FilterStatus, Mode, OffOnStatus
from .coordinator import DelonghiCoordinator
from .entity import DelonghiEntity, async_setup_platform_entities
from .helpers import properties as props


@dataclass(frozen=True, slots=True)
class SensorSpec:
    translation_key: str
    reader: Callable[[dict[str, Any]], Any]
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    unit: str | None = None
    enum_type: type[Enum] | None = None
    options: tuple[str, ...] | None = None
    extra_attrs: Callable[[dict[str, Any]], dict[str, Any]] | None = None


def _enum_key(reader: Callable[[dict[str, Any]], Enum | None]):
    def _read(data: dict[str, Any]) -> str | None:
        value = reader(data)
        return None if value is None else value.name.lower()

    return _read


def _alarm_extra(data: dict[str, Any]) -> dict[str, Any]:
    raw = props.alarm_state(data)
    return {"alarm_code": raw}


SENSOR_SPECS: tuple[SensorSpec, ...] = (
    SensorSpec(
        "current_humidity",
        props.current_humidity,
        SensorDeviceClass.HUMIDITY,
        SensorStateClass.MEASUREMENT,
        PERCENTAGE,
    ),
    SensorSpec(
        "target_humidity",
        props.humidity_setpoint,
        SensorDeviceClass.HUMIDITY,
        SensorStateClass.MEASUREMENT,
        PERCENTAGE,
    ),
    SensorSpec(
        "current_speed",
        props.current_speed,
        SensorDeviceClass.SPEED,
        SensorStateClass.MEASUREMENT,
        UnitOfSpeed.METERS_PER_SECOND,
    ),
    SensorSpec(
        "filter_status",
        _enum_key(props.filter_status),
        SensorDeviceClass.ENUM,
        enum_type=FilterStatus,
    ),
    SensorSpec(
        "alarm_state",
        props.alarm_state_label,
        SensorDeviceClass.ENUM,
        options=ALARM_LABELS,
        extra_attrs=_alarm_extra,
    ),
    SensorSpec(
        "room_temperature",
        props.room_temp,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        UnitOfTemperature.CELSIUS,
    ),
    SensorSpec(
        "heat_exchanger_temperature",
        props.heat_exchanger_temp,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        UnitOfTemperature.CELSIUS,
    ),
    SensorSpec(
        "device_mode",
        _enum_key(props.device_mode),
        SensorDeviceClass.ENUM,
        enum_type=Mode,
    ),
    SensorSpec(
        "eco_mode",
        _enum_key(props.eco),
        SensorDeviceClass.ENUM,
        enum_type=OffOnStatus,
    ),
    SensorSpec(
        "swing_mode",
        _enum_key(props.swing),
        SensorDeviceClass.ENUM,
        enum_type=OffOnStatus,
    ),
    SensorSpec(
        "filter_change_alarm",
        _enum_key(props.filter_change_alarm),
        SensorDeviceClass.ENUM,
        enum_type=OffOnStatus,
    ),
    SensorSpec(
        "filter_life",
        props.get_filter_life_days,
        SensorDeviceClass.DURATION,
        SensorStateClass.MEASUREMENT,
        UnitOfTime.DAYS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[DelonghiCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    def build(coordinator: DelonghiCoordinator) -> list[GenericSensor]:
        return [GenericSensor(coordinator, spec) for spec in SENSOR_SPECS]

    await async_setup_platform_entities(config_entry, async_add_entities, build)


class GenericSensor(DelonghiEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: DelonghiCoordinator, spec: SensorSpec) -> None:
        super().__init__(
            coordinator,
            translation_key=spec.translation_key,
            object_id=spec.translation_key,
            kind=ENTITY_KIND_SENSOR,
        )
        self._spec = spec
        if spec.options is not None:
            self._attr_options = list(spec.options)
        elif spec.enum_type is not None:
            self._attr_options = [m.name.lower() for m in spec.enum_type]
        self._attr_device_class = spec.device_class
        self._attr_state_class = spec.state_class
        self._attr_native_unit_of_measurement = spec.unit
        self._extra_attrs: dict[str, Any] = {}
        self._apply_data()

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return self._extra_attrs or None

    @callback
    def _handle_coordinator_update(self) -> None:
        self._apply_data()
        self.async_write_ha_state()

    def _apply_data(self) -> None:
        try:
            self._attr_native_value = self._spec.reader(self.props)
        except TypeError, ValueError, KeyError:
            self._attr_native_value = None
        if self._spec.extra_attrs is not None:
            self._extra_attrs = self._spec.extra_attrs(self.props)
        else:
            self._extra_attrs = {}
