"""
Created on May 8, 2021

CONTEXT MANAGEMENT ONLY

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

import signals.radar as radar

# Subregion Contexts
SUBREGION_CONTEXT_IGNORE = radar.SUBREGION_CONTEXT_IGNORE

# Bedroom
SUBREGION_CONTEXT_BED = radar.SUBREGION_CONTEXT_BED
SUBREGION_CONTEXT_BED_KING = radar.SUBREGION_CONTEXT_BED_KING
SUBREGION_CONTEXT_BED_CALKING = radar.SUBREGION_CONTEXT_BED_CALKING
SUBREGION_CONTEXT_BED_QUEEN = radar.SUBREGION_CONTEXT_BED_QUEEN
SUBREGION_CONTEXT_BED_FULL = radar.SUBREGION_CONTEXT_BED_FULL
SUBREGION_CONTEXT_BED_TWINXL = radar.SUBREGION_CONTEXT_BED_TWINXL
SUBREGION_CONTEXT_BED_TWIN = radar.SUBREGION_CONTEXT_BED_TWIN
SUBREGION_CONTEXT_BED_CRIB = radar.SUBREGION_CONTEXT_BED_CRIB
SUBREGION_CONTEXT_END_TABLE = radar.SUBREGION_CONTEXT_END_TABLE
SUBREGION_CONTEXT_CPAP = radar.SUBREGION_CONTEXT_CPAP

# Bathroom
SUBREGION_CONTEXT_BATHROOM = radar.SUBREGION_CONTEXT_BATHROOM
SUBREGION_CONTEXT_TOILET = radar.SUBREGION_CONTEXT_TOILET
SUBREGION_CONTEXT_BATHTUB = radar.SUBREGION_CONTEXT_BATHTUB
SUBREGION_CONTEXT_WALK_IN_SHOWER = radar.SUBREGION_CONTEXT_WALK_IN_SHOWER
SUBREGION_CONTEXT_SINK = radar.SUBREGION_CONTEXT_SINK
SUBREGION_CONTEXT_TOILET_TANK = radar.SUBREGION_CONTEXT_TOILET_TANK

# Living Room and other
SUBREGION_CONTEXT_CHAIR = radar.SUBREGION_CONTEXT_CHAIR
SUBREGION_CONTEXT_COUCH = radar.SUBREGION_CONTEXT_COUCH
SUBREGION_CONTEXT_TABLE = radar.SUBREGION_CONTEXT_TABLE

SUBREGION_CONTEXT_OTHER = radar.SUBREGION_CONTEXT_OTHER
SUBREGION_CONTEXT_EXIT = radar.SUBREGION_CONTEXT_EXIT

# fall_sensitivity
FALL_SENSITIVITY_NO_FALLING = radar.FALL_SENSITIVITY_NO_FALLING
FALL_SENSITIVITY_LOW = radar.FALL_SENSITIVITY_LOW
FALL_SENSITIVITY_NORMAL = radar.FALL_SENSITIVITY_NORMAL

# led_mode
LED_MODE_OFF = radar.LED_MODE_OFF
LED_MODE_ON = radar.LED_MODE_ON

# Volume
VOLUME_ON = radar.VOLUME_ON
VOLUME_OFF = radar.VOLUME_OFF

# telementry_policy
TELEMETRY_POLICY_OFF = 0
TELEMETRY_POLICY_ON = 1
TELEMETRY_POLICY_FALLS_ONLY = 2
TELEMETRY_POLICY_PRESENCE_ONLY = 3

# Feedback classification
FEEDBACK_CLASSIFICATION_TRUE_POSITIVE = radar.FEEDBACK_CLASSIFICATION_TRUE_POSITIVE
FEEDBACK_CLASSIFICATION_FALSE_POSITIVE = radar.FEEDBACK_CLASSIFICATION_FALSE_POSITIVE
FEEDBACK_CLASSIFICATION_FALSE_NEGATIVE = radar.FEEDBACK_CLASSIFICATION_FALSE_NEGATIVE
FEEDBACK_CLASSIFICATION_TEST_FALL = radar.FEEDBACK_CLASSIFICATION_TEST_FALL

# Dry Contacts
DRY_CONTACT_PRIMARY_KEY = "primary"
DRY_CONTACT_SECONDARY_KEY = "secondary"

DRY_CONTACT_MODE_ACTIVE_LOW = 0
DRY_CONTACT_MODE_ACTIVE_HIGH = 1

DRY_CONTACT_POLICY_OFF = 0
DRY_CONTACT_POLICY_ON_FALL = 1
DRY_CONTACT_POLICY_OUT_OF_BED = 2
DRY_CONTACT_POLICY_ON_SENSITIVE_FALL = 3
DRY_CONTACT_POLICY_ON_ANY_FALL = 4

# Default occupancy target reporting rate in milliseconds
DEFAULT_REPORTING_RATE_MS = 5500

# Default enter duration
DEFAULT_ENTER_DURATION = radar.DEFAULT_ENTER_DURATION

# Default exit duration
DEFAULT_EXIT_DURATION = radar.DEFAULT_EXIT_DURATION

# Fall location target ID
TARGET_ID_FALL_LOC = radar.TARGET_ID_FALL_LOC


def context_to_name(context_id):
    """
    Convert a context_id to a descriptive name
    :param context_id: Context ID
    :return: Descriptive name
    """
    return radar.context_to_name(context_id)


def context_to_recommended_falls_and_presence_detects(context_id):
    """
    Convert a context_id to a recommendation of whether to detect falls and presence
    :param context_id: Context ID
    :return: (detect_falls, detect_presence, force) tuple of Booleans
    """
    return radar.context_to_recommended_falls_and_presence_detects(context_id)


def context_to_recommended_low_sensor_energy_and_is_door(context_id):
    """
    Convert a context_id to a recommendation of whether to low sensor energy and is door
    :param context_id: Context ID
    :return: (low_sensor_energy, is_door, force) tuple of Booleans
    """
    return radar.context_to_recommended_low_sensor_energy_and_is_door(context_id)


def at_or_in(context_id):
    """
    Should I use 'at' or 'in'? For example, a person may be 'in' bed or 'at' the sink.
    Hopefully this translates cleanly to other languages... ?

    :param context_id: context_id
    :return: 'at' or 'in'
    """
    return radar.at_or_in(context_id)


def is_context_bed(context_id):
    """
    Is this context a bed?
    :param context_id: Context ID
    :return: True if the context_id is a bed
    """
    return radar.is_context_bed(context_id)


def is_context_chair(context_id):
    """
    Is this context a chair?
    :param context_id: Context ID
    :return: True if the context_id is a chair
    """
    return radar.is_context_chair(context_id)


def is_context_shower(context_id):
    """
    Is this context a shower?
    :param context_id: Context ID
    :return: True if the context_id is a shower
    """
    return radar.is_context_shower(context_id)


def is_context_bathroom(context_id):
    """
    Is this context a bathroom?
    :param context_id: Context ID
    :return: True if the context_id is a bathroom
    """
    return radar.is_context_bathroom(context_id)


def is_context_toilet(context_id):
    """
    Is this context a toilet?
    :param context_id: Context ID
    :return: True if the context_id is a toilet
    """
    return radar.is_context_toilet(context_id)


def is_same_general_context(context_id_1, context_id_2):
    """
    Are these two context ID's the same general context - for example, a bed is a bed, and a chair is a chair... but a bed is not a shower.
    :param context_id_1: Context ID #1
    :param context_id_2: Context ID #2
    :return: True if these two are the same general contexts
    """
    return radar.is_same_general_context(context_id_1, context_id_2)
