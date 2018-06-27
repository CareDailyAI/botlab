'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.siren.siren import SirenDevice


#1.  Alarm sound.
#Parameters:
#ppc.alarmWarn - Alarm sound from 1 to 3.
#ppc.alarmDuration - duration in seconds. I think 240 is maximum, but I did not try.
#ppc.alarmStrobe - 1 - to flash LED's
#
#2. "Beep"
#Parameters:
#ppc.alarmSquawk - 0 = once, 1 = twice
#ppc.alarmStrobe - 1 - to flash LED's


# ALARM SQUAWK
ALARM_SQUAWK_A = 0
ALARM_SQUAWK_B = 1

# ALARM STROBE
ALARM_STROBE_OFF = 0
ALARM_STROBE_ON = 1

# ALARM SQUAWK MODE
ALARM_SQUAWK_MODE_ARMED = 0
ALARM_SQUAWK_MODE_DISARMED = 1

# ALARM WARNING SOUNDS
ALARM_WARN_OFF = 0
ALARM_WARN_HIGH_PITCH = 1
ALARM_WARN_WOOP_WOOP = 2
ALARM_WARN_WAH_WAH = 3
ALARM_WARN_ER = 4
ALARM_WARN_SAN = 5
ALARM_WARN_SI = 6
ALARM_WARN_WU = 7
ALARM_WARN_LIU = 8
ALARM_WARN_QI = 9
ALARM_WARN_BA = 10
ALARM_WARN_JIU = 11
ALARM_WARN_SAI = 12  #??
ALARM_WARN_SHI_YEN = 13 #??
ALARM_WARN_STROBE_ONLY = 14
ALARM_WARN_DOORBELL = 15


class SmartenitZbalarmDevice(SirenDevice):
    """Siren"""

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9002]

    #===========================================================================
    # Commands
    #===========================================================================
    def squawk(self, botengine, warning=False):
        """
        Squawk
        :param warning: True for a little warning squawk, False for a more alarming squawk
        """
        style = ALARM_WARN_WOOP_WOOP
        if not warning:
            style = ALARM_WARN_HIGH_PITCH

        self.custom_squawk(botengine, style, ALARM_STROBE_ON)


    def alarm(self, botengine, on):
        """
        Sound the alarm
        :param on: True for on, False for off
        """
        if on:
            self.custom_alarm(botengine, ALARM_WARN_WOOP_WOOP, 900, ALARM_STROBE_ON)
        else:
            self.custom_alarm(botengine, ALARM_WARN_OFF, 1, ALARM_STROBE_OFF)




    def custom_squawk(self, botengine, alarm_warn, alarm_strobe):
        """
        Custom Squawk
        :param alarm_squawk: 0 or 1
        :param alarm_strobe: Strobe light off or on (0 or 1)
        """
        squawk = {
                  "name": "ppc.alarmWarn",
                  "value": alarm_warn
                  }

        strobe = {
                  "name": "ppc.alarmStrobe",
                  "value": alarm_strobe
                  }

        duration = {
                  "name": "ppc.alarmDuration",
                  "value": "1"
                  }

        botengine.send_commands(self.device_id, [squawk, strobe, duration])


    def custom_alarm(self, botengine, alarm_warn, alarm_duration, alarm_strobe):
        """
        Custom Alarm
        :param alarm_warn: Which sound to make (see ALARM_WARN_* definitions)
        :param alarm_duration: How long in seconds
        :param alarm_strobe: Strobe light off or on (0 or 1)
        """
        warn = {
                "name": "ppc.alarmWarn",
                "value": alarm_warn
                }

        duration = {
                    "name": "ppc.alarmDuration",
                    "value": alarm_duration
                    }

        strobe = {
                  "name": "ppc.alarmStrobe",
                  "value": alarm_strobe
                  }

        botengine.send_commands(self.device_id, [warn, duration, strobe])

