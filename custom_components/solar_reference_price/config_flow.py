"""Config and options flow for the Swiss Solar Reference Price integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback

from .const import (
    CONF_GOO_SURCHARGE_RP,
    CONF_MIN_PRICE_RP,
    DEFAULT_GOO_SURCHARGE_RP,
    DEFAULT_MIN_PRICE_RP,
    DOMAIN,
    PRICE_RP_MAX,
    PRICE_RP_MIN,
)
from .localization import t

# Same range as the number entities: an out-of-range value is rejected by the
# dialog instead of being stored and then shown outside the entity's bounds.
_PRICE_RP = vol.All(vol.Coerce(float), vol.Range(min=PRICE_RP_MIN, max=PRICE_RP_MAX))


def _schema(defaults: dict[str, float]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_MIN_PRICE_RP, default=defaults[CONF_MIN_PRICE_RP]
            ): _PRICE_RP,
            vol.Required(
                CONF_GOO_SURCHARGE_RP, default=defaults[CONF_GOO_SURCHARGE_RP]
            ): _PRICE_RP,
        }
    )


class SolarReferencePriceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Setup wizard (only one instance allowed)."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title=t("device_name", self.hass),
                data={},
                options={
                    CONF_MIN_PRICE_RP: user_input[CONF_MIN_PRICE_RP],
                    CONF_GOO_SURCHARGE_RP: user_input[CONF_GOO_SURCHARGE_RP],
                },
            )

        defaults = {
            CONF_MIN_PRICE_RP: DEFAULT_MIN_PRICE_RP,
            CONF_GOO_SURCHARGE_RP: DEFAULT_GOO_SURCHARGE_RP,
        }
        return self.async_show_form(step_id="user", data_schema=_schema(defaults))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> "SolarReferencePriceOptionsFlow":
        return SolarReferencePriceOptionsFlow()


class SolarReferencePriceOptionsFlow(OptionsFlow):
    """Change the minimum price / GoO surcharge after setup."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options
        defaults = {
            CONF_MIN_PRICE_RP: current.get(CONF_MIN_PRICE_RP, DEFAULT_MIN_PRICE_RP),
            CONF_GOO_SURCHARGE_RP: current.get(
                CONF_GOO_SURCHARGE_RP, DEFAULT_GOO_SURCHARGE_RP
            ),
        }
        return self.async_show_form(step_id="init", data_schema=_schema(defaults))
