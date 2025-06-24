"""
Created on May 8, 2021

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
FALL_SENSITIVITY_NO_FALLING = 0
FALL_SENSITIVITY_LOW = 1
FALL_SENSITIVITY_NORMAL = 2

# led_mode
LED_MODE_OFF = 0
LED_MODE_ON = 1

# Volume
VOLUME_ON = 100
VOLUME_OFF = 0

# Feedback classification
FEEDBACK_CLASSIFICATION_TRUE_POSITIVE = "TRUE_POSITIVE"
FEEDBACK_CLASSIFICATION_FALSE_POSITIVE = "FALSE_POSITIVE"
FEEDBACK_CLASSIFICATION_FALSE_NEGATIVE = "FALSE_NEGATIVE"
FEEDBACK_CLASSIFICATION_TEST_FALL = "TEST_FALL"

# Default enter duration
DEFAULT_ENTER_DURATION = 120

# Default exit duration
DEFAULT_EXIT_DURATION = 120

# Fall location target ID
TARGET_ID_FALL_LOC = "FALL_LOC"


def context_to_name(context_id):
    """
    Convert a context_id to a descriptive name
    :param context_id: Context ID
    :return: Descriptive name
    """
    if context_id == SUBREGION_CONTEXT_IGNORE:
        return _("Ignore Region")

    elif context_id == SUBREGION_CONTEXT_BED:
        return _("Bed")

    elif context_id == SUBREGION_CONTEXT_BED_KING:
        return _("King Bed")

    elif context_id == SUBREGION_CONTEXT_BED_CALKING:
        return _("California King Bed")

    elif context_id == SUBREGION_CONTEXT_BED_QUEEN:
        return _("Queen Bed")

    elif context_id == SUBREGION_CONTEXT_BED_FULL:
        return _("Full Bed")

    elif context_id == SUBREGION_CONTEXT_BED_TWINXL:
        return _("Twin XL Bed")

    elif context_id == SUBREGION_CONTEXT_BED_TWIN:
        return _("Twin Bed")

    elif context_id == SUBREGION_CONTEXT_BED_CRIB:
        return _("Crib")

    elif context_id == SUBREGION_CONTEXT_END_TABLE:
        return _("End Table")

    elif context_id == SUBREGION_CONTEXT_CPAP:
        return _("CPAP Machine")

    elif context_id == SUBREGION_CONTEXT_TOILET:
        return _("Toilet")

    elif context_id == SUBREGION_CONTEXT_TOILET_TANK:
        return _("Toilet Tank")

    elif context_id == SUBREGION_CONTEXT_BATHTUB:
        return _("Bathtub / Shower")

    elif context_id == SUBREGION_CONTEXT_WALK_IN_SHOWER:
        return _("Shower")

    elif context_id == SUBREGION_CONTEXT_SINK:
        return _("Sink")

    elif context_id == SUBREGION_CONTEXT_CHAIR:
        return _("Chair")

    elif context_id == SUBREGION_CONTEXT_COUCH:
        return _("Couch")

    elif context_id == SUBREGION_CONTEXT_EXIT:
        return _("Exit Door")

    return _("Subregion")


def context_to_recommended_falls_and_presence_detects(context_id):
    """
    Convert a context_id to a recommendation of whether to detect falls and presence
    :param context_id: Context ID
    :return: (detect_falls, detect_presence, force) tuple of Booleans
    """
    if context_id == SUBREGION_CONTEXT_IGNORE:
        return False, False, True

    elif context_id == SUBREGION_CONTEXT_BED:
        return False, True, True

    elif context_id == SUBREGION_CONTEXT_BED_KING:
        return False, True, True

    elif context_id == SUBREGION_CONTEXT_BED_CALKING:
        return False, True, True

    elif context_id == SUBREGION_CONTEXT_BED_QUEEN:
        return False, True, True

    elif context_id == SUBREGION_CONTEXT_BED_FULL:
        return False, True, True

    elif context_id == SUBREGION_CONTEXT_BED_TWINXL:
        return False, True, True

    elif context_id == SUBREGION_CONTEXT_BED_TWIN:
        return False, True, True

    elif context_id == SUBREGION_CONTEXT_BED_CRIB:
        return False, True, True

    elif context_id == SUBREGION_CONTEXT_END_TABLE:
        return False, False, True

    elif context_id == SUBREGION_CONTEXT_CPAP:
        return False, False, True

    elif context_id == SUBREGION_CONTEXT_TOILET:
        return True, True, False

    elif context_id == SUBREGION_CONTEXT_TOILET_TANK:
        return False, False, True

    elif context_id == SUBREGION_CONTEXT_BATHTUB:
        return (
            False,
            True,
            False,
        )  # Controversial - a bathtub full of water will produce a fall detect. Need to handle that based on the duration of time spent in the bathtub.

    elif context_id == SUBREGION_CONTEXT_WALK_IN_SHOWER:
        return True, True, False

    elif context_id == SUBREGION_CONTEXT_SINK:
        return True, True, False

    elif context_id == SUBREGION_CONTEXT_CHAIR:
        return False, True, True

    elif context_id == SUBREGION_CONTEXT_COUCH:
        return False, True, True

    elif context_id == SUBREGION_CONTEXT_EXIT:
        return False, True, False

    return True, True, False


def context_to_recommended_low_sensor_energy_and_is_door(context_id):
    """
    Convert a context_id to a recommendation of whether to low sensor energy and is door
    :param context_id: Context ID
    :return: (low_sensor_energy, is_door, force) tuple of Booleans
    """
    if context_id == SUBREGION_CONTEXT_EXIT:
        return False, True, True

    return True, False, False


def at_or_in(context_id):
    """
    Should I use 'at' or 'in'? For example, a person may be 'in' bed or 'at' the sink.
    Hopefully this translates cleanly to other languages... ?

    :param context_id: context_id
    :return: 'at' or 'in'
    """
    if (
        context_id == SUBREGION_CONTEXT_TOILET
        or context_id == SUBREGION_CONTEXT_SINK
        or context_id == SUBREGION_CONTEXT_EXIT
    ):
        # Note: You are 'at' the sink or 'at' the toilet or 'at' the exit
        return _("at")

    # Note: You are 'in' bed or 'in' the shower or 'in' the chair
    return _("in")


def is_context_bed(context_id):
    """
    Is this context a bed?
    :param context_id: Context ID
    :return: True if the context_id is a bed
    """
    return (
        context_id == SUBREGION_CONTEXT_BED
        or context_id == SUBREGION_CONTEXT_BED_KING
        or context_id == SUBREGION_CONTEXT_BED_CALKING
        or context_id == SUBREGION_CONTEXT_BED_QUEEN
        or context_id == SUBREGION_CONTEXT_BED_FULL
        or context_id == SUBREGION_CONTEXT_BED_TWINXL
        or context_id == SUBREGION_CONTEXT_BED_TWIN
        or context_id == SUBREGION_CONTEXT_BED_CRIB
    )


def is_context_chair(context_id):
    """
    Is this context a chair?
    :param context_id: Context ID
    :return: True if the context_id is a chair
    """
    return (
        context_id == SUBREGION_CONTEXT_CHAIR or context_id == SUBREGION_CONTEXT_COUCH
    )


def is_context_shower(context_id):
    """
    Is this context a shower?
    :param context_id: Context ID
    :return: True if the context_id is a shower
    """
    return (
        context_id == SUBREGION_CONTEXT_BATHTUB
        or context_id == SUBREGION_CONTEXT_WALK_IN_SHOWER
    )


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
