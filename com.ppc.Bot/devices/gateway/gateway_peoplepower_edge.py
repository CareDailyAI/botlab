"""
Created on July 31, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.gateway.gateway_develco_squidlink import DevelcoSquidlinkDevice


class PeoplePowerEdgeDevice(DevelcoSquidlinkDevice):
    """
    People Power edge computing gateway on Develco
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [32]

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Smart Home Center")
