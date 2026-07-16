"""Directly adjustable minimum-price / guarantee-of-origin-surcharge entities."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_GOO_SURCHARGE_RP,
    CONF_MIN_PRICE_RP,
    DEFAULT_GOO_SURCHARGE_RP,
    DEFAULT_MIN_PRICE_RP,
)
from .device import device_info
from .localization import t


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities(
        [
            MinPriceNumber(hass, entry),
            GooSurchargeNumber(hass, entry),
        ]
    )


class _OptionNumber(NumberEntity):
    """Base class: reads/writes a config entry option value."""

    _attr_has_entity_name = False
    _attr_native_unit_of_measurement = "Rp/kWh"
    _attr_native_min_value = 0
    _attr_native_max_value = 50
    _attr_native_step = 0.1
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:cash-edit"

    _option_key: str
    _default: float

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_device_info = device_info(hass, entry)

    @property
    def native_value(self) -> float:
        return self._entry.options.get(self._option_key, self._default)

    async def async_set_native_value(self, value: float) -> None:
        new_options = {**self._entry.options, self._option_key: value}
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        # The update_listener registered in __init__.py reloads the config entry
        # (and therefore all sensors) automatically with the new value.


class MinPriceNumber(_OptionNumber):
    """Minimum price floor (Rp/kWh) for the feed-in remuneration."""

    _option_key = CONF_MIN_PRICE_RP
    _default = DEFAULT_MIN_PRICE_RP

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry)
        self._attr_name = t("min_price_name", hass)
        self._attr_unique_id = f"{entry.entry_id}_min_price"
        self.entity_id = "number.min_price"


class GooSurchargeNumber(_OptionNumber):
    """Guarantee-of-origin surcharge (Rp/kWh) for the feed-in remuneration."""

    _option_key = CONF_GOO_SURCHARGE_RP
    _default = DEFAULT_GOO_SURCHARGE_RP

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry)
        self._attr_name = t("goo_surcharge_name", hass)
        self._attr_unique_id = f"{entry.entry_id}_goo_surcharge"
        self.entity_id = "number.goo_surcharge"
