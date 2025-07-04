"""
Created on April 4, 2022

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

from devices.proxy.proxy import ProxyDevice


class WithingsWatchProxyDevice(ProxyDevice):
    """Withings Watch Proxy"""

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [4031]

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name.
        return _("Withings Watch")
