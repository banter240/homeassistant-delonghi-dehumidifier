## 1.0.0 (2026-08-07)
* feat(core): rewrite integration with coordinator, tank, Real Feel, and tado-style CI

Maintained-fork overhaul of the DeLonghi Ayla/Gigya cloud integration: single
DataUpdateCoordinator poll, HA-native entities/translations, bugfixes for
temps/filter/tank, and project scaffolding aligned with modern HACS releases.

Addresses upstream:

* ci: align tooling with tado_hijack (custom HACS)

Match workflows, pre-commit (sourcery, mypy, local checks),
pyproject (strict mypy/ruff/poetry), and requirements layout.
Skip hacs/action: custom repo only, not hacs/default (topics/issues
store checks do not apply). Keep local hacs.json/manifest script.

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
via [semantic-release](https://semantic-release.gitbook.io/).
