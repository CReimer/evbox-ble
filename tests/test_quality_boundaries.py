"""Regression tests for cancellation, late notifications and legacy edge cases."""

import asyncio
import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from evbox_ble import client as c
from evbox_ble import protocol as p


class NotificationTests(unittest.IsolatedAsyncioTestCase):
    async def test_unsolicited_and_duplicate_events_do_not_replace_results(
        self,
    ) -> None:
        router = c._ResponseRouter()
        future = router.expect_marker("scan")
        for marker, value in [
            ("unsolicited", "ignored"),
            ("scan", "first"),
            ("scan", "late"),
        ]:
            raw = json.dumps(
                [2, "event", "DataTransfer", {"messageId": marker, "data": value}]
            )
            router.notification(None, bytearray(p.frame_message(raw)))
        self.assertEqual(await future, "first")
        self.assertEqual(router.take_event_message_id("unsolicited"), "event")

    async def test_protocol_failure_preserves_completed_futures(self) -> None:
        router = c._ResponseRouter()
        completed = asyncio.get_running_loop().create_future()
        completed.set_result("previous reply")
        waiting = asyncio.get_running_loop().create_future()
        router._pending.update(completed=completed, waiting=waiting)
        marker_done = router.expect_marker("completed")
        marker_done.set_result("previous event")
        marker_waiting = router.expect_marker("waiting")
        router.notification(None, bytearray(p.frame_message('[2,"x","Unknown",{}]')))
        for future in (waiting, marker_waiting):
            with self.assertRaisesRegex(p.EVBoxProtocolError, "Unexpected OCPP"):
                await future
        self.assertEqual(await completed, "previous reply")
        self.assertEqual(await marker_done, "previous event")

    async def test_marked_callresult_completes_request_and_marker(self) -> None:
        router = c._ResponseRouter()
        pending = asyncio.get_running_loop().create_future()
        router._pending["request"] = pending
        marker = router.expect_marker("wifi")
        router.notification(
            None, bytearray(p.frame_message('[3,"request",{"data":"wifi"}]'))
        )
        self.assertEqual(await pending, "wifi")
        self.assertEqual(await marker, "wifi")

    async def test_request_failure_retrieves_both_future_exceptions(self) -> None:
        router = c._ResponseRouter()
        loop = asyncio.get_running_loop()
        previous = loop.get_exception_handler()
        unhandled = []
        loop.set_exception_handler(lambda _loop, context: unhandled.append(context))

        async def malformed_reply(*args, **kwargs) -> None:
            router.notification(None, bytearray(p.frame_message("[invalid]")))

        try:
            with self.assertRaises(p.EVBoxProtocolError):
                await router.request(
                    SimpleNamespace(write_gatt_char=malformed_reply),
                    "r",
                    "request",
                    "uuid",
                    100,
                    "wifi",
                )
            await asyncio.sleep(0)
        finally:
            loop.set_exception_handler(previous)
        self.assertEqual(unhandled, [])
        self.assertEqual(router._pending, {})
        self.assertEqual(router._markers, {})

    async def test_cancelled_request_releases_pending_work(self) -> None:
        router = c._ResponseRouter()
        writing = asyncio.Event()
        captured = []

        async def blocked_write(*args, **kwargs) -> None:
            captured.extend([router._pending["r"], router._markers["wifi"]])
            writing.set()
            await asyncio.Event().wait()

        task = asyncio.create_task(
            router.request(
                SimpleNamespace(write_gatt_char=blocked_write),
                "r",
                "request",
                "uuid",
                100,
                "wifi",
            )
        )
        await writing.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertTrue(all(future.cancelled() for future in captured))
        self.assertEqual(router._pending, {})
        self.assertEqual(router._markers, {})


class TransactionTests(unittest.IsolatedAsyncioTestCase):
    async def test_nested_transaction_serializes_tasks_and_recovers_from_cancellation(
        self,
    ) -> None:
        client = c.EVBoxClient("AA", "secret", ble_device_callback=lambda: None)
        started = asyncio.Event()
        entered = asyncio.Event()

        async def contender() -> None:
            started.set()
            async with client.transaction():
                entered.set()
                await asyncio.Event().wait()

        async with client.transaction():
            async with client.transaction():
                task = asyncio.create_task(contender())
                await started.wait()
                self.assertFalse(entered.is_set())
        await asyncio.wait_for(entered.wait(), 1)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        async with client.transaction():
            self.assertIs(client._transaction_owner, asyncio.current_task())
        self.assertIsNone(client._transaction_owner)

    async def test_connection_information_event_is_acknowledged(self) -> None:
        client = c.EVBoxClient("AA", "secret", ble_device_callback=lambda: None)
        ble = SimpleNamespace(
            services=SimpleNamespace(get_characteristic=lambda _uuid: None),
            start_notify=AsyncMock(),
            stop_notify=AsyncMock(),
            disconnect=AsyncMock(),
            is_connected=True,
        )
        client._connect = AsyncMock(return_value=ble)
        client._authenticate = AsyncMock()
        client._acknowledge_event = AsyncMock()

        async def trigger(_ble, router, *args) -> dict:
            raw = json.dumps(
                [
                    2,
                    "event",
                    "DataTransfer",
                    {
                        "messageId": "evbConnectionInfo",
                        "data": "WiFi,{1,1,1,-54,12},{1,1,1,1,-71,8}",
                    },
                ]
            )
            router.notification(None, bytearray(p.frame_message(raw)))
            return {"status": "Accepted"}

        client._ocpp = AsyncMock(side_effect=trigger)
        result = await client.connection_info()
        self.assertTrue(result["wifi"]["still_online"])
        self.assertEqual(result["wifi"]["signal_strength"], -54)
        client._acknowledge_event.assert_awaited_once()
        ble.stop_notify.assert_awaited_once()
        ble.disconnect.assert_awaited_once()

    async def test_set_configuration_preserves_wire_types(self) -> None:
        client = c.EVBoxClient("AA", "secret", ble_device_callback=lambda: None)
        client.session = AsyncMock(return_value=[{"status": "Accepted"}])
        for value, wire in [(True, "true"), (False, "false"), (200, "200")]:
            with self.subTest(value=value):
                self.assertEqual(
                    await client.set_configuration("key", value), {"status": "Accepted"}
                )
                client.session.assert_awaited_with(
                    [("ocpp", "ChangeConfiguration", {"key": "key", "value": wire})]
                )


class LegacyProtocolTests(unittest.TestCase):
    def test_missing_and_legacy_connector_values(self) -> None:
        for value in (None, "invalid"):
            self.assertIsNone(p.current_to_amperes(value))
        self.assertEqual(p.auto_start_configuration("card-id")["card_id"], "card-id")
        self.assertEqual(p.auto_start_value("card-id", "rfid"), "")
        self.assertEqual(p.split_evb_csv(None), [])
        self.assertIsNone(p.connector_value("2.other", "1"))
        self.assertEqual(
            p.ccid_ac_configuration(None), {"connector_id": 1, "status": "disabled"}
        )
        for value in (None, ""):
            self.assertEqual(p.rf_modules(value), [])
            self.assertEqual(p.card_list(value), [])
        self.assertEqual(
            p.rf_modules("ChargeBox.1"), [{"type": "ChargeBox", "id": "1"}]
        )
        self.assertEqual(
            p.satellite_scan_results("{ChargeBox,1}"),
            [{"type": "ChargeBox", "id": "1"}],
        )

    def test_unknown_ocpp_message_type_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            p.EVBoxProtocolError, "Unexpected OCPP message type 2"
        ):
            p.parse_response('[2,"id",{}]')

    def test_unknown_connection_type_uses_wifi_fallback(self) -> None:
        self.assertTrue(
            p.valid_internet_connection({"current_connection": "unknown"}, "7,Home")
        )

    def test_legacy_scan_with_invalid_numbers_and_plain_authentication(self) -> None:
        self.assertEqual(
            p.wifi_scan_networks("{Guest,MAC,bad,,bad,WPA2,CCMP,CCMP}"),
            [{"ssid": "Guest", "mac_address": "MAC", "authentication": ["WPA2"]}],
        )

    def test_json_network_scan_is_normalized(self) -> None:
        raw = json.dumps({"networks": [{"ssid": "Home", "signal_strength": -60}]})
        self.assertEqual(
            p.wifi_scan_networks(raw), [{"ssid": "Home", "signal_strength": -60}]
        )
