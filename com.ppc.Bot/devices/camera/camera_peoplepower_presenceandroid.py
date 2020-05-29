'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.camera.camera_peoplepower_presence import PeoplePowerPresenceCameraDevice

class PeoplePowerPresenceAndroidCameraDevice(PeoplePowerPresenceCameraDevice):
    """Camera Device"""
    
    DEVICE_TYPES = [23]
    
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Android Camera")
    
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        if 'ppc.robotConnected' in self.measurements:
            if len(self.measurements['ppc.robotConnected']) > 0:
                if self.measurements['ppc.robotConnected'][0][0] == self.ROBOT_PRESENCE_360:
                    return "360"
        
        return "camera-android"
    