'''
Created on February 25, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence
import signals.daylight as daylight
import utilities.utilities as utilities

class LocationMidnightMicroservice(Intelligence):

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # Timestamp last hour fired
        self.last_hour_timestamp = 0

        # Timestamp last hour fired
        self.last_midnight_timestamp = 0

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        return

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        # Added October 8, 2022
        if not hasattr(self, 'last_midnight_timestamp'):
            self.last_midnight_timestamp = 0

        if not hasattr(self, 'last_hour_timestamp'):
            self.last_hour_timestamp = 0

    """
    Announce midnight throughout the microservices framework
    """
    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """
        if schedule_id == "MIDNIGHT":
            if botengine.get_timestamp() - self.last_midnight_timestamp < utilities.ONE_MINUTE_MS * 30:
                botengine.get_logger().error("Server error. Duplicate 'MIDNIGHT' schedule fired. now={}; self.last_midnight_timestamp={}".format(botengine.get_timestamp(), self.last_midnight_timestamp))
                return

            self.last_midnight_timestamp = botengine.get_timestamp()
            daylight.midnight_fired(botengine, self.parent)

        elif schedule_id == "HOUR":
            if botengine.get_timestamp() - self.last_hour_timestamp < utilities.ONE_MINUTE_MS * 30:
                botengine.get_logger().error("Server error. Duplicate 'HOUR' schedule fired. now={}; self.last_hour_timestamp={}".format(botengine.get_timestamp(), self.last_hour_timestamp))
                return

            self.last_hour_timestamp = botengine.get_timestamp()
            daylight.hour_fired(botengine, self.parent)

