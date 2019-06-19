'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device


class SirenDevice(Device):
    """Siren"""

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Siren")
    
    def get_image_name(self):
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
    
    def squawk(self, botengine, warning=False, microservice_identifier=""):
        """
        Squawk
        :param warning: True for a little warning squawk, False for a more alarming squawk
        """
        raise NotImplementedError
    
    def alarm(self, botengine, on, microservice_identifier=""):
        """
        Sound the alarm
        :param on: True for on, False for off
        """
        raise NotImplementedError
    
        
    def play_sound(self, botengine, sound_id, strobe, duration_sec, microservice_identifier=""):
        """
        Squawk the given sound ID
        :param botengine: BotEngine
        :param sound_id: Sound ID to play
        :param strobe: True to activate the strobe light
        :param duration_sec: 1 = play once; 2+ = play this many seconds.
        """
        raise NotImplementedError

    def doorbell(self, botengine):
        """
        Doorbell noise
        :param botengine: BotEngine
        """
        raise NotImplementedError

    def lock(self, botengine, microservice_identifier):
        """
        Lock the siren to some microservice - for example to use the siren exclusively for security purposes.
        :param botengine:
        :param microservice_identifier:
        :return:
        """
        raise NotImplementedError

    def unlock(self, botengine):
        """
        Unlock the siren
        :param botengine:
        :param microservice_identifier:
        :return:
        """
        raise NotImplementedError
