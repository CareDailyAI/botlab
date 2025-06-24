"""
Created on September 22, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.button.button_multi import MultiButtonDevice


class LinkHighMultiButtonDevice(MultiButtonDevice):
    """
    LinkHigh Button Device
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9014]

    # Measurement name for the button status
    MEASUREMENT_NAME_BUTTON_STATUS = "buttonStatus"

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_cr2032"

    # Type of battery
    BATTERY_TYPE = "CR2032"

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
        MultiButtonDevice.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )
