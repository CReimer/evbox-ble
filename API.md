# EVBox BLE API

## Installation and connection

Install the published package with `python -m pip install evbox-ble`. Python 3.11 or newer is required. The supported device family is EVBox Elvi Gen4 with the EVBox Bluetooth configuration service; other hardware and firmware need device-level verification.

Construct `EVBoxClient(address, security_code, *, ble_device_callback=provider)`. `address` is the charger address, `security_code` is its Bluetooth authentication code, and `provider` is a synchronous callable returning the latest connectable `bleak.backends.device.BLEDevice`, or `None` if unreachable. The library calls the provider for every new connection so an application can select the current adapter or proxy. Configure the charger and obtain its security code using its supplied information or EVBox Connect; close the vendor app before connecting.

All client operations are asynchronous. Each session authenticates, executes its operations, stops notifications, and disconnects in `finally`. There are no background polling tasks or persistent BLE connections. Calls use asynchronous Bleak connection retries, with at most three connection attempts. Optional command failures are explicitly distinguished from mandatory failures.

## Public client operations

| Method | Result and behavior |
| --- | --- |
| `get_configuration(keys)` | A dictionary of supported configuration values. Unsupported or malformed optional keys are omitted, so callers must check required keys. An empty key list returns an empty dictionary. |
| `get_snapshot(keys)` | `(configuration, diagnostics)`, collected in one authenticated session. Optional diagnostics may be `None` or an empty dictionary. |
| `set_configuration(key, value)` | The charger command response. Boolean values use lowercase wire strings. `RebootRequired` is preserved; the library does not reboot or claim a stored value was verified. |
| `set_server(url)` | Command results for the server URL followed by its two companion compatibility flags. A rejected command stops later writes. |
| `set_auto_start(value)` | The command response after checking the local authorization-list precondition. |
| `connection_info()` | Parsed connection information; an empty dictionary means the optional information was unavailable. |
| `set_wifi(values)` | The final Wi-Fi status if provided, otherwise the direct acknowledgement after the event timeout. A generic acknowledgement is not proof of connectivity. |
| `scan_satellites(timeout=40)` | Parsed satellite records from the asynchronous RF scan; the device scan duration is followed by the command timeout. |
| `evb(command, values=())` | A mandatory EVBox DataTransfer command response. |
| `ocpp(action, payload)` | A mandatory OCPP command response. |
| `session(operations)` | Results for `(kind, name, payload)` operations in one connection. Supported kinds are `evb`, `optional_evb`, `wifi_set`, `ocpp`, `optional_ocpp`, `auto_start`, `connection_info`, and `rf_scan`. |
| `transaction()` | An async context manager serializing a complete operation. The owning task may nest transactions and call session methods; competing tasks wait. Cancellation releases ownership. |

For an application-level read/check/write/read operation, wrap all calls in one `transaction()`. The library serializes its own callers; another phone or controller can still change charger settings externally. The application must validate permitted values and confirm stored configuration where required. Setting a value does not itself prove that the charger applied it, or that no restart is needed.

## Errors and cancellation

- `evbox_ble.EVBoxAuthError`: The charger explicitly rejected authentication. It subclasses `EVBoxConnectionError`, so catch it first when distinguishing credentials from transport failures.
- `evbox_ble.EVBoxConnectionError`: No connectable device or a failed BLE connection/session. Restore range or adapter availability before retrying.
- `evbox_ble.protocol.EVBoxProtocolError`: Malformed protocol data or a rejected mandatory command. Read the exception type rather than matching its human-readable message.
- `evbox_ble.protocol.EVBoxCallError`: An OCPP CALLERROR; its `code` and `description` preserve the remote error. It subclasses `EVBoxProtocolError`.
- `asyncio.CancelledError`: Cancellation propagates while session resources and transaction ownership are cleaned up. Applications can use `asyncio.timeout` for their own overall deadlines.

The library does not log security codes, Wi-Fi credentials, or raw command payloads. Applications should likewise exclude credentials from diagnostic output. Device responses may contain identifiers and network details; the integration controls redaction and UI presentation.

## Protocol helpers

`evbox_ble.protocol` provides UTF-8 length-prefixed framing (`frame_message`, `chunks`, `FrameDecoder`), OCPP builders and parsers, DataTransfer events, configuration-value extraction, deciampere conversions, and parsers for phase rotation, AutoStart, meters, CCID, Wi-Fi, satellites, cards, connection information, boot information, and LED schedules. These helpers parse protocol values and do not enforce application-specific electrical limits.

Frame errors and malformed mandatory response envelopes raise `EVBoxProtocolError`. Optional configuration values use `None`, empty collections, or omitted keys rather than invented measurements. Read the method's type signature and docstring for its particular result shape. The package includes `py.typed` and all library source passes strict mypy.

Firmware payload construction is included, but firmware download/FTP orchestration remains outside this library. Tests simulate Bluetooth peers; they do not replace physical-device testing for a new model or firmware.

## Troubleshooting and removal

If no device is found, verify the charger address, power, range, and a connectable adapter or proxy. Close EVBox Connect to avoid competing connections. For rejected authentication, obtain the current Bluetooth security code. Missing optional keys indicate firmware capabilities and must not be treated as zero or false configuration values. After transport recovery, start a new operation; the provider will resolve the device again.

Report reproducible defects in the [issue tracker](https://github.com/CReimer/evbox-ble/issues), with package version, Python version, model/firmware, and a credential-free description. To remove the package, uninstall it with `python -m pip uninstall evbox-ble`; this does not reset charger settings. Uninstalling a dependency managed by Home Assistant should instead be handled through the integration's lifecycle.
