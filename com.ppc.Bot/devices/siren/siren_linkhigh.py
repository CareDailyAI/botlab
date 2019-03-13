'''
Created on March 3, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.siren.siren import SirenDevice


# For the LinkHigh siren, send all 3 parameters simultaneously:
# ppc.alarmWarn = sound id to play
# ppc.alarmDuration = 1 is play once, 2+ is play for that many seconds
# ppc.alarmStrobe = 0 or 1 to turn the strobe light off or on.


class LinkhighSirenDevice(SirenDevice):
    """Siren"""

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9009]

    # Sound library
    SOUNDS = {
        "alarm": 1,
        "dog": 2,
        "warning": 3,
        "bling": 4,
        "bird": 5,
        "droid": 6,
        "lock": 7,
        "phaser": 8,
        "doorbell": 9,
        "guncock": 10,
        "gunshot": 11,
        "switch": 12,
        "trumpet": 13,
        "whistle": 14
    }

    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        SirenDevice.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Last sound played
        self.last_sound = None

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
    def squawk(self, botengine, warning=False):
        """
        Squawk
        :param warning: True for a little warning squawk, False for a more alarming squawk
        """
        style = self.SOUNDS['warning']
        self.play_sound(botengine, style, False, 1)

    def alarm(self, botengine, on):
        """
        Sound the alarm
        :param on: True for on, False for off
        """
        if on:
            self.last_sound = self.SOUNDS['alarm']
            self.play_sound(botengine, self.SOUNDS['alarm'], True, 900)

        else:
            self.play_sound(botengine, self.SOUNDS['alarm'], False, 0)


    def play_sound(self, botengine, sound_id, strobe, duration_sec):
        """
        Squawk the given sound ID
        :param botengine: BotEngine
        :param sound_id: Sound ID to play
        :param strobe: True to activate the strobe light
        :param duration_sec: 1 = play once; 2+ = play this many seconds.
        """
        param_sound = {
                  "name": "ppc.alarmWarn",
                  "value": int(sound_id)
                  }

        param_strobe = {
                  "name": "ppc.alarmStrobe",
                  "value": int(strobe)
                  }

        param_duration = {
                  "name": "ppc.alarmDuration",
                  "value": int(duration_sec)
                  }

        botengine.send_commands(self.device_id, [param_sound, param_strobe, param_duration], command_timeout_ms=5000)
