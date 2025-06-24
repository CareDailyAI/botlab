import unittest

from devices.gateway.gateway import GatewayDevice
from intelligence.dailyreport.location_dailyreport_microservice import (
    DAILY_REPORT_ADDRESS,
    REASON_ML,
)
from locations.location import Location

from botengine_pytest import BotEnginePyTest
import pytest


class TestDailyReportOccupancyMicroservice(unittest.TestCase):
    def test_dailyreport_occupancy_status_updated_sleep_beforenoon(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684076795000)

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)

        gateway_device = GatewayDevice(
            botengine, location_object, "A", 10031, "Test Gateway"
        )
        gateway_device.is_connected = True
        location_object.born_on = botengine.get_timestamp()
        gateway_device.measurements["rssi"] = [[-67, botengine.get_timestamp()]]

        location_object.devices[gateway_device.device_id] = gateway_device

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]
        try:
            import signals.occupancy as occupancy
        except ImportError:
            # If the import fails, we assume the occupancy module is not available.
            pytest.skip("signals.occupancy module not available, skipping test.")

        occupancy.update_occupancy_status(
            botengine, location_object, "HOME.:.SLEEP", REASON_ML, "", ""
        )
        assert mut.started_sleeping_ms == botengine.get_timestamp()

        report = botengine.get_state(
            DAILY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        assert report is not None
        assert report == {
            "created_ms": 1684047600000,
            "period": "dailyreport",
            "sections": [
                {
                    "color": "00AD9D",
                    "icon": "clipboard-list-check",
                    "description": "List of to-do items scheduled for today.",
                    "id": "tasks",
                    "items": [
                        {
                            "comment": "8:06 AM - A task was added: Add People to your Trusted Circle.",
                            "comment_raw": "A task was added: Add People to your Trusted Circle.",
                            "timestamp_ms": 1684076795000,
                            "timestamp_str": "8:06 AM",
                        }
                    ],
                    "subtitle": "Updated one task today.",
                    "title": "Today's Tasks",
                    "weight": 10,
                },
                {
                    "color": "946C49",
                    "icon": "moon",
                    "description": "Sleep quality and other insightful information.",
                    "id": "sleep",
                    "items": [
                        {
                            "comment": "8:06 AM Sunday - Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                            "comment_raw": "Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                            "timestamp_ms": 1684076795000,
                            "timestamp_str": "8:06 AM Sunday",
                        },
                    ],
                    "title": "Sleep",
                    "weight": 15,
                },
            ],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT",
        }

    def test_dailyreport_occupancy_status_updated_sleep_afternoon(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684109195000)

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)

        gateway_device = GatewayDevice(
            botengine, location_object, "A", 10031, "Test Gateway"
        )
        gateway_device.is_connected = True
        location_object.born_on = botengine.get_timestamp()
        gateway_device.measurements["rssi"] = [[-67, botengine.get_timestamp()]]

        location_object.devices[gateway_device.device_id] = gateway_device

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]
        try:
            import signals.occupancy as occupancy
        except ImportError:
            # If the import fails, we assume the occupancy module is not available.
            pytest.skip("signals.occupancy module not available, skipping test.")

        occupancy.update_occupancy_status(
            botengine, location_object, "HOME.:.SLEEP", REASON_ML, "", ""
        )
        assert mut.started_sleeping_ms == botengine.get_timestamp()
        assert mut.last_emailed_report_ms == mut.current_report_ms

        report = botengine.get_state(
            DAILY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        assert report is not None
        assert report == {
            "created_ms": 1684047600000,
            "period": "dailyreport",
            "sections": [
                {
                    "color": "00AD9D",
                    "description": "List of to-do items scheduled for today.",
                    "icon": "clipboard-list-check",
                    "id": "tasks",
                    "items": [
                        {
                            "comment": "5:06 PM - A task was added: Add People to your Trusted Circle.",
                            "comment_raw": "A task was added: Add People to your Trusted Circle.",
                            "timestamp_ms": 1684109195000,
                            "timestamp_str": "5:06 PM",
                        }
                    ],
                    "subtitle": "Updated one task today.",
                    "title": "Today's Tasks",
                    "weight": 10,
                },
                {
                    "color": "946C49",
                    "description": "Sleep quality and other insightful information.",
                    "icon": "moon",
                    "id": "sleep",
                    "items": [
                        {
                            "comment": "5:06 PM Sunday - Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                            "comment_raw": "Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                            "timestamp_ms": 1684109195000,
                            "timestamp_str": "5:06 PM Sunday",
                        },
                    ],
                    "title": "Sleep",
                    "weight": 15,
                },
            ],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT",
        }

    def test_dailyreport_occupancy_status_updated_sleep_to_home(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684076795000)

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)

        gateway_device = GatewayDevice(
            botengine, location_object, "A", 10031, "Test Gateway"
        )
        gateway_device.is_connected = True
        location_object.born_on = botengine.get_timestamp()
        gateway_device.measurements["rssi"] = [[-67, botengine.get_timestamp()]]

        location_object.devices[gateway_device.device_id] = gateway_device

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]
        try:
            import signals.occupancy as occupancy
        except ImportError:
            # If the import fails, we assume the occupancy module is not available.
            pytest.skip("signals.occupancy module not available, skipping test.")

        occupancy.update_occupancy_status(
            botengine, location_object, "HOME.:.SLEEP", REASON_ML, "", ""
        )
        assert mut.started_sleeping_ms == botengine.get_timestamp()

        occupancy.update_occupancy_status(
            botengine, location_object, "HOME.:.PRESENT", REASON_ML, "", ""
        )
        assert mut.started_sleeping_ms is None

        report = botengine.get_state(
            DAILY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        assert report is not None
        assert report == {
            "created_ms": 1684047600000,
            "period": "dailyreport",
            "sections": [
                {
                    "color": "00AD9D",
                    "description": "List of to-do items scheduled for today.",
                    "icon": "clipboard-list-check",
                    "id": "tasks",
                    "items": [
                        {
                            "comment": "8:06 AM - A task was added: Add People to your Trusted Circle.",
                            "comment_raw": "A task was added: Add People to your Trusted Circle.",
                            "timestamp_ms": 1684076795000,
                            "timestamp_str": "8:06 AM",
                        }
                    ],
                    "subtitle": "Updated one task today.",
                    "title": "Today's Tasks",
                    "weight": 10,
                },
                {
                    "color": "946C49",
                    "description": "Sleep quality and other insightful information.",
                    "icon": "moon",
                    "id": "sleep",
                    "items": [
                        {
                            "comment": "8:06 AM Sunday - Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                            "comment_raw": "Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                            "timestamp_ms": 1684076795000,
                            "timestamp_str": "8:06 AM Sunday",
                        }
                    ],
                    "title": "Sleep",
                    "weight": 15,
                },
            ],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT",
        }
