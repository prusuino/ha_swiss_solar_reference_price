"""Repair notices: an unreachable or unreadable SFOE file after three failed
refreshes, withdrawn with the next good download."""
from __future__ import annotations

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.solar_reference_price.const import DOMAIN
from custom_components.solar_reference_price.coordinator import SolarReferencePriceCoordinator

from .test_coordinator import CSV, _Response, _Session

SESSION = "custom_components.solar_reference_price.coordinator.async_get_clientsession"


def _issue(hass, key, entry):
    return ir.async_get(hass).async_get_issue(DOMAIN, f"{key}_{entry.entry_id}")


async def test_unreachable_then_unreadable_then_fine(hass: HomeAssistant, enable_custom_integrations) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="SFOE", data={}, options={})
    entry.add_to_hass(hass)
    coordinator = SolarReferencePriceCoordinator(hass, entry)
    with patch(SESSION, return_value=_Session(_Response("", status=503))):
        for n in range(3):
            await coordinator.async_refresh()
            assert (_issue(hass, "unreachable", entry) is not None) is (n == 2)
    with patch(SESSION, return_value=_Session(_Response("Jahr,Quartal\n2026,Q1\n"))):
        for n in range(3):
            await coordinator.async_refresh()
            assert (_issue(hass, "unreadable", entry) is not None) is (n == 2)
    assert _issue(hass, "unreachable", entry) is None  # the download works again
    with patch(SESSION, return_value=_Session(_Response(CSV))):
        await coordinator.async_refresh()
    assert coordinator.data["quarter"] == "Q2 2026"
    assert _issue(hass, "unreadable", entry) is None
