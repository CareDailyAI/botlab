import bot
from devices.motion.motion import MotionDevice
from locations.location import Location

from botengine_pytest import BotEnginePyTest


class TestDevice:
    def test_device_motion_init(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 0
        device_desc = "Test"

        mut = MotionDevice(botengine, location_object, device_id, device_type, device_desc)
        assert mut is not None

    def test_device_motion_run_measurements(self):
        """
        This test initializes a new bot instance with a trigger type of 8 (measurements).
        :return:
        """
        botengine = BotEnginePyTest(
            {
                "time": 1687170210000,
                "trigger": 8,
                "source": 8,
                "locationId": 1,
                "triggerIds": ["__motion__"],
                "access": [
                    {
                        "category": 1,
                        "trigger": False,
                        "read": True,
                        "control": True,
                        "location": {
                            "locationId": 1,
                            "name": "Destry Teeter's Home",
                            "event": "HOME.:.PRESENT.AI",
                            "timezone": {
                                "id": "America/Los_Angeles",
                                "offset": -480,
                                "dst": True,
                                "name": "Pacific Standard Time",
                            },
                            "zip": "83501",
                            "latitude": "46.39950",
                            "longitude": "-117.02710",
                            "language": "en",
                            "priorityCategory": 4,
                            "priorityRank": 73,
                            "priorityDateMs": 1687363210000,
                            "organizationId": 202,
                            "organization": {
                                "organizationId": 202,
                                "organizationName": "PPCg Dev",
                                "domainName": "ppcgdev",
                                "brand": "familycare",
                                "parentId": 104,
                                "features": "b,g,m,n,p",
                            },
                        },
                    },
                    {
                        "category": 4,
                        "trigger": True,
                        "read": True,
                        "control": True,
                        "device": {
                            "deviceId": "__motion__",
                            "deviceType": 10038,
                            "description": "Motion Sensor",
                            "locationId": 1,
                            "startDate": 1654623396000,
                            "connected": True,
                        },
                    },
                ],
                "measures": [
                    {
                        "deviceId": "__motion__",
                        "name": "motionStatus",
                        "value": "1",
                        "time": 1687170200000,
                        "updated": True,
                    },
                    {
                        "deviceId": "__motion__",
                        "name": "motionStatus",
                        "value": "0",
                        "time": 1687170209000,
                        "updated": True,
                    }
                ],
            }
        )

        # botengine.logging_service_names = ["motion"]

        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1

        location_object = controller.locations[1]
        device_object = location_object.devices.get("__motion__")
        assert device_object is not None

        assert device_object.measurements["motionStatus"] == [(0, 1687170209000), (1, 1687170200000)]