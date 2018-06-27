'''
Created on January 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device


class ButtonDevice(Device):
    """Button Device"""

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9014]

    # List of available button indices
    BUTTON_INDEX_LIST = [1, 2]

    # Measurement name for the button status
    MEASUREMENT_NAME_BUTTON_STATUS = 'alarmStatus'

    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)
        
    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Button")
    
    def get_image_name(self, botengine):
        """
        :return: the font icon name of this device type
        """
        return "button"

    def is_single_button_pressed(self, botengine, button_index=BUTTON_INDEX_LIST[0]):
        """
        Find out if a single button is pressed on this device
        :param botengine:
        :param button_index: Button index if there are multiple buttons on this device.
        :return: True if the button is currently pressed
        """
        button_parameter = self.MEASUREMENT_NAME_BUTTON_STATUS

        if button_index is not None:
            button_parameter = "{}.{}".format(self.MEASUREMENT_NAME_BUTTON_STATUS, button_index)

        return button_parameter in self.last_updated_params and self.measurements[button_parameter][0][0]

