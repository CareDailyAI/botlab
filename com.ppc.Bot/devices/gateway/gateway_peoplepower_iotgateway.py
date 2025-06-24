"""
Created on June 28, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.gateway.gateway import GatewayDevice


class PeoplePowerIotGatewayDevice(GatewayDevice):
    """
    M-Series Gateway
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [31]

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Smart Home Center")
