"""Sensors for the Swiss Solar Reference Price integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_GOO_SURCHARGE_RP,
    CONF_MIN_PRICE_RP,
    DEFAULT_GOO_SURCHARGE_RP,
    DEFAULT_MIN_PRICE_RP,
    DOMAIN,
)
from .coordinator import SolarReferencePriceCoordinator
from .device import device_info as _device_info
from .localization import t


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: SolarReferencePriceCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            ReferenceMarketPriceSensor(hass, coordinator, entry),
            FeedInPriceSensor(hass, coordinator, entry),
        ]
    )


class ReferenceMarketPriceSensor(CoordinatorEntity[SolarReferencePriceCoordinator], SensorEntity):
    """Current PV reference market price (Rp/kWh), published quarterly by the SFOE."""

    _attr_has_entity_name = False
    _attr_native_unit_of_measurement = "Rp/kWh"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:cash-sync"

    def __init__(
        self, hass: HomeAssistant, coordinator: SolarReferencePriceCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = t("reference_price_name", hass)
        self._attr_unique_id = f"{entry.entry_id}_reference_price"
        self._attr_device_info = _device_info(hass, entry)
        self.entity_id = "sensor.solar_reference_price"

    @property
    def native_value(self):
        data = self.coordinator.data
        return data["rp_kwh"] if data else None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        return {
            "quarter": data["quarter"],
            "chf_kwh": data["chf_kwh"],
            "history": data["history"],
        }


class FeedInPriceSensor(CoordinatorEntity[SolarReferencePriceCoordinator], SensorEntity):
    """Computed feed-in price: max(reference market price, minimum price) + GoO surcharge."""

    _attr_has_entity_name = False
    _attr_native_unit_of_measurement = "CHF/kWh"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:transmission-tower-export"

    def __init__(
        self, hass: HomeAssistant, coordinator: SolarReferencePriceCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = t("feedin_price_name", hass)
        self._attr_unique_id = f"{entry.entry_id}_feedin_price"
        self._attr_device_info = _device_info(hass, entry)
        self.entity_id = "sensor.feedin_price"

    def _min_price_rp(self) -> float:
        return self._entry.options.get(CONF_MIN_PRICE_RP, DEFAULT_MIN_PRICE_RP)

    def _goo_surcharge_rp(self) -> float:
        return self._entry.options.get(CONF_GOO_SURCHARGE_RP, DEFAULT_GOO_SURCHARGE_RP)

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None
        price_rp = max(data["rp_kwh"], self._min_price_rp()) + self._goo_surcharge_rp()
        return round(price_rp / 100, 4)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        return {
            "reference_price_chf_kwh": data["chf_kwh"],
            "min_price_chf_kwh": round(self._min_price_rp() / 100, 4),
            "goo_surcharge_chf_kwh": round(self._goo_surcharge_rp() / 100, 4),
        }
