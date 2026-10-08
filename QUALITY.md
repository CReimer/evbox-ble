# Library quality requirements

The library follows the integration's applicable engineering requirements. Home Assistant-specific rules for configuration flows, entities, devices, repairs, brand assets, and UI documentation belong to the integration. The library itself has no Home Assistant Quality Scale tier.

## Required checks

- Test supported Python versions 3.11 and 3.14 against an installed wheel, without a Home Assistant dependency.
- Require exactly 100% executable-line and branch coverage. Check missing counts in coverage JSON to avoid a rounded percentage accepting gaps.
- Run strict mypy on all library source and Ruff linting and formatting on source, tests, and quality tools.
- Build and validate source and wheel distributions. Rebuild a wheel from the source distribution in CI and test it in a fresh environment.
- Include the `py.typed` marker, license, test sources, quality tools, and public package metadata in the appropriate artifacts.
- Publish only after all checks pass, using the existing PyPI Trusted Publisher. Maintain source tags and a changelog for every release.

## Behavioral contracts

Tests exercise UTF-8 framing, partial and malformed messages, authentication rejection, optional versus required commands, both characteristic layouts, notification races, timeouts, cancellation, connection cleanup, nested transactions, competing tasks, and configuration wire values. They assert observable results and cleanup, not just execution counts.

These tests simulate Bluetooth peers and do not prove physical-device compatibility. Hardware behavior must still be checked for new charger models or firmware. The current firmware/FTP orchestration remains in the HACS integration and is outside this library's released API.

## Local verification

```sh
python -m pip install '.[test,quality]'
ruff check src tests tools
ruff format --check src tests tools
mypy
python -m coverage run -m unittest discover -s tests -v
python -m coverage report
python -m coverage json
python tools/check_coverage.py coverage.json
python -m build
python -m twine check dist/*
```


## Complete integration-rule applicability review

All 54 Integration Quality Scale rules were considered. **Adapted** means the engineering requirement is implemented for this SDK; **Integration only** means the Home Assistant framework owns it. This is an applicability review, not an official tier claim. See the [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/).

| Rule | Applicability and evidence |
| --- | --- |
| `action-exceptions` | Adapted — Named authentication, connection, protocol, and OCPP call errors; API error contract. |
| `action-setup` | Integration only — Service/action registration is performed by the integration. |
| `appropriate-polling` | Integration only — The caller owns scheduling; this SDK only performs requested operations. |
| `async-dependency` | Adapted — All BLE I/O uses asynchronous Bleak and bleak-retry-connector. |
| `brands` | Integration only — The SDK has no frontend or brands registration. |
| `common-modules` | Adapted — Client/session logic, protocol parsing, and constants are separate modules. |
| `config-entry-unloading` | Adapted — Adapted to SDK lifecycle: notifications and connections close in finally; no background tasks. |
| `config-flow` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `config-flow-test-coverage` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `dependency-transparency` | Adapted — Apache-2.0 source, public dependencies, issue tracker, sdist, tags, and Trusted Publishing provenance. |
| `devices` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `diagnostics` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `discovery` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `discovery-update-info` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `docs-actions` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `docs-conditions` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `docs-configuration-parameters` | Adapted — API guide documents client arguments, transaction ownership, and wire-value semantics. |
| `docs-data-update` | Adapted — API guide describes request-driven sessions and no background polling. |
| `docs-examples` | Adapted — Existing README demonstrates a direct Bleak provider and a Home Assistant adapter. |
| `docs-high-level-description` | Adapted — README describes local EVBox Gen4 BLE communication and extraction origin. |
| `docs-installation-instructions` | Adapted — API guide and quality guide provide installation and verification commands. |
| `docs-installation-parameters` | Adapted — API guide documents charger address, Bluetooth security code, and device provider. |
| `docs-known-limitations` | Adapted — API guide separates acknowledgements from verified state, optional features, and firmware orchestration. |
| `docs-removal-instructions` | Adapted — API guide describes package removal and preserved charger settings. |
| `docs-supported-devices` | Adapted — API guide limits the supported family to Elvi Gen4 and requires verification for other hardware/firmware. |
| `docs-supported-functions` | Adapted — API guide lists all public client operations and protocol helper categories. |
| `docs-triggers` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `docs-troubleshooting` | Adapted — API guide covers unavailable devices, competing apps, rejected codes, optional keys, and defect reporting. |
| `docs-use-cases` | Adapted — README and API guide describe local configuration, snapshots, and serialized read/write verification. |
| `dynamic-devices` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `entity-category` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `entity-device-class` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `entity-disabled-by-default` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `entity-event-setup` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `entity-translations` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `entity-unavailable` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `entity-unique-id` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `exception-translations` | Integration only — The SDK supplies typed errors; the integration translates UI exceptions. |
| `has-entity-name` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `icon-translations` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `inject-websession` | Integration only — No HTTP client or web session is used. |
| `integration-owner` | Adapted — Adapted to SDK ownership: package author, repository owner, issue tracker, and CODEOWNERS are CReimer. |
| `log-when-unavailable` | Integration only — Availability transitions and rate-limited user logs belong to the coordinator. |
| `parallel-updates` | Adapted — Sessions and complete operations serialize through a reentrant, cancellation-safe task-owned transaction. |
| `reauthentication-flow` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `reconfiguration-flow` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `repair-issues` | Integration only — Home Assistant repairs belong to the integration; the SDK preserves charger restart responses. |
| `runtime-data` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `stale-devices` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
| `strict-typing` | Adapted — All library source passes strict mypy; py.typed is checked in the installed wheel. |
| `test-before-configure` | Adapted — Every command session authenticates before executing operations; callers validate their required configuration. |
| `test-before-setup` | Adapted — The application supplies the connectable device; sessions reject unavailable devices and failed authentication. |
| `test-coverage` | Adapted — Exactly 100 percent line and branch coverage, enforced by missing counts for wheel and rebuilt sdist on both Python versions. |
| `unique-config-entry` | Integration only — Home Assistant configuration, discovery, entities, devices, or UI lifecycle; no corresponding SDK component. |
