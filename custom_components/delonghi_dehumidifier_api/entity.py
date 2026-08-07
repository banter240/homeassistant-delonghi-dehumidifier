"""Entity base."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import APIClient
from .coordinator import DelonghiCoordinator
from .helpers.device import unique_id

EntityBuilder = Callable[[DelonghiCoordinator], Sequence[Entity]]


class DelonghiEntity(CoordinatorEntity[DelonghiCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DelonghiCoordinator,
        *,
        translation_key: str,
        object_id: str,
        kind: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_translation_key = translation_key
        self._attr_unique_id = unique_id(coordinator.device_dsn, object_id, kind)
        self._attr_device_info = coordinator.device_info

    @property
    def client(self) -> APIClient:
        return self.coordinator.client

    @property
    def props(self) -> dict[str, Any]:
        return self.coordinator.data or {}


async def async_setup_platform_entities(
    config_entry: ConfigEntry[DelonghiCoordinator],
    async_add_entities: AddEntitiesCallback,
    build_entities: EntityBuilder,
) -> None:
    coordinator = config_entry.runtime_data
    async_add_entities(build_entities(coordinator))
