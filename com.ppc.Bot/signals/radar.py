"""
Created on May 8, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss

Information vs Knowledge
------------------------
Radar-originated presence events can be surfaced as either information (fast,
lower-reliability) or knowledge (slower, higher-reliability after promotion).

- information: Immediate device observations suitable for quick reactions and
  tentative state. These may be noisy or transient.
- knowledge: Conclusions promoted from information after durability or
  corroboration criteria are met, suitable for stable decisions and
  downstream automation.

Note: Bed-related information delegators are provided at the bottom of this file for
backwards compatibility. Prefer calling `com.ppc.Bot.signals.bed` directly.
"""

# Your microservices can implement the following events:
#
# def did_set_subregion(self, botengine, device_object, unique_id, context_id, name)
# def did_delete_subregion(self, botengine, device_object, unique_id, context_id, name)
#
# def information_did_arrive_bed(self, botengine, device_object, unique_id, context_id, name)
# def information_did_leave_bed(self, botengine, device_object, unique_id, context_id, name)
#
# def information_did_arrive_toilet(self, botengine, device_object, unique_id, context_id, name)
# def information_did_leave_toilet(self, botengine, device_object, unique_id, context_id, name)
#
# def information_did_arrive_shower(self, botengine, device_object, unique_id, context_id, name)
# def information_did_leave_shower(self, botengine, device_object, unique_id, context_id, name)
#
# def information_did_arrive_sink(self, botengine, device_object, unique_id, context_id, name)
# def information_did_leave_sink(self, botengine, device_object, unique_id, context_id, name)
#
# def information_did_arrive_chair(self, botengine, device_object, unique_id, context_id, name)
# def information_did_leave_chair(self, botengine, device_object, unique_id, context_id, name)
#
# def information_did_arrive_exit(self, botengine, device_object, unique_id, context_id, name)
# def information_did_leave_exit(self, botengine, device_object, unique_id, context_id, name)


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

# Mounting options
SENSOR_MOUNTING_WALL = 0
SENSOR_MOUNTING_WALL_45_DEGREE = 3
SENSOR_MOUNTING_CEILING = 1
SENSOR_MOUNTING_CEILING_45_DEGREE = 2
SENSOR_MOUNTING_CORNER = 4


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
    if context_id in [
        SUBREGION_CONTEXT_TOILET,
        SUBREGION_CONTEXT_TOILET_TANK,
        SUBREGION_CONTEXT_SINK,
        SUBREGION_CONTEXT_EXIT
    ]:
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
    return context_id in [SUBREGION_CONTEXT_TOILET, SUBREGION_CONTEXT_TOILET_TANK]


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


#===========================================================================
# Internal Microservice Signals
#===========================================================================
def set_radar_config(botengine, location_object, device_id, content={}):
    """
    Configure the Radar device with a bunch of optional parameters
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_id: Device ID
    :param content: Content dictionary
    """
    try:
        message = {
            "device_id": device_id
        }
        message.update(content)
    except Exception as e:
        botengine.get_logger(f'{__name__}').error("|set_radar_config() - Error: " + str(e))
        return

    location_object.distribute_datastream_message(botengine,
                                                  "set_radar_config",
                                                  message,
                                                  internal=True,
                                                  external=False)


def set_radar_room(botengine, location_object, device_id, content={}):
    """
    Set the Radar room
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_id: Device ID
    :param content: Content dictionary
    """
    try:
        message = {
            "device_id": device_id
        }
        message.update(content)
    except Exception as e:
        botengine.get_logger(f'{__name__}').error("|set_radar_room() - Error: " + str(e))
        return

    location_object.distribute_datastream_message(botengine,
                                                  "set_radar_room",
                                                  message,
                                                  internal=True,
                                                  external=False)

def set_radar_subregion(botengine, location_object, device_id, content={}):
    """
    Set or update a Radar subregion.
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_id: Device ID
    :param content: Content dictionary
    """
    try:
        message = {
            "device_id": device_id
        }
        message.update(content)
    except Exception as e:
        botengine.get_logger(f'{__name__}').error("|set_radar_subregion() - Error: " + str(e))
        return

    location_object.distribute_datastream_message(botengine,
                                                  "set_radar_subregion",
                                                  message,
                                                  internal=True,
                                                  external=False)

def delete_radar_subregion(botengine, location_object, device_id, content={}):
    """
    Delete a Radar subregion
    :param botengine: BotEngine
    :param location_object: Location Object
    :param device_id: Device ID
    :param content: Content dictionary
    """
    try:
        message = {
            "device_id": device_id
        }
        message.update(content)
    except Exception as e:
        botengine.get_logger(f'{__name__}').error("|delete_radar_subregion() - Error: " + str(e))
        return

    location_object.distribute_datastream_message(botengine,
                                                  "delete_radar_subregion",
                                                  message,
                                                  internal=True,
                                                  external=False)


def set_radar_filter(botengine, location_object, device_id, content={}):
    """
    Radar Filter - Ignore a 3D subregion
    :param botengine: BotEngine
    :param location_object: Location Object
    :param device_id: Device ID
    :param content: Content dictionary
    """
    try:
        message = {
            "device_id": device_id
        }
        message.update(content)
    except Exception as e:
        botengine.get_logger(f'{__name__}').error("|set_radar_filter() - Error: " + str(e))
        return

    location_object.distribute_datastream_message(botengine,
                                                  "set_radar_filter",
                                                  message,
                                                  internal=True,
                                                  external=False)

#===========================================================================
# Signals from the Radar microservice package to the other microservices
#===========================================================================
def _enforce_name(name, context_id):
    """
    Ensure the name is not None, and appropriate for the given context
    :param name: Name
    :param context_id: Context
    :return: Refined Name
    """
    if name is not None:
        return name

    return context_to_name(context_id)


def did_set_subregion(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Subregion defined
    :param botengine:
    :param device_object:
    :param unique_id:
    :param context_id:
    :param name:
    :return:
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'did_set_subregion'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].did_set_subregion(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'did_set_subregion' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'did_set_subregion'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].did_set_subregion(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'did_set_subregion' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())
    return


def did_delete_subregion(botengine, location_object, device_object, unique_id):
    """
    Subregion deleted
    Triggers the event: did_delete_subregion(botengine, device_object, unique_id)

    :param self:
    :param botengine:
    :param device_object:
    :param unique_id:
    :return:
    """
    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'did_delete_subregion'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].did_delete_subregion(botengine, device_object, unique_id)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'did_delete_subregion' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'did_delete_subregion'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].did_delete_subregion(botengine, device_object, unique_id)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'did_delete_subregion' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())
    return

def information_did_update_targets(botengine, location_object, device_object, targets):
    """
    Signal that these targets passed through our filters.
    :param botengine: BotEngine
    :param location_object: Location Object
    :param device_object: Device Object
    :param targets: Targets that passed through all filters and ignorable subregions, in the form { 'target_id': { 'x': x, 'y': y, 'z': z } }
    """
    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_update_targets'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_update_targets(botengine, device_object, targets)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_update_targets' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_update_targets'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_update_targets(botengine, device_object, targets)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_update_targets' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_did_update_radar_occupants(botengine, location_object, device_object, total_occupants):
    """
    Captured instantaneous information about the occupants observed near this Radar device
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_object: Device object
    :param total_occupants: Information about total occupants observed at this Radar
    """
    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_update_radar_occupants'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_update_radar_occupants(botengine, device_object, total_occupants)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_update_radar_occupants' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_update_radar_occupants'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_update_radar_occupants(botengine, device_object, total_occupants)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_update_radar_occupants' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def knowledge_did_update_radar_occupants(botengine, location_object, device_object, total_occupants):
    """
    Gained more refined knowledge over time of the occupants observed near this Radar device
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_object: Device object
    :param total_occupants: Knowledge of total occupants observed at this Radar device
    """
    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'knowledge_did_update_radar_occupants'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].knowledge_did_update_radar_occupants(botengine, device_object, total_occupants)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_update_radar_occupants' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'knowledge_did_update_radar_occupants'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].knowledge_did_update_radar_occupants(botengine, device_object, total_occupants)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_update_radar_occupants' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_fall_status_updated(botengine, location_object, device_object, targets, fall_status):
    """
    Detected a fall status change for the given targets

    targets = { 'target_id' : { 'x': x, 'y': y, 'z': z }, ... }

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_object: Device object
    :param targets: Dictionary of targets that meet the qualifications for a fall detect
    :param fall_status: Radar fall status
    """
    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_fall_status_updated'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_fall_status_updated(botengine, device_object, targets, fall_status)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_fall_status_updated' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_fall_status_updated'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_fall_status_updated(botengine, device_object, targets, fall_status)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_fall_status_updated' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_did_arrive_bed(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Information: Signal throughout all microservices that an occupant was seen entering this subregion
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_arrive_bed'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_arrive_bed(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_arrive_bed' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_arrive_bed'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_arrive_bed(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_arrive_bed' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_did_leave_bed(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Information: Signal throughout all microservices that an occupant was seen leaving this subregion
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_leave_bed'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_leave_bed(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_leave_bed' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_leave_bed'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_leave_bed(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_leave_bed' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def knowledge_did_arrive_bed(botengine, location_object, device_object, unique_id=None, context_id=None, name=None):
    """
    DEPRECATED: This function has been moved to signals.bed.knowledge_did_arrive_bed().
    This function is maintained for backwards compatibility and forwards the call to the new implementation.
    
    Knowledge: Signal throughout all microservices that an occupant was seen entering the bed recently
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param unique_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    import signals.bed as bed
    bed.knowledge_did_arrive_bed(botengine, location_object, device_object, unique_id, context_id, name)


def knowledge_did_leave_bed(botengine, location_object, device_object, unique_id=None, context_id=None, name=None):
    """
    DEPRECATED: This function has been moved to signals.bed.knowledge_did_leave_bed().
    This function is maintained for backwards compatibility and forwards the call to the new implementation.
    
    Knowledge: Signal throughout all microservices that an occupant was seen leaving the bed recently
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param unique_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    import signals.bed as bed
    bed.knowledge_did_leave_bed(botengine, location_object, device_object, unique_id, context_id, name)


def information_did_arrive_toilet(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Signal throughout all microservices that an occupant was seen entering this region
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_arrive_toilet'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_arrive_toilet(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_arrive_toilet' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_arrive_toilet'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_arrive_toilet(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_arrive_toilet' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_did_leave_toilet(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Signal throughout all microservices that an occupant was seen leaving this region
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_leave_toilet'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_leave_toilet(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_leave_toilet' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_leave_toilet'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_leave_toilet(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_leave_toilet' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def knowledge_did_arrive_shower(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Knowledge: Signal throughout all microservices that an occupant was seen entering the shower recently
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'knowledge_did_arrive_shower'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].knowledge_did_arrive_shower(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_arrive_shower' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'knowledge_did_arrive_shower'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].knowledge_did_arrive_shower(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_arrive_shower' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def knowledge_did_leave_shower(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Knowledge: Signal throughout all microservices that an occupant was seen leaving the shower recently
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'knowledge_did_leave_shower'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].knowledge_did_leave_shower(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_leave_shower' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'knowledge_did_leave_shower'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].knowledge_did_leave_shower(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_leave_shower' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_did_arrive_shower(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Signal throughout all microservices that an occupant was seen entering this region
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_arrive_shower'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_arrive_shower(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_arrive_shower' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_arrive_shower'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_arrive_shower(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_arrive_shower' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_did_leave_shower(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Signal throughout all microservices that an occupant was seen leaving this region
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_leave_shower'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_leave_shower(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_leave_shower' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_leave_shower'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_leave_shower(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_leave_shower' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def knowledge_did_arrive_chair(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Knowledge: Signal throughout all microservices that an occupant was seen entering the chair recently
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'knowledge_did_arrive_chair'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].knowledge_did_arrive_chair(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_arrive_chair' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'knowledge_did_arrive_chair'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].knowledge_did_arrive_chair(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_arrive_chair' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def knowledge_did_leave_chair(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Knowledge: Signal throughout all microservices that an occupant was seen leaving the chair recently
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'knowledge_did_leave_chair'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].knowledge_did_leave_chair(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_leave_chair' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'knowledge_did_leave_chair'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].knowledge_did_leave_chair(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'knowledge_did_leave_chair' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_did_arrive_chair(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Signal throughout all microservices that an occupant was seen entering this region
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_arrive_chair'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_arrive_chair(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_arrive_chair' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_arrive_chair'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_arrive_chair(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_arrive_chair' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_did_leave_chair(botengine, location_object, device_object, unique_id, context_id, name):
    """
    Signal throughout all microservices that an occupant was seen leaving this region
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    name = _enforce_name(name, context_id)

    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'information_did_leave_chair'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].information_did_leave_chair(botengine, device_object, unique_id, context_id, name)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'information_did_leave_chair' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_leave_chair'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].information_did_leave_chair(botengine, device_object, unique_id, context_id, name)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'information_did_leave_chair' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def did_start_detecting_visitor(botengine, location_object):
    """
    Signal throughout all microservices that 2 or more people are reliably detected in the home
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'did_start_detecting_visitor'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].did_start_detecting_visitor(botengine)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'did_start_detecting_visitor' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'did_start_detecting_visitor'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].did_start_detecting_visitor(botengine)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'did_start_detecting_visitor' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def did_stop_detecting_visitor(botengine, location_object):
    """
    Signal throughout all microservices that 1 or fewer people are currently detected in the home
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'did_stop_detecting_visitor'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].did_stop_detecting_visitor(botengine)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'did_stop_detecting_visitor' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'did_stop_detecting_visitor'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].did_stop_detecting_visitor(botengine)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'did_stop_detecting_visitor' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def did_start_detecting_together(botengine, location_object):
    """
    Signal throughout all microservices that 2 or more people are believed to be in the same room
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'did_start_detecting_together'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].did_start_detecting_together(botengine)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'did_start_detecting_together' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'did_start_detecting_together'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].did_start_detecting_together(botengine)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'did_start_detecting_together' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def did_stop_detecting_together(botengine, location_object):
    """
    Signal throughout all microservices that there are no 2 or more people detected in the same room
    :param botengine: BotEngine
    :param location_object: Location object
    :param device_object: Device object
    :param subregion_id: Subregion ID
    :param context_id: Context ID
    :param name: Name of the subregion, None if not given
    """
    # Location microservices
    for microservice in location_object.intelligence_modules:
        if hasattr(location_object.intelligence_modules[microservice], 'did_stop_detecting_together'):
            try:
                import time
                t = time.time()
                location_object.intelligence_modules[microservice].did_stop_detecting_together(botengine)
                location_object.intelligence_modules[microservice].track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering 'did_stop_detecting_together' to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

    # Device microservices
    for device_id in location_object.devices:
        if hasattr(location_object.devices[device_id], "intelligence_modules"):
            for microservice in location_object.devices[device_id].intelligence_modules:
                if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'did_stop_detecting_together'):
                    try:
                        location_object.devices[device_id].intelligence_modules[microservice].did_stop_detecting_together(botengine)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering 'did_stop_detecting_together' message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())


def information_out_of_bed(botengine, location_object, start_time_ms, device_object):
    """
    User go out of bed
    :param botengine: BotEngine
    :param location_object: Location Object
    :param start_time_ms: Start time of the leave bed in milliseconds - used as a unique identifier for this fall
    :param device_object: Device object that is detecting the out of bed
    """
    body = {
        "start_time_ms": start_time_ms,
        "device_id": device_object.device_id,
        "device_desc": device_object.description,
        "device_type": device_object.device_type
    }

    location_object.distribute_datastream_message(botengine, "information_out_of_bed", body, internal=True, external=False)


def information_returned_to_bed(botengine, location_object, start_time_ms, end_time_ms):
    """
    User returned to bed
    :param botengine:
    :param location_object:
    :param start_time_ms:
    :param end_time_ms:
    :return:
    """
    body = {
        "start_time_ms": start_time_ms,
        "end_time_ms": end_time_ms
    }

    location_object.distribute_datastream_message(botengine, "information_out_of_bed", body, internal=True, external=False)


# ---------------------------------------------------------------------------
# Backward-compatible bed information signals
# These were moved to `com.ppc.Bot/signals/bed.py`. Keep delegators here.
def knowledge_did_arrive_bed(botengine, location_object, device_object, unique_id=None, context_id=None, name=None):
    """
    Backwards compatibility delegator to bed signals.

    Semantics: This is a knowledge-level (slower, higher-reliability) indication that
    someone has arrived in bed. Prefer calling
    `com.ppc.Bot.signals.bed.knowledge_did_arrive_bed` directly.
    """
    import signals.bed as bed
    return bed.knowledge_did_arrive_bed(
        botengine, location_object, device_object, unique_id, context_id, name
    )


def knowledge_did_leave_bed(botengine, location_object, device_object, unique_id=None, context_id=None, name=None):
    """
    Backwards compatibility delegator to bed signals.

    Semantics: This is a knowledge-level (slower, higher-reliability) indication that
    someone has left the bed. Prefer calling
    `com.ppc.Bot.signals.bed.knowledge_did_leave_bed` directly.
    """
    import signals.bed as bed
    return bed.knowledge_did_leave_bed(
        botengine, location_object, device_object, unique_id, context_id, name
    )


def information_did_arrive_bed(botengine, location_object, device_object, unique_id=None, context_id=None, name=None):
    """
    Backwards compatibility delegator to bed signals.

    Semantics: This is an information-level (fast, lower-reliability) indication that
    someone may have arrived in bed. Prefer calling
    `com.ppc.Bot.signals.bed.information_did_arrive_bed` directly.
    """
    import signals.bed as bed
    return bed.information_did_arrive_bed(
        botengine, location_object, device_object, unique_id, context_id, name
    )


def information_did_leave_bed(botengine, location_object, device_object, unique_id=None, context_id=None, name=None):
    """
    Backwards compatibility delegator to bed signals.

    Semantics: This is an information-level (fast, lower-reliability) indication that
    someone may have left the bed. Prefer calling
    `com.ppc.Bot.signals.bed.information_did_leave_bed` directly.
    """
    import signals.bed as bed
    return bed.information_did_leave_bed(
        botengine, location_object, device_object, unique_id, context_id, name
    )