"""Swiss Solar Reference Price (SFOE) integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import SolarReferencePriceCoordinator

type SolarReferencePriceConfigEntry = ConfigEntry[SolarReferencePriceCoordinator]

PLATFORMS = ["sensor", "number"]


async def async_setup_entry(hass: HomeAssistant, entry: SolarReferencePriceConfigEntry) -> bool:
    coordinator = SolarReferencePriceCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: SolarReferencePriceConfigEntry) -> None:
    """Apply changed options without reloading the entry.

    The two price parameters live in entry.options and the feed-in sensor
    reads them on every state write, so notifying the coordinator's
    listeners is all it takes. The CSV data is not affected by an option
    change, so nothing is downloaded again either.
    """
    entry.runtime_data.async_update_listeners()


async def async_unload_entry(hass: HomeAssistant, entry: SolarReferencePriceConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
