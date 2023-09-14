from intelligence.analytics_amplitude.location_amplitude_microservice  import LocationAmplitudeMicroservice

from locations.location import Location

import properties
import bundle

from botengine_pytest import BotEnginePyTest

import unittest
import requests_mock
from unittest.mock import MagicMock, patch


class TestLocationConversationMicroservice(unittest.TestCase):


    def test_analytics_amplitude_token(self):
        """
        :return:
        """

        botengine = BotEnginePyTest({})
        token = ''
        amplitude_tokens = properties.get_property(botengine, "AMPLITUDE_TOKENS")

        assert amplitude_tokens is not None

        amplitude_tokens[bundle.CLOUD_ADDRESS] = "test_token"
        botengine.organization_properties["AMPLITUDE_TOKENS"] = amplitude_tokens

        if amplitude_tokens is not None:
            for cloud_address in amplitude_tokens:
                if cloud_address in bundle.CLOUD_ADDRESS:
                    token = amplitude_tokens[cloud_address]
        
        assert token is not ''
    
    @requests_mock.mock()
    def test_analytics_amplitude_event(self, mock_for_requests):
        botengine = BotEnginePyTest({})
        
        token = 'test_token'
        amplitude_tokens = properties.get_property(botengine, "AMPLITUDE_TOKENS")
        assert amplitude_tokens is not None

        amplitude_tokens[bundle.CLOUD_ADDRESS] = token
        botengine.organization_properties["AMPLITUDE_TOKENS"] = amplitude_tokens

        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        microservice_under_test = LocationAmplitudeMicroservice(botengine, location_object)
        
        timestamp = botengine.get_timestamp()
        botengine.is_test_location = MagicMock(return_value=False)
        botengine.is_playback = MagicMock(return_value=False)

        mock_for_requests.post("https://api.amplitude.com/2/httpapi", headers={}, json={"status": 200})
        import time
        time.sleep(1)
        microservice_under_test.analytics_track(botengine, {"event_name": "test",
                                                            "properties": {"test": "test"}})

        assert mock_for_requests.called
        assert mock_for_requests.call_count == 1

        request_json = mock_for_requests.last_request.json()
        assert request_json['api_key'] == token
        assert request_json['events'][0]['user_id'] == 'bot_0'
        assert request_json['events'][0]['device_id'] == 'com.ppc.Tests'
        assert int(request_json['events'][0]['time'] / 1000) == int((timestamp + 1000) / 1000)
        assert request_json['events'][0]['event_type'] == 'test'
        assert request_json['events'][0]['event_properties'] == {'test': 'test', 'locationId': 0, 'organizationId': 0}

        