"""
Created on March 3, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

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
        "silence": 0,
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
        "whistle": 14,
    }

    def did_tamper(self, botengine):
        """
        Did someone tamper with this device
        :param botengine:
        :return:
        """
        return False

    # ===========================================================================
    # Capabilities
    # ===========================================================================
    def has_dogbark(self, botengine):
        """
        Determine if this siren supports a dog bark sound
        :param botengine:
        :return: True if this siren supports a dog bark sound
        """
        return True

    def has_doorbell(self, botengine):
        """
        Determine if this siren supports a doorbell sound
        :param botengine:
        :return:
        """
        return True

    # ===========================================================================
    # Commands
    # ===========================================================================
    def play_sound(
        self, botengine, sound_id, strobe, duration_sec, microservice_identifier=""
    ):
        """
        Squawk the given sound ID
        :param botengine: BotEngine
        :param sound_id: Sound ID to play
        :param strobe: True to activate the strobe light
        :param duration_sec: 1 = play once; 2+ = play this many seconds.
        """
        if self.locked_microservice is not None:
            if self.locked_microservice != microservice_identifier:
                botengine.get_logger().info(
                    "Siren: Currently locked by {}, cannot play sound from microservice {}".format(
                        self.locked_microservice, microservice_identifier
                    )
                )
                return

        param_sound = {"name": "ppc.alarmWarn", "value": int(sound_id)}

        param_strobe = {"name": "ppc.alarmStrobe", "value": int(strobe)}

        param_duration = {"name": "ppc.alarmDuration", "value": int(duration_sec)}

        botengine.send_commands(
            self.device_id,
            [param_sound, param_strobe, param_duration],
            command_timeout_ms=5000,
        )

    def force_silence(self, botengine):
        """
        Force silence, even if this is locked by some other service.
        :param botengine:
        :return:
        """
        self.play_sound(
            botengine,
            self.SOUNDS["silence"],
            False,
            0,
            microservice_identifier=self.locked_microservice,
        )

    def silence(self, botengine, microservice_identifier=""):
        """
        Silence
        :param botengine:
        :return:
        """
        self.play_sound(
            botengine, self.SOUNDS["silence"], False, 0, microservice_identifier
        )

    def squawk(self, botengine, warning=False, microservice_identifier=""):
        """
        Squawk
        :param warning: True for a little warning squawk, False for a more alarming squawk
        """
        if self.locked_microservice is not None:
            if self.locked_microservice != microservice_identifier:
                botengine.get_logger().info(
                    "Siren: Currently locked by {}, cannot play sound from microservice {}".format(
                        self.locked_microservice, microservice_identifier
                    )
                )
                return

        style = self.SOUNDS["warning"]
        self.play_sound(
            botengine, style, False, 1, microservice_identifier=microservice_identifier
        )

    def alarm(self, botengine, on, microservice_identifier=""):
        """
        Sound the alarm
        :param on: True for on, False for off
        """
        if self.locked_microservice is not None:
            if self.locked_microservice != microservice_identifier:
                botengine.get_logger().info(
                    "Siren: Currently locked by {}, cannot play sound from microservice {}".format(
                        self.locked_microservice, microservice_identifier
                    )
                )
                return

        if on:
            self.play_sound(
                botengine,
                self.SOUNDS["alarm"],
                True,
                900,
                microservice_identifier=microservice_identifier,
            )

        else:
            self.play_sound(
                botengine, self.SOUNDS["silence"], False, 0, microservice_identifier
            )

    def disarmed(self, botengine, microservice_identifier=""):
        """
        Make a sound that the home is disarmed
        :param botengine:
        :return:
        """
        self.play_sound(
            botengine,
            LinkhighSirenDevice.SOUNDS["trumpet"],
            False,
            1,
            microservice_identifier,
        )

    def short_warning(self, botengine, microservice_identifier=""):
        """
        Make a sound that the home is disarmed
        :param botengine:
        :return:
        """
        self.play_sound(
            botengine,
            LinkhighSirenDevice.SOUNDS["bling"],
            True,
            1,
            microservice_identifier,
        )

    def about_to_arm(self, botengine, seconds_left, microservice_identifier=""):
        """
        Make a unique aggressive warning noise the amount of time remaining
        :param botengine:
        :param seconds_left: Seconds left before arming
        :return:
        """
        self.play_sound(
            botengine,
            LinkhighSirenDevice.SOUNDS["warning"],
            True,
            seconds_left,
            microservice_identifier,
        )

    def armed(self, botengine, microservice_identifier=""):
        """
        Make a sound that the home is disarmed
        :param botengine:
        :return:
        """
        self.play_sound(
            botengine,
            LinkhighSirenDevice.SOUNDS["lock"],
            False,
            1,
            microservice_identifier,
        )

    def bark(self, botengine, duration_sec, microservice_identifier=""):
        """
        Dog bark
        :param botengine:
        :param duration_sec
        :return:
        """
        self.play_sound(
            botengine,
            LinkhighSirenDevice.SOUNDS["dog"],
            True,
            duration_sec,
            microservice_identifier,
        )

    def doorbell(self, botengine, microservice_identifier=""):
        """
        Make a doorbell sound.
        :param botengine:
        :return:
        """
        if self.locked_microservice is None:
            self.play_sound(
                botengine, self.SOUNDS["doorbell"], True, 1, microservice_identifier
            )

    def door_opened(self, botengine, microservice_identifier=""):
        """
        Door opened chime
        :param botengine:
        :return:
        """
        self.play_sound(
            botengine,
            LinkhighSirenDevice.SOUNDS["bird"],
            False,
            1,
            microservice_identifier,
        )
