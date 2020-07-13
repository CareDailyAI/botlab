'''
Created on May 14, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence
import mixpanel
import domain

# Mixpanel HTTP Timeout in seconds
MIXPANEL_HTTP_TIMEOUT_S = 2

# Distinct ID variable
VARIABLE_DISTINCT_ID = "-distinctid-"


class LocationMixpanelMicroservice(Intelligence):
    """
    Mixpanel-specific implementation of analytics.
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        self.analytics_track(botengine, {'event_name': 'reset', 'properties': None})

    def analytics_track(self, botengine, content):
        """
        Track an event. This is for a mixpanel-specific implementation.
        This will buffer your events and flush them to the server altogether at the end of all bot executions,
        and before variables get saved.

        :param botengine: BotEngine environment
        :param event_name: (string) A name describing the event
        :param properties: (dict) Additional data to record; keys should be strings and values should be strings, numbers, or booleans
        """
        if botengine.is_test_location():
            return

        event_name = content['event_name']
        properties = content['properties']

        mp = mixpanel.Mixpanel(domain.MIXPANEL_TOKEN, consumer=mixpanel.BufferedConsumer(request_timeout=MIXPANEL_HTTP_TIMEOUT_S))
        mp.track(self._get_distinct_id(botengine), event_name, properties)
        self._flush(botengine, mp)

    def analytics_people_set(self, botengine, content):
        """
        Set some key/value attributes for this user
        :param botengine: BotEngine environment
        :param properties_dict: Dictionary of key/value pairs to track
        """
        if botengine.is_test_location():
            return

        properties_dict = content['properties_dict']

        botengine.get_logger().info("analytics.py: Setting user info - {}".format(properties_dict))
        mp = mixpanel.Mixpanel(domain.MIXPANEL_TOKEN, consumer=mixpanel.BufferedConsumer(request_timeout=MIXPANEL_HTTP_TIMEOUT_S))
        mp.people_set(self._get_distinct_id(botengine), properties_dict)
        self._flush(botengine, mp)

    def analytics_people_increment(self, botengine, content):
        """
        Adds numerical values to properties of a people record. Nonexistent properties on the record default to zero. Negative values in properties will decrement the given property.
        :param botengine: BotEngine environment
        :param properties_dict: Dictionary of key/value pairs. The value is numeric, either positive or negative. Default record is 0. The value will increment or decrement the property by that amount.
        """
        if botengine.is_test_location():
            return

        properties_dict = content['properties_dict']

        botengine.get_logger().info("Analytics: Incrementing user info - {}".format(properties_dict))
        mp = mixpanel.Mixpanel(domain.MIXPANEL_TOKEN, consumer=mixpanel.BufferedConsumer(request_timeout=MIXPANEL_HTTP_TIMEOUT_S))
        mp.people_increment(self._get_distinct_id(botengine), properties_dict)
        self._flush(botengine, mp)

    def analytics_people_unset(self, botengine, content):
        """
        Delete a property from a user
        :param botengine: BotEngine
        :param properties_dict: Key/Value dictionary pairs to remove from a people record.
        """
        if botengine.is_test_location():
            return

        properties_list = content['properties_list']

        botengine.get_logger().info("Analytics: Removing user info - {}".format(properties_list))
        mp = mixpanel.Mixpanel(domain.MIXPANEL_TOKEN, consumer=mixpanel.BufferedConsumer(request_timeout=MIXPANEL_HTTP_TIMEOUT_S))
        mp.people_unset(self._get_distinct_id(botengine), properties_list)
        self._flush(botengine, mp)

    def _flush(self, botengine, mp):
        """
        Required. Implement the mechanisms to flush your analytics.
        :param botengine: BotEngine
        """
        try:
            self._sync_user(botengine, mp)
            mp._consumer._consumer._request_timeout = MIXPANEL_HTTP_TIMEOUT_S
            mp._consumer.flush()

        except Exception as e:
            import traceback
            botengine.get_logger().error(str(e) + "; " + traceback.format_exc())

    def _sync_user(self, botengine, mp):
        """
        Sync the user account information
        :param botengine: BotEngine environment
        """
        anonymize = False
        if hasattr(domain, "ANONYMIZE_ANALYTICS"):
            anonymize = domain.ANONYMIZE_ANALYTICS

        if anonymize:
            mp.people_set(self._get_distinct_id(botengine), {
                'location_id': botengine.get_location_id()
            })

        else:
            mp.people_set(self._get_distinct_id(botengine), {
                'location_id': botengine.get_location_id(),
                '$first_name': botengine.get_location_name(),
                '$last_name': ""
            })

    def _get_distinct_id(self, botengine):
        """
        Get the distinct ID for this user
        :param botengine:
        :return: distinct ID
        """
        distinct_id = botengine.load_variable(VARIABLE_DISTINCT_ID)
        if distinct_id is None:
            distinct_id = botengine.get_location_id()
            botengine.save_variable(VARIABLE_DISTINCT_ID, distinct_id, required_for_each_execution=True)

        return distinct_id