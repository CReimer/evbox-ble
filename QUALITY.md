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
