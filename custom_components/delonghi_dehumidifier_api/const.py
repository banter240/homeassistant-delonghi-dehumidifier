"""Constants for the DeLonghi Dehumidifier integration."""

DOMAIN = "delonghi_dehumidifier_api"
RUNTIME_REAUTH_ID = "_delonghi_runtime_reauth_id"
# Minimum seconds between cloud property reads; entity polling stays at one minute.
CONF_POLL_INTERVAL = "poll_interval"
DEFAULT_POLL_CACHE_SECONDS = 10
MIN_POLL_CACHE_SECONDS = 10
MAX_POLL_CACHE_SECONDS = 600
REAL_FEEL_ACTIVATION_PAYLOAD = "AQIDChIXHEY8Mig="
REAL_FEEL_DEACTIVATION_PAYLOAD = "AAIDChIXHEY8Mig="
