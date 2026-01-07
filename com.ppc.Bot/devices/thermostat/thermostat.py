# -*- coding: utf-8 -*-
"""
Created on March 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

import signals.analytics as analytics
import utilities.utilities as utilities
from devices.device import cancel_reliable_command, Device, send_command_reliably

# Element index numbers for our last_command_* tuples
COMMAND_VALUE_INDEX = 0
COMMAND_TIMESTAMP_INDEX = 1
COMMAND_VERIFIED_INDEX = 2

ONE_DEGREE_F_TO_C = 0.5556

# TODO
# We currently use the "preferred" setpoint as the offset for DR and EE events.
# These offsets should become relative to the current setpoint that the user selected without any offsets applied.
# When the user adjusts the temperature, all EE offsets should be removed and the DR offset should remain relative to the original temperature at the start of the DR event with no offsets applied.
#
# The DR intelligence above needs to be modified to rely more on this class for the heavy lifting of these features:
#   * Specifying the absolute temperature to go to (given some offset) relative to the current setpoint with no offsets applied.
#   * Identifying when the user adjusts the thermostat, especially when the current setpoint violates the predefined DR boundary.
#
# The DR intelligence above doesn't know how to subtract out any current energy efficiency offsets to define the real DR boundary.
#
# One DR question is what the behavior should be when the user is away from home and their thermostat is saving energy already, and then a DR event gets applied.
# The current thinking is we don't care - the DR event offset is applied relative to the setpoint temperature (without EE offsets) that was in place when the DR event started.
#
# We also need one more level of complexity on identifying if the user adjusted the thermostat.
# If the temperature read back from the thermostat is different than the temperature it was previously at and different from the target temperature we wanted to go to, then the user adjusted it.
#
# What if demand response is really about lowering the average thermostat temperature across the entire user base

# Maximum and Minimum cooling and heating setpoint values for DR and EE programs
# Maximum cooling setpoint = 84 degrees F
MAXIMUM_COOLING_SETPOINT_C = 28.9

# Minimum heating setpoint = 60 degrees F
MINIMUM_HEATING_SETPOINT_C = 15.6


class ThermostatDevice(Device):
    """
    Abstract Thermostat class, providing a predictable interface for all Thermostat definition
    """

    # Parameter names
    MEASUREMENT_NAME_AMBIENT_TEMPERATURE_C = "degC"
    MEASUREMENT_NAME_SYSTEM_MODE = "systemMode"
    MEASUREMENT_NAME_COOLING_SETPOINT_C = "coolingSetpoint"
    MEASUREMENT_NAME_HEATING_SETPOINT_C = "heatingSetpoint"
    MEASUREMENT_NAME_FAN_MODE = "fanMode"
    MEASUREMENT_NAME_MANUFACTURER = "manufacturer"
    MEASUREMENT_NAME_MODEL = "model"

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_AMBIENT_TEMPERATURE_C,
        MEASUREMENT_NAME_SYSTEM_MODE,
        MEASUREMENT_NAME_COOLING_SETPOINT_C,
        MEASUREMENT_NAME_HEATING_SETPOINT_C,
        MEASUREMENT_NAME_FAN_MODE,
    ]

    # systemMode values
    SYSTEM_MODE__OFF = 0
    SYSTEM_MODE__AUTO = 1
    SYSTEM_MODE__COOL = 3
    SYSTEM_MODE__HEAT = 4
    SYSTEM_MODE__EMERGENCY_HEAT = 5
    SYSTEM_MODE__PRECOOLING = 6
    SYSTEM_MODE__FAN_ONLY = 7

    # fanMode values
    FAN_MODE__OFF = 0
    FAN_MODE__LOW = 1
    FAN_MODE__MED = 2
    FAN_MODE__HIGH = 3
    FAN_MODE__ON = 4
    FAN_MODE__AUTO = 5
    FAN_MODE__SMART = 6

    def __init__(
        self,
        botengine,
        location_object,
        device_id,
        device_type,
        device_description,
        precache_measurements=True,
    ):
        # Saved system mode
        self.saved_system_mode = None

        # Stack of energy efficiency policies.
        # Each policy is a dictionary of the form:
        #
        #   "name of the policy so it can be cancelled later": offset_c relative to the user's preferred temperature while home (always a positive number)
        #
        # The act of having a policy stored implies the policy is active.
        # The most aggressive energy efficiency policy is applied.
        # Energy efficiency policies are additive to any current demand response event.
        self.ee_stack_cool = {}
        self.ee_stack_heat = {}

        # Stack of demand response policies.
        # Each policy is a dictionary of the form:
        #
        #   "name of the policy so it can be cancelled later": offset_c relative to the user's preferred temperature while home (always a positive number)
        #
        # The act of having a policy stored implies the policy is active.
        # The most aggressive demand response policy is applied.
        # Demand response policies are additive to any current energy efficiency policies.
        self.dr_stack_cool = {}
        self.dr_stack_heat = {}

        # Tuple (value, timestamp, verified): the last system mode command we sent the thermostat
        self.last_system_mode_command = None

        # Tuple (value, timestamp, verified): the last cooling setpoint command we sent the thermostat
        self.last_cooling_setpoint_command = None

        # Tuple (value, timestamp, verified): the last heating setpoint command we sent the thermostat
        self.last_heating_setpoint_command = None

        # Timestamp at which the user last adjusted their thermostat
        self.user_adjusted_timestamp = None

        # Preferred heating setpoint for this thermostat while you're home
        self.preferred_heating_setpoint_home_c = 20.0  # 68F

        # Preferred cooling setpoint for this thermostat while you're home
        self.preferred_cooling_setpoint_home_c = 23.9  # 75F

        # Absolute maximum heating offset (when you're on vacation or something)
        self.absolute_max_heating_offset_c = 8.3  # 15F

        # Absolute maximum cooling offset (when you're on vacation or something)
        self.absolute_max_cooling_offset_c = 8.3  # 15F

        # Preferred cooling offset when we're in away mode
        self.preferred_heating_offset_away_c = 2.4  # 5F

        # Preferred heating offset when we're in away mode
        self.preferred_cooling_offset_away_c = 2.4  # 5F

        # Preferred cooling offset when we're in away mode
        self.preferred_heating_offset_sleep_c = 1.6  # 3F

        # Preferred heating offset when we're in away mode
        self.preferred_cooling_offset_sleep_c = 1.6  # 3F

        # Start timestamp of DR events for tracking
        self.dr_timestamp_ms = None

        # Start timestamp of EE events for tracking
        self.ee_timestamp_ms = None

        # Last total offset applied, in C
        self.last_offset_c = 0

        Device.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )

    def initialize(self, botengine):
        """
        Initializer
        :param botengine: BotEngine
        """
        if self.preferred_heating_offset_away_c < ONE_DEGREE_F_TO_C:
            self.preferred_heating_offset_away_c = ONE_DEGREE_F_TO_C

        if self.preferred_cooling_offset_away_c < ONE_DEGREE_F_TO_C:
            self.preferred_cooling_offset_away_c = ONE_DEGREE_F_TO_C

        if self.preferred_heating_offset_sleep_c < ONE_DEGREE_F_TO_C:
            self.preferred_heating_offset_sleep_c = ONE_DEGREE_F_TO_C

        if self.preferred_cooling_offset_sleep_c < ONE_DEGREE_F_TO_C:
            self.preferred_cooling_offset_sleep_c = ONE_DEGREE_F_TO_C

        Device.initialize(self, botengine)

    def did_change_mode(self, botengine=None):
        """
        :param botengine:
        :return: True if we changed the mode
        """
        return ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE in self.last_updated_params

    def did_change_cooling_setpoint(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if the cooling set point changed
        """
        return (
            ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
            in self.last_updated_params
        )

    def did_change_heating_setpoint(self, botengine=None):
        """
        :param botengine:
        :return: True if the heating set point changed
        """
        return (
            ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
            in self.last_updated_params
        )

    def did_change_ambient_temperature(self, botengine=None):
        """
        :param botengine:
        :return: True if the ambient temperature changed
        """
        return (
            ThermostatDevice.MEASUREMENT_NAME_AMBIENT_TEMPERATURE_C
            in self.last_updated_params
        )

    def add_measurement(self, botengine, name, value, timestamp):
        """
        Overriding the method from the parent to add a measurement,
        in order to see if the user is messing with their thermostat or if we are.
        :param botengine:
        :param name:
        :param value:
        :param timestamp:
        :return:
        """
        botengine.get_logger().info("\t{} = {}".format(name, value))
        measurement_updated = Device.add_measurement(
            self, botengine, name, value, timestamp
        )

        # Sometimes the user adjusts the thermostat during or immediately after a command is sent.
        # In that case, the reliability() methods underneath end up overridding the user, which is a cause for anger and backlash.
        # If we're controlling the thermostat alone, the setpoint should either be what it used to be or it should be what we're setting it to now.
        # TODO Check to see if a new setpoint has appeared which is neither what it used to be nor what we're setting it to now - this is the user overriding us and we should give in to that.
        # The one case where that doesn't work is if the user was right in front of their thermostat when we change the temperature, and they immediately set it back to what it used to be.
        # Can we check the timestamp when the value was updated to know if it was actually adjusted, or just old data?
        if name in self.measurements:
            if (
                name == ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE
                and self.last_system_mode_command is not None
            ):
                if (
                    self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][
                        0
                    ]
                    != self.last_system_mode_command[COMMAND_VALUE_INDEX]
                ):
                    # Latest measurement doesn't match up with the last command we sent.
                    if (
                        self.last_system_mode_command[COMMAND_VERIFIED_INDEX]
                        or (botengine.get_timestamp() - (utilities.ONE_MINUTE_MS))
                        > self.last_system_mode_command[COMMAND_TIMESTAMP_INDEX]
                    ):
                        # Our last command was already verified, therefore this new measurement is an external adjustment.
                        # Or, our last command never got verified, but it's been over 2 minutes ago. The system mode is now adjusted from what we set it to.
                        self.user_adjusted_timestamp = botengine.get_timestamp()
                        self.last_system_mode_command = None

                        if self.location_object is not None:
                            # NOTE: Thermostat mode set.
                            self.location_object.narrate(
                                botengine,
                                title=_("'{}' now set to {}").format(
                                    self.description,
                                    self.thermostat_mode_to_string(
                                        self.measurements[
                                            ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE
                                        ][0][0]
                                    ),
                                ),
                                description=_("Your '{}' is set to {}.").format(
                                    self.description,
                                    self.thermostat_mode_to_string(
                                        self.measurements[
                                            ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE
                                        ][0][0]
                                    ),
                                ),
                                priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                                icon="thermostat",
                                extra_json_dict={"device_id": self.device_id},
                                event_type="thermostat.thermostat_mode",
                            )
                            analytics.track(
                                botengine,
                                self.location_object,
                                "thermostat_mode",
                                properties={
                                    "device_id": self.device_id,
                                    "description": self.description,
                                    "ai": True,
                                    "thermostat_mode": self.thermostat_mode_to_string(
                                        self.measurements[
                                            ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE
                                        ][0][0]
                                    ),
                                },
                            )

                    else:
                        # Our last command wasn't verified, and it's been under 2 minutes. Keep waiting.
                        botengine.get_logger().info(
                            "[{} '{}'] Last system mode command not verified and it's under 2 minutes, keep waiting".format(
                                self.device_id, self.description
                            )
                        )
                        pass

                else:
                    botengine.get_logger().info(
                        "[{} '{}'] Last system mode command verified".format(
                            self.device_id, self.description
                        )
                    )
                    self.last_system_mode_command = (
                        self.last_system_mode_command[COMMAND_VALUE_INDEX],
                        self.last_system_mode_command[COMMAND_TIMESTAMP_INDEX],
                        True,
                    )

            elif (
                name == ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                and self.last_cooling_setpoint_command is not None
            ):
                if self.is_temperature_different(
                    self.measurements[
                        ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                    ][0][0],
                    self.last_cooling_setpoint_command[COMMAND_VALUE_INDEX],
                ):
                    if (
                        self.last_cooling_setpoint_command[COMMAND_VERIFIED_INDEX]
                        or (botengine.get_timestamp() - (utilities.ONE_MINUTE_MS))
                        > self.last_cooling_setpoint_command[COMMAND_TIMESTAMP_INDEX]
                    ):
                        # Our last command was already verified, therefore this new measurement is an external adjustment.
                        # Or, our last command was delivered over 2 minutes ago, and the cooling setpoint is now adjusted from what we set it to.
                        self.user_adjusted_timestamp = botengine.get_timestamp()
                        self.last_cooling_setpoint_command = None

                        if self.location_object is not None:
                            # NOTE: Thermostat cooling set point adjusted.
                            self.location_object.narrate(
                                botengine,
                                title=_("Cooling set point adjusted"),
                                description=_(
                                    "Your '{}' cooling set point is set to {}."
                                ).format(
                                    self.description,
                                    self._celsius_to_narrative(
                                        self.measurements[
                                            ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                                        ][0][0]
                                    ),
                                ),
                                priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                                icon="thermostat",
                                extra_json_dict={"device_id": self.device_id},
                                event_type="thermostat.thermostat_cooling_setpoint",
                            )
                            analytics.track(
                                botengine,
                                self.location_object,
                                "thermostat_cooling_setpoint",
                                properties={
                                    "device_id": self.device_id,
                                    "description": self.description,
                                    "ai": True,
                                    "cooling_setpoint": self.measurements[
                                        ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                                    ][0][0],
                                },
                            )

                    else:
                        # Our last command wasn't verified, and it's been under 2 minutes. Keep waiting.
                        botengine.get_logger().info(
                            "[{} '{}'] Last cooling setpoint command not verified and it's under 2 minutes, keep waiting".format(
                                self.device_id, self.description
                            )
                        )
                        pass

                else:
                    botengine.get_logger().info(
                        "[{} '{}'] Last cooling setpoint command verified".format(
                            self.device_id, self.description
                        )
                    )
                    self.last_cooling_setpoint_command = (
                        self.last_cooling_setpoint_command[COMMAND_VALUE_INDEX],
                        self.last_cooling_setpoint_command[COMMAND_TIMESTAMP_INDEX],
                        True,
                    )

            elif (
                name == ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                and self.last_heating_setpoint_command is not None
            ):
                # Heating setpoint measurement received
                if self.is_temperature_different(
                    self.measurements[
                        ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                    ][0][0],
                    self.last_heating_setpoint_command[COMMAND_VALUE_INDEX],
                ):
                    # The temperature is different from our most recent command.
                    if (
                        self.last_heating_setpoint_command[COMMAND_VERIFIED_INDEX]
                        or (botengine.get_timestamp() - (utilities.ONE_MINUTE_MS))
                        > self.last_heating_setpoint_command[COMMAND_TIMESTAMP_INDEX]
                    ):
                        # Our last command was already verified, therefore this new measurement is an external adjustment.
                        # Or, our last command was delivered over 2 minutes ago, and the heating setpoint is now adjusted from what we set it to.
                        self.user_adjusted_timestamp = botengine.get_timestamp()
                        self.last_heating_setpoint_command = None

                        if self.location_object is not None:
                            # NOTE: Thermostat heating set point adjusted.
                            self.location_object.narrate(
                                botengine,
                                title=_("Heating set point adjusted"),
                                description=_(
                                    "Your '{}' heating set point is set to {}."
                                ).format(
                                    self.description,
                                    self._celsius_to_narrative(
                                        self.measurements[
                                            ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                                        ][0][0]
                                    ),
                                ),
                                priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                                icon="thermostat",
                                extra_json_dict={"device_id": self.device_id},
                                event_type="thermostat.thermostat_heating_setpoint",
                            )
                            analytics.track(
                                botengine,
                                self.location_object,
                                "thermostat_heating_setpoint",
                                properties={
                                    "device_id": self.device_id,
                                    "description": self.description,
                                    "ai": True,
                                    "heating_setpoint": self.measurements[
                                        ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                                    ][0][0],
                                },
                            )

                    else:
                        # Our last command wasn't verified, and it's been under 2 minutes. Keep waiting.
                        botengine.get_logger().info(
                            "[{} '{}'] Last heating setpoint command not verified and it's under 2 minutes, keep waiting".format(
                                self.device_id, self.description
                            )
                        )
                        pass

                else:
                    botengine.get_logger().info(
                        "[{} '{}'] Last heating setpoint command verified".format(
                            self.device_id, self.description
                        )
                    )
                    self.last_heating_setpoint_command = (
                        self.last_heating_setpoint_command[COMMAND_VALUE_INDEX],
                        self.last_heating_setpoint_command[COMMAND_TIMESTAMP_INDEX],
                        True,
                    )

            elif (
                name == ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE
                and self.last_system_mode_command is None
            ):
                # User adjusted the mode - we didn't send a command recently
                if self.location_object is not None:
                    # Thermostat set mode by user.
                    self.location_object.narrate(
                        botengine,
                        title=_("'{}' now set to {}").format(
                            self.description,
                            self.thermostat_mode_to_string(
                                self.measurements[
                                    ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE
                                ][0][0]
                            ),
                        ),
                        description=_("Your '{}' is now set to {}.").format(
                            self.description,
                            self.thermostat_mode_to_string(
                                self.measurements[
                                    ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE
                                ][0][0]
                            ),
                        ),
                        priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                        icon="thermostat",
                        extra_json_dict={"device_id": self.device_id},
                        event_type="thermostat.thermostat_mode",
                    )
                    analytics.track(
                        botengine,
                        self.location_object,
                        "thermostat_mode",
                        properties={
                            "device_id": self.device_id,
                            "description": self.description,
                            "ai": False,
                            "thermostat_mode": self.thermostat_mode_to_string(
                                self.measurements[
                                    ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE
                                ][0][0]
                            ),
                        },
                    )

            elif (
                name == ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                and self.last_cooling_setpoint_command is None
            ):
                # User adjusted the cooling setpoint - we didn't send a command recently.
                self.user_adjusted_timestamp = botengine.get_timestamp()

                if self.location_object is not None:
                    # NOTE: Thermostat adjusted the cooling setpoint by user.
                    self.location_object.narrate(
                        botengine,
                        title=_("Cooling set point adjusted"),
                        description=_(
                            "Your '{}' cooling set point was manually adjusted to {}."
                        ).format(
                            self.description,
                            self._celsius_to_narrative(
                                self.measurements[
                                    ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                                ][0][0]
                            ),
                        ),
                        priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                        icon="thermostat",
                        extra_json_dict={"device_id": self.device_id},
                        event_type="thermostat.thermostat_cooling_setpoint",
                    )

                    analytics.track(
                        botengine,
                        self.location_object,
                        "thermostat_cooling_setpoint",
                        properties={
                            "device_id": self.device_id,
                            "description": self.description,
                            "ai": False,
                            "cooling_setpoint": self.measurements[
                                ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                            ][0][0],
                        },
                    )

            elif (
                name == ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                and self.last_heating_setpoint_command is None
            ):
                # User adjusted the heating setpoint - we didn't send a command recently.
                self.user_adjusted_timestamp = botengine.get_timestamp()

                if self.location_object is not None:
                    # NOTE: Thermostat adjusted the heating setpoint by user.
                    self.location_object.narrate(
                        botengine,
                        title=_("Heating set point adjusted"),
                        description=_(
                            "Your '{}' heating set point was manually adjusted to {}."
                        ).format(
                            self.description,
                            self._celsius_to_narrative(
                                self.measurements[
                                    ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                                ][0][0]
                            ),
                        ),
                        priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                        icon="thermostat",
                        extra_json_dict={"device_id": self.device_id},
                        event_type="thermostat.thermostat_heating_setpoint",
                    )
                    analytics.track(
                        botengine,
                        self.location_object,
                        "thermostat_heating_setpoint",
                        properties={
                            "device_id": self.device_id,
                            "description": self.description,
                            "ai": False,
                            "heating_setpoint": self.measurements[
                                ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                            ][0][0],
                        },
                    )

        return measurement_updated

    def get_device_type_name(self):
        """
        Return the human-friendly name of this device
        :param language: Language, like 'en'
        :return: Human friendly name like "Centralite Pearl Thermostat"
        """
        raise NotImplementedError

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "thermostat"

    def get_system_mode(self, botengine=None):
        """
        Get the current system mode
        :param botengine:
        :return: None if the system mode has not been set yet
        """
        if ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE in self.measurements:
            return self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][
                0
            ]

        return None

    def is_cool_mode(self, botengine=None):
        """
        :param botengine:
        :return: True if the system is in COOL mode.
        """
        if ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE in self.measurements:
            return (
                self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][0]
                == self.SYSTEM_MODE__COOL
                or self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][
                    0
                ]
                == self.SYSTEM_MODE__PRECOOLING
            )

        return False

    def is_heat_mode(self, botengine=None):
        """
        :param botengine:
        :return: True if the system is in HEAT mode
        """
        if ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE in self.measurements:
            return (
                self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][0]
                == self.SYSTEM_MODE__HEAT
                or self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][
                    0
                ]
                == self.SYSTEM_MODE__EMERGENCY_HEAT
            )

        return False

    def get_ambient_temperature(self, botengine=None):
        """
        :param botengine:
        :return: ambient temperature in celsius. None if it's not available.
        """
        if ThermostatDevice.MEASUREMENT_NAME_AMBIENT_TEMPERATURE_C in self.measurements:
            return self.measurements[
                ThermostatDevice.MEASUREMENT_NAME_AMBIENT_TEMPERATURE_C
            ][0][0]

        return None

    def get_cooling_setpoint(self, botengine=None):
        """
        Get the cooling setpoint
        :param botengine: BotEngine environment
        :return: None if the cooling setpoint has not been set yet.
        """
        if ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C in self.measurements:
            return self.measurements[
                ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
            ][0][0]

        return None

    def get_heating_setpoint(self, botengine=None):
        """
        Get the heating setpoint
        :param botengine: BotEngine environment
        :return: None if the heating setpoint has not been set yet.
        """
        if ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C in self.measurements:
            return self.measurements[
                ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
            ][0][0]

        return None

    def get_dr_offset(self, botengine=None):
        """
        Return the current demand response offset in Celsius
        :param botengine: BotEngine environment
        :return: Float
        """
        dr_offset = 0.0
        for d in self.dr_stack_heat:
            if self.dr_stack_heat[d] > dr_offset:
                dr_offset = self.dr_stack_heat[d]

        for d in self.dr_stack_cool:
            if self.dr_stack_cool[d] > dr_offset:
                dr_offset = self.dr_stack_cool[d]

        return dr_offset

    def set_system_mode(self, botengine, system_mode, reliably=True):
        """
        Set the system mode
        :param botengine:
        :param system_mode:
        :param reliably: True to keep retrying to get the command through
        :return:
        """
        botengine.get_logger().info(
            "\t\t["
            + self.device_id
            + "]: Set system mode to {}".format(
                self.thermostat_mode_to_string(system_mode)
            )
        )
        self.last_system_mode_command = (system_mode, botengine.get_timestamp(), False)
        if reliably:
            send_command_reliably(
                botengine,
                self.device_id,
                ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE,
                system_mode,
            )
        else:
            botengine.send_command(
                self.device_id,
                ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE,
                system_mode,
            )

        # Because Dmitry says we might see specific errors better if we issue commands one-by-one, especially to cloud-connected thermostats.
        botengine.flush_commands()

    def set_cooling_setpoint(self, botengine, setpoint_celsius, reliably=False):
        """
        Set the cooling setpoint
        :param botengine: BotEngine environment
        :param setpoint_celsius: Absolute setpoint in Celsius
        :param reliably: True to keep retrying to get the command through
        """
        setpoint_celsius = float(setpoint_celsius)
        if self.is_temperature_different(
            setpoint_celsius,
            self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][0][
                0
            ],
        ):
            botengine.get_logger().info(
                "\t\t["
                + self.device_id
                + "] ("
                + self.description
                + "): Set cooling setpoint from "
                + str(
                    self.measurements[
                        ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                    ][0][0]
                )
                + " to "
                + str("%.1f" % setpoint_celsius)
            )
            self.last_cooling_setpoint_command = (
                setpoint_celsius,
                botengine.get_timestamp(),
                False,
            )

            if reliably:
                send_command_reliably(
                    botengine,
                    self.device_id,
                    ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C,
                    float(str("%.1f" % setpoint_celsius)),
                )
            else:
                botengine.send_command(
                    self.device_id,
                    ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C,
                    float(str("%.1f" % setpoint_celsius)),
                )

            # Because Dmitry says we might see specific errors better if we issue commands one-by-one, especially to cloud-connected thermostats.
            botengine.flush_commands()

        else:
            botengine.get_logger().info(
                "\t\t{}: Set cooling setpoint {} is the same as the current setpoint, skipping.".format(
                    self.device_id, str("%.1f" % setpoint_celsius)
                )
            )
            botengine.cancel_command(
                self.device_id, ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
            )
            cancel_reliable_command(
                botengine,
                self.device_id,
                ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C,
            )

    def set_heating_setpoint(self, botengine, setpoint_celsius, reliably=False):
        """
        Set the heating set-point
        :param botengine: BotEngine environmnet
        :param setpoint_celsius: Temperature in Celsius
        :param reliably: True to keep retrying to get the command through
        """
        setpoint_celsius = float(setpoint_celsius)
        if self.is_temperature_different(
            setpoint_celsius,
            self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][0][
                0
            ],
        ):
            botengine.get_logger().info(
                "\t\t["
                + self.device_id
                + "] ("
                + self.description
                + "): Set heating setpoint from "
                + str(
                    self.measurements[
                        ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                    ][0][0]
                )
                + " to "
                + str("%.1f" % setpoint_celsius)
            )
            self.last_heating_setpoint_command = (
                setpoint_celsius,
                botengine.get_timestamp(),
                False,
            )

            if reliably:
                send_command_reliably(
                    botengine,
                    self.device_id,
                    ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C,
                    float(str("%.1f" % setpoint_celsius)),
                )
            else:
                botengine.send_command(
                    self.device_id,
                    ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C,
                    float(str("%.1f" % setpoint_celsius)),
                )

            # Because Dmitry says we might see specific errors better if we issue commands one-by-one, especially to cloud-connected thermostats.
            botengine.flush_commands()

        else:
            botengine.get_logger().info(
                "\t\t{}: Set heating setpoint {} is the same as the current setpoint, skipping.".format(
                    self.device_id, str("%.1f" % setpoint_celsius)
                )
            )
            botengine.cancel_command(
                self.device_id, ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
            )
            cancel_reliable_command(
                botengine,
                self.device_id,
                ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C,
            )

    def set_cooler(self, botengine, offset_c=ONE_DEGREE_F_TO_C, reliably=False):
        """
        Set the thermostat cooler by the given offset in degrees C.
        May be useful for inducing the circadian rhythm to go to bed.
        :param botengine: BotEngine environment
        :param offset_c: Offset in degrees C to make the thermostat cooler. Default is 1 degree F.
        :param reliably: Deliver the command reliably (multiple retries)
        """
        if ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C in self.measurements:
            temperature_c = (
                self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][
                    0
                ][0]
                - offset_c
            )
            self.set_cooling_setpoint(botengine, temperature_c, reliably)

        if ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C in self.measurements:
            temperature_c = (
                self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][
                    0
                ][0]
                - offset_c
            )
            self.set_heating_setpoint(botengine, temperature_c, reliably)

    def record_preferred_home_setpoint(self, botengine):
        """
        Record the preferred setpoint right now for the home mode set point
        :param botengine: BotEngine environment
        """
        botengine.get_logger().info(
            "{} {}: Updating your preferred home set point".format(
                self.description, self.device_id
            )
        )
        system_mode = self.get_system_mode(botengine)
        if system_mode is not None:
            if (
                ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                in self.last_updated_params
            ):
                self.preferred_cooling_setpoint_home_c = self.measurements[
                    ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                ][0][0]
                # NOTE: Learned HOME thermostat cooling set point.
                self.location_object.narrate(
                    botengine,
                    title=_("'{}': Learned HOME cooling set point.").format(
                        self.description
                    ),
                    description=_(
                        "Your '{}' learned you want the cooling set point set to {} when you are home."
                    ).format(
                        self.description,
                        self._celsius_to_narrative(
                            self.preferred_cooling_setpoint_home_c
                        ),
                    ),
                    priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                    icon="thermostat",
                    extra_json_dict={"device_id": self.device_id},
                    event_type="thermostat.thermostat_cooling_setpoint_learned",
                )
                analytics.track(
                    botengine,
                    self.location_object,
                    "thermostat_cooling_setpoint_learned",
                    properties={
                        "device_id": self.device_id,
                        "description": self.description,
                        "thermostat_mode": "COOL",
                        "mode": "HOME",
                        "setpoint_c": self.preferred_cooling_setpoint_home_c,
                    },
                )

            if (
                ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                in self.last_updated_params
            ):
                self.preferred_heating_setpoint_home_c = self.measurements[
                    ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                ][0][0]
                # NOTE: Learned HOME thermostat heating set point.
                self.location_object.narrate(
                    botengine,
                    title=_("'{}': Learned HOME heating set point.").format(
                        self.description
                    ),
                    description=_(
                        "Your '{}' learned you want the heating set point set to {} when you are home."
                    ).format(
                        self.description,
                        self._celsius_to_narrative(
                            self.preferred_heating_setpoint_home_c
                        ),
                    ),
                    priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                    icon="thermostat",
                    extra_json_dict={"device_id": self.device_id},
                    event_type="thermostat.thermostat_heating_setpoint_learned",
                )
                analytics.track(
                    botengine,
                    self.location_object,
                    "thermostat_heating_setpoint_learned",
                    properties={
                        "device_id": self.device_id,
                        "description": self.description,
                        "thermostat_mode": "HEAT",
                        "mode": "HOME",
                        "setpoint_c": self.preferred_heating_setpoint_home_c,
                    },
                )

        # This number will represent the total amount of time across ALL devices.
        # For example, if you have 1 thermostat and a DR event for 10000s, then the total is 10000s.
        # But if you have 2 thermostats and a DR event for 10000s, then the total is 20000s
        analytics.people_set(
            botengine,
            self.location_object,
            {
                self.device_id
                + "_cooling_offset_sleep_c": self.preferred_cooling_offset_sleep_c,
                self.device_id
                + "_heating_offset_sleep_c": self.preferred_heating_offset_sleep_c,
                self.device_id
                + "_cooling_offset_away_c": self.preferred_cooling_offset_away_c,
                self.device_id
                + "_heating_offset_away_c": self.preferred_heating_offset_away_c,
                self.device_id
                + "_cooling_setpoint_home_c": self.preferred_cooling_setpoint_home_c,
                self.device_id
                + "_heating_setpoint_home_c": self.preferred_heating_setpoint_home_c,
            },
        )

    def record_preferred_sleep_offset(self, botengine):
        """
        Record the preferred temperature offset for sleep mode
        :param botengine:
        """
        botengine.get_logger().info(
            "{} {}: Updating your preferred sleep offset".format(
                self.description, self.device_id
            )
        )
        system_mode = self.get_system_mode(botengine)

        if system_mode is not None:
            if (
                ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                in self.last_updated_params
            ):
                current_absolute_setpoint_c = self.measurements[
                    ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                ][0][0]
                current_absolute_cooling_c = (
                    self.preferred_cooling_setpoint_home_c
                    + self.preferred_cooling_offset_sleep_c
                )

                if current_absolute_setpoint_c > current_absolute_cooling_c:
                    # More energy efficient.
                    self.preferred_cooling_offset_sleep_c += ONE_DEGREE_F_TO_C
                    botengine.get_logger().info(
                        "Sleep mode cooling offset is now more efficient (offset={}C)".format(
                            self.preferred_cooling_offset_sleep_c
                        )
                    )

                elif current_absolute_setpoint_c < current_absolute_cooling_c:
                    # Less energy efficient. Adjust it slightly, but don't hit 0 adjustment
                    self.preferred_cooling_offset_sleep_c -= ONE_DEGREE_F_TO_C
                    if self.preferred_cooling_offset_sleep_c < ONE_DEGREE_F_TO_C:
                        self.preferred_cooling_offset_sleep_c = ONE_DEGREE_F_TO_C
                    botengine.get_logger().info(
                        "Sleep mode cooling offset is now less efficient (offset={}C)".format(
                            self.preferred_cooling_offset_sleep_c
                        )
                    )

                # NOTE: Thermostat cooling setpoint learned night time preferences.
                self.location_object.narrate(
                    botengine,
                    title=_("'{}': Learned night time preferences.").format(
                        self.description
                    ),
                    description=_(
                        "Your '{}' learned the night time cooling setpoint."
                    ).format(self.description),
                    priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                    icon="thermostat",
                    extra_json_dict={"device_id": self.device_id},
                    event_type="thermostat.thermostat_cooling_sleep_setpoint_learned",
                )

                # analytics.track(botengine, self.location_object, 'thermostat_cooling_sleep_setpoint_learned', properties={
                #     "device_id": self.device_id,
                #     "description": self.description,
                #     "thermostat_mode": "COOL",
                #     "mode": "SLEEP",
                #     "preferred_cooling_offset_sleep_c": self.preferred_cooling_offset_sleep_c,
                #     "preferred_heating_offset_sleep_c": self.preferred_heating_offset_sleep_c,
                #     "preferred_cooling_offset_away_c": self.preferred_cooling_offset_away_c,
                #     "preferred_heating_offset_away_c": self.preferred_heating_offset_away_c,
                #     "preferred_cooling_setpoint_home_c": self.preferred_cooling_setpoint_home_c,
                #     "preferred_heating_setpoint_home_c": self.preferred_heating_setpoint_home_c})

            if (
                ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                in self.last_updated_params
            ):
                current_absolute_setpoint_c = self.measurements[
                    ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                ][0][0]
                current_absolute_heating_c = (
                    self.preferred_heating_setpoint_home_c
                    - self.preferred_heating_offset_sleep_c
                )

                if current_absolute_setpoint_c < current_absolute_heating_c:
                    # More energy efficient. Set it directly.
                    self.preferred_heating_offset_sleep_c += ONE_DEGREE_F_TO_C
                    botengine.get_logger().info(
                        "Sleep mode heating offset is now more efficient (offset={}C)".format(
                            self.preferred_heating_offset_sleep_c
                        )
                    )

                elif current_absolute_setpoint_c > current_absolute_heating_c:
                    # Less energy efficient. Adjust it slightly, but don't hit 0 adjustment
                    self.preferred_heating_offset_sleep_c -= ONE_DEGREE_F_TO_C
                    if self.preferred_heating_offset_sleep_c < ONE_DEGREE_F_TO_C:
                        self.preferred_heating_offset_sleep_c = ONE_DEGREE_F_TO_C
                    botengine.get_logger().info(
                        "Sleep mode heating offset is now less efficient (offset={}C)".format(
                            self.preferred_heating_offset_sleep_c
                        )
                    )

                # NOTE: Thermostat heating setpoint learned night time preferences.
                self.location_object.narrate(
                    botengine,
                    title=_("'{}': Learned night time preferences.").format(
                        self.description
                    ),
                    description=_(
                        "Your '{}' learned the night time heating setpoint."
                    ).format(self.description),
                    priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                    icon="thermostat",
                    extra_json_dict={"device_id": self.device_id},
                    event_type="thermostat.thermostat_heating_sleep_setpoint_learned",
                )

                # analytics.track(botengine, self.location_object, 'thermostat_heating_sleep_setpoint_learned', properties={
                #     "device_id": self.device_id,
                #     "description": self.description,
                #     "thermostat_mode": "HEAT",
                #     "mode": "SLEEP",
                #     "preferred_cooling_offset_sleep_c": self.preferred_cooling_offset_sleep_c,
                #     "preferred_heating_offset_sleep_c": self.preferred_heating_offset_sleep_c,
                #     "preferred_cooling_offset_away_c": self.preferred_cooling_offset_away_c,
                #     "preferred_heating_offset_away_c": self.preferred_heating_offset_away_c,
                #     "preferred_cooling_setpoint_home_c": self.preferred_cooling_setpoint_home_c,
                #     "preferred_heating_setpoint_home_c": self.preferred_heating_setpoint_home_c})

        # This number will represent the total amount of time across ALL devices.
        # For example, if you have 1 thermostat and a DR event for 10000s, then the total is 10000s.
        # But if you have 2 thermostats and a DR event for 10000s, then the total is 20000s
        analytics.people_set(
            botengine,
            self.location_object,
            {
                self.device_id
                + "_cooling_offset_sleep_c": self.preferred_cooling_offset_sleep_c,
                self.device_id
                + "_heating_offset_sleep_c": self.preferred_heating_offset_sleep_c,
                self.device_id
                + "_cooling_offset_away_c": self.preferred_cooling_offset_away_c,
                self.device_id
                + "_heating_offset_away_c": self.preferred_heating_offset_away_c,
                self.device_id
                + "_cooling_setpoint_home_c": self.preferred_cooling_setpoint_home_c,
                self.device_id
                + "_heating_setpoint_home_c": self.preferred_heating_setpoint_home_c,
            },
        )

    def record_preferred_away_offset(self, botengine):
        """
        Record the preferred temperature offset for away mode
        :param botengine:
        """
        botengine.get_logger().info(
            "{} {}: Updating your preferred away offset".format(
                self.description, self.device_id
            )
        )
        system_mode = self.get_system_mode(botengine)
        if system_mode is not None:
            if (
                ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                in self.last_updated_params
            ):
                current_absolute_setpoint_c = self.measurements[
                    ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C
                ][0][0]
                current_absolute_cooling_c = (
                    self.preferred_cooling_setpoint_home_c
                    + self.preferred_cooling_offset_away_c
                )

                if current_absolute_setpoint_c > current_absolute_cooling_c:
                    # More energy efficient.
                    self.preferred_cooling_offset_away_c += ONE_DEGREE_F_TO_C
                    botengine.get_logger().info(
                        "Away mode cooling offset is now more efficient (offset={}C)".format(
                            self.preferred_cooling_offset_away_c
                        )
                    )

                elif current_absolute_setpoint_c < current_absolute_cooling_c:
                    # Less energy efficient. Adjust it slightly, but don't hit 0 adjustment
                    self.preferred_cooling_offset_away_c -= ONE_DEGREE_F_TO_C
                    if self.preferred_cooling_offset_away_c < ONE_DEGREE_F_TO_C:
                        self.preferred_cooling_offset_away_c = ONE_DEGREE_F_TO_C
                    botengine.get_logger().info(
                        "Away mode cooling offset is now less efficient (offset={}C)".format(
                            self.preferred_cooling_offset_away_c
                        )
                    )

                # NOTE: Thermostat cooling setpoint learned away preferences.
                self.location_object.narrate(
                    botengine,
                    title=_("'{}': Learned away preferences.").format(self.description),
                    description=_(
                        "Your '{}' learned the away cooling setpoint should be {} from HOME mode."
                    ).format(
                        self.description,
                        self._celsius_to_narrative(
                            self.preferred_cooling_offset_away_c
                        ),
                    ),
                    priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                    icon="thermostat",
                    extra_json_dict={
                        "device_id": self.device_id,
                        "preferred_cooling_offset_sleep_c": self.preferred_cooling_offset_sleep_c,
                        "preferred_heating_offset_sleep_c": self.preferred_heating_offset_sleep_c,
                        "preferred_cooling_offset_away_c": self.preferred_cooling_offset_away_c,
                        "preferred_heating_offset_away_c": self.preferred_heating_offset_away_c,
                        "preferred_cooling_setpoint_home_c": self.preferred_cooling_setpoint_home_c,
                        "preferred_heating_setpoint_home_c": self.preferred_heating_setpoint_home_c,
                    },
                    event_type="thermostat.thermostat_cooling_away_setpoint_learned",
                )

                # analytics.track(botengine, self.location_object, 'thermostat_cooling_away_setpoint_learned', properties={
                #     "device_id": self.device_id,
                #     "description": self.description,
                #     "thermostat_mode": "COOL",
                #     "mode": "AWAY",
                #     "preferred_cooling_offset_sleep_c": self.preferred_cooling_offset_sleep_c,
                #     "preferred_heating_offset_sleep_c": self.preferred_heating_offset_sleep_c,
                #     "preferred_cooling_offset_away_c": self.preferred_cooling_offset_away_c,
                #     "preferred_heating_offset_away_c": self.preferred_heating_offset_away_c,
                #     "preferred_cooling_setpoint_home_c": self.preferred_cooling_setpoint_home_c,
                #     "preferred_heating_setpoint_home_c": self.preferred_heating_setpoint_home_c})

            if (
                ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                in self.last_updated_params
            ):
                current_absolute_setpoint_c = self.measurements[
                    ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C
                ][0][0]
                current_absolute_heating_c = (
                    self.preferred_heating_setpoint_home_c
                    - self.preferred_heating_offset_away_c
                )

                if current_absolute_setpoint_c < current_absolute_heating_c:
                    # More energy efficient. Set it directly.
                    self.preferred_heating_offset_away_c += ONE_DEGREE_F_TO_C
                    botengine.get_logger().info(
                        "Away mode heating offset is now more efficient (offset={}C)".format(
                            self.preferred_heating_offset_away_c
                        )
                    )

                elif current_absolute_setpoint_c > current_absolute_heating_c:
                    # Less energy efficient. Adjust it slightly, but don't hit 0 adjustment
                    self.preferred_heating_offset_away_c -= ONE_DEGREE_F_TO_C
                    if self.preferred_heating_offset_away_c < ONE_DEGREE_F_TO_C:
                        self.preferred_heating_offset_away_c = ONE_DEGREE_F_TO_C
                    botengine.get_logger().info(
                        "Away mode heating offset is now less efficient (offset={}C)".format(
                            self.preferred_heating_offset_away_c
                        )
                    )

                # NOTE: Thermostat heating setpoint learned away preferences.
                self.location_object.narrate(
                    botengine,
                    title=_("'{}': Learned night time preferences.").format(
                        self.description
                    ),
                    description=_(
                        "Your '{}' learned the away heating setpoint should be {} from HOME mode."
                    ).format(
                        self.description,
                        self._celsius_to_narrative(
                            self.preferred_heating_offset_away_c
                        ),
                    ),
                    priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                    icon="thermostat",
                    extra_json_dict={
                        "device_id": self.device_id,
                        "preferred_cooling_offset_sleep_c": self.preferred_cooling_offset_sleep_c,
                        "preferred_heating_offset_sleep_c": self.preferred_heating_offset_sleep_c,
                        "preferred_cooling_offset_away_c": self.preferred_cooling_offset_away_c,
                        "preferred_heating_offset_away_c": self.preferred_heating_offset_away_c,
                        "preferred_cooling_setpoint_home_c": self.preferred_cooling_setpoint_home_c,
                        "preferred_heating_setpoint_home_c": self.preferred_heating_setpoint_home_c,
                    },
                    event_type="thermostat.thermostat_heating_away_setpoint_learned",
                )

                # analytics.track(botengine, self.location_object, 'thermostat_heating_away_setpoint_learned', properties={
                #     "device_id": self.device_id,
                #     "description": self.description,
                #     "thermostat_mode": "HEAT",
                #     "mode": "AWAY",
                #     "preferred_cooling_offset_sleep_c": self.preferred_cooling_offset_sleep_c,
                #     "preferred_heating_offset_sleep_c": self.preferred_heating_offset_sleep_c,
                #     "preferred_cooling_offset_away_c": self.preferred_cooling_offset_away_c,
                #     "preferred_heating_offset_away_c": self.preferred_heating_offset_away_c,
                #     "preferred_cooling_setpoint_home_c": self.preferred_cooling_setpoint_home_c,
                #     "preferred_heating_setpoint_home_c": self.preferred_heating_setpoint_home_c})

        # This number will represent the total amount of time across ALL devices.
        # For example, if you have 1 thermostat and a DR event for 10000s, then the total is 10000s.
        # But if you have 2 thermostats and a DR event for 10000s, then the total is 20000s
        analytics.people_set(
            botengine,
            self.location_object,
            {
                self.device_id
                + "_cooling_offset_sleep_c": self.preferred_cooling_offset_sleep_c,
                self.device_id
                + "_heating_offset_sleep_c": self.preferred_heating_offset_sleep_c,
                self.device_id
                + "_cooling_offset_away_c": self.preferred_cooling_offset_away_c,
                self.device_id
                + "_heating_offset_away_c": self.preferred_heating_offset_away_c,
                self.device_id
                + "_cooling_setpoint_home_c": self.preferred_cooling_setpoint_home_c,
                self.device_id
                + "_heating_setpoint_home_c": self.preferred_heating_setpoint_home_c,
            },
        )

    def set_demand_response(self, botengine, active, identifier="dr", offset_c=0):
        """
        Activate demand response, preventing the maximum setpoint from going above the desired DR setpoint if one is defined
        :param botengine: BotEngine environment
        :param active: True to activate the DR event, False to deactivate it.
        :param offset_c: Temperature offset in Celsius relative to the user's preferred temperature
        :param identifier: Identifier of this DR event so it can be updated and cancelled later.
        :return:
        """
        botengine.get_logger().info(
            "thermostat.set_demand_response: active={}; id={}; offset_c={}".format(
                active, identifier, offset_c
            )
        )
        if active:
            self.location_object.increment_location_property(
                botengine, "{}_total_dr_policies_applied".format(self.device_id)
            )
            self.dr_stack_heat[identifier] = offset_c
            self.dr_stack_cool[identifier] = offset_c

        else:
            if identifier in self.dr_stack_cool:
                del self.dr_stack_cool[identifier]

            if identifier in self.dr_stack_heat:
                del self.dr_stack_heat[identifier]

        return self.apply_offsets(botengine)

    def set_energy_efficiency(
        self, botengine, active, identifier, offset_c=2.4, change_temperature=True
    ):
        """
        Adjusting the setpoint in a direction that saves energy by some statically defined offset relative to the preferred temperature while the user is home.
        Energy efficiency offset stack. Once you apply an EE offset, you must later remove it. The thermostat will apply the most aggressive active offset.
        :param botengine: BotEngine environment
        :param active: True to make this energy efficiency setting active, False to deactivate it.
        :param offset_c: Temperature offset it Celsius relative to the preferred temperature when the user is home
        :param identifier: Unique name for this energy efficiency offset, so it can be later cancelled.
        :param change_temperature: True to apply changes now
        :return: the system mode if the thermostat was paused successfully, None if the thermostat was not paused.
        """
        botengine.get_logger().info(
            "thermostat.set_energy_efficiency: active={}; id={}; offset_c={}".format(
                active, identifier, offset_c
            )
        )
        if active:
            self.location_object.increment_location_property(
                botengine, "{}_total_ee_policies_applied".format(self.device_id)
            )
            self.ee_stack_cool[identifier] = offset_c
            self.ee_stack_heat[identifier] = offset_c

            if change_temperature:
                return self.apply_offsets(botengine)

        else:
            found = False
            if identifier in self.ee_stack_cool:
                found = True
                del self.ee_stack_cool[identifier]

            if identifier in self.ee_stack_heat:
                found = True
                del self.ee_stack_heat[identifier]

            if found and change_temperature:
                return self.apply_offsets(botengine)

        return self.get_system_mode(botengine) != self.SYSTEM_MODE__OFF

    def cancel_all_energy_efficiency(self, botengine, change_temperature=True):
        """
        Cancel all energy efficiency offsets
        :param botengine:
        :param change_temperature: Forcefully change the temperature to apply the home mode offset.
        :return:
        """
        self.ee_stack_cool = {}
        self.ee_stack_heat = {}

        if change_temperature:
            return self.apply_offsets(botengine)

        return None

    def apply_offsets(self, botengine):
        """
        Take whatever active DR and EE offsets have been configured relative to the preferred setpoint while home,
        and apply them to this thermostat.
        :param botengine: BotEngine environment
        :return: The system mode of the thermostat if applied, None if the thermostat isn't on and the setpoints currently don't matter.
        """
        system_mode = self.get_system_mode(botengine)

        if system_mode is None:
            return None

        policies = {}

        heat_dr_offset = None
        for d in self.dr_stack_heat:
            if heat_dr_offset is None:
                heat_dr_offset = self.dr_stack_heat[d]

            elif self.dr_stack_heat[d] > heat_dr_offset:
                heat_dr_offset = self.dr_stack_heat[d]

            policies["heat_dr_policy-" + str(d)] = self.dr_stack_heat[d]

        if heat_dr_offset is None:
            # No DR
            heat_dr_offset = 0.0

        cool_dr_offset = None
        for d in self.dr_stack_cool:
            if cool_dr_offset is None:
                cool_dr_offset = self.dr_stack_cool[d]

            elif self.dr_stack_cool[d] > cool_dr_offset:
                cool_dr_offset = self.dr_stack_cool[d]

            policies["cool_dr_policy-" + str(d)] = self.dr_stack_cool[d]

        if cool_dr_offset is None:
            # No DR
            cool_dr_offset = 0.0

        heat_ee_offset = None
        for e in self.ee_stack_heat:
            if heat_ee_offset is None:
                heat_ee_offset = self.ee_stack_heat[e]

            elif self.ee_stack_heat[e] > heat_ee_offset:
                heat_ee_offset = self.ee_stack_heat[e]

            policies["heat_ee_policy-" + str(e)] = self.ee_stack_heat[e]

        if heat_ee_offset is None:
            heat_ee_offset = 0.0

        cool_ee_offset = None
        for e in self.ee_stack_cool:
            if cool_ee_offset is None:
                cool_ee_offset = self.ee_stack_cool[e]

            elif self.ee_stack_cool[e] > cool_ee_offset:
                cool_ee_offset = self.ee_stack_cool[e]

            policies["cool_ee_policy-" + str(e)] = self.ee_stack_cool[e]

        if cool_ee_offset is None:
            cool_ee_offset = 0.0

        policies["heat_ee_offset"] = heat_ee_offset
        policies["heat_dr_offset"] = heat_dr_offset
        policies["cool_ee_offset"] = heat_ee_offset
        policies["cool_dr_offset"] = heat_dr_offset
        policies["total_offset_c"] = heat_ee_offset + heat_dr_offset
        policies["device_id"] = self.device_id
        policies["device_description"] = self.description
        policies["is_connected"] = self.is_connected
        policies["thermostat_mode"] = self.thermostat_mode_to_string(system_mode)

        if self.dr_timestamp_ms is not None:
            policies["dr_start_timestamp_ms"] = self.dr_timestamp_ms

        if self.ee_timestamp_ms is not None:
            policies["ee_start_timestamp_ms"] = self.ee_timestamp_ms

        if system_mode is not None and self.is_connected:
            if (
                abs(heat_ee_offset + heat_dr_offset + cool_ee_offset + cool_dr_offset)
                != self.last_offset_c
            ):
                cooling_setpoint_celsius = float(
                    self.preferred_cooling_setpoint_home_c
                    + cool_ee_offset
                    + cool_dr_offset
                )
                heating_setpoint_celsius = float(
                    self.preferred_heating_setpoint_home_c
                    - heat_ee_offset
                    - heat_dr_offset
                )

                if cooling_setpoint_celsius > MAXIMUM_COOLING_SETPOINT_C:
                    cooling_setpoint_celsius = MAXIMUM_COOLING_SETPOINT_C

                if heating_setpoint_celsius < MINIMUM_HEATING_SETPOINT_C:
                    heating_setpoint_celsius = MINIMUM_HEATING_SETPOINT_C

                self.set_cooling_setpoint(botengine, cooling_setpoint_celsius)
                self.set_heating_setpoint(botengine, heating_setpoint_celsius)

                policies["preferred_cooling_setpoint_home_c"] = (
                    self.preferred_cooling_setpoint_home_c
                )
                policies["cooling_temperature_c"] = cooling_setpoint_celsius
                policies["preferred_heating_setpoint_home_c"] = (
                    self.preferred_heating_setpoint_home_c
                )
                policies["heating_temperature_c"] = heating_setpoint_celsius

                # NOTE: Thermostat update the policy.
                self.location_object.narrate(
                    botengine,
                    title=_("'{}': Applying energy policies").format(self.description),
                    description=_(
                        "Your new cooling set point is {} and heating setpoint is {}."
                    ).format(
                        self._celsius_to_narrative(cooling_setpoint_celsius),
                        self._celsius_to_narrative(heating_setpoint_celsius),
                    ),
                    priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                    icon="thermostat",
                    extra_json_dict={"device_id": self.device_id},
                    event_type="thermostat.thermostat_policy_update",
                )

                if (
                    abs(
                        heat_ee_offset
                        + heat_dr_offset
                        + cool_ee_offset
                        + cool_dr_offset
                    )
                    > 0.0
                ):
                    analytics.track(
                        botengine,
                        self.location_object,
                        "thermostat_policy_set",
                        properties=policies,
                    )
                else:
                    analytics.track(
                        botengine,
                        self.location_object,
                        "thermostat_policy_unset",
                        properties=policies,
                    )

                self.last_offset_c = abs(
                    heat_ee_offset + heat_dr_offset + cool_ee_offset + cool_dr_offset
                )

                if heat_ee_offset + cool_ee_offset > 0:
                    # Some EE
                    if self.ee_timestamp_ms is None:
                        self.ee_timestamp_ms = botengine.get_timestamp()

                else:
                    # No EE
                    if self.ee_timestamp_ms is not None:
                        # End of all EE events
                        duration_s = (
                            botengine.get_timestamp() - self.ee_timestamp_ms
                        ) / 1000
                        self.ee_timestamp_ms = None
                        analytics.track(
                            botengine,
                            self.location_object,
                            "ee_complete",
                            properties={
                                "duration_s": duration_s,
                                "device_id": self.device_id,
                                "description": self.description,
                            },
                        )

                        # This number will represent the total amount of time across ALL devices.
                        # For example, if you have 1 thermostat and a EE event for 10000s, then the total is 10000s.
                        # But if you have 2 thermostats and a EE event for 10000s, then the total is 20000s
                        analytics.people_increment(
                            botengine, self.location_object, {"ee_total_s": duration_s}
                        )

                if heat_dr_offset + cool_dr_offset > 0:
                    # Some DR
                    if self.dr_timestamp_ms is None:
                        self.dr_timestamp_ms = botengine.get_timestamp()

                else:
                    # No DR
                    if self.dr_timestamp_ms is not None:
                        # End of all DR events
                        duration_s = (
                            botengine.get_timestamp() - self.dr_timestamp_ms
                        ) / 1000
                        self.dr_timestamp_ms = None
                        analytics.track(
                            botengine,
                            self.location_object,
                            "dr_complete",
                            properties={
                                "duration_s": duration_s,
                                "device_id": self.device_id,
                                "description": self.description,
                            },
                        )

                        # This number will represent the total amount of time across ALL devices.
                        # For example, if you have 1 thermostat and a DR event for 10000s, then the total is 10000s.
                        # But if you have 2 thermostats and a DR event for 10000s, then the total is 20000s
                        analytics.people_increment(
                            botengine, self.location_object, {"dr_total_s": duration_s}
                        )

                return system_mode

        return None

    def increment_away_energy_efficiency(self, botengine):
        """
        Increment away mode energy efficiency
        :param botengine:
        :return:
        """
        self.increment_energy_efficiency(botengine, "away")

    def increment_sleep_energy_efficiency(self, botengine):
        """
        Increment sleep mode energy efficiency
        :param botengine:
        :return:
        """
        self.increment_energy_efficiency(botengine, "sleep")

    def increment_energy_efficiency(self, botengine, identifier, max_offset_c=2.4):
        """
        Increment the degrees F in a direction that saves energy up to some max.
        This can be called multiple times (up to 3).
        :param botengine: BotEngine environment
        :param max_relative_offset_c: Maximum offset in degrees C to achieve relative to our preferred temperature while in HOME mode. The thermostat increments to this max level after 3 calls to this method.
        :return: the system mode if the thermostat was paused successfully, None if the thermostat was not paused.
        """
        if identifier not in self.ee_stack_cool:
            self.ee_stack_cool[identifier] = 0.0

        if identifier not in self.ee_stack_heat:
            self.ee_stack_heat[identifier] = 0.0

        self.location_object.increment_location_property(
            botengine, "{}_total_ee_incremental_policies_applied".format(self.device_id)
        )

        # Correct the maximum offset
        if "sleep" in identifier:
            self.ee_stack_heat[identifier] += self.preferred_heating_offset_sleep_c / 3
            if self.ee_stack_heat[identifier] > self.preferred_heating_offset_sleep_c:
                self.ee_stack_heat[identifier] = self.preferred_heating_offset_sleep_c

            self.ee_stack_cool[identifier] += self.preferred_cooling_offset_sleep_c / 3
            if self.ee_stack_cool[identifier] > self.preferred_cooling_offset_sleep_c:
                self.ee_stack_cool[identifier] = self.preferred_cooling_offset_sleep_c

        elif "away" in identifier:
            self.ee_stack_heat[identifier] += self.preferred_heating_offset_away_c / 3
            if self.ee_stack_heat[identifier] > self.preferred_heating_offset_away_c:
                self.ee_stack_heat[identifier] = self.preferred_heating_offset_away_c

            self.ee_stack_cool[identifier] += self.preferred_cooling_offset_away_c / 3
            if self.ee_stack_cool[identifier] > self.preferred_cooling_offset_away_c:
                self.ee_stack_cool[identifier] = self.preferred_cooling_offset_away_c

        else:
            self.ee_stack_cool[identifier] += max_offset_c / 3
            if self.ee_stack_cool[identifier] > max_offset_c:
                self.ee_stack_cool[identifier] = max_offset_c

            self.ee_stack_heat[identifier] += max_offset_c / 3
            if self.ee_stack_heat[identifier] > max_offset_c:
                self.ee_stack_heat[identifier] = max_offset_c

        return self.apply_offsets(botengine)

    def set_energy_efficiency_away(self, botengine):
        """
        Add an energy efficiency policy for away mode
        :param botengine: BotEngine environment
        :param identifier: Identifier so we can cancel or modify this energy efficiency policy later.
        :return: The current system mode if the change went into effect, None if nothing happened.
        """
        # Turn off Sleep mode policies
        self.set_energy_efficiency(botengine, False, "sleep", change_temperature=False)
        self.location_object.increment_location_property(
            botengine, "{}_total_ee_away_policies_applied".format(self.device_id)
        )

        self.ee_stack_heat["away"] = self.preferred_heating_offset_away_c
        self.ee_stack_cool["away"] = self.preferred_cooling_offset_away_c

        return self.apply_offsets(botengine)

    def set_energy_efficiency_sleep(self, botengine):
        """
        Add an energy efficiency policy for sleep mode
        :param botengine: BotEngine environment
        :param identifier: Identifier so we can cancel or modify this energy efficiency policy later.
        :return: The current system mode if the change went into effect, Nothing if nothing happened
        """
        # Turn off Away mode policies
        self.set_energy_efficiency(botengine, False, "away", change_temperature=False)

        self.location_object.increment_location_property(
            botengine, "{}_total_ee_sleep_policies_applied".format(self.device_id)
        )

        self.ee_stack_heat["sleep"] = self.preferred_heating_offset_sleep_c
        self.ee_stack_cool["sleep"] = self.preferred_cooling_offset_sleep_c

        return self.apply_offsets(botengine)

    def set_energy_efficiency_home(self, botengine):
        """
        Turn off all away and sleep energy efficiency policies
        :param botengine: BotEngine environment
        """
        botengine.get_logger().info(
            "{}: set_energy_efficiency_home".format(self.device_id)
        )
        away_result = self.set_energy_efficiency(botengine, False, "away")
        sleep_result = self.set_energy_efficiency(botengine, False, "sleep")

        self.location_object.increment_location_property(
            botengine, "{}_total_ee_home_policies_applied".format(self.device_id)
        )

        if away_result is None and sleep_result is None:
            # Nothing else applied offsets, so make sure we sync up at least once.
            self.apply_offsets(botengine)

    def thermostat_mode_to_string(self, mode):
        """
        Transform the thermostat's enumerated mode into an all-caps string
        :param mode: The mode
        :returns: String
        """
        if mode is None:
            return "UNKNOWN"

        mode = int(mode)
        if mode == ThermostatDevice.SYSTEM_MODE__OFF:
            return "OFF"
        elif mode == ThermostatDevice.SYSTEM_MODE__AUTO:
            return "AUTO"
        elif mode == ThermostatDevice.SYSTEM_MODE__COOL:
            return "COOL"
        elif mode == ThermostatDevice.SYSTEM_MODE__HEAT:
            return "HEAT"
        elif mode == ThermostatDevice.SYSTEM_MODE__EMERGENCY_HEAT:
            return "EMERGENCY HEAT"
        elif mode == ThermostatDevice.SYSTEM_MODE__PRECOOLING:
            return "PRECOOLING"
        elif mode == ThermostatDevice.SYSTEM_MODE__FAN_ONLY:
            return "FAN ONLY"

        return "UNKNOWN"

    def is_temperature_different(self, a, b, tolerance=0.1):
        """
        :return: True if the degrees Celsius are truly that different
        """
        # TODO there's gotta be a better way...
        # But when you're comparing two Decimal numbers that look like this, what can we do?
        # a=26.199999999999999289457264239899814128875732421875
        # b=26.16666666666666429819088079966604709625244140625

        if a is None or b is None:
            return True

        a = float("%.1f" % a)
        b = float("%.1f" % b)

        return abs(a - b) > tolerance

    def _celsius_to_narrative(self, temperature_c):
        return "{}°F / {}°C".format(
            str("%.1f" % float(utilities.celsius_to_fahrenheit(temperature_c))),
            str("%.1f" % float(temperature_c)),
        )
