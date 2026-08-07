"""API paths."""

from __future__ import annotations

from ..const import AYLA_ADS_BASE, PATH_DEVICES


def ads_url(path: str) -> str:
    return f"{AYLA_ADS_BASE}/{path}"


def path_devices() -> str:
    return PATH_DEVICES


def path_properties(device_dsn: str) -> str:
    return f"apiv1/dsns/{device_dsn}/properties.json"


def path_datapoint(device_dsn: str, property_name: str) -> str:
    return f"apiv1/dsns/{device_dsn}/properties/{property_name}/datapoints.json"
