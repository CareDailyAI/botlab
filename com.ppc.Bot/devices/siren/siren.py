'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device


class SirenDevice(Device):
    """Siren"""

    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Siren")
    
    def get_image_name(self, botengine):
        """
        :return: the font icon name of this device type
        """
        return "siren"
    
    #===========================================================================
    # Commands
    #===========================================================================
    def is_audible(self, botengine):
        """
        :return: True, this is an audible device
        """
        return True
    
    def squawk(self, botengine, warning=False):
        """
        Squawk
        :param warning: True for a little warning squawk, False for a more alarming squawk
        """
        raise NotImplementedError
    
    def alarm(self, botengine, on):
        """
        Sound the alarm
        :param on: True for on, False for off
        """
        raise NotImplementedError
    
        
    def play_sound(self, botengine, sound_id, strobe, duration_sec):
        """
        Squawk the given sound ID
        :param botengine: BotEngine
        :param sound_id: Sound ID to play
        :param strobe: True to activate the strobe light
        :param duration_sec: 1 = play once; 2+ = play this many seconds.
        """
        raise NotImplementedError
