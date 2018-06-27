'''
Created on March 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device
from devices.device import send_command_reliably
from devices.device import cancel_reliable_command

import utilities

# Element index numbers for our last_command_* tuples
COMMAND_VALUE_INDEX = 0
COMMAND_TIMESTAMP_INDEX = 1
COMMAND_VERIFIED_INDEX = 2

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

class ThermostatDevice(Device):
    '''
    Abstract Thermostat class, providing a predictable interface for all Thermostat definition
    '''
    # Parameter names
    MEASUREMENT_NAME_AMBIENT_TEMPERATURE_C = 'degC'
    MEASUREMENT_NAME_SYSTEM_MODE = 'systemMode'
    MEASUREMENT_NAME_COOLING_SETPOINT_C = 'coolingSetpoint'
    MEASUREMENT_NAME_HEATING_SETPOINT_C = 'heatingSetpoint'
    MEASUREMENT_NAME_FAN_MODE = 'fanMode'
    MEASUREMENT_NAME_MANUFACTURER = 'manufacturer'
    MEASUREMENT_NAME_MODEL = 'model'
    
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

    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):

        # Whether we've saved the state of this thermostat
        self.ee_active = False

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
        self.ee_stack = {}

        # Stack of demand response policies.
        # Each policy is a dictionary of the form:
        #
        #   "name of the policy so it can be cancelled later": offset_c relative to the user's preferred temperature while home (always a positive number)
        #
        # The act of having a policy stored implies the policy is active.
        # The most aggressive demand response policy is applied.
        # Demand response policies are additive to any current energy efficiency policies.
        self.dr_stack = {}

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
        self.preferred_cooling_offset_away_c = 2.4 # 5F

        # Preferred cooling offset when we're in away mode
        self.preferred_heating_offset_sleep_c = 2.4  # 5F

        # Preferred heating offset when we're in away mode
        self.preferred_cooling_offset_sleep_c = 2.4  # 5F

        Device.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)


    def initialize(self, botengine):
        '''
        Initializer
        :param botengine: BotEngine
        '''
        Device.initialize(self, botengine)

        if not hasattr(self, "ee_offset_c"):
            self.ee_offset_c = None

        if not hasattr(self, "absolute_max_cooling_offset_c"):
            self.absolute_max_cooling_offset_c = 8.3

        if not hasattr(self, 'absolute_max_heating_offset_c'):
            self.absolute_max_heating_offset_c = 8.3

        if not hasattr(self, 'dr_stack'):
            self.dr_stack = {}

        if not hasattr(self, 'ee_active'):
            self.ee_active = False

        if not hasattr(self, 'ee_offset_c'):
            self.ee_offset_c = None

        if not hasattr(self, 'ee_stack'):
            self.ee_stack = {}

        if not hasattr(self, 'last_cooling_setpoint_command'):
            self.last_cooling_setpoint_command = None

        if not hasattr(self, 'last_heating_setpoint_command'):
            self.last_heating_setpoint_command = None

        if not hasattr(self, 'last_system_mode_colmmand'):
            self.last_system_mode_command = None

        if not hasattr(self, 'preferred_cooling_offset_away_c'):
            self.preferred_cooling_offset_away_c = 2.4

        if not hasattr(self, 'preferred_heating_offset_away_c'):
            self.preferred_heating_offset_away_c = 2.4

        if not hasattr(self, 'preferred_cooling_setpoint_home_c'):
            self.preferred_cooling_setpoint_home_c = 23.9

        if not hasattr(self, 'preferred_heating_setpoint_home_c'):
            self.preferred_heating_setpoint_home_c = 20.0

        if not hasattr(self, 'preferred_cooling_offset_sleep_c'):
            self.preferred_cooling_offset_sleep_c = 2.4

        if not hasattr(self, 'preferred_heating_offset_sleep_c'):
            self.preferred_heating_offset_sleep_c = 2.4

        if not hasattr(self, 'saved_system_mode'):
            self.saved_system_mode = None

        if not hasattr(self, 'user_adjusted_timestamp'):
            self.user_adjusted_timestamp = None

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
        Device.add_measurement(self, botengine, name, value, timestamp)

        # Sometimes the user adjusts the thermostat during or immediately after a command is sent.
        # In that case, the reliability() methods underneath end up overridding the user, which is a cause for anger and backlash.
        # If we're controlling the thermostat alone, the setpoint should either be what it used to be or it should be what we're setting it to now.
        # TODO Check to see if a new setpoint has appeared which is neither what it used to be nor what we're setting it to now - this is the user overriding us and we should give in to that.
        # The one case where that doesn't work is if the user was right in front of their thermostat when we change the temperature, and they immediately set it back to what it used to be.
        # Can we check the timestamp when the value was updated to know if it was actually adjusted, or just old data?
        if name in self.measurements:
            if name == ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE and self.last_system_mode_command is not None:
                if self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][0] != self.last_system_mode_command[COMMAND_VALUE_INDEX]:
                    # Latest measurement doesn't match up with the last command we sent.
                    if self.last_system_mode_command[COMMAND_VERIFIED_INDEX] or (botengine.get_timestamp() - (utilities.ONE_MINUTE_MS * 2)) > self.last_system_mode_command[COMMAND_TIMESTAMP_INDEX]:
                        # Our last command was already verified, therefore this new measurement is an external adjustment.
                        # Or, our last command never got verified, but it's been over 2 minutes ago. The system mode is now adjusted from what we set it to.
                        self.user_adjusted_timestamp = botengine.get_timestamp()
                        self.last_system_mode_command = None

                    else:
                        # Our last command wasn't verified, and it's been under 2 minutes. Keep waiting.
                        botengine.get_logger().info("[{} '{}'] Last system mode command not verified and it's under 2 minutes, keep waiting".format(self.device_id, self.description))
                        pass

                else:
                    botengine.get_logger().info("[{} '{}'] Last system mode command verified".format(self.device_id, self.description))
                    self.last_system_mode_command = (self.last_system_mode_command[COMMAND_VALUE_INDEX], self.last_system_mode_command[COMMAND_TIMESTAMP_INDEX], True)

            elif name == ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C and self.last_cooling_setpoint_command is not None:
                if self.is_temperature_different(self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][0][0], self.last_cooling_setpoint_command[COMMAND_VALUE_INDEX]):
                    if self.last_cooling_setpoint_command[COMMAND_VERIFIED_INDEX] or (botengine.get_timestamp() - (utilities.ONE_MINUTE_MS * 2)) > self.last_cooling_setpoint_command[COMMAND_TIMESTAMP_INDEX]:
                        # Our last command was already verified, therefore this new measurement is an external adjustment.
                        # Or, our last command was delivered over 2 minutes ago, and the cooling setpoint is now adjusted from what we set it to.
                        self.user_adjusted_timestamp = botengine.get_timestamp()
                        self.last_cooling_setpoint_command = None

                    else:
                        # Our last command wasn't verified, and it's been under 2 minutes. Keep waiting.
                        botengine.get_logger().info("[{} '{}'] Last cooling setpoint command not verified and it's under 2 minutes, keep waiting".format(self.device_id, self.description))
                        pass

                else:
                    botengine.get_logger().info("[{} '{}'] Last cooling setpoint command verified".format(self.device_id, self.description))
                    self.last_cooling_setpoint_command = (self.last_cooling_setpoint_command[COMMAND_VALUE_INDEX], self.last_cooling_setpoint_command[COMMAND_TIMESTAMP_INDEX], True)

            elif name == ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C and self.last_heating_setpoint_command is not None:
                # Heating setpoint measurement received
                if self.is_temperature_different(self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][0][0], self.last_heating_setpoint_command[COMMAND_VALUE_INDEX]):
                    # The temperature is different from our most recent command.
                    if self.last_heating_setpoint_command[COMMAND_VERIFIED_INDEX] or (botengine.get_timestamp() - (utilities.ONE_MINUTE_MS * 2)) > self.last_heating_setpoint_command[COMMAND_TIMESTAMP_INDEX]:
                        # Our last command was already verified, therefore this new measurement is an external adjustment.
                        # Or, our last command was delivered over 2 minutes ago, and the heating setpoint is now adjusted from what we set it to.
                        self.user_adjusted_timestamp = botengine.get_timestamp()
                        self.last_heating_setpoint_command = None

                    else:
                        # Our last command wasn't verified, and it's been under 2 minutes. Keep waiting.
                        botengine.get_logger().info("[{} '{}'] Last heating setpoint command not verified and it's under 2 minutes, keep waiting".format(self.device_id, self.description))
                        pass

                else:
                    botengine.get_logger().info("[{} '{}'] Last heating setpoint command verified".format(self.device_id, self.description))
                    self.last_heating_setpoint_command = (self.last_heating_setpoint_command[COMMAND_VALUE_INDEX], self.last_heating_setpoint_command[COMMAND_TIMESTAMP_INDEX], True)

            elif name == ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C and self.last_cooling_setpoint_command is None:
                # User adjusted the cooling setpoint - we didn't send a command recently.
                self.user_adjusted_timestamp = botengine.get_timestamp()

            elif name == ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C and self.last_heating_setpoint_command is None:
                # User adjusted the heating setpoint - we didn't send a command recently.
                self.user_adjusted_timestamp = botengine.get_timestamp()

    def get_device_type_name(self, language):
        '''
        Return the human-friendly name of this device
        :param language: Language, like 'en'
        :return: Human friendly name like "Centralite Pearl Thermostat"
        '''
        raise NotImplementedError
    
    def get_image_name(self, botengine=None):
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
            return self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][0]

        return None

    def is_cool_mode(self, botengine=None):
        """
        :param botengine:
        :return: True if the system is in COOL mode.
        """
        if ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE in self.measurements:
            return self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][0] == self.SYSTEM_MODE__COOL or self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][0] == self.SYSTEM_MODE__PRECOOLING

        return False

    def is_heat_mode(self, botengine=None):
        """
        :param botengine:
        :return: True if the system is in HEAT mode
        """
        if ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE in self.measurements:
            return self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][0] == self.SYSTEM_MODE__HEAT or self.measurements[ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE][0][0] == self.SYSTEM_MODE__EMERGENCY_HEAT

        return False

    def get_ambient_temperature(self, botengine=None):
        """
        :param botengine:
        :return: ambient temperature in celsius. None if it's not available.
        """
        if ThermostatDevice.MEASUREMENT_NAME_AMBIENT_TEMPERATURE_C in self.measurements:
            return self.measurements[ThermostatDevice.MEASUREMENT_NAME_AMBIENT_TEMPERATURE_C][0][0]

        return False

    def get_cooling_setpoint(self, botengine=None):
        """
        Get the cooling setpoint
        :param botengine: BotEngine environment
        :return: None if the cooling setpoint has not been set yet.
        """
        if ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C in self.measurements:
            return self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][0][0]

        return None

    def get_heating_setpoint(self, botengine=None):
        """
        Get the heating setpoint
        :param botengine: BotEngine environment
        :return: None if the heating setpoint has not been set yet.
        """
        if ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C in self.measurements:
            return self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][0][0]

        return None

    def get_dr_offset(self, botengine=None):
        """
        Return the current demand response offset in Celsius
        :param botengine: BotEngine environment
        :return: Float
        """
        dr_offset = 0.0
        for d in self.dr_stack:
            if self.dr_stack[d] > dr_offset:
                dr_offset = self.dr_stack[d]

        return dr_offset

    def set_system_mode(self, botengine, system_mode, reliably=True):
        """
        Set the system mode
        :param botengine:
        :param system_mode:
        :param reliably: True to keep retrying to get the command through
        :return:
        """
        botengine.get_logger().info("\t\t[" + self.device_id + "]: Set system mode to {}".format(self.thermostat_mode_to_string(system_mode)))
        self.last_system_mode_command = (system_mode, botengine.get_timestamp(), False)
        if reliably:
            send_command_reliably(botengine, self.device_id, ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE, system_mode)
        else:
            botengine.send_command(self.device_id, ThermostatDevice.MEASUREMENT_NAME_SYSTEM_MODE, system_mode)

        # Because Dmitry says we might see specific errors better if we issue commands one-by-one, especially to cloud-connected thermostats.
        botengine.flush_commands()

    def set_cooling_setpoint(self, botengine, setpoint_celsius, reliably=True):
        """
        Set the cooling setpoint
        :param botengine: BotEngine environment
        :param setpoint_celsius: Absolute setpoint in Celsius
        :param reliably: True to keep retrying to get the command through
        """
        setpoint_celsius = float(setpoint_celsius)
        if self.is_temperature_different(setpoint_celsius, self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][0][0]):
            botengine.get_logger().info("\t\t[" + self.device_id + "] (" + self.description + "): Set cooling setpoint from " + str(self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][0][0]) + " to " + str("%.1f" % setpoint_celsius))
            self.last_cooling_setpoint_command = (setpoint_celsius, botengine.get_timestamp(), False)

            if reliably:
                send_command_reliably(botengine, self.device_id, ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C, float(str("%.1f" % setpoint_celsius)))
            else:
                botengine.send_command(self.device_id, ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C, float(str("%.1f" % setpoint_celsius)))

            # Because Dmitry says we might see specific errors better if we issue commands one-by-one, especially to cloud-connected thermostats.
            botengine.flush_commands()

        else:
            botengine.get_logger().info("\t\t{}: Set cooling setpoint {} is the same as the current setpoint, skipping.".format(self.device_id, str("%.1f" % setpoint_celsius)))
            botengine.cancel_command(self.device_id, ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C)
            cancel_reliable_command(botengine, self.device_id, ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C)

    def set_heating_setpoint(self, botengine, setpoint_celsius, reliably=True):
        """
        Set the heating set-point
        :param botengine: BotEngine environmnet
        :param setpoint_celsius: Temperature in Celsius
        :param reliably: True to keep retrying to get the command through
        """
        setpoint_celsius = float(setpoint_celsius)
        if self.is_temperature_different(setpoint_celsius, self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][0][0]):
            botengine.get_logger().info("\t\t[" + self.device_id + "] (" + self.description + "): Set heating setpoint from " + str(self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][0][0]) + " to " + str("%.1f" % setpoint_celsius))
            self.last_heating_setpoint_command = (setpoint_celsius, botengine.get_timestamp(), False)

            if reliably:
                send_command_reliably(botengine, self.device_id, ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C, float(str("%.1f" % setpoint_celsius)))
            else:
                botengine.send_command(self.device_id, ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C, float(str("%.1f" % setpoint_celsius)))

            # Because Dmitry says we might see specific errors better if we issue commands one-by-one, especially to cloud-connected thermostats.
            botengine.flush_commands()

        else:
            botengine.get_logger().info("\t\t{}: Set heating setpoint {} is the same as the current setpoint, skipping.".format(self.device_id, str("%.1f" % setpoint_celsius)))
            botengine.cancel_command(self.device_id, ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C)
            cancel_reliable_command(botengine, self.device_id, ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C)

    def record_preferred_home_setpoint(self, botengine):
        """
        Record the preferred setpoint right now for the home mode set point
        :param botengine: BotEngine environment
        """
        botengine.get_logger().info("{} {}: Updating your preferred home set point".format(self.description, self.device_id))
        system_mode = self.get_system_mode(botengine)
        if system_mode is not None:
            if system_mode == ThermostatDevice.SYSTEM_MODE__COOL and ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C in self.measurements:
                self.preferred_cooling_setpoint_home_c = self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][0][0]

            elif system_mode == ThermostatDevice.SYSTEM_MODE__HEAT and ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C in self.measurements:
                self.preferred_heating_setpoint_home_c = self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][0][0]

    def record_preferred_sleep_offset(self, botengine):
        """
        Record the preferred temperature offset for sleep mode
        :param botengine:
        """
        botengine.get_logger().info("{} {}: Updating your preferred sleep offset".format(self.description, self.device_id))
        system_mode = self.get_system_mode(botengine)

        if system_mode is not None:
            if system_mode == ThermostatDevice.SYSTEM_MODE__COOL:
                self.preferred_cooling_offset_sleep_c = self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][0][0]- self.preferred_cooling_setpoint_home_c
                botengine.get_logger().info("{} {}: Your preferred cooling setpoint while you're home is {}".format(self.description, self.device_id, self.preferred_cooling_setpoint_home_c))
                botengine.get_logger().info("{} {}: This cooling setpoint while you're in SLEEP mode is {}".format(self.description, self.device_id, self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][0][0]))
                botengine.get_logger().info("{} {}: So your preferred cooling offset in SLEEP mode is {}".format(self.description, self.device_id, self.preferred_cooling_offset_sleep_c))

            elif system_mode == ThermostatDevice.SYSTEM_MODE__HEAT:
                self.preferred_heating_offset_sleep_c = self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][0][0] - self.preferred_heating_setpoint_home_c
                botengine.get_logger().info("{} {}: Your preferred heating setpoint while you're home is {}".format(self.description, self.device_id, self.preferred_heating_setpoint_home_c))
                botengine.get_logger().info("{} {}: This heating setpoint while you're in SLEEP mode is {}".format(self.description, self.device_id, self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][0][0]))
                botengine.get_logger().info("{} {}: So your preferred heating offset in SLEEP mode is {}".format(self.description, self.device_id, self.preferred_heating_offset_sleep_c))

    def record_preferred_away_offset(self, botengine):
        """
        Record the preferred temperature offset for away mode
        :param botengine:
        """
        botengine.get_logger().info("{} {}: Updating your preferred away offset".format(self.description, self.device_id))
        system_mode = self.get_system_mode(botengine)
        if system_mode is not None:
            if system_mode == ThermostatDevice.SYSTEM_MODE__COOL:
                self.preferred_cooling_offset_away_c = self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][0][0] - self.preferred_cooling_setpoint_home_c
                botengine.get_logger().info("{} {}: Your preferred cooling setpoint while you're home is {}".format(self.description, self.device_id, self.preferred_cooling_setpoint_home_c))
                botengine.get_logger().info("{} {}: This cooling setpoint while you're in AWAY mode is {}".format(self.description, self.device_id, self.measurements[ThermostatDevice.MEASUREMENT_NAME_COOLING_SETPOINT_C][0][0]))
                botengine.get_logger().info("{} {}: So your preferred cooling offset in AWAY mode is {}".format(self.description, self.device_id, self.preferred_cooling_offset_away_c))

            elif system_mode == ThermostatDevice.SYSTEM_MODE__HEAT:
                self.preferred_heating_offset_away_c = self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][0][0] - self.preferred_heating_setpoint_home_c
                botengine.get_logger().info("{} {}: Your preferred heating setpoint while you're home is {}".format(self.description, self.device_id, self.preferred_heating_setpoint_home_c))
                botengine.get_logger().info("{} {}: This heating setpoint while you're in AWAY mode is {}".format(self.description, self.device_id, self.measurements[ThermostatDevice.MEASUREMENT_NAME_HEATING_SETPOINT_C][0][0]))
                botengine.get_logger().info("{} {}: So your preferred heating offset in AWAY mode is {}".format(self.description, self.device_id, self.preferred_heating_offset_away_c))


    def set_demand_response(self, botengine, active, identifier, offset_c):
        """
        Activate demand response, preventing the maximum setpoint from going above the desired DR setpoint if one is defined
        :param botengine: BotEngine environment
        :param active: True to activate the DR event, False to deactivate it.
        :param offset_c: Temperature offset in Celsius relative to the user's preferred temperature
        :param identifier: Identifier of this DR event so it can be updated and cancelled later.
        :return:
        """
        botengine.get_logger().info("thermostat.set_demand_response: active={}; id={}; offset_c={}".format(active, identifier, offset_c))
        if active:
            self.dr_stack[identifier] = offset_c

        elif identifier in self.dr_stack:
            del(self.dr_stack[identifier])

        return self.apply_offsets(botengine)

    def set_energy_efficiency(self, botengine, active, identifier, offset_c=2.4):
        """
        Adjusting the setpoint in a direction that saves energy by some statically defined offset relative to the preferred temperature while the user is home.
        Energy efficiency offset stack. Once you apply an EE offset, you must later remove it. The thermostat will apply the most aggressive active offset.
        :param botengine: BotEngine environment
        :param active: True to make this energy efficiency setting active, False to deactivate it.
        :param offset_c: Temperature offset it Celsius relative to the preferred temperature when the user is home
        :param identifier: Unique name for this energy efficiency offset, so it can be later cancelled.
        :return: the system mode if the thermostat was paused successfully, None if the thermostat was not paused.
        """
        botengine.get_logger().info("thermostat.set_energy_efficiency: active={}; id={}; offset_c={}".format(active, identifier, offset_c))
        if active:
            self.ee_stack[identifier] = offset_c

        elif identifier in self.ee_stack:
            del(self.ee_stack[identifier])

        return self.apply_offsets(botengine)

    def cancel_all_energy_efficiency(self, botengine):
        """
        Cancel all energy efficiency offsets
        :param botengine:
        :return:
        """
        self.ee_stack = {}
        return self.apply_offsets(botengine)

    def apply_offsets(self, botengine):
        """
        Take whatever active DR and EE offsets have been configured relative to the preferred setpoint while home,
        and apply them to this thermostat.
        :param botengine: BotEngine environment
        :return: The system mode of the thermostat if applied, None if the thermostat isn't on and the setpoints currently don't matter.
        """
        system_mode = self.get_system_mode(botengine)

        dr_offset = None
        for d in self.dr_stack:
            if dr_offset is None:
                dr_offset = self.dr_stack[d]

            elif self.dr_stack[d] > dr_offset:
                dr_offset = self.dr_stack[d]

        if dr_offset is None:
            dr_offset = 0.0


        ee_offset = None
        for e in self.ee_stack:
            if ee_offset is None:
                ee_offset = self.ee_stack[e]

            elif self.ee_stack[e] > ee_offset:
                ee_offset = self.ee_stack[e]

        if ee_offset is None:
            ee_offset = 0.0

        botengine.get_logger().info("thermostat.apply_offsets(): Thermostat '{}' system mode is {}; preferred_cooling_setpoint_home_c={}; dr_offset={}; ee_offset={}".format(self.description, str(system_mode), self.preferred_cooling_setpoint_home_c, dr_offset, ee_offset))
        if system_mode is not None:
            if system_mode == ThermostatDevice.SYSTEM_MODE__COOL:
                self.set_cooling_setpoint(botengine, self.preferred_cooling_setpoint_home_c + ee_offset + dr_offset)
                return system_mode

            elif system_mode == ThermostatDevice.SYSTEM_MODE__HEAT:
                self.set_heating_setpoint(botengine, self.preferred_heating_setpoint_home_c - ee_offset - dr_offset)
                return system_mode

        return None

    def increment_energy_efficiency(self, botengine, identifier, max_offset_c=2.4):
        """
        Increment the degrees F in a direction that saves energy up to some max.
        This can be called multiple times (up to 3).
        :param botengine: BotEngine environment
        :param max_relative_offset_c: Maximum offset in degrees C to achieve relative to our preferred temperature while in HOME mode. The thermostat increments to this max level after 3 calls to this method.
        :return: the system mode if the thermostat was paused successfully, None if the thermostat was not paused.
        """
        if identifier not in self.ee_stack:
            self.ee_stack[identifier] = 0.0

        self.ee_stack[identifier] += (max_offset_c / 3)
        if self.ee_stack[identifier] > max_offset_c:
            self.ee_stack[identifier] = max_offset_c

        return self.apply_offsets(botengine)

    def set_energy_efficiency_away(self, botengine, identifier):
        """
        Add an energy efficiency policy for away mode
        :param botengine: BotEngine environment
        :param identifier: Identifier so we can cancel or modify this energy efficiency policy later.
        :return: The current system mode if the change went into effect, None if nothing happened.
        """
        system_mode = self.get_system_mode(botengine)
        if system_mode is not None:
            if system_mode == ThermostatDevice.SYSTEM_MODE__COOL:
                self.ee_stack[identifier] = self.preferred_cooling_offset_away_c

            elif system_mode == ThermostatDevice.SYSTEM_MODE__HEAT:
                self.ee_stack[identifier] = self.preferred_heating_offset_away_c

        return self.apply_offsets(botengine)

    def set_energy_efficiency_sleep(self, botengine, identifier):
        """
        Add an energy efficiency policy for sleep mode
        :param botengine: BotEngine environment
        :param identifier: Identifier so we can cancel or modify this energy efficiency policy later.
        :return: The current system mode if the change went into effect, Nothing if nothing happened
        """
        system_mode = self.get_system_mode(botengine)
        if system_mode is not None:
            if system_mode == ThermostatDevice.SYSTEM_MODE__COOL:
                self.ee_stack[identifier] = self.preferred_cooling_offset_sleep_c

            elif system_mode == ThermostatDevice.SYSTEM_MODE__HEAT:
                self.ee_stack[identifier] = self.preferred_heating_offset_sleep_c

        return self.apply_offsets(botengine)
        
    def thermostat_mode_to_string(self, mode):
        """
        Transform the thermostat's enumerated mode into an all-caps string
        :param mode: The mode
        :returns: String
        """
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


