'''
Created on December 25, 2016

Yes, I created this on Christmas day.
This is my gift to you.

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import importlib
import datetime
import utilities

from intelligence.intelligence import Intelligence

# Sunrise identifier for timers
SUNRISE = "sunrise"

# Sunset identifier for timers
SUNSET = "sunset"


class LocationDaylightMicroservice(Intelligence):
    """
    Determine sunrise and sunset times for the location
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        if self.parent.latitude is not None and self.parent.longitude is not None:
            self._set_sunrise_sunset_alarm(botengine)

        # Initialize the 'is_daylight' class variable in the Location object.
        self.parent.is_daylight = self.is_daylight(botengine)

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        if not self.is_timer_running(botengine) and not botengine.is_executing_timer():
            if self.parent.latitude is not None and self.parent.longitude is not None:
                self._set_sunrise_sunset_alarm(botengine)

        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        return

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        return

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        return

    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        return

    def device_alert(self, botengine, device_object, alert_type, alert_params):
        """
        Device sent an alert.
        When a device disconnects, it will send an alert like this:  [{u'alertType': u'status', u'params': [{u'name': u'deviceStatus', u'value': u'2'}], u'deviceId': u'eb10e80a006f0d00'}]
        When a device reconnects, it will send an alert like this:  [{u'alertType': u'on', u'deviceId': u'eb10e80a006f0d00'}]
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
        """
        return

    def device_deleted(self, botengine, device_object):
        """
        Device is getting deleted
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting deleted
        """
        return

    def question_answered(self, botengine, question):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question: Question object
        """
        return

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        return

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        """
        return

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        if argument == SUNRISE:
            botengine.get_logger().info("SUNRISE timer fired")

            self.parent.narrate(botengine,
                                title = _("Sunrise"),
                                description = _("It is sunrise at '{}'.").format(self.parent.get_location_name(botengine)),
                                priority = botengine.NARRATIVE_PRIORITY_DEBUG,
                                icon = 'sunrise'
                                )

            self.parent.track(botengine, 'sunrise')
            self.parent.is_daylight = True
            self.parent.distribute_datastream_message(botengine, "sunrise_fired", None, internal=True, external=False)

        elif argument == SUNSET:
            botengine.get_logger().info("SUNSET timer fired")

            self.parent.narrate(botengine,
                                                title = _("Sunset"),
                                                description = _("It is sunset at '{}'.").format(self.parent.get_location_name(botengine)),
                                                priority = botengine.NARRATIVE_PRIORITY_DEBUG,
                                                icon = 'sunset'
                                                )

            self.parent.track(botengine, 'sunset')
            self.parent.is_daylight = False
            self.parent.distribute_datastream_message(botengine, "sunset_fired", None, internal=True, external=False)

        self._set_sunrise_sunset_alarm(botengine)

    def coordinates_updated(self, botengine, latitude, longitude):
        """
        Approximate coordinates of the parent proxy device object have been updated
        :param latitude: Latitude
        :param longitude: Longitude
        """
        botengine.get_logger().info("location_daylight_microservice: Lat/Long updated - recalculating sunrise/sunset times")
        self._set_sunrise_sunset_alarm(botengine)



    #===========================================================================
    # Sunlight
    #===========================================================================
    def is_daylight(self, botengine):
        """
        Is it daylight outside?
        :param botengine: BotEngine environment
        :return: True if we think it's daytime at this location
        """
        next_sunrise_ms = self.next_sunrise_timestamp_ms(botengine)
        next_sunset_ms = self.next_sunset_timestamp_ms(botengine)
        return next_sunset_ms < next_sunrise_ms

    def next_sunrise_timestamp_ms(self, botengine):
        """
        :param botengine: BotEngine environment
        :return: The next sunrise timestamp in ms
        """
        try:
            ephem = importlib.import_module("ephem")
        except ImportError:
            ephem = None

        if self.parent.longitude is None or self.parent.latitude is None or ephem is None:
            # Ya, we don't have any coordinate information. Call it 8 AM.
            dt = self.parent.get_local_datetime(botengine).replace(hour=8)
            now = datetime.datetime.now(dt.tzinfo)
            if dt < now:
                dt = dt + datetime.timedelta(hours=24)
            return int(dt.strftime('%s')) * 1000

        o = ephem.Observer()
        o.lat = str(self.parent.latitude)
        o.long = str(self.parent.longitude)
        dt = ephem.localtime(o.next_rising(ephem.Sun()))
        return int(dt.strftime('%s')) * 1000

    def next_sunset_timestamp_ms(self, botengine):
        """
        :param botengine: BotEngine environment
        :return: The next sunset timestamp in ms
        """
        try:
            ephem = importlib.import_module("ephem")
        except ImportError:
            ephem = None

        if self.parent.longitude is None or self.parent.latitude is None or ephem is None:
            # We don't have any coordinate information. Call it 8 PM.
            dt = self.parent.get_local_datetime(botengine).replace(hour=20)
            now = datetime.datetime.now(dt.tzinfo)
            if dt < now:
                dt = dt + datetime.timedelta(hours=24)

            return int(dt.strftime('%s')) * 1000

        o = ephem.Observer()
        o.lat = str(self.parent.latitude)
        o.long = str(self.parent.longitude)
        dt = ephem.localtime(o.next_setting(ephem.Sun()))
        return int(dt.strftime('%s')) * 1000

    def _set_sunrise_sunset_alarm(self, botengine):
        """
        Internal method to reset the sunrise / sunset alarm
        :param botengine:
        :return:
        """
        self.cancel_timers(botengine)

        sunset_timestamp_ms = self.next_sunset_timestamp_ms(botengine)
        sunrise_timestamp_ms = self.next_sunrise_timestamp_ms(botengine)

        # We're getting double sunrise and double sunset events, and I believe it's from the ephem library not knowing that sunrise/sunset is right now.
        # So we'll check to see if the sunrise and/or sunset happened before now, and then adjust it by 24 hours.
        if sunrise_timestamp_ms - (utilities.ONE_MINUTE_MS * 5) < botengine.get_timestamp():
            sunrise_timestamp_ms += utilities.ONE_DAY_MS

        if sunset_timestamp_ms - (utilities.ONE_MINUTE_MS * 5) < botengine.get_timestamp():
            sunset_timestamp_ms += utilities.ONE_DAY_MS

        self.parent.update_location_properties(botengine, {
                'sunset_ms': sunset_timestamp_ms,
                'sunrise_ms': sunrise_timestamp_ms,
                'latitude': self.parent.latitude,
                'longitude': self.parent.longitude,
                'timezone': self.parent.get_local_timezone_string(botengine)
            })

        if sunrise_timestamp_ms < sunset_timestamp_ms:
            # Sunrise is next
            botengine.get_logger().info("Location: Setting sunrise alarm for " + str(sunrise_timestamp_ms))
            self.set_alarm(botengine, sunrise_timestamp_ms, argument=SUNRISE)
            
        else:
            # Sunset is next
            botengine.get_logger().info("Location: Setting sunset alarm for " + str(sunset_timestamp_ms))
            self.set_alarm(botengine, sunset_timestamp_ms, argument=SUNSET)

        return