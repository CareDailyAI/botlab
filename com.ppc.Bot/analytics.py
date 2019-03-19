'''
Created on September 15, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''


# Global analytics object
analytics_object = None

# Analytics Variable Name
ANALYTICS_VARIABLE = "[a]"

# Mixpanel HTTP Timeout in seconds
MIXPANEL_HTTP_TIMEOUT_S = 2

# Distinct ID variable
VARIABLE_DISTINCT_ID = "-distinctid-"

def has_analytics(botengine):
    """
    Required. See if our analytics_object exists before attempting to get it.
    We don't want to accidentally initialize the analytics_object when we are flushing.

    :return: True if an analytics object exists
    """
    return ANALYTICS_VARIABLE in botengine.variables["-core-"]

def get_analytics(botengine):
    """
    Required. This is the correct method to use to access your Analytics objects across all microservices.
    The Analytics class returned must implement the flush(botengine) method.

    Get the existing analytics object or create a new one.

    :param botengine: BotEngine environment
    :return: Analytics object
    """
    import domain
    if hasattr(domain, "ALLOW_MIXPANEL"):
        if not domain.ALLOW_MIXPANEL:
            raise ImportError
    else:
        raise ImportError

    analytics_object = botengine.load_variable(ANALYTICS_VARIABLE)
    if analytics_object is None:
        analytics_object = Analytics(botengine)
        botengine.save_variable(ANALYTICS_VARIABLE, analytics_object, required_for_each_execution=True)

    # Update the bot's MixPanel token to whatever is currently in the domain.py file
    analytics_object._token = domain.MIXPANEL_TOKEN

    return analytics_object


class Analytics():
    """
    Mixpanel-specific implementation of analytics.

    You can replace this implementation to point to your own analytics service, and it will continue to
    work throughout the entire microservices framework.

    See mixpanel documentation at: https://mixpanel.github.io/mixpanel-python/

    To use in your bot:  First include 'mixpanel' in pip_install or pip_install_remotely in your structure.json file.

        import analytics
        analytics.get_analytics(botengine).track(botengine, event_name, properties=None, meta=None)

    
    Or to make a generalized microservice that may or may not have an analytics.py file implemented in the base class:

        import importlib
        try:
            analytics = importlib.import_module('analytics')
            analytics.get_analytics(botengine).track(botengine, event_name, properties=None, meta=None)

        except ImportError:
            botengine.get_logger().warn("Unable to import analytics module")

    Or another method, leveraging the com.ppc.Bot/locations/location.py object:

        location_object.track(..)

    """
    def __init__(self, botengine):
        """
        :param token:
        :param request_timeout:
        """
        import domain
        import mixpanel

        # Mixpanel Object
        self.mp = mixpanel.Mixpanel(domain.MIXPANEL_TOKEN, consumer=mixpanel.BufferedConsumer(request_timeout=MIXPANEL_HTTP_TIMEOUT_S))

        # Total number of events tracked on this execution, never saved so always 0 on the next execution
        self.temp_total_tracked = 0

        self._sync_user(botengine)


    def track(self, botengine, event_name, properties=None, meta=None):
        """
        Track an event. This is for a mixpanel-specific implementation.
        This will buffer your events and flush them to the server altogether at the end of all bot executions,
        and before variables get saved.

        :param botengine: BotEngine environment
        :param event_name: (string) A name describing the event
        :param properties: (dict) Additional data to record; keys should be strings and values should be strings, numbers, or booleans
        :param meta: (dict) overrides Mixpanel special properties
        """
        self.temp_total_tracked += 1
        botengine.get_logger().info("Analytics: Tracking {} => {}".format(self.temp_total_tracked, event_name))
        self.mp.track(self._get_distinct_id(botengine), event_name, properties, meta)


    def people_set(self, botengine, properties_dict):
        """
        Set some key/value attributes for this user
        :param botengine: BotEngine environment
        :param properties_dict: Dictionary of key/value pairs to track
        """
        self.temp_total_tracked += 1
        botengine.get_logger().info("Analytics: Setting user info - {}".format(properties_dict))
        self.mp.people_set(self._get_distinct_id(botengine), properties_dict)


    def people_increment(self, botengine, properties_dict):
        """
        Adds numerical values to properties of a people record. Nonexistent properties on the record default to zero. Negative values in properties will decrement the given property.
        :param botengine: BotEngine environment
        :param properties_dict: Dictionary of key/value pairs. The value is numeric, either positive or negative. Default record is 0. The value will increment or decrement the property by that amount.
        """
        self.temp_total_tracked += 1
        botengine.get_logger().info("Analytics: Incrementing user info - {}".format(properties_dict))
        self.mp.people_increment(self._get_distinct_id(botengine), properties_dict)


    def people_append(self, botengine, properties_dict):
        """
        Append to the list associated with a property
        :param botengine: BotEngine environment
        :param properties_dict: Key/Value properties to append
        """
        self.temp_total_tracked += 1
        botengine.get_logger().info("Analytics: Appending user info - {}".format(properties_dict))
        self.mp.people_append(self._get_distinct_id(botengine), properties_dict)

    def people_unset(self, botengine, properties_list):
        """
        Delete a property from a user
        :param botengine: BotEngine
        :param properties_dict: Key/Value dictionary pairs to remove from a people record.
        """
        self.temp_total_tracked += 1
        botengine.get_logger().info("Analytics: Removing user info - {}".format(properties_list))
        self.mp.people_unset(self._get_distinct_id(botengine), properties_list)

    def flush(self, botengine):
        """
        Required. Implement the mechanisms to flush your analytics.
        :param botengine: BotEngine
        """
        if self.temp_total_tracked > 0:
            try:
                self._sync_user(botengine)
                self.mp._consumer._consumer._request_timeout = MIXPANEL_HTTP_TIMEOUT_S
                self.mp._consumer.flush()

            except Exception as e:
                import traceback
                botengine.get_logger().error(str(e) + "; " + traceback.format_exc())

        self.temp_total_tracked = 0

    def _sync_user(self, botengine):
        """
        Sync the user account information
        :param botengine: BotEngine environment
        """
        import domain

        anonymize = False
        if hasattr(domain, "ANONYMIZE_MIXPANEL"):
            anonymize = domain.ANONYMIZE_MIXPANEL

        if anonymize:
            self.mp.people_set(self._get_distinct_id(botengine), {
                'location_id': botengine.get_location_id()
            })

        else:
            try:
                self.mp.people_set(self._get_distinct_id(botengine), {
                    'location_id': botengine.get_location_id(),
                    '$first_name': botengine.get_location_users()[0]['firstName'],
                    '$last_name': botengine.get_location_users()[0]['lastName']
                })

            except:
                # This can get removed after January 10, 2019
                self.mp.people_set(self._get_distinct_id(botengine), {
                    'location_id': botengine.get_location_id()
                })

    def _get_distinct_id(self, botengine):
        """
        Get the distinct ID for this user
        :param botengine:
        :return: distinct ID
        """
        # The following is returned from botengine.get_location_users()
        # using an account on sbox that hasn't been touched in any other way.
        # This format is similar to what we would expect from all production users
        # as we transform from user-centric services to location-centric services.
        #
        # [
        #     {
        #         "category": 1,
        #         "email": {
        #             "status": 1,
        #             "verified": false
        #         },
        #         "firstName": "David",
        #         "id": 677,
        #         "language": "en",
        #         "lastName": "Moss",
        #         "locationAccess": 30,
        #         "phoneType": 0,
        #         "smsStatus": 0,
        #         "userName": "dmoss+1@peoplepowerco.com"
        #     }
        # ]
        #

        distinct_id = botengine.load_variable(VARIABLE_DISTINCT_ID)
        if distinct_id is None:

            import domain
            user_centric = False
            if hasattr(domain, 'USER_CENTRIC_MIXPANEL'):
                user_centric = domain.USER_CENTRIC_MIXPANEL

            if user_centric:
                try:
                    users = botengine.get_location_users()
                    distinct_id = users[0]['id']
                except:
                    # This can get removed after January 10, 2019
                    distinct_id = botengine.inputs['userId']

            else:
                # We offset the distinct ID by 1,000,000 to avoid conflict with transitioning
                # from user ID's as the distinct ID to the location ID.
                distinct_id = botengine.get_location_id() + 1000000

            botengine.save_variable(VARIABLE_DISTINCT_ID, distinct_id, required_for_each_execution=True)

        return distinct_id