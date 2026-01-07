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
import utilities.utilities as utilities
import signals.analytics as analytics
import signals.daylight as daylight

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

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(">__init__()")
        Intelligence.__init__(self, botengine, parent)

        if self.parent.latitude is not None and self.parent.longitude is not None:
            self._set_sunrise_sunset_alarm(botengine)

        # Initialize the 'is_daylight' class variable in the Location object.
        self.parent.is_daylight = self.is_daylight(botengine)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<__init__() intelligence_id={}".format(self.intelligence_id))

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(">initialize()")
        if not self.is_timer_running(botengine) and not botengine.is_executing_timer():
            if self.parent.latitude is not None and self.parent.longitude is not None:
                self._set_sunrise_sunset_alarm(botengine)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<initialize()")
        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">destroy()")
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<destroy()")

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
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
        :param alert_params: Alert parameters as key/value dictionary
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

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        """
        return

    def daylight_fire_sunrise(self, botengine, content):
        """
        Fire the sunrise event
        :param botengine: BotEngine environment
        :param content: Json Content
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">daylight_fire_sunrise()")

        self.parent.narrate(botengine,
                            title = _("Sunrise"),
                            description = _("It is sunrise at '{}'.").format(self.parent.get_location_name(botengine)),
                            priority = botengine.NARRATIVE_PRIORITY_DETAIL,
                            icon = 'sunrise',
                            event_type="daylight.sunrise")

        analytics.track(botengine, self.parent, 'sunrise')
        self.parent.is_daylight = True
        daylight.sunrise_fired(botengine, self.parent)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<daylight_fire_sunrise()")
    
    def daylight_fire_sunset(self, botengine, content):
        """
        Fire the sunset event
        :param botengine: BotEngine environment
        :param content: Json Content
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">daylight_fire_sunset()")

        self.parent.narrate(botengine,
                            title = _("Sunset"),
                            description = _("It is sunset at '{}'.").format(self.parent.get_location_name(botengine)),
                            priority = botengine.NARRATIVE_PRIORITY_DETAIL,
                            icon = 'sunset',
                            event_type="daylight.sunset")

        analytics.track(botengine, self.parent, 'sunset')
        self.parent.is_daylight = False
        daylight.sunset_fired(botengine, self.parent)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<daylight_fire_sunset()")

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">timer_fired() argument={}".format(argument))
        if argument == SUNRISE:
            self.daylight_fire_sunrise(botengine, {})

        elif argument == SUNSET:
            self.daylight_fire_sunset(botengine, {})

        self._set_sunrise_sunset_alarm(botengine)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<timer_fired() argument={}".format(argument))

    def coordinates_updated(self, botengine, latitude, longitude):
        """
        Approximate coordinates of the parent proxy device object have been updated
        :param latitude: Latitude
        :param longitude: Longitude
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("location_daylight_microservice: Lat/Long updated - recalculating sunrise/sunset times")
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
        try:
            ephem = importlib.import_module("ephem")
        except ImportError:
            ephem = None

        try:
            next_sunrise_ms = self.next_sunrise_timestamp_ms(botengine)
            next_sunset_ms = self.next_sunset_timestamp_ms(botengine)

        except ephem.AlwaysUpError:
            return True

        except ephem.NeverUpError:
            return False

        return next_sunset_ms < next_sunrise_ms

    def next_sunrise_timestamp_ms(self, botengine):
        """
        :param botengine: BotEngine environment
        :return: The next sunrise timestamp in ms
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">next_sunrise_timestamp_ms()")
        try:
            ephem = importlib.import_module("ephem")
        except ImportError:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|next_sunrise_timestamp_ms() ephem library not found.")
            ephem = None

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|next_sunrise_timestamp_ms() current_date={}".format(self.parent.get_local_datetime(botengine)))
        if self.parent.longitude is None or self.parent.latitude is None or ephem is None:
            # Ya, we don't have any coordinate information. Call it 8 AM.
            dt = self.parent.get_local_datetime(botengine).replace(hour=8)
            now = self.parent.get_local_datetime(botengine)
            if dt < now:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|next_sunrise_timestamp_ms() Already past sunrise. Adding 24 hours.")
                dt = dt + datetime.timedelta(hours=24)
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<next_sunrise_timestamp_ms() local_dt={}".format(dt))
            return int(dt.timestamp()) * 1000

        o = ephem.Observer()
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|next_sunrise_timestamp_ms() current_date={}".format(self.parent.get_local_datetime(botengine)))
        o.date = self.parent.get_local_datetime(botengine)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|next_sunrise_timestamp_ms() latitude={} longitude={}".format(self.parent.latitude, self.parent.longitude))
        o.lat = str(self.parent.latitude)
        o.long = str(self.parent.longitude)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|next_sunrise_timestamp_ms() next_rising={}".format(o.next_rising(ephem.Sun())))
        from zoneinfo import ZoneInfo
        zone = ZoneInfo(self.parent.get_local_timezone_string(botengine))
        local_dt = ephem.to_timezone(o.next_rising(ephem.Sun()), zone)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<next_sunrise_timestamp_ms() local_dt={}".format(local_dt))
        return int(local_dt.timestamp()) * 1000

    def next_sunset_timestamp_ms(self, botengine):
        """
        :param botengine: BotEngine environment
        :return: The next sunset timestamp in ms
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">next_sunset_timestamp_ms()")
        try:
            ephem = importlib.import_module("ephem")
        except ImportError:
            ephem = None

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|next_sunset_timestamp_ms() current_date={}".format(self.parent.get_local_datetime(botengine)))
        if self.parent.longitude is None or self.parent.latitude is None or ephem is None:
            # We don't have any coordinate information. Call it 8 PM.
            dt = self.parent.get_local_datetime(botengine).replace(hour=20)
            now = self.parent.get_local_datetime(botengine)
            if dt < now:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|next_sunset_timestamp_ms() Already past sunset. Adding 24 hours.")
                dt = dt + datetime.timedelta(hours=24)

            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<next_sunset_timestamp_ms() local_dt={}".format(dt))
            return int(dt.timestamp()) * 1000

        o = ephem.Observer()
        o.date = self.parent.get_local_datetime(botengine)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|next_sunset_timestamp_ms() current_date={}".format(self.parent.get_local_datetime(botengine)))
        o.lat = str(self.parent.latitude)
        o.long = str(self.parent.longitude)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|next_sunset_timestamp_ms() latitude={} longitude".format(self.parent.latitude, self.parent.longitude))
        from zoneinfo import ZoneInfo
        zone = ZoneInfo(self.parent.get_local_timezone_string(botengine))
        local_dt = ephem.to_timezone(o.next_setting(ephem.Sun()), zone)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<next_sunset_timestamp_ms() local_dt={}".format(local_dt))
        return int(local_dt.timestamp()) * 1000

    def _set_sunrise_sunset_alarm(self, botengine):
        """
        Internal method to reset the sunrise / sunset alarm
        :param botengine:
        :return:
        """

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_set_sunrise_sunset_alarm()")
        self.cancel_timers(botengine)

        try:
            ephem = importlib.import_module("ephem")
        except ImportError:
            # We don't have this ephem library. Avoid re-executing this code in the meantime and revisit in a future bot update.
            self.start_timer_ms(botengine, utilities.ONE_DAY_MS)
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_set_sunrise_sunset_alarm() missing ephem library")
            return

        try:
            sunset_timestamp_ms = self.next_sunset_timestamp_ms(botengine)
            sunrise_timestamp_ms = self.next_sunrise_timestamp_ms(botengine)

        except ephem.AlwaysUpError:
            # Sun never sets at this location
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("location_daylight_microservice: Sun doesn't set. Try again tomorrow.")
            self.start_timer_ms(botengine, utilities.ONE_DAY_MS)
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_set_sunrise_sunset_alarm()")
            return

        except ephem.NeverUpError:
            # Sun never rises at this location
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("location_daylight_microservice: Sun doesn't rise. Try again tomorrow.")
            self.start_timer_ms(botengine, utilities.ONE_DAY_MS)
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_set_sunrise_sunset_alarm()")
            return

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
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("Location: Setting sunrise alarm for " + str(sunrise_timestamp_ms))
            self.set_alarm(botengine, sunrise_timestamp_ms, argument=SUNRISE)
            
        else:
            # Sunset is next
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("Location: Setting sunset alarm for " + str(sunset_timestamp_ms))
            self.set_alarm(botengine, sunset_timestamp_ms, argument=SUNSET)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_set_sunrise_sunset_alarm()")
        return