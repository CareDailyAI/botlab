import unittest

import bot
import domain
import properties
import pytest
from localization import get_translations

from botengine_pytest import BotEnginePyTest


class TestBot(unittest.TestCase):
    """ """

    def test_bot_run_init(self):
        """
        This test is to ensure that the botengine is initialized correctly with the correct location
        :return:
        """
        botengine = BotEnginePyTest(
            {
                "time": 1687373406646,
                "trigger": 0,
                "source": 0,
                "locationId": 1546987,
                "access": [
                    {
                        "category": 1,
                        "trigger": False,
                        "read": True,
                        "control": True,
                        "location": {
                            "locationId": 1546987,
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
                    }
                ],
            }
        )

        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1

    def test_bot_run_datastream(self):
        """
        This test initializes a new bot instance with a trigger type of 256 (datastream) to remove
        a default system task `__people__` and ensures it is destroyed.
        :return:
        """
        botengine = BotEnginePyTest(
            {
                "time": 1687373406646,
                "trigger": BotEnginePyTest.TRIGGER_DATA_STREAM,
                "source": 0,
                "locationId": 1546987,
                "access": [
                    {
                        "category": 1,
                        "trigger": False,
                        "read": True,
                        "control": True,
                        "location": {
                            "locationId": 1546987,
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
                    }
                ],
                "dataStream": {
                    "feed": {"id": "__people__", "deleted_by": 1203763},
                    "address": "delete_task",
                },
            }
        )

        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1

    def test_bot_run_measurements(self):
        """
        This test initializes a new bot instance with a trigger type of 8 (measurements).
        :return:
        """
        botengine = BotEnginePyTest(
            {
                "time": 1687170210000,
                "trigger": 8,
                "source": 8,
                "locationId": 1546987,
                "triggerIds": ["hk1546987:1250574"],
                "access": [
                    {
                        "category": 1,
                        "trigger": False,
                        "read": True,
                        "control": True,
                        "location": {
                            "locationId": 1546987,
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
                        "trigger": False,
                        "read": False,
                        "control": False,
                        "device": {
                            "deviceId": "20BE44FB-D893-41A0-A5EC-FCD7B75663FC:1546987",
                            "deviceType": 28,
                            "modelId": "appleWatch",
                            "description": "Apple Watch",
                            "remoteAddrHash": "a4f753fffc70eaa761c39a0c6751b2f5206139326ff4545995a26556091a1ec7",
                            "locationId": 1546987,
                            "startDate": 1687068846000,
                            "connected": False,
                        },
                    },
                    {
                        "category": 4,
                        "trigger": True,
                        "read": True,
                        "control": True,
                        "device": {
                            "deviceId": "hk1546987:1250574",
                            "deviceType": 29,
                            "proxyId": "16A104A4-A6A4-481C-B4CC-FB23A806676E:1546987",
                            "description": "My Health",
                            "locationId": 1546987,
                            "startDate": 1654623396000,
                            "connected": True,
                        },
                    },
                ],
                "measures": [
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "age",
                        "value": "38",
                        "time": 1687379792328,
                        "updated": False,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "bloodType",
                        "value": "5",
                        "time": 1687379792328,
                        "updated": False,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "model",
                        "value": "iPhone14,2",
                        "time": 1687379792328,
                        "updated": False,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "sex",
                        "value": "2",
                        "time": 1687379792328,
                        "updated": False,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "sleepAnalysis",
                        "index": "1",
                        "value": "0",
                        "time": 1681651401051,
                        "updated": False,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "sleepAnalysis",
                        "index": "4",
                        "value": "0",
                        "time": 1686735452840,
                        "updated": False,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "sleepAnalysis",
                        "index": "5",
                        "value": "0",
                        "time": 1686747182840,
                        "updated": False,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "version",
                        "value": "16.3.1",
                        "time": 1687379792328,
                        "updated": False,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "steps",
                        "value": "44",
                        "time": 1686920869089,
                        "updated": True,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "steps",
                        "value": "6",
                        "time": 1686920871954,
                        "updated": True,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "steps",
                        "value": "10",
                        "time": 1686920948704,
                        "updated": True,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "hr",
                        "value": "70",
                        "time": 1687170210000,
                        "updated": True,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "hr",
                        "value": "75",
                        "time": 1687170220000,
                        "updated": True,
                    },
                    {
                        "deviceId": "hk1546987:1250574",
                        "name": "hr",
                        "value": "74",
                        "time": 1687181320000,
                        "updated": True,
                    },
                ],
            }
        )

        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1

    def test_bot_run_alerts(self):
        """
        This test initializes a new bot instance with a trigger type of 4 (alerts).
        :return:
        """

        # Test connectionStatus changes True,2 > False,2 > True,1
        botengine = BotEnginePyTest(
            {
                "access": [
                    {
                        "category": 1,
                        "control": True,
                        "location": {
                            "language": "en",
                            "latitude": "46.39948",
                            "locationId": 288029,
                            "longitude": "-117.02719",
                            "name": "Destry's Test Bench",
                            "organization": {
                                "deviceTypes": "39, 9138",
                                "domainName": "jeremi",
                                "features": "g,n,p",
                                "organizationId": 20959,
                                "organizationName": "Jeremi",
                                "parentId": 20958,
                            },
                            "organizationId": 20959,
                            "priorityCategory": 6,
                            "priorityDateMs": 1739919230000,
                            "priorityRank": 79,
                            "timezone": {
                                "dst": True,
                                "id": "US/Pacific",
                                "name": "Pacific Standard Time",
                                "offset": -480,
                            },
                            "zip": "83501",
                        },
                        "read": True,
                        "trigger": False,
                    },
                    {
                        "category": 4,
                        "control": True,
                        "device": {
                            "connected": True,
                            "connectionStatus": 1,
                            "description": "Smart Home Center",
                            "deviceId": "0200000140006A58",
                            "deviceType": 39,
                            "latitude": "40.7607",
                            "locationId": 288029,
                            "longitude": "-111.891",
                            "modelId": "devGateway",
                            "newDevice": True,
                            "remoteAddrHash": "c012404323acbc425eefdcca877b6e403f4fc230ab3407f53c97c26607d6cadc",
                            "startDate": 1736464059000,
                        },
                        "read": True,
                        "trigger": False,
                    },
                    {
                        "category": 4,
                        "control": True,
                        "device": {
                            "connected": True,
                            "connectionStatus": 2,
                            "description": "Motion Sensor 1",
                            "deviceId": "0015BC001A018A89",
                            "deviceType": 9138,
                            "goalId": 50,
                            "locationId": 288029,
                            "modelId": "devMotionSensor",
                            "newDevice": True,
                            "proxyId": "0200000140006A58",
                            "startDate": 1737033754000,
                        },
                        "read": True,
                        "trigger": True,
                    },
                ],
                "locationId": 288029,
                "source": 8,
                "time": 1739926913767,
                "trigger": 4,
                "triggerIds": ["0015BC001A018A89"],
            }
        )

        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1
        assert len(controller.location_devices) == 2
        assert len(controller.locations[288029].devices) == 2
        assert not controller.locations[288029].devices["0015BC001A018A89"].is_connected

        botengine.inputs = {
            "access": [
                {
                    "category": 1,
                    "control": True,
                    "location": {
                        "language": "en",
                        "latitude": "46.39948",
                        "locationId": 288029,
                        "longitude": "-117.02719",
                        "name": "Destry's Test Bench",
                        "organization": {
                            "deviceTypes": "39, 9138",
                            "domainName": "jeremi",
                            "features": "g,n,p",
                            "organizationId": 20959,
                            "organizationName": "Jeremi",
                            "parentId": 20958,
                        },
                        "organizationId": 20959,
                        "priorityCategory": 6,
                        "priorityDateMs": 1739919230000,
                        "priorityRank": 79,
                        "timezone": {
                            "dst": True,
                            "id": "US/Pacific",
                            "name": "Pacific Standard Time",
                            "offset": -480,
                        },
                        "zip": "83501",
                    },
                    "read": True,
                    "trigger": False,
                },
                {
                    "category": 4,
                    "control": True,
                    "device": {
                        "connected": True,
                        "connectionStatus": 1,
                        "description": "Smart Home Center",
                        "deviceId": "0200000140006A58",
                        "deviceType": 39,
                        "latitude": "40.7607",
                        "locationId": 288029,
                        "longitude": "-111.891",
                        "modelId": "devGateway",
                        "newDevice": True,
                        "remoteAddrHash": "c012404323acbc425eefdcca877b6e403f4fc230ab3407f53c97c26607d6cadc",
                        "startDate": 1736464059000,
                    },
                    "read": True,
                    "trigger": False,
                },
                {
                    "category": 4,
                    "control": True,
                    "device": {
                        "connected": False,
                        "connectionStatus": 2,
                        "description": "Motion Sensor 1",
                        "deviceId": "0015BC001A018A89",
                        "deviceType": 9138,
                        "goalId": 50,
                        "locationId": 288029,
                        "modelId": "devMotionSensor",
                        "newDevice": True,
                        "proxyId": "0200000140006A58",
                        "startDate": 1737033754000,
                    },
                    "read": True,
                    "trigger": True,
                },
            ],
            "locationId": 288029,
            "source": 8,
            "time": 1739926913767 + 120000,
            "trigger": 4,
            "triggerIds": ["0015BC001A018A89"],
        }

        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1
        assert not controller.locations[288029].devices["0015BC001A018A89"].is_connected

        botengine.inputs = {
            "access": [
                {
                    "category": 1,
                    "control": True,
                    "location": {
                        "language": "en",
                        "latitude": "46.39948",
                        "locationId": 288029,
                        "longitude": "-117.02719",
                        "name": "Destry's Test Bench",
                        "organization": {
                            "deviceTypes": "39, 9138",
                            "domainName": "jeremi",
                            "features": "g,n,p",
                            "organizationId": 20959,
                            "organizationName": "Jeremi",
                            "parentId": 20958,
                        },
                        "organizationId": 20959,
                        "priorityCategory": 6,
                        "priorityDateMs": 1739919230000,
                        "priorityRank": 79,
                        "timezone": {
                            "dst": True,
                            "id": "US/Pacific",
                            "name": "Pacific Standard Time",
                            "offset": -480,
                        },
                        "zip": "83501",
                    },
                    "read": True,
                    "trigger": False,
                },
                {
                    "category": 4,
                    "control": True,
                    "device": {
                        "connected": True,
                        "connectionStatus": 1,
                        "description": "Smart Home Center",
                        "deviceId": "0200000140006A58",
                        "deviceType": 39,
                        "latitude": "40.7607",
                        "locationId": 288029,
                        "longitude": "-111.891",
                        "modelId": "devGateway",
                        "newDevice": True,
                        "remoteAddrHash": "c012404323acbc425eefdcca877b6e403f4fc230ab3407f53c97c26607d6cadc",
                        "startDate": 1736464059000,
                    },
                    "read": True,
                    "trigger": False,
                },
                {
                    "category": 4,
                    "control": True,
                    "device": {
                        "connected": True,
                        "connectionStatus": 1,
                        "description": "Motion Sensor 1",
                        "deviceId": "0015BC001A018A89",
                        "deviceType": 9138,
                        "goalId": 50,
                        "locationId": 288029,
                        "modelId": "devMotionSensor",
                        "newDevice": True,
                        "proxyId": "0200000140006A58",
                        "startDate": 1737033754000,
                    },
                    "read": True,
                    "trigger": True,
                },
            ],
            "locationId": 288029,
            "source": 8,
            "time": 1739926913767 + 180000,
            "trigger": 4,
            "triggerIds": ["0015BC001A018A89"],
        }

        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1
        assert controller.locations[288029].devices["0015BC001A018A89"].is_connected

    def test_bot_run_messages(self):
        """
        This test initializes a new bot instance with a trigger type of 4096 (datastream) to remove
        a default system task `__people__` and ensures it is destroyed.
        :return:
        """
        botengine = BotEnginePyTest(
            {
                "time": 1446537883000,
                "trigger": 4096,
                "source": 5,
                "locationId": 123,
                "messages": [
                    {
                        "messageId": 123,
                        "scheduleType": 0,
                        "status": 1,
                        "topicId": "general",
                        "appInstanceId": 456,
                        "contentKey": "Short content description",
                        "creationTime": 1646537712000,
                        "maxDeliveryTime": 1666537712000,
                        "deliveryDayTime": 36000,
                        "timeToLive": 3600,
                    },
                    {
                        "messageId": 124,
                        "scheduleType": 0,
                        "status": 2,
                        "topicId": "general",
                        "appInstanceId": 456,
                        "contentKey": "Short content description",
                        "creationTime": 1646537712000,
                        "maxDeliveryTime": 1666537712000,
                        "deliveryDayTime": 36000,
                        "timeToLive": 3600,
                        "deliveryTime": 1666037712000,
                    },
                    {
                        "messageId": 125,
                        "scheduleType": 1,
                        "status": 1,
                        "topicId": "general",
                        "appInstanceId": 457,
                        "contentKey": "Short content description",
                        "creationTime": 1646537712000,
                        "maxDeliveryTime": 1666537712000,
                        "timeToLive": 3600,
                        "schedule": "0 0 10 ? * SUN",
                    },
                    {
                        "messageId": 126,
                        "originalMessageId": 123,
                        "scheduleType": 0,
                        "status": 3,
                        "topicId": "general",
                        "userId": 789,
                        "contentText": "Reply from a user",
                        "lang": "en",
                        "creationTime": 1646537712000,
                    },
                ],
            }
        )

        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1

    def test_bot_run_concurrent_executions(self):
        """
        This test initializes a new bot instance and then follows up with a trigger type of 8 (measurements).
        :return:
        """
        botengine = BotEnginePyTest(
            {
                "time": 1687373406646,
                "trigger": 0,
                "source": 0,
                "locationId": 1546987,
                "access": [
                    {
                        "category": 1,
                        "trigger": False,
                        "read": True,
                        "control": True,
                        "location": {
                            "locationId": 1546987,
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
                        "trigger": False,
                        "read": False,
                        "control": False,
                        "device": {
                            "deviceId": "20BE44FB-D893-41A0-A5EC-FCD7B75663FC:1546987",
                            "deviceType": 28,
                            "modelId": "appleWatch",
                            "description": "Apple Watch",
                            "remoteAddrHash": "a4f753fffc70eaa761c39a0c6751b2f5206139326ff4545995a26556091a1ec7",
                            "locationId": 1546987,
                            "startDate": 1687068846000,
                            "connected": False,
                        },
                    },
                    {
                        "category": 4,
                        "trigger": False,
                        "read": True,
                        "control": True,
                        "device": {
                            "deviceId": "hk1546987:1250574",
                            "deviceType": 29,
                            "proxyId": "16A104A4-A6A4-481C-B4CC-FB23A806676E:1546987",
                            "description": "My Health",
                            "locationId": 1546987,
                            "startDate": 1654623396000,
                            "connected": True,
                        },
                    },
                ],
            }
        )
        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1

        botengine.inputs = {
            "time": 1687374406646,
            "trigger": 8,
            "source": 8,
            "locationId": 1546987,
            "triggerIds": ["hk1546987:1250574"],
            "access": [
                {
                    "category": 1,
                    "trigger": False,
                    "read": True,
                    "control": True,
                    "location": {
                        "locationId": 1546987,
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
                    "trigger": False,
                    "read": False,
                    "control": False,
                    "device": {
                        "deviceId": "20BE44FB-D893-41A0-A5EC-FCD7B75663FC:1546987",
                        "deviceType": 28,
                        "modelId": "appleWatch",
                        "description": "Apple Watch",
                        "remoteAddrHash": "a4f753fffc70eaa761c39a0c6751b2f5206139326ff4545995a26556091a1ec7",
                        "locationId": 1546987,
                        "startDate": 1687068846000,
                        "connected": False,
                    },
                },
                {
                    "category": 4,
                    "trigger": True,
                    "read": True,
                    "control": True,
                    "device": {
                        "deviceId": "hk1546987:1250574",
                        "deviceType": 29,
                        "proxyId": "16A104A4-A6A4-481C-B4CC-FB23A806676E:1546987",
                        "description": "My Health",
                        "locationId": 1546987,
                        "startDate": 1654623396000,
                        "connected": True,
                    },
                },
            ],
            "measures": [
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "age",
                    "value": "38",
                    "time": 1687379792328,
                    "updated": False,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "bloodType",
                    "value": "5",
                    "time": 1687379792328,
                    "updated": False,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "model",
                    "value": "iPhone14,2",
                    "time": 1687379792328,
                    "updated": False,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "sex",
                    "value": "2",
                    "time": 1687379792328,
                    "updated": False,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "sleepAnalysis",
                    "index": "1",
                    "value": "0",
                    "time": 1681651401051,
                    "updated": False,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "sleepAnalysis",
                    "index": "4",
                    "value": "0",
                    "time": 1686735452840,
                    "updated": False,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "sleepAnalysis",
                    "index": "5",
                    "value": "0",
                    "time": 1686747182840,
                    "updated": False,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "version",
                    "value": "16.3.1",
                    "time": 1687379792328,
                    "updated": False,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "steps",
                    "value": "44",
                    "time": 1686920869089,
                    "updated": True,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "steps",
                    "value": "6",
                    "time": 1686920871954,
                    "updated": True,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "steps",
                    "value": "10",
                    "time": 1686920948704,
                    "updated": True,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "hr",
                    "value": "70",
                    "time": 1686921294719,
                    "updated": True,
                },
                {
                    "deviceId": "hk1546987:1250574",
                    "name": "hr",
                    "value": "75",
                    "time": 1686921558964,
                    "updated": True,
                },
            ],
        }

        bot.run(botengine)
        assert len(controller.locations) == 1

    def test_properties(self):
        botengine = BotEnginePyTest({})

        property_name = "ORGANIZATION_SHORT_NAME"
        property_value = getattr(domain, property_name)

        assert (
            properties.get_property(botengine, "ORGANIZATION_SHORT_NAME")
            == property_value
        )

        botengine.organization_properties[property_name] = "test"
        assert properties.get_property(botengine, "ORGANIZATION_SHORT_NAME") == "test"

        botengine.organization_properties[property_name] = "null"
        assert properties.get_property(botengine, "ORGANIZATION_SHORT_NAME") is None

    def test_language_localization(self):
        botengine = BotEnginePyTest({})
        assert botengine.get_language() == "en"
        bot.run(botengine)
        assert _("Entry Sensor") == "Entry Sensor"  # noqa: F821 # type: ignore
        botengine = BotEnginePyTest(
            {
                "access": [
                    {
                        "category": 1,
                        "control": True,
                        "location": {
                            "language": "es",
                            "event": "HOME",
                            "latitude": "47.72328",
                            "locationId": 0,
                            "longitude": "-122.17426",
                            "name": "Apartment 103",
                            "timezone": {
                                "dst": True,
                                "id": "US/Pacific",
                                "name": "Pacific Standard Time",
                                "offset": -480,
                            },
                            "zip": "98034",
                        },
                        "read": True,
                        "trigger": True,
                    }
                ]
            }
        )

        assert botengine.get_language() == "es"
        bot.run(botengine)
        translations = get_translations(botengine, "Entry Sensor")
        if "es" not in translations:
            with pytest.warns(
                UserWarning, match="No translation found for 'es' language"
            ):
                pytest.skip("No translation found for 'es' language")
        assert _("Entry Sensor") == translations["es"]  # noqa: F821 # type: ignore
