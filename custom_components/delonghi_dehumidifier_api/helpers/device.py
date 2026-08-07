"""Device helpers."""

from __future__ import annotations

import re
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo

from ..const import DEVICE_NAME_SUFFIX, DOMAIN, MANUFACTURER
from .properties import (
    appliance_model,
    firmware_version,
    hardware_version,
    product_name,
)


def slugify(name: str) -> str:
    return re.sub(r"\s+", "_", name.lower())


def unique_id(device_dsn: str, name: str, kind: str) -> str:
    return f"{DOMAIN}_{device_dsn}_{slugify(name)}_{kind}"


def humidifier_unique_id(device_dsn: str, suffix: str) -> str:
    return f"{DOMAIN}_{device_dsn}_{suffix}"


def build_device_info(device_dsn: str, props: dict[str, Any]) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, device_dsn)},
        name=f"{product_name(props)} {DEVICE_NAME_SUFFIX}",
        manufacturer=MANUFACTURER,
        model=appliance_model(props),
        sw_version=firmware_version(props),
        hw_version=hardware_version(props),
    )
