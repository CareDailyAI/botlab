'''
Created on June 1, 2022

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
'''

from devices.smartplug.smartplug import SmartplugDevice

from devices.device import send_command_reliably
from devices.device import cancel_reliable_command

# Message to describe that device control is disabled. If provided, a new narrative is created while other messaging and logic continues without actually sending a device command to control.
BLOCK_DEVICE_CONTROL_MESSAGE = "Control of the Smart Circuit Breaker is temporarily disabled."

class SmartBreakerDevice(SmartplugDevice):
    """
    Smart Breaker
    """
    
    # List of Device Types this class is compatible with
    DEVICE_TYPES = []

    # Measurement names
    MEASUREMENT_NAME_STATUS = 'breakerStatus'
    MEASUREMENT_NAME_ENERGY = 'energy'
    MEASUREMENT_NAME_VOLTS = 'volts'
    MEASUREMENT_NAME_VOLTS_A = 'volts.A'
    MEASUREMENT_NAME_VOLTS_B = 'volts.B'
    MEASUREMENT_NAME_CURRENT = 'current'
    MEASUREMENT_NAME_CURRENT_A = 'current.A'
    MEASUREMENT_NAME_CURRENT_B = 'current.B'
    MEASUREMENT_NAME_POWER = 'power'
    MEASUREMENT_NAME_LINE_FREQUENCY = 'lineFrequency'

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS,
        MEASUREMENT_NAME_ENERGY,
        MEASUREMENT_NAME_POWER,
        MEASUREMENT_NAME_VOLTS,
        MEASUREMENT_NAME_CURRENT,
        MEASUREMENT_NAME_LINE_FREQUENCY
    ]

    # Circuit breaker context
    # GOAL_BREAKER_APPLIANCE_MONITORING = 0
    GOAL_BREAKER_KITCHEN = 1
    GOAL_BREAKER_BEDROOM = 2
    GOAL_BREAKER_BATHROOM = 3
    GOAL_BREAKER_GARAGE = 4
    GOAL_BREAKER_HVAC = 5
    GOAL_BREAKER_DRYER = 6
    GOAL_BREAKER_DISHWASHER = 7
    GOAL_BREAKER_HOT_WATER_HEATER = 8
    GOAL_BREAKER_OVEN = 9
    GOAL_BREAKER_POOL_PUMP = 10
    GOAL_BREAKER_HOT_TUB = 11
    GOAL_BREAKER_EV_CHARGER = 12
    GOAL_BREAKER_LIGHT_OUTLET = 13
    GOAL_BREAKER_SKIP = 14

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param location_object:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        SmartplugDevice.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Default behavior
        self.goal_id = SmartBreakerDevice.GOAL_BREAKER_SKIP

    #===========================================================================
    # Attributes
    #===========================================================================
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name - Smart Breaker
        return _("Smart Breaker")
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "meter"

    def did_update_power(self, botengine=None):
        """
        :param botengine:
        :return: True if the last measurement indicated we updated the current
        """
        return self.MEASUREMENT_NAME_POWER in self.last_updated_params

    def did_update_current(self, botengine=None, phase='A'):
        """
        :param botengine:
        :return: True if the last measurement indicated we updated the current
        """
        return "{}.{}".format(self.MEASUREMENT_NAME_CURRENT, phase) in self.last_updated_params

    def did_update_voltage(self, botengine=None, phase='A'):
        """
        :param botengine:
        :return: True if the last measurement indicated we updated the voltage
        """
        return "{}.{}".format(self.MEASUREMENT_NAME_VOLTS, phase) in self.last_updated_params

    def did_update_approximate_power(self, botengine=None, phase='A'):
        """
        :param botengine:
        :return: True if either voltage or current were updated to give us approximate power
        """
        return self.did_update_voltage(botengine, phase) or self.did_update_current(botengine, phase)

    def get_current(self, botengine=None, phase='A'):
        """
        :param botengine:
        :param phase: 'A' or 'B'
        :return: Current
        """
        param_name = "{}.{}".format(self.MEASUREMENT_NAME_CURRENT, phase)
        if param_name in self.measurements:
            return self.measurements[param_name][0][0]

        return 0

    def get_voltage(self, botengine=None, leg='AN'):
        """
        :param botengine:
        :param leg: 'AN' (A-to-Neutral) or 'BN' (B-to-Neutral) or 'AB' (A-to-B)
        :return: Voltage
        """
        param_name = "{}.{}".format(self.MEASUREMENT_NAME_VOLTS, leg)
        if param_name in self.measurements:
            return self.measurements[param_name][0][0]

        return 0

    def get_approximate_power(self, botengine=None, phase='A'):
        """
        This is an AC smart breaker. Technically we should have a phase angle between
        the voltage and the current to calculate active and reactive power. Since we
        aren't given that as a measurement, we're simply going to perform the DC method
        of Power = Voltage * Current and call it.

        :param botengine:
        :param phase: 'A' or 'B'
        :return: Current energy consumption total. None if this device doesn't measure energy.
        """
        leg = phase + "N"
        return round(self.get_current(botengine, phase) * self.get_voltage(botengine, leg), 2)

    def is_in_bedroom(self, botengine):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_BEDROOM):
            return True

        bedroom_names = [_('bed'), _('bett'), _('bdrm'), _('moms room'), _('dads room'), _('mom\'s room'), _('dad\'s room')]

        for name in bedroom_names:
            if name in self.description.lower():
                return True

        return False

    def is_in_bathroom(self, botengine):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_BATHROOM):
            return True

        bathroom_names = [_('schlaf'), _('bath'), _('toilet'), _('shower'), _('powder')]

        for name in bathroom_names:
            if name in self.description.lower():
                return True

        return False

    def is_in_kitchen(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_KITCHEN):
            return True

        bathroom_names = [_('kitch'), _('dinnete'), _('cook'), _('fridge')]

        for name in bathroom_names:
            if name in self.description.lower():
                return True

        return False

    def is_light_outlet(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_LIGHT_OUTLET):
            return True

        light_names = [_('light'), _('lamp'), _('lantern'), _('outlet')]

        for name in light_names:
            if name in self.description.lower():
                return True

        return False

    def is_garage(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_GARAGE):
            return True

        for name in [_('garage')]:
            if name in self.description.lower():
                return True

        return False

    def is_pool_pump(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_POOL_PUMP):
            return True

        for name in [_('pool')]:
            if name in self.description.lower():
                return True

        return False

    def is_hvac(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_HVAC):
            return True

        hvac_names = [_('hvac'), _('air'), _('condition'), _('heater'), _('cooler'), _('furnace')]

        for name in hvac_names:
            if name in self.description.lower():
                return True

        return False

    def is_dryer(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_DRYER):
            return True

        for name in [_('dryer')]:
            if name in self.description.lower():
                return True

        return False

    def is_dishwasher(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_DISHWASHER):
            return True

        for name in [_('dishwasher')]:
            if name in self.description.lower():
                return True

        return False

    def is_oven(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_OVEN):
            return True

        for name in [_('oven'), _('stove')]:
            if name in self.description.lower():
                return True

        return False

    def is_hot_water_heater(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_HOT_WATER_HEATER):
            return True

        for name in [_('water heater')]:
            if name in self.description.lower():
                return True

        return False

    def is_hot_tub(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_HOT_TUB):
            return True

        for name in [_('tub')]:
            if name in self.description.lower():
                return True

        return False

    def is_ev_charger(self):
        if self.is_goal_id(SmartBreakerDevice.GOAL_BREAKER_EV_CHARGER):
            return True

        for name in [_('ev'), _('charger')]:
            if name in self.description.lower():
                return True

        return False


    #===========================================================================
    # Commands
    #===========================================================================
    def save(self, botengine):
        """
        Save the status of this device
        :param botengine: BotEngine environment
        """
        if not self.is_connected:
            return False

        try:
            self.saved_state = self.measurements[self.MEASUREMENT_NAME_STATUS][0][0]
        except:
            self.saved_state = False

        self.saved = True

        botengine.get_logger().info("{}: Smart Breaker '{}' saved state is {}".format(self.device_id, self.description, self.saved_state))
        return True

    def restore(self, botengine, reliably=False):
        """
        Restore the status of the device from the save point
        :param botengine: BotEngine environment
        :param reliably: True to send the command reliably (default is False)
        :return: True if the smart plug was restored, False if there was nothing to restore
        """
        if not self.can_control:
            return False

        botengine.get_logger().info(">restore(" + str(self.device_id) + ")")
        if not self.saved:
            return False

        self.saved = False

        if self.saved_state:
            self.on(botengine, reliably)
        else:
            self.off(botengine, reliably)

        return True

    def on(self, botengine, reliably=True):
        """
        Turn on
        :param botengine: BotEngine environment
        :param reliably: True to send the command reliably (default is False)
        """
        if not self.can_control:
            return False

        if BLOCK_DEVICE_CONTROL_MESSAGE is not None:
            return True

        if reliably:
            cancel_reliable_command(botengine, self.device_id, SmartBreakerDevice.MEASUREMENT_NAME_STATUS)
            send_command_reliably(botengine, self.device_id, SmartBreakerDevice.MEASUREMENT_NAME_STATUS, "1")

        else:
            botengine.send_command(self.device_id, SmartBreakerDevice.MEASUREMENT_NAME_STATUS, "1")

        return True


    def off(self, botengine, reliably=True):
        """
        Turn off
        :param botengine: BotEngine environment
        :param reliably: True to send the command reliably (default is False)
        """
        if not self.can_control:
            return False

        if BLOCK_DEVICE_CONTROL_MESSAGE is not None:
            return True

        if reliably:
            cancel_reliable_command(botengine, self.device_id, SmartBreakerDevice.MEASUREMENT_NAME_STATUS)
            send_command_reliably(botengine, self.device_id, SmartBreakerDevice.MEASUREMENT_NAME_STATUS, "0")

        else:
            botengine.send_command(self.device_id, SmartBreakerDevice.MEASUREMENT_NAME_STATUS, "0")

        return True

    def toggle(self, botengine, reliably=False):
        """
        Toggle the smart plug on or off
        :param botengine:
        :param reliably: True to send the command reliably (default is False)
        """
        if not self.can_control:
            return

        if self.is_on(botengine):
            self.off(botengine, reliably)

        else:
            self.on(botengine, reliably)


    def raw_command(self, botengine, name, value):
        """
        Send a command for the given local parameter name
        """
        if name == self.MEASUREMENT_NAME_STATUS:
            if value:
                self.on(botengine)
            else:
                self.off(botengine)

