'''
Created on April 24, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.siren.siren import SirenDevice


class DevelcoSirenDevice(SirenDevice):
    """
    Siren
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9102]

    # Sound library
    SOUNDS = {
        "silence": 0,               # Silent
        "burglar": 1,               # Slow UFO weeeaaaweeeaaweeeaaaweeaaa
        "fire": 2,                  # Slow looooow-hiiigh-looow-hiiiigh-looow
        "emergency": 3,             # Beep. I don't see how this is an 'emergency' sound at all.
        "panic_p": 4,               # Fast UFO weaweaweaweawea (ppc.alarmDuration=5 => do-da-de-da-do-da-de-da)
        "panic_f": 5,               # Fast low-high-low-high (ppc.alarmDuration=5 => do-da-de-da-do-da-de-da)
        "panic_e": 6,               # Beep every 2 seconds (ppc.alarmDuration=5 => do-da-de-da-do-da-de-da)

        "beepbeep_welcome": 12,     # ppc.alarmDuration=2 gives you a beep-beep and a do-da-de-da-do-da-de-da
        "beep_welcome": 13,         # ppc.alarmDuration=2 gives you a beep and a do-da-de-da-do-da-de-da
        "beepbeep": 14,             # Beep-Beep every second
        "beep": 15,                 # Beep every second
    }

    #===========================================================================
    # Commands
    #===========================================================================
    def play_sound(self, botengine, sound_id, strobe, duration_sec, volume=3, microservice_identifier=""):
        """
        Squawk the given sound ID
        :param botengine: BotEngine
        :param sound_id: Sound ID to play
        :param strobe: True to activate the strobe light
        :param duration_sec: 1 = play once; 2+ = play this many seconds.
        """
        if self.locked_microservice is not None:
            if self.locked_microservice != microservice_identifier:
                botengine.get_logger().info("Siren: Currently locked by {}, cannot play sound from microservice {}".format(self.locked_microservice, microservice_identifier))
                return

        all_params = []

        okay = False
        if "ppc.alarmStrobe" in self.measurements:
            if len(self.measurements["ppc.alarmStrobe"]) > 0:
                if self.measurements["ppc.alarmStrobe"][0][0] == int(strobe):
                    okay = True

        if not okay:
            all_params.append({
                              "name": "ppc.alarmStrobe",
                              "value": int(strobe)
                              })

        okay = False
        if "ppc.alarmDuration" in self.measurements:
            if len(self.measurements["ppc.alarmDuration"]) > 0:
                if self.measurements["ppc.alarmDuration"][0][0] == int(duration_sec):
                    okay = True

        if not okay:
            all_params.append({
                              "name": "ppc.alarmDuration",
                              "value": int(duration_sec)
                              })

        okay = False
        if "ppc.alarmLevel" in self.measurements:
            if len(self.measurements["ppc.alarmLevel"]) > 0:
                if self.measurements["ppc.alarmLevel"][0][0] == int(volume):
                    okay = True

        if not okay:
            all_params.append({
                              "name": "ppc.alarmLevel",
                              "value": int(volume)
                              })

        all_params.append({
                          "name": "ppc.alarmWarn",
                          "value": int(sound_id)
                          })

        botengine.send_commands(self.device_id, all_params, command_timeout_ms=5000)

    def squawk(self, botengine, warning=False, microservice_identifier=""):
        """
        Squawk
        :param warning: True for a little warning squawk, False for a more alarming squawk
        """
        if self.locked_microservice is not None:
            if self.locked_microservice != microservice_identifier:
                botengine.get_logger().info("Siren: Currently locked by {}, cannot play sound from microservice {}".format(self.locked_microservice, microservice_identifier))
                return

        if warning:
            style = self.SOUNDS['panic_p']
        else:
            style = self.SOUNDS['panic_f']

        self.play_sound(botengine, style, False, 1, microservice_identifier=microservice_identifier)

    def alarm(self, botengine, on, microservice_identifier=""):
        """
        Sound the alarm
        :param on: True for on, False for off
        """
        if self.locked_microservice is not None:
            if self.locked_microservice != microservice_identifier:
                botengine.get_logger().info("Siren: Currently locked by {}, cannot play sound from microservice {}".format(self.locked_microservice, microservice_identifier))
                return

        if on:
            self.play_sound(botengine, self.SOUNDS['burglar'], True, 900, microservice_identifier=microservice_identifier)

        else:
            self.play_sound(botengine, self.SOUNDS['silence'], False, 0, microservice_identifier=microservice_identifier)

    def doorbell(self, botengine):
        """
        Make a doorbell sound.
        :param botengine:
        :return:
        """
        if self.locked_microservice is None:
            self.play_sound(botengine, self.SOUNDS['panic_e'], True, 1)

    def silence(self, botengine, microservice_identifier=""):
        """
        Silence
        :param botengine:
        :return:
        """
        self.play_sound(botengine, self.SOUNDS['silence'], False, 0, microservice_identifier=microservice_identifier)

    def disarmed(self, botengine, microservice_identifier=""):
        """
        Make a sound that the home is disarmed
        :param botengine:
        :return:
        """
        self.play_sound(botengine, self.SOUNDS['beepbeep_welcome'], True, 2, microservice_identifier=microservice_identifier)

    def short_warning(self, botengine, microservice_identifier=""):
        """
        Make a sound that the home is disarmed
        :param botengine:
        :return:
        """
        botengine.get_logger().info("siren_develco '{}': short_warning() for microservice '{}'".format(self.device_id, microservice_identifier))
        self.play_sound(botengine, self.SOUNDS['panic_f'], True, 1, microservice_identifier=microservice_identifier)

    def about_to_arm(self, botengine, seconds_left, microservice_identifier=""):
        """
        Make a unique aggressive warning noise for the amount of time remaining
        :param botengine:
        :return:
        """
        self.play_sound(botengine, self.SOUNDS['beep'], True, seconds_left, microservice_identifier=microservice_identifier)

    def armed(self, botengine, microservice_identifier=""):
        """
        Make a sound that the home is disarmed
        :param botengine:
        :return:
        """
        botengine.get_logger().info("siren_develco '{}': armed() for microservice '{}'".format(self.device_id, microservice_identifier))
        self.play_sound(botengine, self.SOUNDS['panic_p'], True, 1, microservice_identifier=microservice_identifier)

    def doorbell(self, botengine, microservice_identifier=""):
        """
        Doorbell sound
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def bark(self, botengine, duration_sec, microservice_identifier=""):
        """
        Dog bark
        :param botengine:
        :param duration_sec
        :return:
        """
        raise NotImplementedError

    def door_opened(self, botengine, microservice_identifier=""):
        """
        Door opened chime
        :param botengine:
        :return:
        """
        self.play_sound(botengine, self.SOUNDS['beepbeep'], True, 1, microservice_identifier=microservice_identifier)
