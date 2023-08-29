from botengine_pytest import BotEnginePyTest

from locations.location import Location

import utilities.utilities as utilities

import bot

from unittest.mock import MagicMock

class TestBot():
    """
    """

    def test_bot_run_init(self):
        """
        This test is to ensure that the botengine is initialized correctly with the correct location
        :return:
        """
        botengine = BotEnginePyTest(
            {
                'time': 1687373406646, 
                'trigger': 0, 
                'source': 0, 
                'locationId': 1546987, 
                'access': [
                    {
                        'category': 1, 
                        'trigger': False, 
                        'read': True, 
                        'control': True, 
                        'location': {
                            'locationId': 1546987, 
                            'name': "Destry Teeter's Home", 
                            'event': 'HOME.:.PRESENT.AI', 
                            'timezone': {'id': 'America/Los_Angeles', 'offset': -480, 'dst': True, 'name': 'Pacific Standard Time'}, 
                            'zip': '83501', 
                            'latitude': '46.39950', 
                            'longitude': '-117.02710', 
                            'language': 'en', 
                            'priorityCategory': 4, 
                            'priorityRank': 73, 
                            'priorityDateMs': 1687363210000, 
                            'organizationId': 202, 
                            'organization': {
                                'organizationId': 202, 
                                'organizationName': 'PPCg Dev', 
                                'domainName': 'ppcgdev', 
                                'brand': 'familycare', 
                                'parentId': 104, 
                                'features': 'b,g,m,n,p'
                            }
                        }
                    }
                ]
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
                'time': 1687373406646, 
                'trigger': 256, 
                'source': 0, 
                'locationId': 1546987, 
                'access': [
                    {
                        'category': 1, 
                        'trigger': False, 
                        'read': True, 
                        'control': True, 
                        'location': {
                            'locationId': 1546987, 
                            'name': "Destry Teeter's Home", 
                            'event': 'HOME.:.PRESENT.AI', 
                            'timezone': {'id': 'America/Los_Angeles', 'offset': -480, 'dst': True, 'name': 'Pacific Standard Time'}, 
                            'zip': '83501', 
                            'latitude': '46.39950', 
                            'longitude': '-117.02710', 
                            'language': 'en', 
                            'priorityCategory': 4, 
                            'priorityRank': 73, 
                            'priorityDateMs': 1687363210000, 
                            'organizationId': 202, 
                            'organization': {
                                'organizationId': 202, 
                                'organizationName': 'PPCg Dev', 
                                'domainName': 'ppcgdev', 
                                'brand': 'familycare', 
                                'parentId': 104, 
                                'features': 'b,g,m,n,p'
                            }
                        }
                    } 
                ], 
                'dataStream': {
                    'feed': {
                        'id': '__people__', 
                        'deleted_by': 1203763
                    }, 
                    'address': 'delete_task'
                }
            }
        )

        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1
        assert len(botengine.get_state("tasks")) == 0

    def test_bot_run_measurements(self):
        """
        This test initializes a new bot instance with a trigger type of 8 (measurements).
        :return:
        """
        botengine = BotEnginePyTest(
            {
                'time': 1687170210000, 
                'trigger': 8, 
                'source': 8, 
                'locationId': 1546987, 
                'triggerIds': ['hk1546987:1250574'], 
                'access': [
                    {
                        'category': 1, 'trigger': False, 'read': True, 'control': True, 'location': {'locationId': 1546987, 'name': "Destry Teeter's Home", 'event': 'HOME.:.PRESENT.AI', 'timezone': {'id': 'America/Los_Angeles', 'offset': -480, 'dst': True, 'name': 'Pacific Standard Time'}, 'zip': '83501', 'latitude': '46.39950', 'longitude': '-117.02710', 'language': 'en', 'priorityCategory': 4, 'priorityRank': 73, 'priorityDateMs': 1687363210000, 'organizationId': 202, 'organization': {'organizationId': 202, 'organizationName': 'PPCg Dev', 'domainName': 'ppcgdev', 'brand': 'familycare', 'parentId': 104, 'features': 'b,g,m,n,p'}}
                    }, 
                    {
                        'category': 4, 'trigger': False, 'read': False, 'control': False, 'device': {'deviceId': '20BE44FB-D893-41A0-A5EC-FCD7B75663FC:1546987', 'deviceType': 28, 'modelId': 'appleWatch', 'description': 'Apple Watch', 'remoteAddrHash': 'a4f753fffc70eaa761c39a0c6751b2f5206139326ff4545995a26556091a1ec7', 'locationId': 1546987, 'startDate': 1687068846000, 'connected': False}
                    },
                    {
                        'category': 4, 'trigger': True, 'read': True, 'control': True, 'device': {'deviceId': 'hk1546987:1250574', 'deviceType': 29, 'proxyId': '16A104A4-A6A4-481C-B4CC-FB23A806676E:1546987', 'description': 'My Health', 'locationId': 1546987, 'startDate': 1654623396000, 'connected': True}
                    }
                ], 
                'measures': [
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'age', 'value': '38', 'time': 1687379792328, 'updated': False
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'bloodType', 'value': '5', 'time': 1687379792328, 'updated': False
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'model', 'value': 'iPhone14,2', 'time': 1687379792328, 'updated': False
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'sex', 'value': '2', 'time': 1687379792328, 'updated': False
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'sleepAnalysis', 'index': '1', 'value': '0', 'time': 1681651401051, 'updated': False
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'sleepAnalysis', 'index': '4', 'value': '0', 'time': 1686735452840, 'updated': False
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'sleepAnalysis', 'index': '5', 'value': '0', 'time': 1686747182840, 'updated': False
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'version', 'value': '16.3.1', 'time': 1687379792328, 'updated': False
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'steps', 'value': '44', 'time': 1686920869089, 'updated': True
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'steps', 'value': '6', 'time': 1686920871954, 'updated': True
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'steps', 'value': '10', 'time': 1686920948704, 'updated': True
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'hr', 'value': '70', 'time': 1687170210000, 'updated': True
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'hr', 'value': '75', 'time': 1687170220000, 'updated': True
                    },
                    {
                        'deviceId': 'hk1546987:1250574', 'name': 'hr', 'value': '74', 'time': 1687181320000, 'updated': True
                    }
                ]
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
                'time': 1687373406646, 
                'trigger': 0, 
                'source': 0, 
                'locationId': 1546987, 
                'access': [
                    {
                        'category': 1, 
                        'trigger': False, 
                        'read': True, 
                        'control': True, 
                        'location': {
                            'locationId': 1546987, 
                            'name': "Destry Teeter's Home", 
                            'event': 'HOME.:.PRESENT.AI', 
                            'timezone': {'id': 'America/Los_Angeles', 'offset': -480, 'dst': True, 'name': 'Pacific Standard Time'}, 
                            'zip': '83501', 
                            'latitude': '46.39950', 
                            'longitude': '-117.02710', 
                            'language': 'en', 
                            'priorityCategory': 4, 
                            'priorityRank': 73, 
                            'priorityDateMs': 1687363210000, 
                            'organizationId': 202, 
                            'organization': {
                                'organizationId': 202, 
                                'organizationName': 'PPCg Dev', 
                                'domainName': 'ppcgdev', 
                                'brand': 'familycare', 
                                'parentId': 104, 
                                'features': 'b,g,m,n,p'
                            }
                        }
                    },
                    {
                        'category': 4, 'trigger': False, 'read': False, 'control': False, 'device': {'deviceId': '20BE44FB-D893-41A0-A5EC-FCD7B75663FC:1546987', 'deviceType': 28, 'modelId': 'appleWatch', 'description': 'Apple Watch', 'remoteAddrHash': 'a4f753fffc70eaa761c39a0c6751b2f5206139326ff4545995a26556091a1ec7', 'locationId': 1546987, 'startDate': 1687068846000, 'connected': False}
                    },
                    {
                        'category': 4, 'trigger': False, 'read': True, 'control': True, 'device': {'deviceId': 'hk1546987:1250574', 'deviceType': 29, 'proxyId': '16A104A4-A6A4-481C-B4CC-FB23A806676E:1546987', 'description': 'My Health', 'locationId': 1546987, 'startDate': 1654623396000, 'connected': True}
                    }
                ]
            }
        )
        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1

    
        botengine.inputs = {
            'time': 1687374406646, 
            'trigger': 8, 
            'source': 8, 
            'locationId': 1546987, 
            'triggerIds': ['hk1546987:1250574'], 
            'access': [
                {
                    'category': 1, 'trigger': False, 'read': True, 'control': True, 'location': {'locationId': 1546987, 'name': "Destry Teeter's Home", 'event': 'HOME.:.PRESENT.AI', 'timezone': {'id': 'America/Los_Angeles', 'offset': -480, 'dst': True, 'name': 'Pacific Standard Time'}, 'zip': '83501', 'latitude': '46.39950', 'longitude': '-117.02710', 'language': 'en', 'priorityCategory': 4, 'priorityRank': 73, 'priorityDateMs': 1687363210000, 'organizationId': 202, 'organization': {'organizationId': 202, 'organizationName': 'PPCg Dev', 'domainName': 'ppcgdev', 'brand': 'familycare', 'parentId': 104, 'features': 'b,g,m,n,p'}}
                }, 
                {
                    'category': 4, 'trigger': False, 'read': False, 'control': False, 'device': {'deviceId': '20BE44FB-D893-41A0-A5EC-FCD7B75663FC:1546987', 'deviceType': 28, 'modelId': 'appleWatch', 'description': 'Apple Watch', 'remoteAddrHash': 'a4f753fffc70eaa761c39a0c6751b2f5206139326ff4545995a26556091a1ec7', 'locationId': 1546987, 'startDate': 1687068846000, 'connected': False}
                },
                {
                    'category': 4, 'trigger': True, 'read': True, 'control': True, 'device': {'deviceId': 'hk1546987:1250574', 'deviceType': 29, 'proxyId': '16A104A4-A6A4-481C-B4CC-FB23A806676E:1546987', 'description': 'My Health', 'locationId': 1546987, 'startDate': 1654623396000, 'connected': True}
                }
            ], 
            'measures': [
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'age', 'value': '38', 'time': 1687379792328, 'updated': False
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'bloodType', 'value': '5', 'time': 1687379792328, 'updated': False
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'model', 'value': 'iPhone14,2', 'time': 1687379792328, 'updated': False
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'sex', 'value': '2', 'time': 1687379792328, 'updated': False
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'sleepAnalysis', 'index': '1', 'value': '0', 'time': 1681651401051, 'updated': False
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'sleepAnalysis', 'index': '4', 'value': '0', 'time': 1686735452840, 'updated': False
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'sleepAnalysis', 'index': '5', 'value': '0', 'time': 1686747182840, 'updated': False
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'version', 'value': '16.3.1', 'time': 1687379792328, 'updated': False
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'steps', 'value': '44', 'time': 1686920869089, 'updated': True
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'steps', 'value': '6', 'time': 1686920871954, 'updated': True
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'steps', 'value': '10', 'time': 1686920948704, 'updated': True
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'hr', 'value': '70', 'time': 1686921294719, 'updated': True
                },
                {
                    'deviceId': 'hk1546987:1250574', 'name': 'hr', 'value': '75', 'time': 1686921558964, 'updated': True
                }
            ]
        }

        bot.run(botengine)
        assert len(controller.locations) == 1