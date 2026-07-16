"""Shared device info for all platforms."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .localization import t


def device_info(hass: HomeAssistant, entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=t("device_name", hass),
        manufacturer=t("manufacturer", hass),
        model=t("model", hass),
        entry_type="service",
    )
