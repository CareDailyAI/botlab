from locations.location import Location

import properties
import bundle

from botengine_pytest import BotEnginePyTest

import unittest
import requests_mock
from unittest.mock import MagicMock, patch

class TestLocationAnalyticsAmplitudeMicroservice(unittest.TestCase):


    def test_analytics_amplitude_token(self):
        """
        :return:
        """
        botengine = BotEnginePyTest({})
        token = None
        amplitude_tokens = properties.get_property(botengine, "AMPLITUDE_TOKENS")

        assert amplitude_tokens is not None
        for cloud_address in amplitude_tokens:
            if cloud_address in bundle.CLOUD_ADDRESS:
                token = amplitude_tokens[cloud_address]
                return

        assert token is not None
    
    @requests_mock.mock()
    @patch('botengine_pytest.BotEnginePyTest.is_test_location')
    @patch('botengine_pytest.BotEnginePyTest.is_playback')
    def test_analytics_amplitude_event(self, mock_for_requests, mock_is_playback, mock_is_test_location):
        botengine = BotEnginePyTest({})
        mock_is_test_location.return_value = True
        mock_is_playback.return_value = False

        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules["intelligence.analytics_amplitude.location_amplitude_microservice"]
        
        token = None
        amplitude_tokens = properties.get_property(botengine, "AMPLITUDE_TOKENS")

        assert amplitude_tokens is not None
        for cloud_address in amplitude_tokens:
            if cloud_address in bundle.CLOUD_ADDRESS:
                token = amplitude_tokens[cloud_address]
                break
        
        mock_is_test_location.return_value = False
        timestamp = botengine.get_timestamp()

        mock_for_requests.post("https://api.amplitude.com/2/httpapi", headers={}, json={"status": 200})
        mut.analytics_track(botengine, {"event_name": "test", "event_time": botengine.get_timestamp(), "properties": {"test": "test"}})

        assert mock_for_requests.called
        assert mock_for_requests.call_count == 1

        request_json = mock_for_requests.last_request.json()
        botengine.get_logger().info("DEBUG: {}".format(request_json))
        {
            'api_key': '267ab5573fc279e3ddaa4da272518a15', 'events': [
                {
                    'user_id': 'bot_0', 
                    'device_id': 'com.ppc.Tests', 
                    'time': 1696014860506, 
                    'event_type': 'test', 
                    'event_properties': {
                        'test': 'test', 
                        'locationId': 0, 
                        'organizationId': 0
                    }, 
                    'user_properties': {
                        'locationId': 0, 
                        'organizationId': 0
                    }}]}
        
        assert request_json['api_key'] == token
        assert request_json['events'][-1]['user_id'] == 'bot_0'
        assert request_json['events'][-1]['device_id'] == 'com.ppc.Tests'
        assert request_json['events'][-1]['time'] == timestamp
        assert request_json['events'][-1]['event_type'] == 'test'
        assert request_json['events'][-1]['event_properties'] == {'test': 'test', 'locationId': 0, 'organizationId': 0}

        