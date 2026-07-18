"""DataUpdateCoordinator for the Swiss (SFOE) solar reference market price."""
from __future__ import annotations

import csv
import io
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import CSV_URL, DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SolarReferencePriceCoordinator(DataUpdateCoordinator[dict]):
    """Fetches the quarterly reference market prices published by the SFOE."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(CSV_URL, timeout=25) as resp:
                resp.raise_for_status()
                text = await resp.text()
        except Exception as err:
            raise UpdateFailed(f"SFOE reference market price source unreachable: {err}") from err

        try:
            rows = list(csv.DictReader(io.StringIO(text)))
            if not rows:
                raise ValueError("Empty CSV response")
            rows.sort(key=lambda r: (int(r["Year"]), r["Period"]))
            history = [
                {
                    "quarter": f"{r['Period']} {r['Year']}",
                    "rp_kwh": round(float(r["Price_pv_CHF_MWh"]) / 10, 2),
                }
                for r in rows
            ]
            latest = rows[-1]
        except Exception as err:
            raise UpdateFailed(f"Failed to parse the SFOE CSV: {err}") from err

        return {
            "quarter": history[-1]["quarter"],
            "rp_kwh": history[-1]["rp_kwh"],
            "chf_kwh": round(float(latest["Price_pv_CHF_MWh"]) / 1000, 5),
            "history": history[-8:],
            "quarters_total": len(history),
            "last_checked": dt_util.utcnow().isoformat(),
        }
