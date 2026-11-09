"""The SFOE CSV reader of the coordinator, against a faked download."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.solar_reference_price.const import DOMAIN
from custom_components.solar_reference_price.coordinator import SolarReferencePriceCoordinator

CSV = """Year,Period,Price_pv_CHF_MWh,Price_CHF_MWh
2025,Q4,61.5,90.1
2026,Q2,48.25,80.0
2026,Q1,75.0,95.5
"""


class _Response:
    def __init__(self, text, status=200):
        self._text = text
        self.status = status

    def raise_for_status(self):
        if self.status >= 400:
            raise OSError(f"HTTP {self.status}")

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Session:
    def __init__(self, response):
        self._response = response

    def get(self, url, **kwargs):
        return self._response


def _coordinator(hass):
    entry = MockConfigEntry(domain=DOMAIN, title="SFOE", data={}, options={})
    entry.add_to_hass(hass)
    return SolarReferencePriceCoordinator(hass, entry)


async def test_latest_quarter_wins_regardless_of_row_order(hass: HomeAssistant, enable_custom_integrations) -> None:
    with patch("custom_components.solar_reference_price.coordinator.async_get_clientsession", return_value=_Session(_Response(CSV))):
        data = await _coordinator(hass)._async_update_data()
    assert data["quarter"] == "Q2 2026"
    assert data["rp_kwh"] == 4.83  # 48.25 CHF/MWh
    assert data["chf_kwh"] == 0.04825
    assert [h["quarter"] for h in data["history"]] == ["Q4 2025", "Q1 2026", "Q2 2026"]
    assert data["quarters_total"] == 3
    assert data["last_checked"]


async def test_unreachable_source_and_broken_csv(hass: HomeAssistant, enable_custom_integrations) -> None:
    with patch("custom_components.solar_reference_price.coordinator.async_get_clientsession", return_value=_Session(_Response("", status=503))):
        with pytest.raises(UpdateFailed, match="unreachable"):
            await _coordinator(hass)._async_update_data()
    with patch("custom_components.solar_reference_price.coordinator.async_get_clientsession", return_value=_Session(_Response("Year,Period\n"))):
        with pytest.raises(UpdateFailed, match="parse"):
            await _coordinator(hass)._async_update_data()
    with patch("custom_components.solar_reference_price.coordinator.async_get_clientsession", return_value=_Session(_Response("Jahr,Quartal,Preis\n2026,Q1,75\n"))):
        with pytest.raises(UpdateFailed, match="parse"):
            await _coordinator(hass)._async_update_data()
