'''
Created on September 15, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# Analytics Variable Names
DEPRECATED_ANALYTICS_VARIABLE = "[a]"
MIXPANEL_VARIABLE = "[mix]"
AMPLITUDE_VARIABLE = "[amp]"

# Global analytics module
analytics_module = None

def get_analytics(botengine, must_exist=False):
    """
    Required. This is the correct method to use to access your Analytics objects across all microservices.
    The Analytics class returned must implement the flush(botengine) method.

    Get the existing analytics object or create a new one.

    :param botengine: BotEngine environment
    :param must_exist: True if the analytics module must have been instantiated before attempting to access it now, so we can skip flushing it.
    :return: Analytics object
    """
    try:
        analytics_deleted = botengine.load_variable("analytics_deleted")
        if analytics_deleted is None:
            if DEPRECATED_ANALYTICS_VARIABLE in botengine.variables:
                del (botengine.variables[DEPRECATED_ANALYTICS_VARIABLE])
            botengine.delete_variable(MIXPANEL_VARIABLE)
            botengine.delete_variable(AMPLITUDE_VARIABLE)
            botengine.delete_variable(DEPRECATED_ANALYTICS_VARIABLE)
            botengine.save_variable("analytics_deleted", True, required_for_each_execution=True)

    except:
        pass

    raise ImportError


class Analytics:
    """
    Base Analytics Class
    """
    def __init__(self, botengine):
        """
        :param token:
        :param request_timeout:
        """
        return

    def track(self, botengine, event_name, properties=None):
        """
        Track an event.
        This will buffer your events and flush them to the server altogether at the end of all bot executions,
        and before variables get saved.

        :param botengine: BotEngine environment
        :param event_name: (string) A name describing the event
        :param properties: (dict) Additional data to record; keys should be strings and values should be strings, numbers, or booleans
        """
        raise NotImplementedError

    def people_set(self, botengine, properties_dict):
        """
        Set some key/value attributes for this user
        :param botengine: BotEngine environment
        :param properties_dict: Dictionary of key/value pairs to track
        """
        raise NotImplementedError

    def people_increment(self, botengine, properties_dict):
        """
        Adds numerical values to properties of a people record. Nonexistent properties on the record default to zero. Negative values in properties will decrement the given property.
        :param botengine: BotEngine environment
        :param properties_dict: Dictionary of key/value pairs. The value is numeric, either positive or negative. Default record is 0. The value will increment or decrement the property by that amount.
        """
        raise NotImplementedError

    def people_append(self, botengine, properties_dict):
        """
        Append to the list associated with a property
        :param botengine: BotEngine environment
        :param properties_dict: Key/Value properties to append
        """
        raise NotImplementedError

    def people_unset(self, botengine, properties_list):
        """
        Delete a property from a user
        :param botengine: BotEngine
        :param properties_dict: Key/Value dictionary pairs to remove from a people record.
        """
        raise NotImplementedError

    def flush(self, botengine):
        """
        Required. Implement the mechanisms to flush your analytics.
        :param botengine: BotEngine
        """
        raise NotImplementedError
