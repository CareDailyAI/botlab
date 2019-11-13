'''
Created on August 2, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# Time conversions to ms
ONE_SECOND_MS = 1000
ONE_MINUTE_MS = 60 * ONE_SECOND_MS
ONE_HOUR_MS = ONE_MINUTE_MS * 60
ONE_DAY_MS = ONE_HOUR_MS * 24
ONE_WEEK_MS = ONE_DAY_MS * 7
ONE_MONTH_MS = ONE_DAY_MS * 30
ONE_YEAR_MS = ONE_DAY_MS * 365

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

# Modes to Ints
MODE_HOME_INT = 0
MODE_AWAY_INT = 1
MODE_STAY_INT = 4
MODE_TEST_INT = 5

# SMS Status
SMS_SUBSCRIBED = 1
SMS_OPT_OUT = 2

# Alarm codes
ALARM_CODE_GENERAL_BURGLARY = "E130"
ALARM_CODE_PERIMETER_WINDOW_BURGLARY = "E131"
ALARM_CODE_PERIMETER_DOOR_BURGLARY = "E134"
ALARM_CODE_LEAK = "E154"
ALARM_CODE_RECENT_CLOSING = "E459"
ALARM_CODE_DURESS = "E122"
ALARM_CODE_HIGH_TEMPERATURE = "E158"
ALARM_CODE_LOW_TEMPERATURE = "E159"
ALARM_CODE_CARBON_MONOXIDE = "E162"
ALARM_CODE_MEDICATION_DISPENCER = "E330"
ALARM_CODE_SMOKE_DETECTOR = "E111"
ALARM_CODE_MEDICAL_ALARM = "E100"
ALARM_CODE_GENERAL_MEDICAL_ALARM = "E102"
ALARM_CODE_WELLNESS_NO_DISPATCH = "E103"
ALARM_CODE_WELLNESS_DISPATCH = "E106"

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

# Official Collection Names
SECURITY_COLLECTION_NAME = "Security Settings"
CARE_COLLECTION_NAME = "Care Settings"
ENERGY_COLLECTION_NAME = "Energy Settings"
HOME_AUTOMATION_COLLECTION_NAME = "Home Automation Settings"
ECC_COLLECTION_NAME = "Emergency Call Center Settings"
DEMO_COLLECTION_NAME = "Demo Settings"


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


def celsius_to_fahrenheit(celsius):
    """
    Celsius to Fahrenheit
    :param celsius: Degrees Celsius
    :return: Fahrenheit
    """
    return float(celsius) * 9.0/5.0 + 32


def fahrenheit_to_celsius(fahrenheit):
    """
    Fahrenheit to Celsius
    :param celsius: Degrees Fahrenheit float
    :return: Fahrenheit float
    """
    return (float(fahrenheit) - 32) * 5.0/9.0


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
        adjustment_f = -(((13 - RH) / 4) * sqrt((17 - abs(T - 95.)) / 17))

    elif RH > 85 and 80 < T < 87:
        adjustment_f = ((RH - 85) / 10) * ((87 - T) / 5)

    hi_f = -42.379 + 2.04901523 * T + 10.14333127 * RH - .22475541 * T * RH - .00683783 * T * T - .05481717 * RH * RH + .00122874 * T * T * RH + .00085282 * T * RH * RH - .00000199 * T * T * RH * RH

    return fahrenheit_to_celsius(hi_f + adjustment_f)


def normalize_measurement(measure):
    """
    Transform a measurement's value, which could be a string, into a real value - like a boolean or int or float
    :param measure: a raw measurement's value
    :return: a value that has been corrected into the right type
    """
    try:
        return eval(measure, {}, {})

    except:
        if measure in ['true', 'True']:
            return True

        elif measure in ['false', 'False']:
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

    if question_object.answer_status == 4:
        return normalize_measurement(question_object.answer)
    return normalize_measurement(question_object.default_answer)

def iso_format(dt):
    """
    Returns an ISO formatted datetime that matches the format the server (Java) gives us, which is in milliseconds and not microseconds.
    :param dt: datetime to transform into an ISO formatted string
    :return: ISO formatted string
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%S." + '%03d' % (dt.microsecond / 1000) + "%z")

def getsize(obj_0):
    """
    Recursively iterate to sum size of object & members.
    https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python
    """
    import sys
    from numbers import Number
    from collections import Set, Mapping, deque

    try: # Python 2
        zero_depth_bases = (basestring, Number, xrange, bytearray)
        iteritems = 'iteritems'
    except NameError: # Python 3
        zero_depth_bases = (str, bytes, Number, range, bytearray)
        iteritems = 'items'

    _seen_ids = set()
    def inner(obj):
        obj_id = id(obj)
        if obj_id in _seen_ids:
            return 0
        _seen_ids.add(obj_id)
        size = sys.getsizeof(obj)
        if isinstance(obj, zero_depth_bases):
            pass # bypass remaining control flow and return
        elif isinstance(obj, (tuple, list, Set, deque)):
            size += sum(inner(i) for i in obj)
        elif isinstance(obj, Mapping) or hasattr(obj, iteritems):
            size += sum(inner(k) + inner(v) for k, v in getattr(obj, iteritems)())
        # Check for custom object instances - may subclass above too
        if hasattr(obj, '__dict__'):
            size += inner(vars(obj))
        if hasattr(obj, '__slots__'): # can have __slots__ with __dict__
            size += sum(inner(getattr(obj, s)) for s in obj.__slots__ if hasattr(obj, s))
        return size
    return inner(obj_0)


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


#===============================================================================
# Color Class for CLI
#===============================================================================
class Color:
    """Color your command line output text with Color.WHATEVER and Color.END"""
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
