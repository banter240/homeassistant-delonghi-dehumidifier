## [0.4.0-dev.1](https://github.com/banter240/homeassistant-delonghi-dehumidifier/compare/v0.3.1-dev.2...v0.4.0-dev.1) (2026-11-13)

### ✨ New Features

* feat(options): let users space out cloud property reads

  The client refreshed its shared property snapshot at least every
  10 seconds. Expose the minimum spacing as an optional field in the
  account options and reconfigure forms (10-600 seconds), clamping
  stored values at setup. Entities keep polling once a minute; a
  higher value serves them cached data and reduces cloud requests.
  The default keeps the existing behaviour so Real Feel command
  confirmations are unaffected.

## [0.3.1-dev.2](https://github.com/banter240/homeassistant-delonghi-dehumidifier/compare/v0.3.1-dev.1...v0.3.1-dev.2) (2026-11-12)

### 🐛 Bug Fixes

* fix(humidifier): initialize control state before the first poll

  Home Assistant reads state_attributes when the entity is added,
  before any poll has succeeded. Upstream never initialized
  _attr_mode, _attr_is_on and the humidity attributes, so a failing
  first poll crashed entity addition with AttributeError and left
  the control entity unavailable. Leave all four attributes unknown
  until the first successful cloud read provides real values.

## [0.3.1-dev.1](https://github.com/banter240/homeassistant-delonghi-dehumidifier/compare/v0.3.0...v0.3.1-dev.1) (2026-11-12)

### 🐛 Bug Fixes

* fix(auth): tolerate consent page signature quoting change

  The consent page started emitting the consentObj2Sig value as a
  double-quoted JavaScript string. The previous split on a fixed
  single-quoted prefix raised IndexError during login, which surfaced
  as an unexplained invalid_cloud_response setup failure for every
  account. Match the marker with either quoting style and raise a
  descriptive authentication error when the marker is absent.
