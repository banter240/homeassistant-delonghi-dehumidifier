## [0.3.1-dev.1](https://github.com/banter240/homeassistant-delonghi-dehumidifier/compare/v0.3.0...v0.3.1-dev.1) (2026-11-12)

### 🐛 Bug Fixes

* fix(auth): tolerate consent page signature quoting change

  The consent page started emitting the consentObj2Sig value as a
  double-quoted JavaScript string. The previous split on a fixed
  single-quoted prefix raised IndexError during login, which surfaced
  as an unexplained invalid_cloud_response setup failure for every
  account. Match the marker with either quoting style and raise a
  descriptive authentication error when the marker is absent.
