'''
Created on October 5, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence
from devices.motion.motion import MotionDevice
from devices.entry.entry import EntryDevice

import utilities.utilities as utilities
import signals.dashboard as dashboard

# Time between narrations
TIME_BETWEEN_NARRATIONS_MS = utilities.ONE_MINUTE_MS

# Minimum time between updates if the person is still in the same room
MINIMUM_UPDATE_TIMESTAMP_MS = utilities.ONE_MINUTE_MS * 5

class LocationLastSeenMicroservice(Intelligence):
    """
    Continually describe where the person was last seen in the house.
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # Last motion object observed to detect motion
        self.last_observed_motion_object = None

        # Last update timestamp
        self.last_timestamp_ms = 0

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        return

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """

        if isinstance(device_object, MotionDevice):
            if device_object == self.last_observed_motion_object:
                # Already got it
                if self.last_timestamp_ms > botengine.get_timestamp() - MINIMUM_UPDATE_TIMESTAMP_MS:
                    botengine.get_logger().info("=> Already got it")
                    return

            if device_object.did_start_detecting_motion(botengine):
                self.last_observed_motion_object = device_object
                self.last_timestamp_ms = botengine.get_timestamp()

                botengine.get_logger().info("Last Seen : Motion detected in '{}'".format(device_object.description))

                if self.parent.is_sleeping(botengine) and not device_object.is_in_bedroom(botengine):
                    dashboard.update_dashboard_header(botengine,
                                                      location_object=self.parent,
                                                      name="lastseen",
                                                      priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                                                      percent_good=70,
                                                      title=_("Last Seen"),
                                                      comment=_("Occupants should be asleep, but someone was last seen near the '{}'").format(device_object.description),
                                                      icon=device_object.get_icon(),
                                                      icon_font=device_object.get_icon_font(),
                                                      resolution_object=None,
                                                      conversation_object=None,
                                                      future_timestamp_ms=None,
                                                      ttl_ms=utilities.ONE_MINUTE_MS * 10)

                else:
                    dashboard.update_dashboard_header(botengine,
                                                      location_object=self.parent,
                                                      name="lastseen",
                                                      priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                                                      percent_good=100,
                                                      title=self.generate_all_good_title(botengine),
                                                      comment=_("Someone was last seen near the '{}'").format(device_object.description),
                                                      icon=device_object.get_icon(),
                                                      icon_font=device_object.get_icon_font(),
                                                      resolution_object=None,
                                                      conversation_object=None,
                                                      future_timestamp_ms=None,
                                                      ttl_ms=None)

        elif isinstance(device_object, EntryDevice):
            if device_object.did_open(botengine):
                botengine.get_logger().info("Last Seen : '{}' door opened".format(device_object.description))

                dashboard.update_dashboard_header(botengine,
                                                  location_object=self.parent,
                                                  name="lastseen",
                                                  priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                                                  percent_good=100,
                                                  title=self.generate_all_good_title(botengine),
                                                  comment=_("Someone was last seen opening the '{}'").format(device_object.description),
                                                  icon=device_object.get_icon(),
                                                  icon_font=device_object.get_icon_font(),
                                                  resolution_object=None,
                                                  conversation_object=None,
                                                  future_timestamp_ms=None,
                                                  ttl_ms=None)

                self.last_observed_motion_object = None

            elif device_object.did_close(botengine):
                botengine.get_logger().info("Last Seen : '{}' door closed".format(device_object.description))

                dashboard.update_dashboard_header(botengine,
                                                  location_object=self.parent,
                                                  name="lastseen",
                                                  priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                                                  percent_good=100,
                                                  title=self.generate_all_good_title(botengine),
                                                  comment=_("Someone was last seen closing the '{}'").format(device_object.description),
                                                  icon=device_object.get_icon(),
                                                  icon_font=device_object.get_icon_font(),
                                                  resolution_object=None,
                                                  conversation_object=None,
                                                  future_timestamp_ms=None,
                                                  ttl_ms=None)

                self.last_observed_motion_object = None

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        return

    def generate_all_good_title(self, botengine):
        """
        When everything is good, produce a random title that describes we're all good.
        :param botengine:
        :return:
        """
        import domain
        if hasattr(domain, 'LAST_SEEN_DASHBOARD'):
            titles = domain.LAST_SEEN_DASHBOARD

        else:
            titles = [
                "Looking Good",
                "Everything Looks Fine",
                "All Right",
                "Going Well",
                "All Good Here",
                "All Good",
                "Okay",
                "No Problems Found",
                "Things are Good",
                "Good"
            ]

        # Every 100 seconds the title will increment.
        return titles[int(str(botengine.get_timestamp())[6:-5]) % len(titles)]

