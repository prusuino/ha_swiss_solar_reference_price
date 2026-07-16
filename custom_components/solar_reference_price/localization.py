"""Runtime string localization (entity names, device info).

Home Assistant's built-in translation system (strings.json / translations/*.json)
only covers config/options flow text. Entity names and device info are set
directly by this integration's Python code and are not covered by that
mechanism, so we do our own minimal lookup here, keyed by hass.config.language.
Falls back to English for any language we don't have strings for.
"""
from __future__ import annotations

from homeassistant.core import HomeAssistant

SUPPORTED_LANGUAGES = ("de", "en", "fr", "it")

STRINGS: dict[str, dict[str, str]] = {
    "device_name": {
        "de": "Referenzmarktpreis Solar Schweiz (BFE)",
        "en": "Swiss Solar Reference Price (SFOE)",
        "fr": "Prix de référence du marché solaire suisse (OFEN)",
        "it": "Prezzo di riferimento di mercato solare svizzero (UFE)",
    },
    "manufacturer": {
        "de": "BFE (Bundesamt für Energie)",
        "en": "SFOE (Swiss Federal Office of Energy)",
        "fr": "OFEN (Office fédéral de l'énergie)",
        "it": "UFE (Ufficio federale dell'energia)",
    },
    "model": {
        "de": "Referenz-Marktpreise, Art. 15 EnFV",
        "en": "Reference Market Prices, Art. 15 EnFV (Energy Support Ordinance)",
        "fr": "Prix de référence du marché, art. 15 EnFV (ordonnance sur l'encouragement énergétique)",
        "it": "Prezzi di riferimento di mercato, art. 15 EnFV (ordinanza sulla promozione energetica)",
    },
    "reference_price_name": {
        "de": "Referenzmarktpreis PV",
        "en": "PV Reference Market Price",
        "fr": "Prix de référence du marché PV",
        "it": "Prezzo di riferimento di mercato FV",
    },
    "feedin_price_name": {
        "de": "Einspeisepreis",
        "en": "Feed-in Price",
        "fr": "Prix de reprise",
        "it": "Prezzo di ripresa",
    },
    "min_price_name": {
        "de": "Mindestpreis",
        "en": "Minimum Price",
        "fr": "Prix minimum",
        "it": "Prezzo minimo",
    },
    "goo_surcharge_name": {
        "de": "Herkunftsnachweis-Aufschlag",
        "en": "Guarantee of Origin Surcharge",
        "fr": "Supplément garantie d'origine",
        "it": "Supplemento garanzia d'origine",
    },
}


def get_language(hass: HomeAssistant) -> str:
    lang = (hass.config.language or "en").lower().split("-")[0]
    return lang if lang in SUPPORTED_LANGUAGES else "en"


def t(key: str, hass: HomeAssistant, **kwargs) -> str:
    """Look up a localized string by key, formatted with kwargs."""
    lang = get_language(hass)
    template = STRINGS.get(key, {}).get(lang) or STRINGS.get(key, {}).get("en") or key
    return template.format(**kwargs) if kwargs else template
