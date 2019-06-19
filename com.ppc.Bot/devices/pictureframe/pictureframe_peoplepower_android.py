'''
Created on September 10, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.pictureframe.pictureframe_peoplepower import PeoplePowerPictureFrameDevice

class PeoplePowerPictureFrameAndroidDevice(PeoplePowerPictureFrameDevice):
    """
    iOS Picture Frame Device
    """

    DEVICE_TYPES = [27]

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Android Picture Frame")
