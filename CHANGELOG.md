# Changelog

## 1.2.0 — 2026-08-29

- The feed-in price sensor and the two adjustable price parameters now carry the integration prefix in their entity ids: `sensor.solar_reference_price_feedin_price`, `number.solar_reference_price_min_price` and `number.solar_reference_price_goo_surcharge` (previously `sensor.feedin_price`, `number.min_price` and `number.goo_surcharge`). The old ids were generic enough to collide with entities of other integrations. **Existing installs keep their current ids**: Home Assistant applies the id suggested by an integration only when an entity is first created, so entities that already exist are not renamed and no automation, template or dashboard needs to change. The new ids apply to fresh setups (or when an entity is removed from the entity registry and recreated).

## 1.1.1 — 2026-08-29

- Added an English translation file. Without it, English — the default language — fell back to raw translation keys in the setup and options dialogs.
- The minimum supported Home Assistant version is now declared correctly as 2024.12.0. The options dialog has always required it, but hacs.json still claimed 2024.1.0.
- The CHF/kWh conversion of the latest quarter now runs inside the same guard as the rest of the CSV parsing, so any future change to the SFOE file is reported as a data problem instead of an unhandled error.

## 1.1.0 — 2026-07-19

- New diagnostic sensors (shown under the device's Diagnostics section), localized in all four languages:
  - Source (Host) — host the quarterly price CSV is fetched from, full URL as attribute
  - Path — path of the CSV file on the source host
  - Quarter/Year — the most recent quarter the published data covers, so a stale source becomes visible
  - Last Checked — timestamp of the last successful fetch and parse

## 1.0.0 — 2026-07-16

Initial public release.

- `sensor.solar_reference_price` — current quarterly PV reference market price (Rp/kWh), with `quarter`, `chf_kwh`, and `history` (last 8 quarters) attributes
- `sensor.feedin_price` — computed feed-in price: `max(reference market price, minimum price) + guarantee-of-origin surcharge`
- `number.min_price` / `number.goo_surcharge` — minimum price and guarantee-of-origin surcharge, directly adjustable (persisted as config entry options)
- Config flow with single-instance guard; options flow for changing the two price parameters later
- Multi-language support (German, English, French, Italian) for entity names, device info, and the config flow, based on the Home Assistant language setting
- Data fetched every 6 hours from the official SFOE Open Data CSV
