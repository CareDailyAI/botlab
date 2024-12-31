'''
Created on October 12, 2023

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Edward Liu
'''

from devices.health.health import HealthDevice

class GoogleHealthDevice(HealthDevice):
    """
    Google Health Device
    """

    MEASUREMENT_PARAMETERS_LIST = [
        HealthDevice.MEASUREMENT_NAME_HEART_RATE,
        HealthDevice.MEASUREMENT_NAME_STEPS,
        HealthDevice.MEASUREMENT_NAME_BREATHING_RATE,
        HealthDevice.MEASUREMENT_NAME_BREATHING_RATE_STABILITY,
        HealthDevice.MEASUREMENT_NAME_HEART_RATE_STABILITY,
        HealthDevice.MEASUREMENT_NAME_MOTION_INDEX,
        HealthDevice.MEASUREMENT_NAME_MOTION_STABILITY,
        HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC,
        HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC,
        HealthDevice.MEASUREMENT_NAME_HEMATOCRIT,
        HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN,
        HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY,
        HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX,
        HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX,
        HealthDevice.MEASUREMENT_NAME_PROTEIN,
        HealthDevice.MEASUREMENT_NAME_SPO2,
    ]

    DEVICE_TYPES = [19]

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Google Health")
