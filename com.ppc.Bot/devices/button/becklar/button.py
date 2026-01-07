'''
Created on January 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.button.button_mpers import MobileButtonDevice


class BecklarButtonDevice(MobileButtonDevice):
    """
    Becklar Button Device (Belle X)
    
    Advanced mobile button device with comprehensive event detection and monitoring
    capabilities. This device extends MobileButtonDevice to provide specialized
    functionality for emergency response, fall detection, and health monitoring.
    
    Device Features:
    - Emergency SOS button functionality
    - Fall detection and cancellation
    - Silent alarm capabilities
    - Charging status monitoring
    - Power state tracking
    - Movement detection
    - Call management
    - Status reporting
    
    Event Types Supported:
    - SOS: Emergency distress signal
    - FALL: Fall detection event
    - CANCEL_FALL: Fall detection cancellation
    - CHARGER_CONNECT/DISCONNECT: Charging status changes
    - POWER_OFF/POWERED_ON: Device power state changes
    - END_CALL: Call termination
    - START_MOVING/STOP_MOVING: Movement detection
    - STATUS_REPORT: Periodic status updates
    - SILENT_ALARM: Silent emergency alert
    
    Measurement Parameters:
    - eventType: String indicating the type of event that occurred
    - batteryLevel: Battery level percentage (inherited from MobileButtonDevice)
    - mobileSignal: Cellular signal strength (inherited from MobileButtonDevice)
    
    Device Type Compatibility:
    - Device Type ID: 4280 (Belle X)
    
    Usage:
    This device is designed for personal safety and health monitoring applications,
    particularly for elderly or at-risk individuals who may need emergency assistance
    or fall detection services.
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [4280]

    # Measurement names
    MEASUREMENT_NAME_EVENT_TYPE = 'eventType'

    # Goals
    GOAL_BUTTON_CALL_FOR_HELP = 0

    # Charging State Enum
    CHARGING_STATE_CHARGING     = "CHARGING"
    CHARGING_STATE_NOT_CHARGING = "NOT_CHARGING"
    
    # Call Progress Enum
    CALL_PROGRESS_NONE          = "NONE"
    CALL_PROGRESS_OUTBOUND_CALL = "OUTBOUND_CALL"
    CALL_PROGRESS_INBOUND_CALL  = "INBOUND_CALL"

    # Event Types
    EVENT_TYPE_SOS                  = 'SOS'
    EVENT_TYPE_FALL                 = 'FALL'
    EVENT_TYPE_CANCEL_FALL          = 'CANCEL_FALL'
    EVENT_TIME_CHARGER_CONNECT      = 'CHARGER_CONNECT'
    EVENT_TYPE_CHARGET_DISCONNECT   = 'CHARGET_DISCONNECT'
    EVENT_TYPE_POWER_OFF            = 'POWER_OFF'
    EVENT_TYPE_POWERED_ON           = 'POWERED_ON'
    EVENT_TYPE_END_CALL             = 'END_CALL'
    EVENT_TYPE_START_MOVING         = 'START_MOVING'
    EVENT_TYPE_STOP_MOVING          = 'STOP_MOVING'
    EVENT_TYPE_STATUS_REPORT        = 'STATUS_REPORT'
    EVENT_TYPE_SILENT_ALARM         = 'SILENT_ALARM'

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        MobileButtonDevice.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Default behavior
        self.goal_id = BecklarButtonDevice.GOAL_BUTTON_CALL_FOR_HELP

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Belle X")
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "push-button"
    
    def did_event_type_change(self, botengine=None):
        """
        Did the event type change?
        :param botengine:
        :return: True if the event type changed
        """
        if BecklarButtonDevice.MEASUREMENT_NAME_EVENT_TYPE in self.measurements:
            if BecklarButtonDevice.MEASUREMENT_NAME_EVENT_TYPE in self.last_updated_params:
                return True

        return False
    
    def get_event_type(self, botengine=None):
        """
        Get the event type
        :param botengine:
        :return: Event type
        """
        if BecklarButtonDevice.MEASUREMENT_NAME_EVENT_TYPE in self.measurements:
            return self.measurements[BecklarButtonDevice.MEASUREMENT_NAME_EVENT_TYPE][0][0]

        return None
    
    def did_start_sos(self, botengine=None):
        """
        Did the button start an SOS?
        :param botengine:
        :return: True if the button started an SOS
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_SOS:
            return True

        return False
    
    def did_start_silent_alarm(self, botengine=None):
        """
        Did the button start a silent alarm?
        :param botengine:
        :return: True if the button started a silent alarm
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_SILENT_ALARM:
            return True

        return False
    
    def did_record_fall(self, botengine=None):
        """
        Did the button record a fall?
        :param botengine:
        :return: True if the button recorded a fall
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_FALL:
            return True

        return False
    
    def did_cancel_fall(self, botengine=None):
        """
        Did the button cancel a fall?
        :param botengine:
        :return: True if the button canceled a fall
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_CANCEL_FALL:
            return True

        return False
    
    def did_connect_charger(self, botengine=None):
        """
        Did the button connect to a charger?
        :param botengine:
        :return: True if the button connected to a charger
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TIME_CHARGER_CONNECT:
            return True

        return False
    
    def did_disconnect_charger(self, botengine=None):
        """
        Did the button disconnect from a charger?
        :param botengine:
        :return: True if the button disconnected from a charger
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_CHARGET_DISCONNECT:
            return True

        return False
    
    def did_power_off(self, botengine=None):
        """
        Did the button power off?
        :param botengine:
        :return: True if the button powered off
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_POWER_OFF:
            return True

        return False
    
    def did_power_on(self, botengine=None):
        """
        Did the button power on?
        :param botengine:
        :return: True if the button powered on
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_POWERED_ON:
            return True

        return False
    
    def did_end_call(self, botengine=None):
        """
        Did the button end a call?
        :param botengine:
        :return: True if the button ended a call
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_END_CALL:
            return True

        return False
    
    def did_start_moving(self, botengine=None):
        """
        Did the button start moving?
        :param botengine:
        :return: True if the button started moving
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_START_MOVING:
            return True

        return False
    
    def did_stop_moving(self, botengine=None):
        """
        Did the button stop moving?
        :param botengine:
        :return: True if the button stopped moving
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_STOP_MOVING:
            return True

        return False
    
    def did_report_status(self, botengine=None):
        """
        Did the button report status?
        :param botengine:
        :return: True if the button reported status
        """
        if self.did_event_type_change(botengine) and \
            self.get_event_type(botengine) == BecklarButtonDevice.EVENT_TYPE_STATUS_REPORT:
            return True

        return False
    
    def get_event_type_timestamp(self, botengine=None):
        """
        Get the timestamp of the last event type measurement received
        :param botengine:
        :return: Timestamp of the last event type measurement in ms; None if it doesn't exist
        """
        if BecklarButtonDevice.MEASUREMENT_NAME_EVENT_TYPE in self.measurements:
            return self.measurements[BecklarButtonDevice.MEASUREMENT_NAME_EVENT_TYPE][0][1]

        return None
    