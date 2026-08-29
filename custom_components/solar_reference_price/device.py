"""Shared device info and entry-id helper for all platforms."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import DOMAIN
from .localization import t


def device_info(hass: HomeAssistant, entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=t("device_name", hass),
        manufacturer=t("manufacturer", hass),
        model=t("model", hass),
        entry_type=DeviceEntryType.SERVICE,
    )


def entry_suffix(entry: ConfigEntry) -> str:
    """Per-entry discriminator appended to the suggested object ids: the last
    four characters of the config entry id, in lower case."""
    return entry.entry_id[-4:].lower()
