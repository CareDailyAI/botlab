'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.display.display import DisplayDevice

# "userId": "hm0vjHUXb7f6nKKadmXqISeLsBJ2",
# "lastCheckIn": 1704984982, // this is the heartbeat from device to backend
# "onlineStatusChangedAt": 1704965483, // if currently online, this is when it was deemed online. If offline, when it went offline
# "online": true, 
# "signalStrength": -57,
# "ping": 43,
# "currentView": "home", // current activity for the device . could be [home, call, message, youtube, zoom, checkin, setup, aicompanion, tv, other]
# "version": "4.0.8.1704811411", // our main software version (app level)
# "model": "KA2", // current model. does not reflect subscription based feature sets
# "hasHdmiInputConnected": false, // true if there is equipment plugged in to units HDMI-In port
# "serialNumber": "55902152003043",
# "romVersion": "1.6",
# "isCamHardwareMuted": false, // manual privacy shutter on unit
# "isMicHardwareMuted": false, // manual switch on unit
# "isCECEnabled": false
class OnscreenDisplayDevice(DisplayDevice):
    """Onscreen Display"""

    # Goals
    GOAL_DEFAULT = 0

    # Measurement Names
    MEASUREMENT_NAME_STATUS = 'currentView'

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS
    ]
    
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [4270]
    
    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        DisplayDevice.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)
        
    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        DisplayDevice.initialize(self, botengine)
        
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Onscreen")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "tv"

    #===========================================================================
    # Attributes
    #===========================================================================

    def last_state_change_timestamp_ms(self, botengine):
        """
        Get the last time this entertainment sensor opened or closed
        :param botengine:
        :return: timestamp in ms
        """
        if OnscreenDisplayDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            return self.measurements[OnscreenDisplayDevice.MEASUREMENT_NAME_STATUS][0][1]

        return None
