"""
Created on July 22, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.button.button_panic import PanicButtonDevice


class DevelcoPanicButtonDevice(PanicButtonDevice):
    """
    Develco Panic Button
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9101]

    def __init__(
        self,
        botengine,
        location_object,
        device_id,
        device_type,
        device_description,
        precache_measurements=True,
    ):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        PanicButtonDevice.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )
