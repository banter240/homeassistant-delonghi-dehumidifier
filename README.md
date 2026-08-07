<div align="center">

# DeLonghi Dehumidifier (API)

Home Assistant custom component for DeLonghi dehumidifiers via the DeLonghi cloud (Ayla/Gigya) API.

<br>

[![Latest Release](https://img.shields.io/github/v/release/banter240/homeassistant-delonghi-dehumidifier?style=for-the-badge&color=e10079&logo=github)](https://github.com/banter240/homeassistant-delonghi-dehumidifier/releases/latest) [![Dev Release](https://img.shields.io/github/v/release/banter240/homeassistant-delonghi-dehumidifier?include_prereleases&label=dev&style=for-the-badge&color=orange&logo=github)](https://github.com/banter240/homeassistant-delonghi-dehumidifier/releases) [![Downloads](https://img.shields.io/github/downloads/banter240/homeassistant-delonghi-dehumidifier/total?style=for-the-badge&color=green&logo=github)](https://github.com/banter240/homeassistant-delonghi-dehumidifier/releases) [![CI](https://img.shields.io/github/actions/workflow/status/banter240/homeassistant-delonghi-dehumidifier/semantic_release.yml?branch=main&style=for-the-badge&logo=github&label=CI)](https://github.com/banter240/homeassistant-delonghi-dehumidifier/actions/workflows/semantic_release.yml) [![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=home-assistant)](https://hacs.xyz) [![License](https://img.shields.io/github/license/banter240/homeassistant-delonghi-dehumidifier?style=for-the-badge&color=blue)](LICENSE)

[![Fluxer](https://img.shields.io/badge/Fluxer-Community-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://fluxer.gg/t5LNln9X) [![Discussions](https://img.shields.io/github/discussions/banter240/homeassistant-delonghi-dehumidifier?style=for-the-badge&logo=github&color=7289DA)](https://github.com/banter240/homeassistant-delonghi-dehumidifier/discussions) [![Open Issues](https://img.shields.io/github/issues/banter240/homeassistant-delonghi-dehumidifier?style=for-the-badge&color=red&logo=github)](https://github.com/banter240/homeassistant-delonghi-dehumidifier/issues) [![Stars](https://img.shields.io/github/stars/banter240/homeassistant-delonghi-dehumidifier?style=for-the-badge&color=yellow&logo=github)](https://github.com/banter240/homeassistant-delonghi-dehumidifier/stargazers)

<br>

<a href="https://buymeacoffee.com/banter240" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 50px !important;width: 181px !important;" ></a>

<br>

**Also by [@banter240](https://github.com/banter240)**

| Project | What |
| :------ | :--- |
| [![tado_hijack](https://img.shields.io/badge/tado__hijack-f1c40f?style=for-the-badge&logo=home-assistant&logoColor=black)](https://github.com/banter240/tado_hijack) | Tado cloud — quota-aware polling, command batching, multi-gen |
| [![HDG Bavaria](https://img.shields.io/badge/HDG_Bavaria-e67e22?style=for-the-badge&logo=home-assistant&logoColor=white)](https://github.com/banter240/hdg_bavaria_homeassistant) | HDG Bavaria boilers — local HTTP, no cloud |

</div>

## Why this repository?

This is a **maintained fork** of [rtfpessoa/homeassistant-delonghi-dehumidifier](https://github.com/rtfpessoa/homeassistant-delonghi-dehumidifier). Full credit for the original reverse‑engineered Ayla/Gigya auth flow and first HA integration goes to that project.

**Why fork instead of only contributing upstream?** Upstream has been effectively inactive while important issues stayed open (tank status, wrong room temperature, startup crashes on null properties, filter life units, and more). Waiting indefinitely was not practical for day‑to‑day use.

**This is not a straight copy.** The integration was largely reworked on top of that foundation:

- Correct scaling and units (temps, filter life), null‑safe cloud property access
- Water tank `binary_sensor` (`alarm_state`), Real Feel mode, humidifier UX aligned with HA
- Single **DataUpdateCoordinator** poll (all entities share one `properties.json` request)
- Modular layout (`helpers/`, coordinator, entity base), en/de translations, quieter production logging
- Project tooling: HACS custom packaging, pre-commit, semantic-release, modern CI

**Where to open issues and PRs:** this repository. Upstream remains linked for history and attribution; if that project becomes active again, relevant fixes can still be offered there.

## Installation

This integration is **not** in the HACS default store. You add it as a **custom repository**.

### HACS (custom repository)

1. Install [HACS][hacs-download] if needed.
2. Open **HACS → Integrations** (three dots menu / overflow).
3. **Custom repositories**
4. Add:
   - **Repository:** `https://github.com/banter240/homeassistant-delonghi-dehumidifier`
   - **Type:** `Integration`
5. Close the dialog, search for **DeLonghi Dehumidifier (API)**, download / install.
6. **Restart Home Assistant.**
7. **Settings → Devices & services → Add integration** → search for **DeLonghi Dehumidifier (API)**, or:

[![Add DeLonghi Dehumidifier (API)][add-integration-badge]][add-integration]

Updates later come through HACS from this repository (when you publish releases/tags).

### Manual

1. Home Assistant **2025.2.4** or newer (see `hacs.json`).
2. Copy `custom_components/delonghi_dehumidifier_api` into your HA `custom_components` folder.
3. Restart Home Assistant and add the integration via the UI.

### Configuration

1. **Settings → Devices & services → Add integration** → **DeLonghi Dehumidifier (API)**.
2. Enter:
   - **Language** — often `en` (must match what Gigya accepts for your account; other codes frequently fail login with no session)
   - **Email** / **password** — same as the official DeLonghi Comfort app
3. On success the integration uses the **first** device on that cloud account and creates humidifier, tank, sensors, and switches under one device entry.
4. Credentials can be changed later via the integration **Configure / options** flow (re-authenticates and reloads).

## Supported appliances

- Tasciugo AriaDry Multi (**DDSX220WFA** / cloud model **DDSX220**)

Requires a DeLonghi Comfort cloud account (EU Ayla/Gigya).

## Limitations

- Only the **first** device on the cloud account is controlled.
- Tank **full** and tank **missing/unseated** share the same cloud signal (`alarm_state == 3`, magnetic float).
- Cloud poll interval is **20 seconds** (one properties request for all entities).

## Entities

| Platform | What you get |
| -------- | ------------ |
| `humidifier` | Main unit: HA states **`on` / `off`**, target/current humidity, modes **`dehumidify`**, **`dry_clothes`**, **`purifier`**, **`real_feel`**. Attribute **`cloud_status`**: raw Ayla status `1` / `2` / `3`. |
| `binary_sensor` | **Water tank** (`device_class: problem`): **`on`** = problem (float alarm), **`off`** = OK. Attribute **`alarm_state`**: raw `0` / `3`. Prefer this for automations. |
| `sensor` | Current / target humidity, fan speed, room & heat-exchanger temperature (°C), filter life (**days** remaining), filter status, filter change alarm, device mode, eco, swing, **alarm** enum (`ok` / `tank` / `unknown`, raw code in **`alarm_code`**). |
| `switch` | Eco mode, swing. |

### Automations (HA-native)

```yaml
# Tank problem
trigger:
  - platform: state
    entity_id: binary_sensor.<device>_water_tank
    to: "on" # problem — use "off" for OK

# Mode (example: Real Feel)
action: humidifier.set_mode
data:
  entity_id: humidifier.<device>_unit
  mode: real_feel
```

## Troubleshooting

### Login / language

If authentication fails, try language code **`en`** in the config flow (Gigya often returns no session for other `lang` values).

### Debug logging (runtime)

[![Logging service][ha-service-badge]][ha-service]

```yaml
service: logger.set_level
data:
  custom_components.delonghi_dehumidifier_api: debug
```

### Debug logging (configuration.yaml)

```yaml
logger:
  logs:
    custom_components.delonghi_dehumidifier_api: debug
```

Restart Home Assistant after changing `configuration.yaml`. Prefer **full logs** when filing an [issue](https://github.com/banter240/homeassistant-delonghi-dehumidifier/issues/new).

On failures look for `Ayla GET` / `Ayla POST` error lines and Gigya login errors.

[![Home Assistant Logs][ha-logs-badge]][ha-logs]

### UI

Lovelace card that works well with dehumidifier entities:

https://github.com/MiguelCosta/Dehumidifier_Comfee_Card

## Credits & license

- **Original integration & cloud reverse engineering:** [rtfpessoa/homeassistant-delonghi-dehumidifier](https://github.com/rtfpessoa/homeassistant-delonghi-dehumidifier) (and related community work such as ECAMpy for token flow ideas)
- **This fork:** continued maintenance, bugfixes, architecture rewrite, packaging, and releases by [@banter240](https://github.com/banter240)

**License:** This fork is **[GPL-3.0](LICENSE)**. Distributed modifications must remain open under GPL-compatible terms. Upstream was MIT; original copyright and MIT notice are preserved in [NOTICE](NOTICE).

### Built with AI assistance

Parts of this project were developed **with AI coding tools** (pair-programming / drafting), then reviewed, tested against a real device, and owned by a human maintainer. That is deliberate: AI speeds up boilerplate and refactors; **correctness, design choices, and what ships** stay with the maintainer.

If you dislike AI-assisted code, this repo may not be for you — no hard feelings. If you care about working integrations and open history, issues and PRs are still welcome here.

## Support the project

Maintained in free time for the Home Assistant community. If this fork saved you from a wet floor, fixed temperatures, or just works when upstream did not, consider supporting development:

<a href="https://buymeacoffee.com/banter240" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 50px !important;width: 181px !important;" ></a>

### Community (Fluxer)

**Support and dev chat live on [Fluxer](https://fluxer.gg/t5LNln9X)** — same community as [tado_hijack](https://github.com/banter240/tado_hijack) and other projects. Prefer Fluxer over Discord for new questions and discussion.

Discord is being phased out (age-verification / data-handling concerns); the old server may still exist for a while, but **new HA support/dev talk belongs on Fluxer**: [join here](https://fluxer.gg/t5LNln9X).

### GitHub

- [Issues](https://github.com/banter240/homeassistant-delonghi-dehumidifier/issues) · [Discussions](https://github.com/banter240/homeassistant-delonghi-dehumidifier/discussions) · Sponsor via [FUNDING.yml](.github/FUNDING.yml)

[add-integration]: https://my.home-assistant.io/redirect/config_flow_start?domain=delonghi_dehumidifier_api
[add-integration-badge]: https://my.home-assistant.io/badges/config_flow_start.svg
[hacs]: https://hacs.xyz
[hacs-download]: https://hacs.xyz/docs/setup/download
[ha-logs]: https://my.home-assistant.io/redirect/logs
[ha-logs-badge]: https://my.home-assistant.io/badges/logs.svg
[ha-service]: https://my.home-assistant.io/redirect/developer_call_service/?service=logger.set_level
[ha-service-badge]: https://my.home-assistant.io/badges/developer_call_service.svg
