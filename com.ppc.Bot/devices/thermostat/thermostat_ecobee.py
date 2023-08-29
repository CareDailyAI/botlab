'''
Created on March 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# Device Model
# https://presence.atlassian.net/wiki/display/devices/Thermostat

from devices.thermostat.thermostat import ThermostatDevice
import signals.analytics as analytics


class ThermostatEcobeeDevice(ThermostatDevice):
    """Honeywell Lyric Thermostat Device"""
    
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [4240]
    
    # Minimum setpoint in Celsius
    MIN_SETPOINT_C = 7.0
    
    # Maximum setpoint in Celsius
    MAX_SETPOINT_C = 29.0

    # Ecobee-specific command to change the mode of the thermostat
    COMMAND_CLIMATE_MODE = "climate"
    

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        ThermostatDevice.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements)

        # Set to True to activate the 'climate' mode switching functionality which is incompatible with demand response events.
        self.ee_only = False

        # Start timestamp of EE events for tracking
        self.ee_timestamp_ms = None


    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        ThermostatDevice.initialize(self, botengine)

        if not hasattr(self, 'ee_only'):
            self.ee_only = False

        if not hasattr(self, 'ee_timestamp_ms'):
            self.ee_timestamp_ms = None

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Ecobee")
        

    def set_system_mode(self, botengine, system_mode, reliably=False):
        """
        Set the system mode
        :param botengine:
        :param system_mode:
        :param reliably: True to keep retrying to get the command through
        :return:
        """
        ThermostatDevice.set_system_mode(self, botengine, system_mode, reliably=False)

    def set_cooling_setpoint(self, botengine, setpoint_celsius, reliably=False):
        """
        Set the cooling setpoint
        :param botengine: BotEngine environment
        :param setpoint_celsius: Absolute setpoint in Celsius
        :param reliably: True to keep retrying to get the command through
        """
        ThermostatDevice.set_cooling_setpoint(self, botengine, setpoint_celsius, reliably=False)

    def set_heating_setpoint(self, botengine, setpoint_celsius, reliably=False):
        """
        Set the heating set-point
        :param botengine: BotEngine environmnet
        :param setpoint_celsius: Temperature in Celsius
        :param reliably: True to keep retrying to get the command through
        """
        ThermostatDevice.set_heating_setpoint(self, botengine, setpoint_celsius, reliably=False)


    def increment_energy_efficiency(self, botengine, identifier, max_offset_c=2.4):
        """
        If the identifier is "sleep" or "away", then the thermostat is put into sleep mode or away mode.
        Otherwise we elevate the request to the generic thermostat handler.
        :param botengine: BotEngine environment
        :param max_relative_offset_c: Maximum offset in degrees C to achieve relative to our preferred temperature while in HOME mode. The thermostat increments to this max level after 3 calls to this method.
        :return: the system mode if the thermostat was paused successfully, None if the thermostat was not paused.
        """
        if not self.ee_only:
            return ThermostatDevice.increment_energy_efficiency(self, botengine, identifier, max_offset_c)

        self.location_object.increment_location_property(botengine, "{}_total_ee_policies_applied".format(self.device_id))
        self.location_object.increment_location_property(botengine, "{}_total_ee_incremental_policies_applied".format(self.device_id))
        if identifier == "sleep":
            if self.ee_timestamp_ms is None:
                self.ee_timestamp_ms = botengine.get_timestamp()

            botengine.send_command(self.device_id, self.COMMAND_CLIMATE_MODE, "sleep")
            # NOTE: Energy efficiency policies for sleeping have been revoked.
            self.location_object.narrate(botengine,
                                         title=_("'{}': Sleep mode").format(self.description),
                                         description=_("Setting your ecobee thermostat into Sleep mode."),
                                         priority=botengine.NARRATIVE_PRIORITY_DEBUG,
                                         icon='thermostat',
                                         event_type="thermostat.thermostat_policy_set")

            policies = {
                'device_id': self.device_id,
                'device_description': self.description,
                'is_connected': self.is_connected,
                'thermostat_mode': self.thermostat_mode_to_string(self.get_system_mode(botengine)),
                'ecobee_climate': "sleep",
                'ee_start_timestamp_ms': self.ee_timestamp_ms
            }

            analytics.track(botengine, self.location_object, 'thermostat_policy_set', properties=policies)

        elif identifier == "away":
            if self.ee_timestamp_ms is None:
                self.ee_timestamp_ms = botengine.get_timestamp()

            botengine.send_command(self.device_id, self.COMMAND_CLIMATE_MODE, "away")
            # NOTE: Energy efficiency policies for away have been revoked.
            self.location_object.narrate(botengine,
                                         title=_("'{}': Away mode").format(self.description),
                                         description=_("Setting your ecobee thermostat into Away mode."),
                                         priority=botengine.NARRATIVE_PRIORITY_DEBUG,
                                         icon='thermostat',
                                         event_type="thermostat.thermostat_policy_set")

            policies = {
                'device_id': self.device_id,
                'device_description': self.description,
                'is_connected': self.is_connected,
                'thermostat_mode': self.thermostat_mode_to_string(self.get_system_mode(botengine)),
                'ecobee_climate': "away",
                'ee_start_timestamp_ms': self.ee_timestamp_ms
            }

            analytics.track(botengine, self.location_object, 'thermostat_policy_set', properties=policies)

        else:
            return ThermostatDevice.increment_energy_efficiency(self, botengine, identifier, max_offset_c)



    def set_energy_efficiency_away(self, botengine):
        """
        Add an energy efficiency policy for away mode
        :param botengine: BotEngine environment
        :param identifier: Identifier so we can cancel or modify this energy efficiency policy later.
        :return: The current system mode if the change went into effect, None if nothing happened.
        """
        if not self.ee_only:
            return ThermostatDevice.set_energy_efficiency_away(self, botengine)

        if self.ee_timestamp_ms is None:
            self.ee_timestamp_ms = botengine.get_timestamp()

        self.location_object.increment_location_property(botengine, "{}_total_ee_policies_applied".format(self.device_id))
        self.location_object.increment_location_property(botengine, "{}_total_ee_away_policies_applied".format(self.device_id))
        botengine.send_command(self.device_id, self.COMMAND_CLIMATE_MODE, "away")
        # NOTE: Energy efficiency policies for away have been revoked.
        self.location_object.narrate(botengine,
                                     title=_("'{}': Away mode").format(self.description),
                                     description=_("Setting your ecobee thermostat into Away mode."),
                                     priority=botengine.NARRATIVE_PRIORITY_DEBUG,
                                     icon='thermostat',
                                     event_type="thermostat.thermostat_policy_set")

        policies = {
            'device_id': self.device_id,
            'device_description': self.description,
            'is_connected': self.is_connected,
            'thermostat_mode': self.thermostat_mode_to_string(self.get_system_mode(botengine)),
            'ecobee_climate': "away",
            'ee_start_timestamp_ms': self.ee_timestamp_ms
        }

        analytics.track(botengine, self.location_object, 'thermostat_policy_set', properties=policies)

    def set_energy_efficiency_sleep(self, botengine):
        """
        Add an energy efficiency policy for sleep mode
        :param botengine: BotEngine environment
        :param identifier: Identifier so we can cancel or modify this energy efficiency policy later.
        :return: The current system mode if the change went into effect, Nothing if nothing happened
        """
        if not self.ee_only:
            return ThermostatDevice.set_energy_efficiency_sleep(self, botengine)

        if self.ee_timestamp_ms is None:
            self.ee_timestamp_ms = botengine.get_timestamp()

        self.location_object.increment_location_property(botengine, "{}_total_ee_policies_applied".format(self.device_id))
        self.location_object.increment_location_property(botengine, "{}_total_ee_sleep_policies_applied".format(self.device_id))
        botengine.send_command(self.device_id, self.COMMAND_CLIMATE_MODE, "sleep")
        # NOTE: Energy efficiency policies for sleeping have been revoked.
        self.location_object.narrate(botengine,
                                     title=_("'{}': Sleep mode").format(self.description),
                                     description=_("Setting your ecobee thermostat into Sleep mode."),
                                     priority=botengine.NARRATIVE_PRIORITY_DEBUG,
                                     icon='thermostat',
                                     event_type="thermostat.thermostat_policy_set")

        policies = {
            'device_id': self.device_id,
            'device_description': self.description,
            'is_connected': self.is_connected,
            'thermostat_mode': self.thermostat_mode_to_string(self.get_system_mode(botengine)),
            'ecobee_climate': "sleep",
            'ee_start_timestamp_ms': self.ee_timestamp_ms
        }

        analytics.track(botengine, self.location_object, 'thermostat_policy_set', properties=policies)

    def set_energy_efficiency_home(self, botengine):
        """
        Turn off all away and sleep energy efficiency policies
        :param botengine: BotEngine environment
        """
        if not self.ee_only:
            return ThermostatDevice.set_energy_efficiency_home(self, botengine)

        self.location_object.increment_location_property(botengine, "{}_total_ee_home_policies_applied".format(self.device_id))

        if self.ee_timestamp_ms is not None:
            # End of all EE events
            duration_s = (botengine.get_timestamp() - self.ee_timestamp_ms) / 1000
            self.ee_timestamp_ms = None
            analytics.track(botengine, self.location_object, "ee_complete", properties={'duration_s': duration_s, 'device_id': self.device_id, 'description': self.description})

            # This number will represent the total amount of time across ALL devices.
            # For example, if you have 1 thermostat and a EE event for 10000s, then the total is 10000s.
            # But if you have 2 thermostats and a EE event for 10000s, then the total is 20000s
            analytics.people_increment(botengine, self.location_object, {'ee_total_s': duration_s})

        botengine.send_command(self.device_id, self.COMMAND_CLIMATE_MODE, "home")

        self.location_object.narrate(botengine,
                                     title=_("'{}': Home mode").format(self.description),
                                     description=_("Setting your ecobee thermostat into Home mode."),
                                     priority=botengine.NARRATIVE_PRIORITY_DEBUG,
                                     icon='thermostat',
                                     event_type="thermostat.thermostat_policy_unset")

        policies = {
            'device_id': self.device_id,
            'device_description': self.description,
            'is_connected': self.is_connected,
            'thermostat_mode': self.thermostat_mode_to_string(self.get_system_mode(botengine)),
            'ecobee_climate': "home"
        }

        # NOTE: Energy efficiency policies for absent or sleeping have been revoked because someone is home.
        analytics.track(botengine, self.location_object, 'thermostat_policy_unset', properties=policies)
