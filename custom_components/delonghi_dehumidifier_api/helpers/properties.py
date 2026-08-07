"""Property map helpers."""

from __future__ import annotations

import logging
from typing import Any

from ..const import (
    ALARM_LABEL_BY_CODE,
    ALARM_LABEL_UNKNOWN,
    FILTER_LIFE_MINUTES_PER_DAY,
    FILTER_STATUS_BY_VALUE,
    MODE_BY_VALUE,
    OFF_ON_STATUS_BY_VALUE,
    PROP_ACTIVATE_REALFEEL,
    PROP_ALARM_STATE,
    PROP_APPLIANCE_MODEL,
    PROP_CURRENT_HUMIDITY,
    PROP_CURRENT_SPEED,
    PROP_DEVICE_MODE,
    PROP_DEVICE_STATUS,
    PROP_FILTER_CHANGE_ALARM,
    PROP_FILTER_LIFE,
    PROP_FILTER_STATUS,
    PROP_FIRMWARE_VERSION,
    PROP_HARDWARE_VERSION,
    PROP_HEAT_EXCHANGER_TEMP,
    PROP_HUMIDITY_SETPOINT,
    PROP_PRODUCT_NAME,
    PROP_ROOM_TEMP,
    PROP_SET_ECO,
    PROP_SWING,
    REAL_FEEL_ACTIVATION_PAYLOAD,
    STATUS_BY_VALUE,
    TEMP_TENTHS_DIVISOR,
    FilterStatus,
    Mode,
    OffOnStatus,
    Status,
)

_LOGGER = logging.getLogger(__name__)


def props_from_list(raw: list[Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in raw:
        if not item:
            continue
        name = item.get("name")
        if name:
            result[name] = item.get("value")
    return result


def get_str(data: dict[str, Any], name: str) -> str:
    value = data.get(name)
    return "" if value is None else str(value)


def get_int(data: dict[str, Any], name: str) -> int | None:
    value = data.get(name)
    if value is None:
        return None
    return int(value)


def get_mapped[T](
    data: dict[str, Any],
    name: str,
    mapping: dict[int, T],
    default: T | None = None,
) -> T:
    value = get_int(data, name)
    if value is None:
        if default is not None:
            return default
        raise KeyError(f"Property {name} is null")
    if value in mapping:
        return mapping[value]
    if default is not None:
        _LOGGER.warning("Unknown %s value %s; using default %s", name, value, default)
        return default
    raise KeyError(f"Unknown {name} value: {value}")


def get_temp_celsius(data: dict[str, Any], name: str) -> float | None:
    raw = get_int(data, name)
    if raw is None:
        return None
    return raw / TEMP_TENTHS_DIVISOR


def get_filter_life_days(data: dict[str, Any]) -> float | None:
    raw = get_int(data, PROP_FILTER_LIFE)
    if raw is None:
        return None
    return round(raw / FILTER_LIFE_MINUTES_PER_DAY, 1)


def product_name(data: dict[str, Any]) -> str:
    return get_str(data, PROP_PRODUCT_NAME) or "DeLonghi"


def appliance_model(data: dict[str, Any]) -> str:
    return get_str(data, PROP_APPLIANCE_MODEL)


def firmware_version(data: dict[str, Any]) -> str:
    return get_str(data, PROP_FIRMWARE_VERSION)


def hardware_version(data: dict[str, Any]) -> str:
    return get_str(data, PROP_HARDWARE_VERSION)


def current_humidity(data: dict[str, Any]) -> int | None:
    return get_int(data, PROP_CURRENT_HUMIDITY)


def humidity_setpoint(data: dict[str, Any]) -> int | None:
    return get_int(data, PROP_HUMIDITY_SETPOINT)


def current_speed(data: dict[str, Any]) -> int | None:
    return get_int(data, PROP_CURRENT_SPEED)


def device_mode(data: dict[str, Any]) -> Mode:
    if data.get(PROP_ACTIVATE_REALFEEL) == REAL_FEEL_ACTIVATION_PAYLOAD:
        return Mode.REAL_FEEL
    return get_mapped(data, PROP_DEVICE_MODE, MODE_BY_VALUE, default=Mode.DEHUMIDIFY)


def device_status(data: dict[str, Any]) -> Status:
    return get_mapped(data, PROP_DEVICE_STATUS, STATUS_BY_VALUE, default=Status.OFF)


def filter_change_alarm(data: dict[str, Any]) -> OffOnStatus:
    return get_mapped(
        data, PROP_FILTER_CHANGE_ALARM, OFF_ON_STATUS_BY_VALUE, default=OffOnStatus.OFF
    )


def filter_status(data: dict[str, Any]) -> FilterStatus:
    return get_mapped(
        data, PROP_FILTER_STATUS, FILTER_STATUS_BY_VALUE, default=FilterStatus.OK
    )


def alarm_state(data: dict[str, Any]) -> int | None:
    return get_int(data, PROP_ALARM_STATE)


def alarm_state_label(data: dict[str, Any]) -> str | None:
    raw = alarm_state(data)
    if raw is None:
        return None
    return ALARM_LABEL_BY_CODE.get(raw, ALARM_LABEL_UNKNOWN)


def room_temp(data: dict[str, Any]) -> float | None:
    return get_temp_celsius(data, PROP_ROOM_TEMP)


def heat_exchanger_temp(data: dict[str, Any]) -> float | None:
    return get_temp_celsius(data, PROP_HEAT_EXCHANGER_TEMP)


def swing(data: dict[str, Any]) -> OffOnStatus:
    return get_mapped(data, PROP_SWING, OFF_ON_STATUS_BY_VALUE, default=OffOnStatus.OFF)


def eco(data: dict[str, Any]) -> OffOnStatus:
    return get_mapped(
        data, PROP_SET_ECO, OFF_ON_STATUS_BY_VALUE, default=OffOnStatus.OFF
    )
