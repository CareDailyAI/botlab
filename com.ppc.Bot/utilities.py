'''
Created on August 2, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# Time conversions to ms
ONE_MINUTE_MS = 60000
ONE_HOUR_MS = ONE_MINUTE_MS * 60
ONE_DAY_MS = ONE_HOUR_MS * 24
ONE_WEEK_MS = ONE_DAY_MS * 7
ONE_MONTH_MS = ONE_DAY_MS * 30

# Modes
MODE_HOME = "HOME"
MODE_AWAY = "AWAY"
MODE_STAY = "STAY"
MODE_TEST = "TEST"
MODE_SLEEP = "SLEEP"
MODE_VACATION = "VACATION"

MODE_ATTRIBUTE_SILENT = "SILENT"
MODE_ATTRIBUTE_DURESS = "DURESS"

# Modes to Ints
MODE_HOME_INT = 0
MODE_AWAY_INT = 1
MODE_VACATION_INT = 2
MODE_SLEEP_INT = 3
MODE_STAY_INT = 4
MODE_TEST_INT = 5
MODE_SILENT_INT = 6

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

def alarm_code_to_description(code):
    """
    'The Moss family {action/incident}'
    """
    if ALARM_CODE_GENERAL_BURGLARY in code:
        # NOTE: "The Moss family <burglary alarm tripped>."
        return _("burglar alarm tripped")
    
    elif ALARM_CODE_PERIMETER_WINDOW_BURGLARY in code:
        # NOTE: "The Moss family <burglary alarm tripped because a window opened>."
        return _("burglar alarm tripped because a window opened")
    
    elif ALARM_CODE_PERIMETER_DOOR_BURGLARY in code:
        # NOTE: "The Moss family <burglary alarm tripped because a door opened>."
        return _("burglar alarm tripped because a door opened")
    
    elif ALARM_CODE_LEAK in code:
        # NOTE: "The Moss family <is experiencing a water leak>."
        return _("is experiencing a water leak")
    
    elif ALARM_CODE_RECENT_CLOSING in code:
        # NOTE: "The Moss family <burglary alarm tripped shortly after arming>."
        return _("burglar alarm tripped shortly after arming")
    
    elif ALARM_CODE_DURESS in code:
        # NOTE: "The Moss family <typed a Duress code into the Touchpad>."
        return _("entered a duress code, indicating a potential threat.")
    
    else:
        # NOTE: "The Moss family <may need some assistance>." - generic message
        return _("may need some assistance")
    

def mode_to_int(mode):
    """
    HOME => 0
    AWAY => 1
    VACATION => 2
    SLEEP => 3
    TEST => 4
    STAY = 5
    :param mode: String version of the mode
    :return: Int version of the mode
    """
    if MODE_HOME in mode:
        return MODE_HOME_INT
    
    elif MODE_AWAY in mode:
        return MODE_AWAY_INT
    
    elif MODE_STAY in mode:
        return MODE_STAY_INT
    
    elif MODE_TEST in mode:
        return MODE_TEST_INT
    
    elif MODE_VACATION in mode:
        return MODE_VACATION_INT
    
    elif MODE_SLEEP in mode:
        return MODE_SLEEP_INT
    
    return -1


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

