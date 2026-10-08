# EVBox BLE

Library extraction for Home Assistant Core consideration. Releases are [published on PyPI](https://pypi.org/project/evbox-ble/). The released HACS integration does not yet use this package. Source and CI are maintained at [CReimer/evbox-ble](https://github.com/CReimer/evbox-ble); report library defects in its issue tracker.

Asynchronous local BLE sessions for EVBox Gen4 chargers, including authentication, configuration and the legacy EVBox/OCPP framing protocol. The protocol and client originate in the Apache-2.0 project [CReimer/evbox-g4-ble](https://github.com/CReimer/evbox-g4-ble), revision `5fbeec3dddbc107deac87a46f12b670b4ca3f264`. No vendor applications or firmware are included.

Supply a synchronous device provider so the latest connectable adapter or Bluetooth proxy can be selected for each new session. The library has no dependency on Home Assistant. For a direct Bleak application:

```python
from bleak import BleakScanner
from evbox_ble import EVBoxClient

device = await BleakScanner.find_device_by_address(address)
client = EVBoxClient(address, security_code, ble_device_callback=lambda: device)
config = await client.get_configuration(["evb_BootInfo"])
```

For Home Assistant, the integration adapter supplies `lambda: bluetooth.async_ble_device_from_address(hass, address, connectable=True)`. A missing device raises `EVBoxConnectionError`; rejected authentication raises `EVBoxAuthError`.

Transactions serialize complete operations. A snapshot reuses one authenticated BLE session. Legacy and ESP32 characteristic layouts are supported. Optional unavailable commands are distinguished from required command failures.

The 75 tests use simulated BLE notifications and malformed protocol inputs without hardware. CI requires 100% line and branch coverage, strict type checking, linting, formatting, and isolated tests of the wheel and a wheel rebuilt from the source distribution. See [quality requirements](QUALITY.md) and the [changelog](CHANGELOG.md). Run `python -m unittest discover -s tests`; build source and wheel artifacts with `python -m build`. The public GitHub Actions workflow tests Python 3.11 and 3.14, builds both source and wheel distributions, and publishes version tags using PyPI Trusted Publishing. [PyPI provenance](https://pypi.org/integrity/evbox-ble/0.1.0/evbox_ble-0.1.0-py3-none-any.whl/provenance) identifies the repository, workflow and publishing environment. Initial library extraction does not include the Home Assistant firmware/FTP orchestration; any later Core firmware platform must move device communication into the library as well.
