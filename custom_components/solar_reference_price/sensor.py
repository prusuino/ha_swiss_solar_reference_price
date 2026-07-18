"""Sensors for the Swiss Solar Reference Price integration."""
from __future__ import annotations

from urllib.parse import urlsplit

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    CONF_GOO_SURCHARGE_RP,
    CONF_MIN_PRICE_RP,
    CSV_URL,
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
            DiagnosticHostSensor(hass, coordinator, entry),
            DiagnosticPathSensor(hass, coordinator, entry),
            DiagnosticQuarterSensor(hass, coordinator, entry),
            DiagnosticLastCheckedSensor(hass, coordinator, entry),
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


class _DiagnosticSensorBase(CoordinatorEntity[SolarReferencePriceCoordinator], SensorEntity):
    """Shared setup for the diagnostic sensors below — each shows exactly one
    piece of source info as its own visible entity (rather than bundled as
    hidden attributes on a single sensor), so they show up as separate rows
    under the device's Diagnostics section."""

    _attr_has_entity_name = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, hass: HomeAssistant, coordinator: SolarReferencePriceCoordinator,
        entry: ConfigEntry, name_key: str, id_suffix: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = t(name_key, hass)
        self._attr_unique_id = f"{entry.entry_id}_diagnostics_{id_suffix}"
        self._attr_device_info = _device_info(hass, entry)
        self.entity_id = f"sensor.solar_reference_price_diagnostics_{id_suffix}"


class DiagnosticHostSensor(_DiagnosticSensorBase):
    """The host the quarterly price CSV is fetched from. The full URL is
    available as an attribute for copy-pasting."""

    _attr_icon = "mdi:web"

    def __init__(self, hass, coordinator, entry):
        super().__init__(hass, coordinator, entry, "diagnostics_host_name", "host")

    @property
    def native_value(self):
        return urlsplit(CSV_URL).netloc

    @property
    def extra_state_attributes(self):
        return {"csv_url": CSV_URL}


class DiagnosticPathSensor(_DiagnosticSensorBase):
    """Path of the CSV file on the source host (the file sits at the root,
    so this includes the file name)."""

    _attr_icon = "mdi:file-outline"

    def __init__(self, hass, coordinator, entry):
        super().__init__(hass, coordinator, entry, "diagnostics_path_name", "path")

    @property
    def native_value(self):
        return urlsplit(CSV_URL).path


class DiagnosticQuarterSensor(_DiagnosticSensorBase):
    """The most recent quarter the published data covers (e.g. "Q2 2026") —
    the data's own validity period, so a stale source becomes visible."""

    _attr_icon = "mdi:calendar-outline"

    def __init__(self, hass, coordinator, entry):
        super().__init__(hass, coordinator, entry, "diagnostics_quarter_name", "quarter")

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("quarter")

    @property
    def extra_state_attributes(self):
        quarters_total = (self.coordinator.data or {}).get("quarters_total")
        return {"quarters_in_dataset": quarters_total} if quarters_total else {}


class DiagnosticLastCheckedSensor(_DiagnosticSensorBase):
    """When the CSV was last successfully fetched and parsed."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, hass, coordinator, entry):
        super().__init__(hass, coordinator, entry, "diagnostics_last_checked_name", "last_checked")

    @property
    def native_value(self):
        last_checked = (self.coordinator.data or {}).get("last_checked")
        return dt_util.parse_datetime(last_checked) if last_checked else None
