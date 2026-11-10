# Changelog

## 1.6.1 — 2026-11-10

- **New icon and logo.** The integration has a new icon and a new logo, now with a variant for the dark theme. They appear under Settings → Devices & services and in the Marketplace. The README gained a header image.

## 1.6.0 — 2026-11-09

- **Version on the service card.** The integration's version now appears on its service card under Settings → Devices & services, where the entities are listed.
- **Repair notices.** An unreachable or unreadable SFOE data file raises a notice under Settings → Repairs after three failed refreshes; it withdraws itself. No change to entities or configuration.

## 1.5.0 — 2026-11-09

- **Quality scale Bronze.** The integration keeps its coordinator in the config entry's runtime data, the README gained removal instructions and a quality-scale section, and the manifest declares the **bronze** tier. A test suite (CSV reader with quarter ordering and error cases, config flow with range check, single instance and options) runs on every push. No change to entities or configuration.

## 1.4.1 — 2026-11-06

- **Fixed: the diagnostics download could contain private values.** The entry's unique id went out unredacted: depending on the integration it holds the coordinates of the entry or, for a VKF entry of Swiss Hail Protection, the device serial. The text of the last error could also repeat a request URL. The unique id, the entry title and the entry's name and location fields are now redacted, and only the type of the last error is reported. If you have shared a diagnostics file from the previous version, consider it exposed.

## 1.4.0 — 2026-11-06

- **New: diagnostics download.** The entry menu under **Settings → Devices & services** offers *Download diagnostics*: the entry's configuration, what was last fetched and the current state of its entities, with coordinates, credentials and other personal values redacted and long lists cut. Attach it to an issue report.

## 1.3.0 — 2026-08-29

- Changing the minimum price or the guarantee-of-origin surcharge — through the two number entities or the integration's **Configure** dialog — now takes effect immediately: the feed-in price is recalculated on the spot, without reloading the integration and without downloading the SFOE CSV again. Previously every change reloaded all entities (briefly `unavailable`) and re-fetched the CSV.
- The setup and **Configure** dialogs now enforce the same 0–50 Rp/kWh range as the two number entities; an out-of-range value is rejected instead of being stored.
- The data update is now bound explicitly to the config entry, which avoids a deprecation warning newer Home Assistant versions log at startup.
- README: the entity table now lists the four diagnostic sensors with their entity ids and attributes. SECURITY.md names the exact endpoint the integration talks to.
- The entity ids suggested for newly created entities now end in a per-entry discriminator — the last four characters of the config entry id, in lower case: `sensor.solar_reference_price_<id>`, `sensor.solar_reference_price_feedin_price_<id>`, `number.solar_reference_price_min_price_<id>`, `number.solar_reference_price_goo_surcharge_<id>` and `sensor.solar_reference_price_diagnostics_{host,path,quarter,last_checked}_<id>` (for example `sensor.solar_reference_price_feedin_price_7f3a`). **Existing installs keep their current ids**: Home Assistant applies a suggested id only when an entity is first created, so entities that already exist are not renamed and no automation, template or dashboard needs to change. The new form applies to fresh setups (or when an entity is removed from the entity registry and recreated).
- Existing entity ids and unique ids are unchanged; there is nothing to do after updating.

## 1.2.0 — 2026-08-29

- The feed-in price sensor and the two adjustable price parameters now carry the integration prefix in their entity ids: `sensor.solar_reference_price_feedin_price`, `number.solar_reference_price_min_price` and `number.solar_reference_price_goo_surcharge` (previously `sensor.feedin_price`, `number.min_price` and `number.goo_surcharge`). The old ids were generic enough to collide with entities of other integrations. **Existing installs keep their current ids**: Home Assistant applies the id suggested by an integration only when an entity is first created, so entities that already exist are not renamed and no automation, template or dashboard needs to change. The new ids apply to fresh setups (or when an entity is removed from the entity registry and recreated).

## 1.1.1 — 2026-08-29

- Added an English translation file. Without it, English — the default language — fell back to raw translation keys in the setup and options dialogs.
- The minimum supported Home Assistant version is now declared correctly as 2024.12.0. The options dialog has always required it, but hacs.json still claimed 2024.1.0.
- The CHF/kWh conversion of the latest quarter now runs inside the same guard as the rest of the CSV parsing, so any future change to the SFOE file is reported as a data problem instead of an unhandled error.
- Device info now uses the current `DeviceInfo`/`DeviceEntryType` location from `homeassistant.helpers.device_registry`.

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
