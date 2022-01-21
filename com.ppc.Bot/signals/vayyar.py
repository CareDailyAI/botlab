"""
Created on May 8, 2021

CONTEXT MANAGEMENT ONLY

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

# Subregion Contexts
SUBREGION_CONTEXT_IGNORE = -1

# Bedroom
SUBREGION_CONTEXT_BED = 0
SUBREGION_CONTEXT_BED_KING = 1
SUBREGION_CONTEXT_BED_CALKING = 2
SUBREGION_CONTEXT_BED_QUEEN = 3
SUBREGION_CONTEXT_BED_FULL = 4
SUBREGION_CONTEXT_BED_TWINXL = 5
SUBREGION_CONTEXT_BED_TWIN = 6
SUBREGION_CONTEXT_BED_CRIB = 7
SUBREGION_CONTEXT_END_TABLE = 8
SUBREGION_CONTEXT_CPAP = 9

# Bathroom
SUBREGION_CONTEXT_BATHROOM = 10
SUBREGION_CONTEXT_TOILET = 11
SUBREGION_CONTEXT_BATHTUB = 12
SUBREGION_CONTEXT_WALK_IN_SHOWER = 13
SUBREGION_CONTEXT_SINK = 14
SUBREGION_CONTEXT_TOILET_TANK = 15

# Living Room and other
SUBREGION_CONTEXT_CHAIR = 20
SUBREGION_CONTEXT_COUCH = 22
SUBREGION_CONTEXT_TABLE = 23

SUBREGION_CONTEXT_OTHER = 99
SUBREGION_CONTEXT_EXIT = 100

# fall_sensitivity
FALL_SENSITIVITY_LOW = 1
FALL_SENSITIVITY_NORMAL = 2

# led_mode
LED_MODE_OFF = 0
LED_MODE_ON = 1

# Volume
VOLUME_ON = 100
VOLUME_OFF = 0

# telementry_policy
TELEMETRY_POLICY_OFF = 0
TELEMETRY_POLICY_ON = 1
TELEMETRY_POLICY_FALLS_ONLY = 2


def is_context_bed(context_id):
    """
    Is this context a bed?
    :param context_id: Context ID
    :return: True if the context_id is a bed
    """
    return context_id == SUBREGION_CONTEXT_BED or context_id == SUBREGION_CONTEXT_BED_KING or context_id == SUBREGION_CONTEXT_BED_CALKING or context_id == SUBREGION_CONTEXT_BED_QUEEN or context_id == SUBREGION_CONTEXT_BED_FULL or context_id == SUBREGION_CONTEXT_BED_TWINXL or context_id == SUBREGION_CONTEXT_BED_TWIN or context_id == SUBREGION_CONTEXT_BED_CRIB

def is_context_chair(context_id):
    """
    Is this context a chair?
    :param context_id: Context ID
    :return: True if the context_id is a chair
    """
    return context_id == SUBREGION_CONTEXT_CHAIR or context_id == SUBREGION_CONTEXT_COUCH

def is_context_shower(context_id):
    """
    Is this context a shower?
    :param context_id: Context ID
    :return: True if the context_id is a shower
    """
    return context_id == SUBREGION_CONTEXT_BATHTUB or context_id == SUBREGION_CONTEXT_WALK_IN_SHOWER

def is_context_bathroom(context_id):
    """
    Is this context a bathroom?
    :param context_id: Context ID
    :return: True if the context_id is a bathroom
    """
    return context_id == SUBREGION_CONTEXT_BATHROOM

def is_context_toilet(context_id):
    """
    Is this context a toilet?
    :param context_id: Context ID
    :return: True if the context_id is a toilet
    """
    return context_id == SUBREGION_CONTEXT_TOILET


def is_same_general_context(context_id_1, context_id_2):
    """
    Are these two context ID's the same general context - for example, a bed is a bed, and a chair is a chair... but a bed is not a shower.
    :param context_id_1: Context ID #1
    :param context_id_2: Context ID #2
    :return: True if these two are the same general contexts
    """
    if is_context_bed(context_id_1):
        return is_context_bed(context_id_2)

    elif is_context_chair(context_id_1):
        return is_context_chair(context_id_2)

    elif is_context_shower(context_id_1):
        return is_context_shower(context_id_2)

    elif is_context_toilet(context_id_1):
        return is_context_toilet(context_id_2)

    return context_id_1 == context_id_2

