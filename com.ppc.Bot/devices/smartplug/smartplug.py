'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device

from devices.device import send_command_reliably
from devices.device import cancel_reliable_command

class SmartplugDevice(Device):
    """Smart Plug Device"""

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [10035]

    # Measurement names
    MEASUREMENT_NAME_STATUS = 'outletStatus'
    MEASUREMENT_NAME_POWER = 'power'
    MEASUREMENT_NAME_ENERGY = 'energy'

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS,
        MEASUREMENT_NAME_POWER,
        MEASUREMENT_NAME_ENERGY
    ]

    # Smart plug goals
    GOAL_SMARTPLUG_SAVE_ENERGY = 80
    GOAL_SMARTPLUG_LEAVE_LIGHTS_ON_FOR_PETS = 81
    GOAL_SMARTPLUG_SECURITY = 82
    GOAL_SMARTPLUG_ALWAYS_ON = 84
    GOAL_SMARTPLUG_DEHUMIDIFIER = 85
    GOAL_SMARTPLUG_FAN = 86
    GOAL_SMARTPLUG_SPACEHEATER = 87
    GOAL_SMARTPLUG_WINDOW_AC = 88
    GOAL_SMARTPLUG_SKIP = 89
    GOAL_SMARTPLUG_COFFEE_AUTO_ON = 90
    GOAL_SMARTPLUG_APPLIANCE_MONITORING = 91
    GOAL_SMARTPLUG_MICROWAVE = 92

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
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # The boolean on/off state of this device that was saved
        self.saved_state = False

        # Whether the saved_state is valid or not
        self.saved = False

    def initialize(self, botengine):
        """
        Initialize on every execution
        :param botengine:
        :return:
        """
        Device.initialize(self, botengine)

    #===========================================================================
    # Attributes
    #===========================================================================
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name - abstract smart plug
        return _("Smart Plug")
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "plug"
    
    def is_command(self, measurement_name):
        """
        :param measurement_name: Name of a local measurement name
        :return: True if the given parameter name is a command
        """
        return measurement_name == self.MEASUREMENT_NAME_STATUS
        
    def is_light(self):
        """
        :return: True if this is a light
        """
        return False

    def can_control_brightness(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if we can control brightness on this device
        """
        return False

    def can_measure_power(self, botengine=None):
        """
        :param botengine:
        :return: True if this device can measure power
        """
        return self.MEASUREMENT_NAME_POWER in self.measurements

    def can_measure_energy(self, botengine=None):
        """
        :param botengine:
        :return: True if this device can measure energy
        """
        return self.MEASUREMENT_NAME_ENERGY in self.measurements

    def is_on(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if this plug is on
        """
        if self.MEASUREMENT_NAME_STATUS in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_STATUS][0][0]

        return False

    def is_off(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if this plug is on
        """
        if self.MEASUREMENT_NAME_STATUS in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_STATUS][0][0] == False

        return False

    def did_turn_on(self, botengine=None):
        """
        Did the light just turn on in the last execution
        :param botengine: BotEngine environment
        :return: True if the light turned on in the last execution
        """
        if self.MEASUREMENT_NAME_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_STATUS in self.last_updated_params:
                return self.measurements[self.MEASUREMENT_NAME_STATUS][0][0] == True

        return False

    def did_turn_off(self, botengine=None):
        """
        Did the light just turn off in the last execution
        :param botengine: BotEngine environment
        :return: True if the light turned off in the last execution
        """
        if self.MEASUREMENT_NAME_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_STATUS in self.last_updated_params:
                return self.measurements[self.MEASUREMENT_NAME_STATUS][0][0] == False

        return False

    def current_power(self, botengine=None):
        """
        :param botengine:
        :return: Current power levels. None if this device doesn't measure power
        """
        if self.MEASUREMENT_NAME_POWER in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_POWER][0][0]

        return 0

    def current_energy(self, botengine=None):
        """
        :param botengine:
        :return: Current energy consumption total. None if this device doesn't measure energy.
        """
        if self.MEASUREMENT_NAME_ENERGY in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_ENERGY][0][0]

        return 0

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

        botengine.get_logger().info("{}: Smart Plug '{}' saved state is {}".format(self.device_id, self.description, self.saved_state))
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
    
    def on(self, botengine, reliably=False):
        """
        Turn on
        :param botengine: BotEngine environment
        :param reliably: True to send the command reliably (default is False)
        """
        if not self.can_control:
            return False

        if reliably:
            cancel_reliable_command(botengine, self.device_id, SmartplugDevice.MEASUREMENT_NAME_STATUS)
            send_command_reliably(botengine, self.device_id, SmartplugDevice.MEASUREMENT_NAME_STATUS, "1")

        else:
            botengine.send_command(self.device_id, SmartplugDevice.MEASUREMENT_NAME_STATUS, "1") # This does work with the keyword True.

        return True
    
    
    def off(self, botengine, reliably=False):
        """
        Turn off
        :param botengine: BotEngine environment
        :param reliably: True to send the command reliably (default is False)
        """
        if not self.can_control:
            return False

        if reliably:
            cancel_reliable_command(botengine, self.device_id, SmartplugDevice.MEASUREMENT_NAME_STATUS)
            send_command_reliably(botengine, self.device_id, SmartplugDevice.MEASUREMENT_NAME_STATUS, "0")

        else:
            botengine.send_command(self.device_id, SmartplugDevice.MEASUREMENT_NAME_STATUS, "0") # TODO this should be able to say the keyword False, but that doesn't work. Needs a server fix.

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
        
    