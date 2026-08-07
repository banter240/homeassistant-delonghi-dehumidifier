"""Switch platform."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ENTITY_KIND_SWITCH, OffOnStatus
from .coordinator import DelonghiCoordinator
from .entity import DelonghiEntity, async_setup_platform_entities
from .helpers import properties as props


@dataclass(frozen=True, slots=True)
class SwitchSpec:
    translation_key: str
    reader: Callable[[dict[str, Any]], OffOnStatus]
    setter: str


SWITCH_SPECS: tuple[SwitchSpec, ...] = (
    SwitchSpec("eco_mode", props.eco, "set_eco"),
    SwitchSpec("swing_mode", props.swing, "set_swing"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[DelonghiCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    def build(coordinator: DelonghiCoordinator) -> list[GenericOffOnSwitch]:
        return [GenericOffOnSwitch(coordinator, spec) for spec in SWITCH_SPECS]

    await async_setup_platform_entities(config_entry, async_add_entities, build)


class GenericOffOnSwitch(DelonghiEntity, SwitchEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: DelonghiCoordinator, spec: SwitchSpec) -> None:
        super().__init__(
            coordinator,
            translation_key=spec.translation_key,
            object_id=spec.translation_key,
            kind=ENTITY_KIND_SWITCH,
        )
        self._reader = spec.reader
        self._set_status: Callable[[OffOnStatus], Awaitable[dict[Any, Any]]] = getattr(
            coordinator.client, spec.setter
        )
        self._apply_data()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._apply_data()
        self.async_write_ha_state()

    def _apply_data(self) -> None:
        self._attr_is_on = self._reader(self.props) == OffOnStatus.ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._set_status(OffOnStatus.ON)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._set_status(OffOnStatus.OFF)
        await self.coordinator.async_request_refresh()
