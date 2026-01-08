"""
Created on August 2, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

# Time conversions to ms
ONE_SECOND_MS = 1000
ONE_MINUTE_MS = 60 * ONE_SECOND_MS
ONE_HOUR_MS = ONE_MINUTE_MS * 60
ONE_DAY_MS = ONE_HOUR_MS * 24
ONE_WEEK_MS = ONE_DAY_MS * 7
ONE_MONTH_MS = ONE_DAY_MS * 30
ONE_YEAR_MS = ONE_DAY_MS * 365

# Icon Font types
# Use http://FontAwesome.com to discover FontAwesome icons
# Use https://peoplepowerco.com/icons/ to discover People Power and Weather icons
ICON_FONT_FONTAWESOME_REGULAR = "far"
ICON_FONT_FONTAWESOME_BOLD = "fab"
ICON_FONT_FONTAWESOME_LIGHT = "fal"
ICON_FONT_FONTAWESOME_SOLID = "fas"
ICON_FONT_PEOPLEPOWER_REGULAR = "iotr"
ICON_FONT_PEOPLEPOWER_LIGHT = "iotl"
ICON_FONT_WEATHER_REGULAR = "wir"
ICON_FONT_WEATHER_LIGHT = "wil"

# Modes
MODE_HOME = "HOME"
MODE_AWAY = "AWAY"
MODE_STAY = "STAY"
MODE_TEST = "TEST"

MODE_ATTRIBUTE_SILENT = "SILENT"
MODE_ATTRIBUTE_DURESS = "DURESS"

# Occupancy status
OCCUPANCY_STATUS_PRESENT = "PRESENT"
OCCUPANCY_STATUS_ABSENT = "ABSENT"
OCCUPANCY_STATUS_H2S = "H2S"
OCCUPANCY_STATUS_SLEEP = "SLEEP"
OCCUPANCY_STATUS_S2H = "S2H"
OCCUPANCY_STATUS_H2A = "H2A"
OCCUPANCY_STATUS_A2H = "A2H"
OCCUPANCY_STATUS_VACATION = "VACATION"

# Alarm codes

# DID NOT GET THE DISPATCH SERVICE UDPATES "AG_EVENTS"

ALARM_CODE_GENERAL_BURGLARY = "E130"  # Confirmed Dispatch
ALARM_CODE_PERIMETER_WINDOW_BURGLARY = "E131"  # Confirmed Dispatch
ALARM_CODE_PERIMETER_DOOR_BURGLARY = "E134"  # Confirmed Dispatch
ALARM_CODE_BURGLARY_NO_DISPATCH = "E136"  # Non-Dispatch
ALARM_CODE_LEAK = "E154"  # Non-Dispatch
ALARM_CODE_RECENT_CLOSING = "E459"  # Logging Event Only
ALARM_CODE_DURESS = "E122"  # Confirmed Dispatch (NO CALLS)
ALARM_CODE_HIGH_TEMPERATURE = "E158"  # Non-Dispatch
ALARM_CODE_LOW_TEMPERATURE = "E159"  # Non-Dispatch
ALARM_CODE_CARBON_MONOXIDE = "E162"  # Confirmed Dispatch
ALARM_CODE_MEDICATION_DISPENCER = "E330"  # Non-Dispatch
ALARM_CODE_SMOKE_DETECTOR = "E111"  # Confirmed Dispatch
ALARM_CODE_MEDICAL_ALARM = "E100"  # Confirmed Dispatch
ALARM_CODE_GENERAL_MEDICAL_ALARM = "E102"  # Confirmed Dispatch
ALARM_CODE_WELLNESS_NO_DISPATCH = "E103"  # Non-Dispatch
ALARM_CODE_WELLNESS_DISPATCH = "E106"  # Confirmed Dispatch
ALARM_CODE_COMMS_FAILURE = "E354"  # Non-Dispatch
ALARM_CODE_PRIORITY_MEDICAL_ALARM = "E200"  # Confirmed Dispatch

# Professional Monitoring
PROFESSIONAL_MONITORING_NEVER_PURCHASED = 0
PROFESSIONAL_MONITORING_PURCHASED_BUT_NOT_ENOUGH_INFO = 1
PROFESSIONAL_MONITORING_REGISTRATION_PENDING = 2
PROFESSIONAL_MONITORING_REGISTERED = 3
PROFESSIONAL_MONITORING_CANCELLATION_PENDING = 4
PROFESSIONAL_MONITORING_CANCELLED = 5

# Professional monitoring alert status
PROFESSIONAL_MONITORING_ALERT_STATUS_QUIET = 0
PROFESSIONAL_MONITORING_ALERT_STATUS_RAISED = 1
PROFESSIONAL_MONITORING_ALERT_STATUS_CANCELLED = 2
PROFESSIONAL_MONITORING_ALERT_STATUS_REPORTED = 3

# Push notification sound library
PUSH_SOUND_ALARM = "alarm.wav"
PUSH_SOUND_BEEP = "beep.wav"
PUSH_SOUND_BELL = "bell.wav"
PUSH_SOUND_BIRD = "bird.wav"
PUSH_SOUND_BLING = "bling.wav"
PUSH_SOUND_CAMERA = "camera_shutter.wav"
PUSH_SOUND_CLICK = "click.wav"
PUSH_SOUND_DOG = "dog.wav"
PUSH_SOUND_DROID = "droid.wav"
PUSH_SOUND_ENTRY_DELAY = "entry_delay.wav"
PUSH_SOUND_FULLY_ARMED = "fullyarmed.wav"
PUSH_SOUND_GUN_COCK = "guncock.wav"
PUSH_SOUND_GUN_SHOT = "gunshot.wav"
PUSH_SOUND_LOCK = "lock.wav"
PUSH_SOUND_PHASER = "phaser.wav"
PUSH_SOUND_PONG = "pong.wav"
PUSH_SOUND_SILENCE = "silence.wav"
PUSH_SOUND_TOGGLE = "toggle.wav"
PUSH_SOUND_TRUMPET = "trumpet.wav"
PUSH_SOUND_WARNING = "warning.wav"
PUSH_SOUND_WHISTLE = "whistle.wav"
PUSH_SOUND_WHOOPS = "whoops.wav"

# Organization User Notification Categories
ORGANIZATION_USER_NOTIFICATION_CATEGORY_MANAGER = 1
ORGANIZATION_USER_NOTIFICATION_CATEGORY_TECHNICIAN = 2
ORGANIZATION_USER_NOTIFICATION_CATEGORY_BILLING = 3
ORGANIZATION_USER_NOTIFICATION_CATEGORY_RESEARCHER = 4
ORGANIZATION_USER_NOTIFICATION_CATEGORY_PROVIDER = 5
ORGANIZATION_USER_NOTIFICATION_CATEGORY_RESPONDER = 6

# Default name for AI Chat Assistant (common for all locales)
DEFAULT_CHAT_ASSISTANT_NAME = "Arti"


def can_contact_customer_support(botengine):
    """
    Leverages the com.domain.YourBot/domain.py file or organization properties to determine if customer support is available for this bot
    :return:
    """
    import importlib

    try:
        properties = importlib.import_module("properties")
    except ImportError:
        return False

    if properties.get_property(botengine, "CS_SCHEDULE_URL", False) is not None:
        if len(properties.get_property(botengine, "CS_SCHEDULE_URL", False)) > 0:
            return True

    if properties.get_property(botengine, "CS_EMAIL_ADDRESS", False) is not None:
        if len(properties.get_property(botengine, "CS_EMAIL_ADDRESS", False)) > 0:
            return True

    if properties.get_property(botengine, "CS_PHONE_NUMBER", False) is not None:
        if len(properties.get_property(botengine, "CS_PHONE_NUMBER", False)) > 0:
            return True


def alarm_code_to_description(code):
    """
    'The Moss family {action/incident}'
    """
    if ALARM_CODE_GENERAL_BURGLARY in code:
        # NOTE: "The Moss family <burglary alarm tripped>."
        return _("has a burglar alarm")

    elif ALARM_CODE_PERIMETER_WINDOW_BURGLARY in code:
        # NOTE: "The Moss family <burglary alarm tripped because a window opened>."
        return _("has a burglar alarm because a window opened")

    elif ALARM_CODE_PERIMETER_DOOR_BURGLARY in code:
        # NOTE: "The Moss family <burglary alarm tripped because a door opened>."
        return _("has a burglar alarm because a door opened")

    elif ALARM_CODE_LEAK in code:
        # NOTE: "The Moss family <is experiencing a water leak>."
        return _("is experiencing a water leak")

    elif ALARM_CODE_RECENT_CLOSING in code:
        # NOTE: "The Moss family <burglary alarm tripped shortly after arming>."
        return _("has a burglar alarm, shortly after arming")

    elif ALARM_CODE_DURESS in code:
        # NOTE: "The Moss family <typed a Duress code into the Touchpad>."
        return _("entered a duress code, indicating a potential threat.")

    else:
        # NOTE: "The Moss family <may need some assistance>." - generic message
        return _("may need some assistance")


def good_enough_unique_id():
    """
    Return a UUID4 unique ID that is "good enough"
    "e363f4f3-8ea1-4a01-a480-b12d560a84f5" => "b12d560a84f5"
    :return: String pseudo-unique ID
    """
    import uuid

    return str(uuid.uuid4()).split("-")[-1]


def float_round(number, count=1):
    if isinstance(number, float):
        return round(number, count)
    else:
        return round(float(number), count)


def celsius_to_fahrenheit(celsius):
    """
    Celsius to Fahrenheit
    :param celsius: Degrees Celsius
    :return: Fahrenheit
    """
    return float(celsius) * 9.0 / 5.0 + 32


def fahrenheit_to_celsius(fahrenheit):
    """
    Fahrenheit to Celsius
    :param celsius: Degrees Fahrenheit float
    :return: Fahrenheit float
    """
    return (float(fahrenheit) - 32) * 5.0 / 9.0


def relative_f_to_c_degree(fahrenheit_degree):
    """
    Convert relative degrees Fahrenheit to Celsius
    For example, if I want to increase the thermostat 3 degrees F, then I need to adjust it 1.66668 degrees C.
    :param fahrenheit_degree: relative number of degrees F
    :return: relative number of degrees C
    """
    return float(fahrenheit_degree) * 0.555556


def calculate_heat_index(degrees_c, humidity):
    """
    Get the heat index in Celsius using a Rothfusz regression.
    This is generally valid for a heat index above 80F
    https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
    :param degrees_c: Degrees C
    :param humidity: Humidity
    :return: Heat index in degrees C
    """
    from math import sqrt

    T = celsius_to_fahrenheit(degrees_c)
    RH = humidity

    adjustment_f = 0

    if RH < 13 and 80 < T < 112:
        adjustment_f = -(((13 - RH) / 4) * sqrt((17 - abs(T - 95.0)) / 17))

    elif RH > 85 and 80 < T < 87:
        adjustment_f = ((RH - 85) / 10) * ((87 - T) / 5)

    hi_f = (
        -42.379
        + 2.04901523 * T
        + 10.14333127 * RH
        - 0.22475541 * T * RH
        - 0.00683783 * T * T
        - 0.05481717 * RH * RH
        + 0.00122874 * T * T * RH
        + 0.00085282 * T * RH * RH
        - 0.00000199 * T * T * RH * RH
    )

    return fahrenheit_to_celsius(hi_f + adjustment_f)


def temperature_to_human_readable_string(temperature_c):
    """
    Convert the given temperature to a huamn-readable string
    :param temperature_c: Temperature in Celsius
    :return: String that describes the temperature in both Celsius and fahrenheit as a string.
    """
    return "{}°F / {}°C".format(
        str("%.1f" % float(celsius_to_fahrenheit(temperature_c))),
        str("%.1f" % float(temperature_c)),
    )


def ms_to_human_readable_string(ms, include_seconds=False):
    """
    Transform milliseconds to human-readable minutes and seconds string
    :param ms: Milliseconds
    :param include_seconds: True to specify seconds granularity (default False)
    :return: String "1 hour 30 minutes 26 seconds"
    """
    import time

    ts = time.gmtime(ms / 1000)
    hour = ts.tm_hour
    min = ts.tm_min
    sec = ts.tm_sec

    str = ""
    if hour == 1:
        str += _("1 hour")
    elif hour > 1:
        str += _("{} hours").format(hour)

    if min == 1:
        str += " " + _("1 minute")
    elif min > 1:
        str += " " + _("{} minutes").format(min)

    if include_seconds or (hour == 0 and min == 0):
        if sec == 1:
            str += " " + _("1 second")
        elif sec > 1:
            str += " " + _("{} seconds").format(sec)

        elif hour == 0 and min == 0:
            str += " " + _("0 seconds")

    return str.strip()


def normalize_measurement(measure):
    """
    Transform a measurement's value, which could be a string, into a real value - like a boolean or int or float
    :param measure: a raw measurement's value
    :return: a value that has been corrected into the right type
    """
    try:
        return eval(measure, {}, {})

    except Exception:
        if measure in ["true", "True"]:
            return True

        elif measure in ["false", "False"]:
            return False

        else:
            return measure


def get_answer(question_object):
    """
    Easily extract an answer from a question object and normalize it.
    If the question hasn't been answered by the user, then this will return the default answer.

    :param question_object: Question object to extract a normalized answer for
    :return: Normalized answer
    """
    # ANSWER_STATUS_ANSWERED = 4
    if question_object is None:
        return None

    if question_object.answer_status == 4 and question_object.answer is not None:
        return normalize_measurement(question_object.answer)
    return normalize_measurement(question_object.default_answer)


def human_readable_format(dt):
    """
    Returns an ISO formatted datetime that matches the format the server (Java) gives us, which is in milliseconds and not microseconds.
    :param dt: datetime to transform into an ISO formatted string
    :return: ISO formatted string
    """
    return strftime(dt, "%Y-%m-%d %H:%M:%S")


def strftime(dt, strftime_string):
    """
    Cross-platform strftime()
    https://docs.python.org/3.9/library/datetime.html#strftime-strptime-behavior
    The ability to remove the leading 0 from an strftime() string is different between Linux/Unix and Windows.
    In an effort to become more cross-platform accessible, we need to transform the '-' character which
    removes leading 0's into a '#' character for Windows. Underneath Python, it's using the OS's native strftime()
    which is why we need to implement a better abstraction layer ourselves.
    :param dt: Datetime to transform into the given strftime string format
    :param strftime_string: strftime() string
    :return: Cross-platform corrected strftime() string
    """
    try:
        return dt.strftime(strftime_string.replace("%#", "%-"))
    except ValueError:
        return dt.strftime(strftime_string.replace("%-", "%#"))


def iso_format(dt):
    """
    Returns an ISO formatted datetime that matches the format the server (Java) gives us, which is in milliseconds and not microseconds.
    :param dt: datetime to transform into an ISO formatted string
    :return: ISO formatted string
    """
    return strftime(dt, "%Y-%m-%dT%H:%M:%S." + "%03d" % (dt.microsecond / 1000) + "%z")


def override_timestamp(botengine, location_object):
    """
    Return the override timestamp.(10 mins before the midnight.)
    :param botengine:
    :param location_object
    :return:
    """
    current_timestamp = botengine.get_timestamp()
    today_dt = location_object.get_local_datetime_from_timestamp(
        botengine, botengine.get_timestamp()
    ).replace(hour=0, minute=0, second=0, microsecond=0)
    todays_timestamp = location_object.timezone_aware_datetime_to_unix_timestamp(
        botengine, today_dt
    )
    if current_timestamp - todays_timestamp < ONE_MINUTE_MS * 10:
        timestamp_override_ms = current_timestamp - ONE_MINUTE_MS * 10
    else:
        timestamp_override_ms = None

    return timestamp_override_ms


def cumulative_moving_average(new_value, previous_average, previous_count):
    """
    Calculate a Cumulative Moving Average (running average). Use this when you want to calculate an average value
    without storing each data point.

    :param new_value: New value
    :param previous_average: Previous average
    :param previous_count: Previous total count of the times this function has been executed up until now.
    :return: New average
    """
    return previous_average + (new_value - previous_average) / (previous_count + 1)


def zscore(x, avg, stdev):
    """
    Calculate the standard z-score, which measures how many standard deviations a data point is from the mean.

    The z-score normalizes data points based on their distance from the mean, scaled by standard deviation.
    A z-score of 0 means the data point equals the mean, while a z-score of 1 means it's one standard
    deviation above the mean.

    Args:
        x: The data point to calculate the z-score for
        avg: The mean (average) of the dataset
        stdev: The standard deviation of the dataset

    Returns:
        float: The z-score. Returns 0 if standard deviation is 0 to avoid division by zero.
    """
    if stdev == 0:
        return 0

    return (x - avg) / stdev


def modify_zscore(x, values, k=1.4826):
    """
    Calculate the modified z-score using median absolute deviation (MAD), which is more robust to outliers
    than the standard z-score.

    The modified z-score uses the median instead of mean and MAD instead of standard deviation. This makes
    it less sensitive to extreme values while still effectively identifying unusual data points. The scaling
    factor k=1.4826 makes the MAD scale comparable to standard deviation for normal distributions.

    Args:
        x: The data point to calculate the modified z-score for
        values: Array of values from the dataset
        k: Scaling constant (default 1.4826) to make MAD comparable to standard deviation

    Returns:
        float: The modified z-score. Returns 0 if MAD is 0 to avoid division by zero.
    """
    from statistics import median

    data_median = median(values)
    dev_from_med = []
    for data in values:
        # print(
        #     f"data: {data}, data_median: {data_median}, abs(data - data_median): {abs(data - data_median)}"
        # )
        dev_from_med.append(abs(data - data_median))

    mad = median(dev_from_med)
    if mad == 0:
        return 0

    return (x - data_median) / (k * mad)


def get_chat_assistant_name(botengine):
    """
    Return the name of the chat assistant.
    This can be overridden by setting the bot bundle domain property "CHAT_ASSISTANT_NAME".

    :param botengine: BotEngine environment
    :return: Name of the chat assistant.
    """
    import properties

    name = properties.get_property(
        botengine, "CHAT_ASSISTANT_NAME", complain_if_missing=False
    )
    if name is None:
        name = DEFAULT_CHAT_ASSISTANT_NAME
    return name


def get_admin_url(botengine):
    """
    Attempt to return the URL of the command center.

    To make this work, you'll need a file in the base of the bot called 'domain.py' containing configuration settings,
    or set the properties in your organization.

    It should have a property like this:

        # Command Center URLs
        COMMAND_CENTER_URLS = {
            "app.peoplepowerco.com": "https://console.peoplepowerfamily.com",
            "sboxall.peoplepowerco.com": "https://maestro-sbox.peoplepowerco.com"
            or
            "app.peoplepowerco.com": "https://app.caredaily.ai",
            "sboxall.peoplepowerco.com": "https://app-sbox.caredaily.ai"
        }

    :return: URL to this home in the appropriate command center
    """
    # The domain.COMMAND_CENTER_URLS (or your organization property) should be formatted like this: https://console.peoplepowerfamily.com
    import bundle
    import properties

    url = "https://app.caredaily.ai"
    if properties.get_property(botengine, "COMMAND_CENTER_URLS") is not None:
        for u in properties.get_property(botengine, "COMMAND_CENTER_URLS"):
            if u in bundle.CLOUD_ADDRESS:
                url = properties.get_property(botengine, "COMMAND_CENTER_URLS")[u]

    return url


def get_admin_url_for_location(botengine):
    """
    Attempt to return the URL of the command center for this home.

    To make this work, you'll need a file in the base of the bot called 'domain.py' containing configuration settings,
    or set the properties in your organization.

    It should have a property like this:

        # Command Center URLs
        COMMAND_CENTER_URLS = {
            "app.peoplepowerco.com": "https://console.peoplepowerfamily.com",
            "sboxall.peoplepowerco.com": "https://maestro-sbox.peoplepowerco.com"
            or
            "app.peoplepowerco.com": "https://app.caredaily.ai",
            "sboxall.peoplepowerco.com": "https://app-sbox.caredaily.ai"
        }

    :return: URL to this home in the appropriate command center
    """
    # The domain.COMMAND_CENTER_URLS (or your organization property) should be formatted like this: https://console.peoplepowerfamily.com
    import bundle
    import properties

    url = None
    if properties.get_property(botengine, "COMMAND_CENTER_URLS") is not None:
        for u in properties.get_property(botengine, "COMMAND_CENTER_URLS"):
            if u in bundle.CLOUD_ADDRESS:
                url = properties.get_property(botengine, "COMMAND_CENTER_URLS")[u]

    if url is None:
        botengine.get_logger(f"{__name__}").warning(
            "utilities.get_admin_url_for_location(): No COMMAND_CENTER_URLS defined in domain.py for address {}".format(
                bundle.CLOUD_ADDRESS
            )
        )
        return ""

    # Check if the url contains caredaily
    if any([domain in url for domain in ["console", "maestro"]]):
        # Return the url for Maestro
        return "{}/#!/main/locations/edit/{}".format(url, botengine.get_location_id())

    # Return the url for CareDailyInsights
    return "{}/org/{}/locations/{}/dashboard".format(
        url, botengine.get_organization_id(), botengine.get_location_id()
    )


def get_organization_user_notification_categories(
    botengine, location, excluded_categories=[], notify_responders=False
):
    """
    Return a list of Organization User Notification categories for this location
    :param botengine: BotEngine environment
    :param location: Location object
    :param excluded_categories: List of categories to exclude
    :return: List of categories
    """
    import properties

    # [1.0] Disable notifications for all categories
    if (
        properties.get_property(
            botengine, "ALLOW_ADMINISTRATIVE_MONITORING", complain_if_missing=False
        )
        is not None
    ):
        if not properties.get_property(
            botengine, "ALLOW_ADMINISTRATIVE_MONITORING", complain_if_missing=False
        ):
            botengine.get_logger(f"{__name__}").info("utilities: Do not contact admins")
            return []

    # [1.1] Limit the time of day for Technicians
    before_hour = properties.get_property(
        botengine,
        "DO_NOT_CONTACT_ADMINS_BEFORE_RELATIVE_HOUR",
        complain_if_missing=False,
    )
    after_hour = properties.get_property(
        botengine,
        "DO_NOT_CONTACT_ADMINS_AFTER_RELATIVE_HOUR",
        complain_if_missing=False,
    )
    timezone = location.get_local_timezone_string(botengine)
    if (
        properties.get_property(
            botengine, "ADMIN_DEFAULT_TIMEZONE", complain_if_missing=False
        )
        is not None
    ):
        timezone = properties.get_property(
            botengine, "ADMIN_DEFAULT_TIMEZONE", complain_if_missing=False
        )

    categories = [ORGANIZATION_USER_NOTIFICATION_CATEGORY_MANAGER]
    if before_hour is not None and after_hour is not None:
        botengine.get_logger(f"{__name__}").info(
            "utilities: Check if we should contact technicians: {} <= {} <= {}".format(
                before_hour,
                location.get_relative_time_of_day(botengine, timezone=timezone),
                after_hour,
            )
        )
        if (
            before_hour
            <= location.get_relative_time_of_day(botengine, timezone=timezone)
            <= after_hour
        ):
            categories.append(ORGANIZATION_USER_NOTIFICATION_CATEGORY_TECHNICIAN)
        else:
            botengine.get_logger(f"{__name__}").info(
                "utilities: Do not contact technicians because it's after hours"
            )

    # [1.2] Notify Responders
    if notify_responders:
        if (
            properties.get_property(
                botengine,
                "ALLOW_ADMINISTRATIVE_RESPONDERS_MONITORING",
                complain_if_missing=False,
            )
            is not None
        ):
            if properties.get_property(
                botengine,
                "ALLOW_ADMINISTRATIVE_RESPONDERS_MONITORING",
                complain_if_missing=False,
            ):
                botengine.get_logger(f"{__name__}").info(
                    "utilities: Contacting responders"
                )
                categories.append(ORGANIZATION_USER_NOTIFICATION_CATEGORY_RESPONDER)

    # Excluded categories
    categories = [c for c in categories if c not in excluded_categories]
    return categories


def is_core_bot(botengine, is_core_dependent=False):
    """
    Return True if this bot is a core or core-dependent bot as described by the marketing.json file.
    :param botengine: BotEngine environment
    :param is_core_dependent: True if check for core-dependent
    :return: True if core or core-dependent
    """
    import json
    import os
    from pathlib import Path

    core_bot = 0
    try:
        with open(
            os.path.join(
                Path(os.path.abspath(os.path.dirname(__file__))).parent,
                "marketing.json",
            )
        ) as f:
            j = json.load(f)
            core_bot = j.get("app", {}).get("core", core_bot)
    except Exception:
        botengine.get_logger().warn(
            "utilities.is_core_bot(): Unable to read marketing.json file"
        )

    if is_core_dependent:
        return core_bot == -1
    return core_bot == 1


def get_dashboard_status_expiration_time(botengine, location_object):
    """
    Return the dashboard status expiration local time (17 pm default)
    :param botengine:
    :param location_object
    :return:

    To make this work, you'll need a file in the base of the bot called 'domain.py' containing configuration settings,
    or set the properties in your organization.

    It should have a property like this:

        # Command Center URLs
        DASHBOARD_STATUS_EXPIRATION_HH_MM_SS_MS = "12:00:00:00"
    """
    botengine.get_logger(f"{__name__}").debug(">get_dashboard_status_expiration_time()")
    import properties

    time_string = properties.get_property(
        botengine, "DASHBOARD_STATUS_EXPIRATION_HH_MM_SS_MS", complain_if_missing=False
    )
    if time_string is None:
        expiration_time = location_object.get_local_datetime(botengine).replace(
            hour=19, minute=0, second=0, microsecond=0
        )
    else:
        hours, minutes, seconds, microseconds = map(int, time_string.split(":"))
        expiration_time = location_object.get_local_datetime(botengine).replace(
            hour=hours, minute=minutes, second=seconds, microsecond=microseconds
        )

    if expiration_time < location_object.get_local_datetime(botengine):
        from datetime import timedelta

        expiration_time += timedelta(days=1)

    botengine.get_logger(f"{__name__}").debug(
        "<get_dashboard_status_expiration_time() expiration_time={}".format(
            expiration_time
        )
    )
    return expiration_time


def getsize(obj_0):
    """
    Recursively iterate to sum size of object & members.
    https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python
    """
    import sys
    from collections import deque
    from numbers import Number

    try:
        from collections.abc import Mapping

        zero_depth_bases = (str, bytes, Number, range, bytearray)
        iteritems = "items"
    except ImportError:  # Python 2
        from collections import Mapping

        zero_depth_bases = (basestring, Number, xrange, bytearray)  # noqa: F821
        iteritems = "iteritems"

    _seen_ids = set()

    def inner(obj):
        obj_id = id(obj)
        if obj_id in _seen_ids:
            return 0
        _seen_ids.add(obj_id)
        size = sys.getsizeof(obj)
        if isinstance(obj, zero_depth_bases):
            pass  # bypass remaining control flow and return
        elif isinstance(obj, (tuple, list, set, deque)):
            size += sum(inner(i) for i in obj)
        elif isinstance(obj, Mapping) or hasattr(obj, iteritems):
            size += sum(inner(k) + inner(v) for k, v in getattr(obj, iteritems)())
        # Check for custom object instances - may subclass above too
        if hasattr(obj, "__dict__"):
            size += inner(vars(obj))
        if hasattr(obj, "__slots__"):  # can have __slots__ with __dict__
            size += sum(
                inner(getattr(obj, s)) for s in obj.__slots__ if hasattr(obj, s)
            )
        return size

    return inner(obj_0)


def _isinstance(object, classinfo):
    """
    Check if an object is an instance of a class or a subclass of a class using
    built-in isinstance().

    Supports fallback to checking module comparisons to ensure compatibility with
    consecutive executions of the same lifecycle across various Python runtimes.
    """
    # __isinstance = isinstance(object, classinfo)
    # if __isinstance:
    #     return True
    # if not hasattr(object, "__module__") or not hasattr(classinfo, "__module__"):
    #     return False
    # return object.__module__ == classinfo.__module__ or object.__module__ in [
    #     subclass.__module__
    #     for subclass in classinfo.__subclasses__()
    #     if hasattr(subclass, "__module__")
    # ]

    # print(f">_isinstance() called with object={object}, classinfo={classinfo}")
    # print(f"|_isinstance() Object type: {type(object)}, Classinfo type: {type(classinfo)}")
    __isinstance = isinstance(object, classinfo)
    if __isinstance:
        # print(f"<_isinstance()={__isinstance}>")
        return True
    __classinfo = classinfo if isinstance(classinfo, tuple) else (classinfo,)
    for _classinfo in __classinfo:
        if not hasattr(object, "__module__") or not hasattr(_classinfo, "__module__"):
            # print(f"<_isinstance()={__isinstance}>")
            return False
        # print(f"_isinstance() Object module: {object.__module__ if hasattr(object, '__module__') else 'N/A'}")
        # print(f"_isinstance() Classinfo module: {_classinfo.__module__ if hasattr(_classinfo, '__module__') else 'N/A'}")
        # print(f"_isinstance() Classinfo subclasses: {[subclass.__module__ for subclass in _classinfo.__subclasses__()]}")
        # print(f"_isinstance() isinstance(object, classinfo): {isinstance(object, _classinfo)}")
        # print(f"_isinstance() object.__module__ == classinfo.__module__: {object.__module__ == _classinfo.__module__}")
        # print(f"_isinstance() object.__module__ in [subclass.__module__ for subclass in classinfo.__subclasses__()]: {object.__module__ in [subclass.__module__ for subclass in _classinfo.__subclasses__() if hasattr(subclass, '__module__')]}")
        __isinstance = (
            object.__module__ == _classinfo.__module__
            or object.__module__ in [subclass.__module__ for subclass in _classinfo.__subclasses__() if hasattr(subclass, "__module__")]
        )
        if __isinstance:
            # print(f"<_isinstance()={__isinstance}>")
            return True
    # print(f"<_isinstance()={__isinstance}>")
    return __isinstance


class MachineLearningError(Exception):
    """
    Machine learning exception class
    """

    def __init__(self, message):
        """
        Constructor
        :param message: Message that describes what happened, for logging
        """
        self.message = message


def pause_playback(botengine, seconds=1):
    """
    Pause playback helper function to avoid mistakes.
    :param botengine:
    :param seconds:
    :return:
    """
    if botengine.playback:
        import time

        time.sleep(seconds)


# ===============================================================================
# Color Class for CLI
# ===============================================================================
class Color:
    """
    Color your command line output text with Color.WHATEVER and Color.END
    This is maintained for backwards compatibility with our original Color class.
    """

    # Cross-platform color compatibility. Please see notes at:
    # https://github.com/tartley/colorama
    from colorama import Fore, reinit, Style

    # reinit() runs faster vs. init().
    # Color only matters when running locally, so we init() colorama in the main() method.
    reinit()

    PURPLE = Fore.MAGENTA
    CYAN = Fore.CYAN
    BLUE = Fore.BLUE
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    BOLD = Style.BRIGHT
    END = Style.RESET_ALL


def intify_tstmp(tstmp):
    """
    Convert a timestamp to millisecond ints for efficient interval calculation.
    Handles both ISO format timestamps and Unix timestamps in milliseconds.
    
    :param tstmp: timestamp string (ISO format like '2023-01-01T12:00:00.000' or Unix timestamp like '1680002949610')
    :return: millisecond timestamp as int
    """
    from datetime import datetime
    import calendar
    
    try:
        # Try to parse as ISO format timestamp
        tmp = datetime.strptime(tstmp[0:19], '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        # Handle case where timestamp is already a Unix timestamp in milliseconds
        # Convert from unix time in ms to datetime
        dt = datetime.utcfromtimestamp(int(int(tstmp[0:19]) / 1000))
        dt_2 = datetime.isoformat(dt)
        tmp = datetime.strptime(dt_2, '%Y-%m-%dT%H:%M:%S')
    
    val = 0
    if len(tstmp) > 20:
        val = int(tstmp[20:23])
    
    # Use calendar.timegm to avoid overflow issues with large timestamps
    return int(calendar.timegm(tmp.timetuple()) * 1000) + val


def distance_between_points(latitude_1, longitude_1, latitude_2, longitude_2):
    """
    Calculate the distance between two points on the earth.
    :param latitude_1: Latitude of the first point
    :param longitude_1: Longitude of the first point
    :param latitude_2: Latitude of the second point
    :param longitude_2: Longitude of the second point
    :return: Distance in meters
    """
    from math import atan2, cos, radians, sin, sqrt

    # Approximate radius of earth in km
    R = 6373.0

    # Convert to radians
    lat1 = radians(float(latitude_1))
    lon1 = radians(float(longitude_1))
    lat2 = radians(float(latitude_2))
    lon2 = radians(float(longitude_2))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    # distance rounded down to the nearest meter
    return int(distance * 1000)
