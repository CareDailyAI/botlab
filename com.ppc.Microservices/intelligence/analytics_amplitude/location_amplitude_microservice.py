"""
Created on May 14, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

import datetime
import json
import traceback

import bundle  # type: ignore
import properties  # type: ignore
import pytz
import requests
from intelligence.intelligence import Intelligence  # type: ignore

# Variable name for tracking people
AMPLITUDE_USER_PROPERTIES_VARIABLE_NAME = "amplitude_user"

# HTTP timeout
AMPLITUDE_HTTP_TIMEOUT_S = 2


class LocationAmplitudeMicroservice(Intelligence):
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        self.analytics_track(botengine, {"event_name": "reset", "properties": None})

    def analytics_track(self, botengine, content):
        """
        Track an event.
        This will buffer your events and flush them to the server altogether at the end of all bot executions,
        and before variables get saved.

        :param botengine: BotEngine environment
        :param content: (dict) A dictionary containing:
            event_name: (string) A name describing the event
            event_time: (int) (optional) The time of the event in milliseconds since the epoch
            properties: (dict) additional data to record; keys should be strings and values should be strings, numbers, or booleans
        :return:
        """
        if botengine.is_test_location():
            return

        event_name = content.get("event_name")
        event_properties = content.get("properties")
        if event_name is None or event_properties is None:

            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                "<analytics_track() Missing event_name or properties. content={} traceback={}".format(
                    content, traceback.format_exc()
                )
            )
            return

        event_time = content.get("event_time")
        if event_time is None:
            timezone = self.parent.get_local_timezone_string(botengine)
            event_time = int(
                datetime.datetime.fromtimestamp(
                    datetime.datetime.now().timestamp(), pytz.timezone(timezone)
                ).timestamp()
                * 1000
            )

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "|analytics_track() Tracking {} (trigger_time={} event_time={})".format(
                event_name, botengine.get_timestamp(), event_time
            )
        )

        if event_properties is None:
            event_properties = {}

        event_properties["locationId"] = botengine.get_location_id()
        event_properties["organizationId"] = botengine.get_organization_id()

        self._flush(
            botengine,
            [
                {
                    "user_id": self._get_user_id(botengine),
                    "device_id": self._get_device_id(botengine),
                    "time": event_time,
                    "event_type": event_name,
                    "event_properties": event_properties,
                    "user_properties": {
                        "locationId": botengine.get_location_id(),
                        "organizationId": botengine.get_organization_id(),
                    },
                }
            ],
        )

    def analytics_people_set(self, botengine, content):
        """
        Set some key/value attributes for this user
        :param botengine: BotEngine environment
        :param properties_dict: Dictionary of key/value pairs to track
        """
        if botengine.is_test_location():
            return

        properties_dict = content["properties_dict"]

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "|analytics_people_set() Setting user info - {}".format(properties_dict)
        )

        focused_properties = botengine.load_variable(
            AMPLITUDE_USER_PROPERTIES_VARIABLE_NAME
        )
        if focused_properties is None:
            focused_properties = properties_dict
        focused_properties.update(properties_dict)
        focused_properties["locationId"] = botengine.get_location_id()
        focused_properties["organizationId"] = botengine.get_organization_id()
        botengine.save_variable(
            AMPLITUDE_USER_PROPERTIES_VARIABLE_NAME,
            focused_properties,
            required_for_each_execution=False,
        )

        self._flush(
            botengine,
            [
                {
                    "user_id": self._get_user_id(botengine),
                    "device_id": self._get_device_id(botengine),
                    "time": botengine.get_timestamp(),
                    "user_properties": focused_properties,
                }
            ],
        )

    def analytics_people_increment(self, botengine, content):
        """
        Adds numerical values to properties of a people record. Nonexistent properties on the record default to zero. Negative values in properties will decrement the given property.
        :param botengine: BotEngine environment
        :param properties_dict: Dictionary of key/value pairs. The value is numeric, either positive or negative. Default record is 0. The value will increment or decrement the property by that amount.
        """
        if botengine.is_test_location():
            return

        properties_dict = content["properties_dict"]

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "|analytics_people_increment() Incrementing user info - {}".format(
                properties_dict
            )
        )

        focused_properties = botengine.load_variable(
            AMPLITUDE_USER_PROPERTIES_VARIABLE_NAME
        )

        if focused_properties is None:
            focused_properties = properties_dict

        for p in properties_dict:
            if p not in focused_properties:
                focused_properties[p] = 0
            focused_properties[p] += properties_dict[p]

        focused_properties["locationId"] = botengine.get_location_id()
        focused_properties["organizationId"] = botengine.get_organization_id()
        botengine.save_variable(
            AMPLITUDE_USER_PROPERTIES_VARIABLE_NAME,
            focused_properties,
            required_for_each_execution=False,
        )

        self._flush(
            botengine,
            [
                {
                    "user_id": self._get_user_id(botengine),
                    "device_id": self._get_device_id(botengine),
                    "time": botengine.get_timestamp(),
                    "user_properties": focused_properties,
                }
            ],
        )

    def analytics_people_unset(self, botengine, content):
        """
        Delete a property from a user
        :param botengine: BotEngine
        :param properties_dict: Key/Value dictionary pairs to remove from a people record.
        """
        if botengine.is_test_location():
            return

        properties_list = content["properties_list"]

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "|analytics_people_unset() Removing user info - {}".format(properties_list)
        )

        focused_properties = botengine.load_variable(
            AMPLITUDE_USER_PROPERTIES_VARIABLE_NAME
        )

        if focused_properties is None:
            # Nothing to unset
            return

        for p in properties_list:
            if p in focused_properties:
                del focused_properties[p]

        focused_properties["locationId"] = botengine.get_location_id()
        focused_properties["organizationId"] = botengine.get_organization_id()
        botengine.save_variable(
            AMPLITUDE_USER_PROPERTIES_VARIABLE_NAME,
            focused_properties,
            required_for_each_execution=False,
        )

        self._flush(
            botengine,
            [
                {
                    "user_id": self._get_user_id(botengine),
                    "device_id": self._get_device_id(botengine),
                    "time": botengine.get_timestamp(),
                    "user_properties": focused_properties,
                }
            ],
        )

    def _flush(self, botengine, data):
        """
        Required. Implement the mechanisms to flush your analytics.
        :param botengine: BotEngine
        """
        if botengine.is_test_location() or botengine.is_playback():
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "<_flush() This test location will not record analytics."
            )
            return

        token = None
        amplitude_tokens = properties.get_property(botengine, "AMPLITUDE_TOKENS")
        if amplitude_tokens is not None:
            for cloud_address in amplitude_tokens:
                if cloud_address in bundle.CLOUD_ADDRESS:
                    token = amplitude_tokens[cloud_address]

        if token is None:
            # Nothing to do
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "|flush() No analytics token for {}".format(bundle.CLOUD_ADDRESS)
            )
            return

        if token == "":
            # Nothing to do
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "|flush() No analytics token for {}".format(bundle.CLOUD_ADDRESS)
            )
            return

        http_headers = {"Content-Type": "application/json"}

        body = {"api_key": token, "events": data}

        url = "https://api.amplitude.com/2/httpapi"

        try:
            requests.post(
                url,
                headers=http_headers,
                data=json.dumps(body),
                timeout=AMPLITUDE_HTTP_TIMEOUT_S,
            )
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|flush() body={}".format(json.dumps(body))
            )
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "|flush() Flushed"
            )

        except requests.HTTPError:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "|flush() Generic HTTP error calling POST " + url
            )

        except requests.ConnectionError:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "|flush() Connection HTTP error calling POST " + url
            )

        except requests.Timeout:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "|flush()"
                + str(AMPLITUDE_HTTP_TIMEOUT_S)
                + " second HTTP Timeout calling POST "
                + url
            )

        except requests.TooManyRedirects:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "|flush() Too many redirects HTTP error calling POST " + url
            )

        except Exception as e:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "|flush() Generale error " + str(e)
            )
            return

    def _get_user_id(self, botengine):
        """
        Generate an Amplitude User ID
        To us, this user ID will always have a "bot_" prefix, followed by the bot instance ID.
        :return:
        """
        return "bot_{}".format(botengine.bot_instance_id)

    def _get_device_id(self, botengine):
        """
        Get the Device ID
        :param botengine:
        :return:
        """
        return botengine.get_bundle_id()
