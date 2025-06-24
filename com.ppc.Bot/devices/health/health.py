"""
Created on April 4, 2022

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

from devices.device import Device


class HealthDevice(Device):
    """
    Health Device
    """

    # Parameters
    MEASUREMENT_NAME_BED_STATUS = "bedStatus"
    MEASUREMENT_NAME_HEART_RATE = "hr"
    MEASUREMENT_NAME_HEART_RATE_RESTING = "hrResting"
    MEASUREMENT_NAME_STEPS = "steps"
    MEASUREMENT_NAME_BREATHING_RATE = "br"
    MEASUREMENT_NAME_BREATHING_RATE_STABILITY = "brStability"
    MEASUREMENT_NAME_HEART_RATE_STABILITY = "hrStability"
    MEASUREMENT_NAME_MOTION_INDEX = "motionIndex"
    MEASUREMENT_NAME_MOTION_STABILITY = "motionStability"
    MEASUREMENT_NAME_BLOOD_PRESSURE_DIA_MAX = "bloodPressure.diastolic_max"  # REMOVE. Provide non-aggregated measurements only.
    MEASUREMENT_NAME_BLOOD_PRESSURE_SYS_MAX = "bloodPressure.systolic_max"  # REMOVE. Provide non-aggregated measurements only.
    MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC = "bloodPressureDiastolic"
    MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC = "bloodPressureSystolic"
    MEASUREMENT_NAME_HEMATOCRIT = "hematocrit"
    MEASUREMENT_NAME_HEMOGLOBIN = "hemoglobin"
    MEASUREMENT_NAME_HR_VARIABILITY = "hrVariability"
    MEASUREMENT_NAME_PERFUSION_INDEX = "perfusionIndex"
    MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX = "plethVariabilityIndex"
    MEASUREMENT_NAME_PROTEIN = "protein"
    MEASUREMENT_NAME_SPO2 = "spo2"

    # Bed Status
    BED_STATUS_IN_BED = 1
    BED_STATUS_OUT_OF_BED = 0

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_BED_STATUS,
        MEASUREMENT_NAME_HEART_RATE,
        MEASUREMENT_NAME_STEPS,
        MEASUREMENT_NAME_BREATHING_RATE,
        MEASUREMENT_NAME_BREATHING_RATE_STABILITY,
        MEASUREMENT_NAME_HEART_RATE_STABILITY,
        MEASUREMENT_NAME_MOTION_INDEX,
        MEASUREMENT_NAME_MOTION_STABILITY,
        MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC,
        MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC,
        MEASUREMENT_NAME_HEMATOCRIT,
        MEASUREMENT_NAME_HEMOGLOBIN,
        MEASUREMENT_NAME_HR_VARIABILITY,
        MEASUREMENT_NAME_PERFUSION_INDEX,
        MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX,
        MEASUREMENT_NAME_PROTEIN,
        MEASUREMENT_NAME_SPO2,
    ]

    # Device types
    DEVICE_TYPES = []

    def __init__(
        self,
        botengine,
        location_object,
        device_id,
        device_type,
        device_description,
        precache_measurements=True,
    ):
        Device.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )

    def new_version(self, botengine):
        """
        New version
        :param botengine: BotEngine environment
        """
        Device.new_version(self, botengine)
        return

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Health")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "heartbeat"

    def did_update_bed_status(self, botengine):
        """
        Determine if we updated the bed status in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the bed status in this execution
        """
        return HealthDevice.MEASUREMENT_NAME_BED_STATUS in self.last_updated_params

    def get_bed_status(self, botengine):
        """
        Retrieve the most recent bed status value
        :param botengine:
        :return:
        """
        if HealthDevice.MEASUREMENT_NAME_BED_STATUS in self.measurements:
            return self.measurements[HealthDevice.MEASUREMENT_NAME_BED_STATUS][0][0]
        return None

    def is_detecting_in_bed(self, botengine):
        """
        Is this Health device detecting someone in bed
        :param botengine: BotEngine
        :return: True if this Health device is detecting someone in bed
        """
        status = self.get_bed_status(botengine)
        if status is not None:
            return status == HealthDevice.BED_STATUS_IN_BED
        return False

    def did_update_breathing_rate(self, botengine):
        """
        Determine if we updated the breathing rate in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the breathing rate in this execution
        """
        return HealthDevice.MEASUREMENT_NAME_BREATHING_RATE in self.last_updated_params

    def get_breathing_rate(self, botengine):
        """
        Retrieve the most recent breathing_rate value
        :param botengine:
        :return:
        """
        if HealthDevice.MEASUREMENT_NAME_BREATHING_RATE in self.measurements:
            return self.measurements[HealthDevice.MEASUREMENT_NAME_BREATHING_RATE][0][0]
        return None

    def did_update_heart_rate(self, botengine):
        """
        Determine if we updated the heart rate in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the heart rate in this execution
        """
        return HealthDevice.MEASUREMENT_NAME_HEART_RATE in self.last_updated_params

    def get_heart_rate(self, botengine):
        """
        Retrieve the most recent heart_rate value
        :param botengine:
        :return:
        """
        if HealthDevice.MEASUREMENT_NAME_HEART_RATE in self.measurements:
            return self.measurements[HealthDevice.MEASUREMENT_NAME_HEART_RATE][0][0]
        return None

    def get_average_heart_rate(self, botengine):
        """
        Retrieve the most recent heart_rate value
        :param botengine:
        :return:
        """
        if HealthDevice.MEASUREMENT_NAME_HEART_RATE in self.measurements:
            from statistics import mean

            return mean(
                [
                    x[0]
                    for x in self.measurements[HealthDevice.MEASUREMENT_NAME_HEART_RATE]
                ]
            )
        return None

    def did_update_heart_rate_resting(self, botengine):
        """
        Determine if we updated the heart rate resting in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the heart rate resting in this execution
        """
        return (
            HealthDevice.MEASUREMENT_NAME_HEART_RATE_RESTING in self.last_updated_params
        )

    def get_heart_rate_resting(self, botengine):
        """
        Retrieve the most recent heart rate resting value
        :param botengine:
        :return:
        """
        if HealthDevice.MEASUREMENT_NAME_HEART_RATE_RESTING in self.measurements:
            return self.measurements[HealthDevice.MEASUREMENT_NAME_HEART_RATE_RESTING][
                0
            ][0]
        return None

    def get_average_heart_rate_resting(self, botengine):
        """
        Retrieve the most recent heart rate resting value
        :param botengine:
        :return:
        """
        if HealthDevice.MEASUREMENT_NAME_HEART_RATE_RESTING in self.measurements:
            from statistics import mean

            return mean(
                [
                    x[0]
                    for x in self.measurements[
                        HealthDevice.MEASUREMENT_NAME_HEART_RATE_RESTING
                    ]
                ]
            )
        return None

    def did_update_steps(self, botengine):
        """
        Determine if we updated the steps in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the steps in this execution
        """
        return HealthDevice.MEASUREMENT_NAME_STEPS in self.last_updated_params

    def get_steps(self, botengine):
        """
        Retrieve the most recent steps value with timestamp
        :param botengine:
        :return:
        """

        if HealthDevice.MEASUREMENT_NAME_STEPS in self.measurements:
            return self.measurements[HealthDevice.MEASUREMENT_NAME_STEPS][0][0]
        return None

    def did_change_blood_pressure_systolic_max(self, botengine):
        """
        Did the Systolic blood pressure max change? (Bottom number of blood pressure)
        :param botengine:
        :return: True if the diastolic blood pressure changed
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYS_MAX in self.measurements:
            return (
                HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYS_MAX
                in self.last_updated_params
            )

    def did_change_blood_pressure_diastolic_max(self, botengine):
        """
        Did the Diastolic blood pressure max change? (Bottom number of blood pressure)
        :param botengine:
        :return: True if the diastolic blood pressure changed
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIA_MAX in self.measurements:
            return (
                HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIA_MAX
                in self.last_updated_params
            )

    def did_change_blood_pressure_diastolic(self, botengine):
        """
        Did the Diastolic blood pressure change? (Bottom number of blood pressure)
        :param botengine:
        :return: True if the diastolic blood pressure changed
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC in self.measurements:
            return (
                HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC
                in self.last_updated_params
            )

    def did_change_blood_pressure_systolic(self, botengine):
        """
        Did the systolic blood pressure change? (Top number of blood pressure)
        :param botengine:
        :return: True if systolic blood pressure changed
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC in self.measurements:
            return (
                HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC
                in self.last_updated_params
            )

    def did_change_hematocrit(self, botengine):
        """
        Did hematocrit change? (Percentage of red blood cells in your blood)
        :param botengine:
        :return: True if hematocrit changed
        """
        if HealthDevice.MEASUREMENT_NAME_HEMATOCRIT in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_HEMATOCRIT in self.last_updated_params

    def did_change_hemoglobin(self, botengine):
        """
        Did the hemoglobin change?  (Protein in red blood cell that carries oxygen - low or high oxygenated red blood
        cell count - tells if one is anemic or not)
        :param botengine:
        :return: True if hemoglobin changed
        """
        if HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN in self.last_updated_params

    def did_change_heart_rate(self, botengine):
        """
        Did the heart rate change? (Pulse Rate per minute)
        :param botengine:
        :return: True if heart rate changed
        """
        if HealthDevice.MEASUREMENT_NAME_HEART_RATE in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_HEART_RATE in self.last_updated_params

    def did_change_hr_variability(self, botengine):
        """
        Did the heart rate variability change? (The variance in time between the beats of your heart. If 60 beats
        per minute, it's not beating once per second, there may be .9 seconds between two beats and
         1.15 seconds between two beats. The greater the variability, the healthier a patient is )
        :param botengine:
        :return: True if hr variability changed
        """
        if HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.measurements:
            return (
                HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.last_updated_params
            )

    def did_change_perfusion_index(self, botengine):
        """
        Did the perfusion index change? (Oxygen levels in blood)
        :param botengine:
        :return: True if perfusion index change
        """
        if HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX in self.measurements:
            return (
                HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX
                in self.last_updated_params
            )

    def did_change_pleth_variability_index(self, botengine):
        """
        Did the pleth variablity index change?
        :param botengine:
        :return: True if pleth variability index changed
        """
        if HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX in self.measurements:
            return (
                HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX
                in self.last_updated_params
            )

    def did_change_protein(self, botengine):
        """
        Did protein change?
        :param botengine:
        :return: True if protein changed
        """
        if HealthDevice.MEASUREMENT_NAME_PROTEIN in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_PROTEIN in self.last_updated_params

    def did_change_spo2(self, botengine):
        """
        Did spO2 change? (Oxygen Perfusion
        :param botengine:
        :return: True if spo2 changed
        """
        if HealthDevice.MEASUREMENT_NAME_SPO2 in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_SPO2 in self.last_updated_params

    def get_blood_pressure_diastolic_max(self, botengine):
        """
        Retrieve the Diastolic blood pressure max change (Bottom number of blood pressure)
        :param botengine:
        :return: diastolic blood pressure measurement
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIA_MAX in self.measurements:
            if (
                len(
                    self.measurements[
                        HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIA_MAX
                    ]
                )
                > 0
            ):
                return self.measurements[
                    HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIA_MAX
                ][0][0]

        return None

    def get_blood_pressure_systolic_max(self, botengine):
        """
        Retrieve the Systolic blood pressure max change (Bottom number of blood pressure)
        :param botengine:
        :return: systolic blood pressure measurement
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYS_MAX in self.measurements:
            if (
                len(
                    self.measurements[
                        HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYS_MAX
                    ]
                )
                > 0
            ):
                return self.measurements[
                    HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYS_MAX
                ][0][0]

        return None

    def get_blood_pressure_diastolic(self, botengine):
        """
        Retrieve the Diastolic blood pressure change (Bottom number of blood pressure)
        :param botengine:
        :return: diastolic blood pressure measurement
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC in self.measurements:
            if (
                len(
                    self.measurements[
                        HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC
                    ]
                )
                > 0
            ):
                return self.measurements[
                    HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC
                ][0][0]

        return None

    def get_blood_pressure_systolic(self, botengine):
        """
        Retrieve systolic blood pressure (Top number of blood pressure)
        :param botengine:
        :return: systolic blood pressure measurement
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC in self.measurements:
            if (
                len(
                    self.measurements[
                        HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC
                    ]
                )
                > 0
            ):
                return self.measurements[
                    HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC
                ][0][0]

        return None

    def get_hematocrit(self, botengine):
        """
        Retrieve hematocrit (Percentage of red blood cells in your blood)
        :param botengine:
        :return: hematocrit measurement
        """
        if HealthDevice.MEASUREMENT_NAME_HEMATOCRIT in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_HEMATOCRIT]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_HEMATOCRIT][0][0]

        return None

    def get_hemoglobin(self, botengine):
        """
        Retrieve hemoglobin  (Protein in red blood cell that carries oxygen - low or high oxygenated red blood
        cell count - tells if one is anemic or not)
        :param botengine:
        :return: hemoglobin measurement
        """
        if HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN][0][0]

        return None

    def get_hr_variability(self, botengine):
        """
        Retrieve hr variability (The variance in time between the beats of your heart. If 60 beats
        per minute, it's not beating once per second, there may be .9 seconds between two beats and
         1.15 seconds between two beats. The greater the variability, the healthier a patient is )
        :param botengine:
        :return: hr variability measurement
        """
        if HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY][
                    0
                ][0]

        return None

    def get_average_hr_variability(self, botengine):
        """
        Retrieve hr variability (The variance in time between the beats of your heart. If 60 beats
        per minute, it's not beating once per second, there may be .9 seconds between two beats and
         1.15 seconds between two beats. The greater the variability, the healthier a patient is )
        :param botengine:
        :return: hr variability measurement
        """
        if HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY]) > 0:
                from statistics import mean

                return mean(
                    [
                        x[0]
                        for x in self.measurements[
                            HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY
                        ]
                    ]
                )

        return None

    def get_perfusion_index(self, botengine):
        """
        Retrieve perfusion index (Oxygen levels in blood)
        :param botengine:
        :return: perfusion index measurement
        """
        if HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX in self.measurements:
            if (
                len(self.measurements[HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX])
                > 0
            ):
                return self.measurements[HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX][
                    0
                ][0]

        return None

    def get_pleth_variability_index(self, botengine):
        """
        Retrieve pleth variability
        :param botengine:
        :return: pleth variability measurement
        """
        if HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX in self.measurements:
            if (
                len(
                    self.measurements[
                        HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX
                    ]
                )
                > 0
            ):
                return self.measurements[
                    HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX
                ][0][0]

        return None

    def get_protein(self, botengine):
        """
        Retrieve protein
        :param botengine:
        :return: protein measurement
        """
        if HealthDevice.MEASUREMENT_NAME_PROTEIN in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_PROTEIN]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_PROTEIN][0][0]

        return None

    def get_spo2(self, botengine):
        """
        Retrieve sp02 (Oxygen Perfusion)
        :param botengine:
        :return: sp02 measurement
        """
        if HealthDevice.MEASUREMENT_NAME_SPO2 in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_SPO2]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_SPO2][0][0]

        return None

    # - (Deprecated) -#

    def set_health_user(self, botengine, detect_movements):
        # Deprecated
        pass

    def set_user_position(self, botengine, latitude, longitude):
        # Deprecated
        pass

    def did_update_movement_status(self, botengine):
        # Deprecated
        pass

    def get_movement_status(self, botengine):
        # Deprecated
        pass

    def is_detecting_movement(self, botengine):
        # Deprecated
        pass

    def did_update_sleep(self, botengine):
        # Deprecated
        pass

    def get_sleep_analysis(self, botengine, index=0):
        # Deprecated
        pass

    def get_health_user(self, botengine):
        # Deprecated
        pass

    def record_moving_information(self, botengine, moving):
        # Deprecated
        pass

    def record_moving_knowledge(self, botengine, moving):
        # Deprecated
        pass

    def information_did_update_user(botengine, location_object, device_object):
        # Deprecated
        pass

    def health_movement_status_updated(
        botengine, location_object, device_object, movement_detected, movement_count
    ):
        # Deprecated
        pass
