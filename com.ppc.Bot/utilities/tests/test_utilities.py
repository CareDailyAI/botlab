import unittest
from unittest.mock import MagicMock, patch
import logging
import json

from botengine_pytest import BotEnginePyTest
from locations.location import Location
import properties

import utilities.utilities as utilities

class TestUtilities(unittest.TestCase):

    @patch('locations.location.Location.get_relative_time_of_day')
    def test_get_organization_user_notification_categories(self, mock_get_relative_time_of_day):
        
        # Initial setup
        botengine = BotEnginePyTest({})
        location_object = Location(botengine, 0)

        # Set domain features
        botengine.organization_properties["ALLOW_ADMINISTRATIVE_MONITORING"] = True
        botengine.organization_properties["DO_NOT_CONTACT_ADMINS_BEFORE_RELATIVE_HOUR"] = 6
        botengine.organization_properties["DO_NOT_CONTACT_ADMINS_AFTER_RELATIVE_HOUR"] = 18
        botengine.organization_properties["ADMIN_DEFAULT_TIMEZONE"] = "America/Los_Angeles"
        
        # Set time
        mock_get_relative_time_of_day.return_value = 12

        # Test 1: [1.0] Enabled
        categories = utilities.get_organization_user_notification_categories(botengine, location_object)
        assert categories == [1,2]

        # Test 2: [1.0] Disabled
        botengine.organization_properties["ALLOW_ADMINISTRATIVE_MONITORING"] = False
        categories = utilities.get_organization_user_notification_categories(botengine, location_object)
        assert categories == []
        botengine.organization_properties["ALLOW_ADMINISTRATIVE_MONITORING"] = True # Reset

        # Test 3: [1.1] Disabled by time of day
        mock_get_relative_time_of_day.return_value = 0

        categories = utilities.get_organization_user_notification_categories(botengine, location_object)
        assert categories == [1]
        mock_get_relative_time_of_day.return_value = 12

        # Test 4: Exclusion
        categories = utilities.get_organization_user_notification_categories(botengine, location_object, excluded_categories=[1,2])
        assert categories == []
    
    @patch("properties.get_property")
    def test_get_chat_assistant_name(self, mock_get_property):

        # Initial setup
        botengine = BotEnginePyTest({})

        # Check default
        mock_get_property.return_value = None
        assert utilities.get_chat_assistant_name(botengine) == utilities.DEFAULT_CHAT_ASSISTANT_NAME

        mock_get_property.return_value = "Test"
        assert utilities.get_chat_assistant_name(botengine) == "Test"

    def test_utilities_distance_between_points(self):
        p1 = (46.3995886, -117.0269895)
        p2 = (46.3991002, -117.0229983)
        p3 = (46.4012163, -117.0295858)
        p4 = (46.3981976, -117.0307875)
        p5 = (46.4009055, -117.0333624)
        p6 = (46.3995294, -117.0259166)

        assert utilities.distance_between_points(p1[0], p1[1], p1[0], p1[1]) == 0
        assert utilities.distance_between_points(p1[0], p1[1], p2[0], p2[1]) == 310
        assert utilities.distance_between_points(p1[0], p1[1], p3[0], p3[1]) == 269
        assert utilities.distance_between_points(p1[0], p1[1], p4[0], p4[1]) == 329
        assert utilities.distance_between_points(p1[0], p1[1], p5[0], p5[1]) == 510
        assert utilities.distance_between_points(p1[0], p1[1], p6[0], p6[1]) == 82

    @patch('botengine_pytest.BotEnginePyTest.get_location_id', MagicMock(return_value=123))
    @patch('botengine_pytest.BotEnginePyTest.get_organization_id', MagicMock(return_value=123))
    @patch('properties.get_property')
    def test_utilities_get_admin_url_for_location(self, get_property_mock):
        botengine = BotEnginePyTest({})

        get_property_mock.return_value = None
        assert utilities.get_admin_url_for_location(botengine) == "" 

        get_property_mock.return_value = {"app.peoplepowerco.com": "https://console.peoplepowerfamily.com"}
        assert utilities.get_admin_url_for_location(botengine) == "https://console.peoplepowerfamily.com/#!/main/locations/edit/123"

        get_property_mock.return_value = {"app.peoplepowerco.com": "https://app.caredaily.ai"}
        assert utilities.get_admin_url_for_location(botengine) == "https://app.caredaily.ai/org/123/locations/123/dashboard"

    def test_utilities_getsize(self):
        assert utilities.getsize({}) is not None
        assert utilities.getsize({}) == 64

    @patch("json.loads")
    def test_utilities_core_bot(self, json_loads_mock):
        botengine = BotEnginePyTest({})

        json_loads_mock.return_value = {"app": {}}
        assert utilities.is_core_bot(botengine) == False
        
        json_loads_mock.return_value = {"app": {"core": 1}}
        assert utilities.is_core_bot(botengine) == True

        json_loads_mock.return_value = {"app": {"core": -1}}
        assert utilities.is_core_bot(botengine) == False

        json_loads_mock.return_value = {"app": {}}
        assert utilities.is_core_bot(botengine, True) == False
        
        json_loads_mock.return_value = {"app": {"core": 1}}
        assert utilities.is_core_bot(botengine, True) == False

        json_loads_mock.return_value = {"app": {"core": -1}}
        assert utilities.is_core_bot(botengine, True) == True