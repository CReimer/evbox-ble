# Changelog

## 0.1.1

- Clean up both request and event futures after errors and cancellation to prevent unhandled asynchronous exceptions.
- Remove an unreachable response-router fallback; valid unsolicited charger events still follow the dedicated event path.
- Complete strict type checking for the public library and bind legacy scan-parser values explicitly.
- Cover late and duplicate notifications, malformed replies, nested and competing transactions, cancellation, connection-information events, wire-value conversion, and legacy parsing boundaries.
- Enforce 100% line and branch coverage, strict mypy, Ruff linting and formatting, wheel tests, and source-distribution rebuild tests in CI.

## 0.1.0

- Extract the standalone asynchronous EVBox Gen4 BLE client and framing protocol from the HACS integration.
- Publish source and wheel distributions using PyPI Trusted Publishing and provenance attestations.
