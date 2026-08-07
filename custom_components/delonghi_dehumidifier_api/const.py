"""Constants."""

from __future__ import annotations

import base64
from datetime import timedelta
from enum import Enum
from typing import Any, Final

from homeassistant.const import Platform

DOMAIN = "delonghi_dehumidifier_api"
MANUFACTURER = "DeLonghi"

POLL_INTERVAL_SECONDS = 20
SCAN_INTERVAL = timedelta(seconds=POLL_INTERVAL_SECONDS)

DEFAULT_LANGUAGE = "en"
CONFIG_FLOW_VERSION = 1

PLATFORMS: Final[list[Platform]] = [
    Platform.BINARY_SENSOR,
    Platform.HUMIDIFIER,
    Platform.SENSOR,
    Platform.SWITCH,
]

HUMIDITY_MIN = 0
HUMIDITY_MAX = 100

DEVICE_NAME_SUFFIX = "Dehumidifier"
ENTITY_KIND_SENSOR = "sensor"
ENTITY_KIND_SWITCH = "switch"
ENTITY_KIND_BINARY_SENSOR = "binary_sensor"
ENTITY_KIND_DEHUMIDIFIER = "dehumidifier"
HUMIDIFIER_UNIQUE_ID_SUFFIX = "dehumidifier"

ALARM_OK = 0
ALARM_TANK = 3
KNOWN_ALARM_STATES: Final[frozenset[int]] = frozenset({ALARM_OK, ALARM_TANK})

ALARM_LABEL_OK = "ok"
ALARM_LABEL_TANK = "tank"
ALARM_LABEL_UNKNOWN = "unknown"
ALARM_LABELS: Final[tuple[str, ...]] = (
    ALARM_LABEL_OK,
    ALARM_LABEL_TANK,
    ALARM_LABEL_UNKNOWN,
)
ALARM_LABEL_BY_CODE: Final[dict[int, str]] = {
    ALARM_OK: ALARM_LABEL_OK,
    ALARM_TANK: ALARM_LABEL_TANK,
}

TEMP_TENTHS_DIVISOR = 10.0
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
FILTER_LIFE_MINUTES_PER_DAY = MINUTES_PER_HOUR * HOURS_PER_DAY

FIRST_DEVICE_INDEX = 0

HTTP_OK = 200
HTTP_CLIENT_ERROR = 400

CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_FORM = "application/x-www-form-urlencoded"
AUTH_TOKEN_PREFIX = "auth_token "
TIME_FORMAT_HMS = "%H:%M:%S"

REAL_FEEL_ACTIVATION_PAYLOAD = "AQIDChIXHEY8Mig="
REAL_FEEL_IDLE_PAYLOAD = "AAIDChIXHEY8Mig="

PROP_PRODUCT_NAME = "product_name"
PROP_APPLIANCE_MODEL = "appliance_model"
PROP_FIRMWARE_VERSION = "firmware_version"
PROP_HARDWARE_VERSION = "hardware_version"
PROP_CURRENT_HUMIDITY = "current_humidity"
PROP_HUMIDITY_SETPOINT = "humidity_setpoint"
PROP_CURRENT_SPEED = "current_speed"
PROP_DEVICE_MODE = "device_mode"
PROP_DEVICE_STATUS = "device_status"
PROP_FILTER_CHANGE_ALARM = "filter_change_alarm"
PROP_FILTER_LIFE = "filter_life"
PROP_FILTER_STATUS = "filter_status"
PROP_ALARM_STATE = "alarm_state"
PROP_HEAT_EXCHANGER_TEMP = "heat_exchanger_temp"
PROP_ROOM_TEMP = "room_temp"
PROP_SWING = "swing"
PROP_SET_ECO = "set_eco"
PROP_SET_STATUS = "set_status"
PROP_ACTIVATE_REALFEEL = "activate_realfeel"


class Status(Enum):
    ON = 1
    OFF = 2
    FAULT = 3


STATUS_BY_VALUE: Final = {status.value: status for status in Status}


class Mode(Enum):
    DEHUMIDIFY = 1
    DRY_CLOTHES = 2
    PURIFIER = 3
    REAL_FEEL = 100


MODE_BY_VALUE: Final = {mode.value: mode for mode in Mode}
MODE_BY_KEY: Final = {mode.name.lower(): mode for mode in Mode}

HUMIDIFIER_MODES: Final[tuple[str, ...]] = tuple(
    mode.name.lower()
    for mode in (
        Mode.DEHUMIDIFY,
        Mode.DRY_CLOTHES,
        Mode.PURIFIER,
        Mode.REAL_FEEL,
    )
)


class OffOnStatus(Enum):
    OFF = 0
    ON = 1


OFF_ON_STATUS_BY_VALUE: Final = {status.value: status for status in OffOnStatus}


class FilterStatus(Enum):
    OK = 0
    ATTENTION = 1
    NEEDS_REPLACEMENT = 2


FILTER_STATUS_BY_VALUE: Final = {status.value: status for status in FilterStatus}

PATH_DEVICES = "apiv1/devices.json"

# https://docs.aylanetworks.com/reference
# Token flow: https://github.com/duckwc/ECAMpy
SDK_BUILD = 16650

API_KEY = "3_e5qn7USZK-QtsIso1wCelqUKAK_IVEsYshRIssQ-X-k55haiZXmKWDHDRul2e5Y2"
CLIENT_ID = "1S8q1WJEs-emOB43Z0-66WnL"
CLIENT_SECRET = "lmnceiD0B-4KPNN5ZS6WuWU70j9V5BCuSlz2OPsvHkyLryhMkJkPvKsivfTq3RfNYj8GpCELtOBvhaDIzKcBtg"
AUTHORIZATION_HEADER = (
    "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
)
APP_ID = "DeLonghiComfort2-mw-id"
APP_SECRET = "DeLonghiComfort2-Yg4miiqiNcf0Or-EhJwRh7ACfBY"

BROWSER_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "CriOS/79.0.3945.73 Mobile/15E148 Safari/604.1"
)
TOKEN_USER_AGENT = "DeLonghiComfort/3 CFNetwork/1568.300.101 Darwin/24.2.0"
API_USER_AGENT = "DeLonghiComfort/5.1.1 (iPhone; iOS 18.2; Scale/3.00)"

GIGYA_OIDC_BASE = f"https://fidm.eu1.gigya.com/oidc/op/v1.0/{API_KEY}"
GIGYA_AUTHORIZE_URL = f"{GIGYA_OIDC_BASE}/authorize"
GIGYA_AUTHORIZE_CONTINUE_URL = f"{GIGYA_OIDC_BASE}/authorize/continue"
GIGYA_TOKEN_URL = f"{GIGYA_OIDC_BASE}/token"
GIGYA_GET_IDS_URL = "https://socialize.eu1.gigya.com/socialize.getIDs"
GIGYA_LOGIN_URL = "https://accounts.eu1.gigya.com/accounts.login"
GIGYA_GET_USER_INFO_URL = "https://socialize.eu1.gigya.com/socialize.getUserInfo"
DELONGHI_OIDC_PAGE_URL = "https://aylaopenid.delonghigroup.com/"
DELONGHI_CONSENT_URL = "https://aylaopenid.delonghigroup.com/OIDCConsentPage.php"
AYLA_USER_BASE = "https://user-field-eu.aylanetworks.com"
AYLA_ADS_BASE = "https://ads-eu.aylanetworks.com"
AYLA_REFRESH_TOKEN_URL = f"{AYLA_USER_BASE}/users/refresh_token.json"
AYLA_TOKEN_SIGN_IN_URL = f"{AYLA_USER_BASE}/api/v1/token_sign_in"

OAUTH_REDIRECT_URI = "https://google.it"
OAUTH_SCOPE = "openid email profile UID comfort en alexa"
OAUTH_SCOPE_PLUS = "openid+email+profile+UID+comfort+en+alexa"
GIGYA_SDK = "js_latest"
GIGYA_FORMAT_JSON = "json"
GIGYA_SESSION_EXPIRATION = 7884009

CONSENT_SIGNATURE_PREFIX = "const consentObj2Sig = '"
CONSENT_SIGNATURE_SUFFIX = "';"

GIGYA_RISK_CONTEXT_BASE: Final[dict[str, Any]] = {
    "b0": 4494,
    "b1": [0, 2, 2, 0],
    "b2": 2,
    "b3": [],
    "b4": 2,
    "b5": 1,
    "b7": [
        {"name": "PDF Viewer", "filename": "internal-pdf-viewer", "length": 2},
        {"name": "Chrome PDF Viewer", "filename": "internal-pdf-viewer", "length": 2},
        {"name": "Chromium PDF Viewer", "filename": "internal-pdf-viewer", "length": 2},
        {
            "name": "Microsoft Edge PDF Viewer",
            "filename": "internal-pdf-viewer",
            "length": 2,
        },
        {
            "name": "WebKit built-in PDF",
            "filename": "internal-pdf-viewer",
            "length": 2,
        },
    ],
    "b9": 0,
    "b10": {"state": "denied"},
    "b11": False,
    "b13": [5, "440|956|24", False, True],
}
