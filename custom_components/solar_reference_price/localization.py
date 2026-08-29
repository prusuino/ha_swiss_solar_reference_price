"""Runtime string localization (entity names, device info).

Home Assistant's translation system (strings.json / translations/*.json)
covers the config/options flow text here. It could also translate entity
names through translation keys, but it has no mechanism for the device
name, manufacturer and model, and an object id generated from a translated
entity name would differ per language. This integration therefore keeps
fixed, non-localized object ids (set explicitly in sensor.py / number.py)
and localizes the displayed names and the device info itself with this
minimal lookup, keyed by hass.config.language. Falls back to English for
any language there are no strings for.
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
    "diagnostics_host_name": {
        "de": "Diagnose: Quelle (Host)",
        "en": "Diagnostics: Source (Host)",
        "fr": "Diagnostic : source (hôte)",
        "it": "Diagnostica: fonte (host)",
    },
    "diagnostics_path_name": {
        "de": "Diagnose: Pfad",
        "en": "Diagnostics: Path",
        "fr": "Diagnostic : chemin",
        "it": "Diagnostica: percorso",
    },
    "diagnostics_quarter_name": {
        "de": "Diagnose: Quartal/Jahr",
        "en": "Diagnostics: Quarter/Year",
        "fr": "Diagnostic : trimestre/année",
        "it": "Diagnostica: trimestre/anno",
    },
    "diagnostics_last_checked_name": {
        "de": "Diagnose: Letzte Prüfung",
        "en": "Diagnostics: Last Checked",
        "fr": "Diagnostic : dernière vérification",
        "it": "Diagnostica: ultimo controllo",
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
