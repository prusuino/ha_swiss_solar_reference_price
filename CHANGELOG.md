# Changelog

## 1.0.0 — 2026-07-16

Initial public release.

- `sensor.solar_reference_price` — current quarterly PV reference market price (Rp/kWh), with `quarter`, `chf_kwh`, and `history` (last 8 quarters) attributes
- `sensor.feedin_price` — computed feed-in price: `max(reference market price, minimum price) + guarantee-of-origin surcharge`
- `number.min_price` / `number.goo_surcharge` — minimum price and guarantee-of-origin surcharge, directly adjustable (persisted as config entry options)
- Config flow with single-instance guard; options flow for changing the two price parameters later
- Multi-language support (German, English, French, Italian) for entity names, device info, and the config flow, based on the Home Assistant language setting
- Data fetched every 6 hours from the official SFOE Open Data CSV
