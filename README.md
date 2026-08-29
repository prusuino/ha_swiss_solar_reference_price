# Swiss Solar Reference Price (SFOE)

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
<a href="https://www.buymeacoffee.com/prusuino"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" height="20"></a>

A Home Assistant custom integration that tracks the Swiss **reference market price for solar power** (*Referenz-Marktpreis*, per Art. 15 EnFV), published quarterly by the Swiss Federal Office of Energy (SFOE), and computes a feed-in price from it.

## Background

Under the Swiss Energy Support Ordinance (EnFV), grid operators may base solar feed-in remuneration on a quarterly **reference market price** published by the [SFOE](https://www.bfe.admin.ch/). This integration fetches that price automatically from the SFOE's official Open Data CSV and turns it into Home Assistant entities you can use in dashboards, energy-cost calculations, or automations — instead of manually looking up and updating the value every quarter.

## What it provides

| Entity | Type | Description |
|---|---|---|
| `sensor.solar_reference_price_<id>` | Sensor | Current quarterly PV reference market price, in **Rp/kWh** (Swiss Rappen). Attributes: `quarter` (e.g. `"Q2 2026"`), `chf_kwh` (same value in CHF/kWh), `history` (list of the last 8 quarters) |
| `sensor.solar_reference_price_feedin_price_<id>` | Sensor | Computed feed-in price in **CHF/kWh**: `max(reference market price, minimum price) + guarantee-of-origin surcharge` |
| `number.solar_reference_price_min_price_<id>` | Number | Minimum price floor (Rp/kWh) — directly adjustable |
| `number.solar_reference_price_goo_surcharge_<id>` | Number | Guarantee-of-origin surcharge (Rp/kWh) — directly adjustable |
| `sensor.solar_reference_price_diagnostics_host_<id>` | Sensor (diagnostic) | Host the CSV is fetched from (`www.bfe-ogd.ch`). Attribute: `csv_url` (the full URL) |
| `sensor.solar_reference_price_diagnostics_path_<id>` | Sensor (diagnostic) | Path of the CSV file on that host (`/ogd60_rmp_quartalspreise.csv`) |
| `sensor.solar_reference_price_diagnostics_quarter_<id>` | Sensor (diagnostic) | Most recent quarter the published data covers (e.g. `"Q2 2026"`), so a stale source becomes visible. Attribute: `quarters_in_dataset` (number of quarters in the CSV) |
| `sensor.solar_reference_price_diagnostics_last_checked_<id>` | Sensor (diagnostic) | Timestamp (`timestamp` device class) of the last successful fetch and parse of the CSV |

The four diagnostic sensors carry the *diagnostic* entity category: Home Assistant lists them in the device's **Diagnostics** section and leaves them out of auto-generated dashboards.

The integration suggests these object ids itself when an entity is first created, so they do not depend on your Home Assistant language — only the displayed names are localized. `<id>` stands for the last four characters of the config entry's id, in lower case (for example `sensor.solar_reference_price_feedin_price_7f3a`); it keeps each id tied to the config entry it belongs to. Installs set up with version 1.2.0 or earlier keep the ids they already have — the unsuffixed form (`sensor.solar_reference_price`, `sensor.solar_reference_price_feedin_price`, …) or, from version 1.1.1 and earlier, `sensor.feedin_price`, `number.min_price` and `number.goo_surcharge`: Home Assistant applies a suggested id only on first creation. Rename them in the entity settings if you want a different form.

Data is fetched from `https://www.bfe-ogd.ch/ogd60_rmp_quartalspreise.csv` (the SFOE's official Open Government Data source) every 6 hours. The SFOE publishes new figures roughly 2 weeks after each quarter ends, so 6-hourly polling is more than sufficient — it exists to promptly reflect the new quarter's price once published, not to catch faster changes.

## Language

Entity names, the device name/manufacturer/model, and the config flow adapt automatically to your Home Assistant language setting — German, English, French, and Italian are supported, with English as the fallback for any other language.

## Installation

### HACS (recommended)

1. Open **HACS**, search for **"Swiss Solar Reference Price"** and download it — or use the button, which opens the integration directly in your HACS:

   [![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=prusuino&repository=ha_swiss_solar_reference_price&category=integration)

2. Restart Home Assistant.

Until the integration shows up in the HACS search, the button above adds it as a custom repository.

### Manual

1. Copy the `custom_components/solar_reference_price` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **"Swiss Solar Reference Price (SFOE)"**.
3. Enter your **minimum price** and **guarantee-of-origin surcharge** (both in Rp/kWh, 0–50) — defaults are 6 and 2 Rp/kWh, matching common grid-operator practice, but adjust to whatever your own grid operator applies.
4. Done — the entities above appear immediately, and the two price parameters can be changed later either via the integration's **Configure** dialog or directly through the `number.solar_reference_price_min_price_<id>` / `number.solar_reference_price_goo_surcharge_<id>` entities (e.g. from a dashboard). Either way the feed-in price is recalculated immediately, without reloading the integration or downloading the CSV again.

## Example: using `sensor.solar_reference_price_feedin_price_<id>` in a cost calculation

Replace `<id>` with the suffix of your own entity (see above).

```yaml
template:
  - sensor:
      - name: "Feed-in revenue rate"
        unit_of_measurement: "CHF/h"
        state: >
          {% set feed_in_w = states('sensor.grid_export_power') | float(0) %}
          {% set price = states('sensor.solar_reference_price_feedin_price_<id>') | float(0) %}
          {{ ((max(feed_in_w, 0) / 1000) * price) | round(6) }}
```

## Notes

- Only one instance of this integration can be configured (there is only one Swiss reference market price).
- If the SFOE data source is unreachable or the CSV format changes, `sensor.solar_reference_price_<id>`, `sensor.solar_reference_price_feedin_price_<id>` and the diagnostic sensors become `unavailable` rather than reporting a stale or incorrect value.
- This integration is unofficial and not affiliated with the SFOE. It only reads their published Open Data.

## Disclaimer

This integration is provided **as-is, without any warranty**. Prices are computed from third-party published data and may be inaccurate, delayed, or unavailable. Do not rely on it as your sole source for financial or contractual decisions. The author(s) accept **no responsibility or liability** for any damage, financial loss, incorrect readings, or other issues arising from using this integration, whether it stops working, behaves unexpectedly, or never worked correctly for your setup in the first place.

## License

MIT — see [LICENSE](LICENSE).

## Related integrations

More Home Assistant integrations from the same author:

- [Swiss Waters](https://github.com/prusuino/ha_swiss_waters) — live water temperature, water level, discharge and flood danger levels of Swiss rivers and lakes
- [Swiss Charging Stations](https://github.com/prusuino/ha_swiss_charging_stations) — real-time availability and prices of public EV charging stations in Switzerland
- [Austrian Charging Stations](https://github.com/prusuino/ha_austrian_charging_stations) — real-time availability of public EV charging stations in Austria
- [Swiss Transport](https://github.com/prusuino/ha_swiss_transport) — live public-transport departure boards and saved connections
- [Swiss Parking](https://github.com/prusuino/ha_swiss_parking) — live free parking spaces in Swiss cities
- [Swiss Electricity Price](https://github.com/prusuino/ha_swiss_electricity_price) — electricity tariffs of any Swiss grid operator (ElCom)
- [Swiss Earthquakes](https://github.com/prusuino/ha_swiss_earthquakes) — recent Swiss earthquakes on the built-in map
- [Swiss Public Alerts](https://github.com/prusuino/ha_swiss_public_alerts) — official Swiss public alerts (Alertswiss) with home-location matching
- [Swiss Avalanche Bulletin](https://github.com/prusuino/ha_swiss_avalanche_bulletin) — the official SLF avalanche bulletin for your location
- [Innoxel Master 3](https://github.com/prusuino/ha_innoxel_master3) — local control of the Innoxel Master 3 home-automation system

## Support

If this integration is useful to you, you can support its development:

<a href="https://www.buymeacoffee.com/prusuino"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="41"></a>
