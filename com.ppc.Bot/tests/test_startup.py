import unittest

from startup import StartUpUtil

from botengine_pytest import BotEnginePyTest


class TestStartUpUtil(unittest.TestCase):
    def test_startup(self):
        botengine = BotEnginePyTest(
            {
                "time": 1687374406646,
                "trigger": 8,
                "source": 8,
                "locationId": 123,
                "triggerIds": ["ABC", "DEF"],
                "access": [
                    {
                        "category": 4,
                        "trigger": True,
                        "read": True,
                        "control": True,
                        "device": {
                            "deviceId": "ABC",
                            "deviceType": 10014,
                            "locationId": 123,
                            "startDate": 1687068846000,
                            "connected": True,
                        },
                    },
                    {
                        "category": 4,
                        "trigger": True,
                        "read": True,
                        "control": True,
                        "device": {
                            "deviceId": "DEF",
                            "deviceType": 10014,
                            "locationId": 123,
                            "startDate": 1687068846000,
                            "connected": True,
                        },
                    },
                ],
                "measures": [
                    {
                        "deviceId": "ABC",
                        "name": "doorStatus",
                        "value": "0",
                        "time": 1687379792328,
                        "updated": True,
                    },
                    {
                        "deviceId": "DEF",
                        "name": "doorStatus",
                        "value": "0",
                        "time": 1687379792328,
                        "updated": True,
                    },
                ],
            }
        )

        mut = StartUpUtil()
        assert mut is not None
        assert mut.event_queue == []
        assert not mut.is_preparing
        assert mut.start_timestamps == 0
        assert mut.data_request_data is None

        mut.queue_triggers(botengine.get_triggers())
        assert mut.event_queue == [botengine.get_triggers()]
        mut.set_is_preparing(True)
        assert mut.is_preparing
        mut.set_start_time(botengine)
        assert mut.start_timestamps == botengine.get_timestamp()
