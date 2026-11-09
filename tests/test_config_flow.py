"""Config flow tests: setup with the two price parameters, range check, one
instance only and the options flow."""
from __future__ import annotations

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.solar_reference_price.const import CONF_GOO_SURCHARGE_RP, CONF_MIN_PRICE_RP, DOMAIN


async def test_setup_stores_the_prices_as_options(hass: HomeAssistant, enable_custom_integrations) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["step_id"] == "user"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_MIN_PRICE_RP: 6, CONF_GOO_SURCHARGE_RP: 2.5})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {}
    assert result["options"] == {CONF_MIN_PRICE_RP: 6.0, CONF_GOO_SURCHARGE_RP: 2.5}


async def test_out_of_range_price_is_rejected_by_the_form(hass: HomeAssistant, enable_custom_integrations) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    try:
        await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_MIN_PRICE_RP: 99, CONF_GOO_SURCHARGE_RP: 2})
    except InvalidData:
        pass
    else:
        raise AssertionError("a price of 99 Rp/kWh must not pass the schema")


async def test_only_one_instance(hass: HomeAssistant, enable_custom_integrations) -> None:
    MockConfigEntry(domain=DOMAIN, title="SFOE", data={}, options={CONF_MIN_PRICE_RP: 6.0, CONF_GOO_SURCHARGE_RP: 2.0}).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_options_flow(hass: HomeAssistant, enable_custom_integrations) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="SFOE", data={}, options={CONF_MIN_PRICE_RP: 6.0, CONF_GOO_SURCHARGE_RP: 2.0})
    entry.add_to_hass(hass)
    with patch("custom_components.solar_reference_price.async_setup_entry", return_value=True):
        assert await hass.config_entries.async_setup(entry.entry_id)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["step_id"] == "init"
    result = await hass.config_entries.options.async_configure(result["flow_id"], {CONF_MIN_PRICE_RP: 8, CONF_GOO_SURCHARGE_RP: 1.5})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {CONF_MIN_PRICE_RP: 8.0, CONF_GOO_SURCHARGE_RP: 1.5}
