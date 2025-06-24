"""
Created on May 7, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""


def set_rule_phrase(botengine, location_object, phrase_id, phrase_object):
    """
    Declare a rule phrase to be dynamically added (or removed) from our rules engine.
    Only one primary rules engine should execute in a location. This will save the rule phrase information as a
    shared variable to be delivered to the primary bot, allowing developers to invent and apply their own rules
    from their own bots.

    If the phrase_object is None, then the rule phrase gets removed.

    The phrase_id is a globally unique name for the phrase.

    The phrase_object should contain a dictionary with this type of content:

    {
        # 'type' field can be 0 (trigger), 1 (state), or 2 (action)
        "type": TYPE_TRIGGER,

        # If we evaluate a device: the device type of the device so we could summarize actions for specific types of devices.
        "device_types": self.parent.device_type,

        # Description of the phrase in the user's native language. Fill in the ___:
        # [If my] ____
        # [and my] ____
        # [then] ____
        "description": "'{}' is pressed",

        # Past-tense of the description, for notifications. Fill in the ___:
        # [Your] ____
        # [while your] ___
        "past": "'{}' was pressed",

        # Evaluation function for triggers and states.
        # If dealing with a device, the function is responsible for checking if the device ID is the object that made an update,
        # and then testing to see if that device is in the triggered state.
        # Function arguments are action_function(botengine, rules_engine, location_object, device_object, rule_id)
        # Functions should return a tuple: ( True|False to execute, "past-tense comment describing why" )
        # Any time the function changes, we need to update the rule phrase.
        "eval": evaluation_function,

        # Evaluation function for any timer fires related to this rule / trigger
        # Function arguments are timer_function(botengine, rules_engine, location_object, device_object, rule_id)
        # Functions should return a tuple: ( True|False to execute, "past-tense comment describing why" )
        # Any time the function changes, we need to update the rule phrase.
        "timer_eval": trigger_button_held_timer_fired,

        # Action function for actions.
        # Function arguments are action_function(botengine, rules_engine, location_object, device_object, rule_id)
        # Any time the function changes, we need to update the rule phrase.
        "action": action_function,

        # Icon to apply at the application layer
        "icon": "touch"

        # List of dynamic parameters that need to be captured in the rule
        # Each parameter has a globally unique name.
        # See the "Rule Phrase Parameters" table at https://iotapps.docs.apiary.io/#reference/rules-engine
        "parameters": [

            {
                # Name of this parameter. The application should save the parameter into the rule data stream message with "unique_rule_phrase_id-parameter_name": "final_value"
                "name": "unique_rule_phrase_id-parameter_name",

                # Optional. Know what order to fill out parameters when dealing with multiple parameters.
                # Higher numbers are filled out later than lower numbers.
                "order": 0,

                # Type of input desired
                #  0 = Device ID
                #  1 = Text input
                #  2 = Absolute time-of-day (seconds from the start of the day)
                #  3 = Day-of-the-week multiple-choice multi-select (0 = Sunday). Remember in Python, Monday = 0 so we have to offset.
                #  4 = Relative time from when the rule was created (seconds from now) - "Alexa turn off the lights in 5 minutes"
                #  5 = Multiple-choice single-select (see the list of values below).
                #  6 = Mode "HOME", "AWAY", "STAY"
                #  7 = Security system state integer (from the security state enumerator)
                #  8 = Occupancy status "PRESENT", "ABSENT", "H2A", "A2H", "SLEEP", "H2S", "S2H", "VACATION"
                "category": parameter_categories_type,

                "description": "A short user friendly question or brief instruction to display to the user to get them to correctly fill out this parameter.",

                "values": [
                    "list",
                    "of",
                    "choices",
                    "if",
                    "applicable"
                ],

                # Default value of the parameter, if applicable
                "value": "Default Value",

                # For UI slider type category
                "min_value": 0,

                # For UI slider type category
                "max_value": 10,

                # 1=int, 2=float
                "value_type": 1,

                # Unit of measurements
                "unit": "Hours"
            }
        ]
    }

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param phrase_id: Globally unique name for the phrase
    :param phrase_object: Dictionary, described above
    """
    botengine.save_shared_variable(phrase_id, phrase_object)
    location_object.distribute_datastream_message(
        botengine,
        "set_rule_phrase",
        {"phrase_id": phrase_id},
        internal=True,
        external=True,
    )
