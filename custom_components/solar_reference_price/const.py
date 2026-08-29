"""Constants for the Swiss Solar Reference Price integration."""
from datetime import timedelta

DOMAIN = "solar_reference_price"
CSV_URL = "https://www.bfe-ogd.ch/ogd60_rmp_quartalspreise.csv"
UPDATE_INTERVAL = timedelta(hours=6)

CONF_MIN_PRICE_RP = "min_price_rp"
CONF_GOO_SURCHARGE_RP = "goo_surcharge_rp"

DEFAULT_MIN_PRICE_RP = 6.0
DEFAULT_GOO_SURCHARGE_RP = 2.0

# Bounds shared by the setup/options dialog and the two number entities, so
# both ways of setting a price parameter accept exactly the same values.
PRICE_RP_MIN = 0.0
PRICE_RP_MAX = 50.0
PRICE_RP_STEP = 0.1
