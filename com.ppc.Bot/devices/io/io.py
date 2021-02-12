'''
Created on June 30, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device
import utilities.utilities as utilities

class IoDevice(Device):
    """
    Digital IO Device

    https://www.develcoproducts.com/products/smart-relays/io-module/
    Four digital inputs with dry contact
    Two relay outputs with NO and NC contacts
    On/off or pulse functionality
    Saves cabling efforts
    Remote data collection and control of wired devices
    """
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9104]

    # Goals
    GOAL_CUSTOM = 0
    GOAL_WIRED_SECURITY_SYSTEM = 1

    # Parameter names
    MEASUREMENT_NAME_INPUT = "input"
    MEASUREMENT_NAME_REVERSEPOLARITY = "reversePolarity"
    COMMAND_NAME_OUTPUT = "output"

    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        Device.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Default behavior
        self.goal_id = IoDevice.GOAL_CUSTOM

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("IO Module")
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "wave-square"

    def get_icon_font(self):
        """
        Get the icon font package from which to render an icon
        :return: The name of the icon font package
        """
        return utilities.ICON_FONT_FONTAWESOME_REGULAR

    def get_input(self, botengine, index):
        """
        Get the input value for the given index, starting with 0
        :param botengine:
        :param index: Index number 0-3
        :return: True or False or None
        """
        param_name = "{}.{}".format(self.MEASUREMENT_NAME_INPUT, index)
        if param_name in self.measurements:
            return self.measurements[param_name][0][0]

    def set_output(self, botengine, on, index):
        """
        Set the output to the Digital IO module for the given index starting with 0
        :param botengine: BotEngine environment
        :param on: True to turn the output on, False to turn it off.
        :param index: Output index 0 or 1
        """
        if not self.can_control:
            return

        botengine.send_command(self.device_id, IoDevice.COMMAND_NAME_OUTPUT, on, index)

    def was_input_updated(self, botengine, index):
        """
        Check if an input was updated
        :param index:
        :return:
        """
        return "{}.{}".format(self.MEASUREMENT_NAME_INPUT, index) in self.last_updated_params





