"""
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.smartplug.smartplug import SmartplugDevice

# Be careful deleting this module because it's already in some services
# Fact is multiple brands of smart plugs share device type 10035


class Centralite3SeriesSmartplugDevice(SmartplugDevice):
    """Camera Device"""

    # List of Device Types this class is compatible with
    DEVICE_TYPES = []  # [10035] < Deprecated, see smartplug.py >

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name - Centralte 3-series smart plug
        return _("Smart Plug")
