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
    PRICE_RP_MAX,
    PRICE_RP_MIN,
    PRICE_RP_STEP,
)
from .device import device_info, entry_suffix
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
    _attr_should_poll = False
    _attr_native_unit_of_measurement = "Rp/kWh"
    _attr_native_min_value = PRICE_RP_MIN
    _attr_native_max_value = PRICE_RP_MAX
    _attr_native_step = PRICE_RP_STEP
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

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        # Follow changes made elsewhere (options dialog, the other number
        # entity) without an entry reload.
        self.async_on_remove(self._entry.add_update_listener(self._async_options_updated))

    async def _async_options_updated(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        new_options = {**self._entry.options, self._option_key: value}
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        # Only an option changed: write the new state right away. The update
        # listener in __init__.py pushes the value to the feed-in sensor; the
        # entry is neither reloaded nor is the CSV fetched again.
        self.async_write_ha_state()


class MinPriceNumber(_OptionNumber):
    """Minimum price floor (Rp/kWh) for the feed-in remuneration."""

    _option_key = CONF_MIN_PRICE_RP
    _default = DEFAULT_MIN_PRICE_RP

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry)
        self._attr_name = t("min_price_name", hass)
        self._attr_unique_id = f"{entry.entry_id}_min_price"
        # Fixed object ids (here and below), independent of the localized
        # name, with the entry's discriminator appended so they stay tied
        # to their config entry.
        self.entity_id = f"number.solar_reference_price_min_price_{entry_suffix(entry)}"


class GooSurchargeNumber(_OptionNumber):
    """Guarantee-of-origin surcharge (Rp/kWh) for the feed-in remuneration."""

    _option_key = CONF_GOO_SURCHARGE_RP
    _default = DEFAULT_GOO_SURCHARGE_RP

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry)
        self._attr_name = t("goo_surcharge_name", hass)
        self._attr_unique_id = f"{entry.entry_id}_goo_surcharge"
        self.entity_id = f"number.solar_reference_price_goo_surcharge_{entry_suffix(entry)}"
