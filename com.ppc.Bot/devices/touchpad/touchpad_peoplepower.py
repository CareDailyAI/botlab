"""
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.device import Device

# Here are a list of .mp3 files pre-installed on the Touchpad device:
#
#   * 30seconds_en.mp3
#   * 60seconds_en.mp3
#   * alarm.mp3
#   * arming_en.mp3
#   * armingrestart_en.mp3
#   * beep.mp3
#   * beep_07.mp3
#   * camera_shutter.mp3
#   * compliment_0_en.mp3
#   * compliment_10_en.mp3
#   * compliment_11_en.mp3
#   * compliment_12_en.mp3
#   * compliment_13_en.mp3
#   * compliment_14_en.mp3
#   * compliment_15_en.mp3
#   * compliment_16_en.mp3
#   * compliment_17_en.mp3
#   * compliment_18_en.mp3
#   * compliment_19_en.mp3
#   * compliment_1_en.mp3
#   * compliment_20_en.mp3
#   * compliment_21_en.mp3
#   * compliment_22_en.mp3
#   * compliment_23_en.mp3
#   * compliment_24_en.mp3
#   * compliment_25_en.mp3
#   * compliment_26_en.mp3
#   * compliment_2_en.mp3
#   * compliment_3_en.mp3
#   * compliment_4_en.mp3
#   * compliment_5_en.mp3
#   * compliment_6_en.mp3
#   * compliment_7_en.mp3
#   * compliment_8_en.mp3
#   * compliment_9_en.mp3
#   * disarmed_en.mp3
#   * dispatch_en.mp3
#   * enteringtestmode_en.mp3
#   * fullyarmed_en.mp3
#   * incorrectcode_en.mp3
#   * leak_en.mp3
#   * leavingtestmode_en.mp3
#   * low_beep.mp3
#   * perimeterarmed_en.mp3
#   * welcomehome_en.mp3
#
# Enjoy.


class PeoplePowerTouchpadDevice(Device):
    """Touchpad Device"""

    DEVICE_TYPES = [25]

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

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Touchpad")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "touchpad"

    # ===========================================================================
    # Commands
    # ===========================================================================
    def play_sound(self, botengine, sound, command_timeout_ms=5000):
        """
        :param sound: Play the given sound file, for example "beep.mp3" or "alarm.mp3"
        """
        if not self.is_connected:
            return False

        # self.log("Playing " + sound + " on touchpad " + self.description)
        botengine.send_command(
            self.device_id,
            "ppc.playSound",
            sound,
            command_timeout_ms=command_timeout_ms,
        )
        return True

    def play_countdown(
        self, botengine, audio_seconds, visual_seconds, command_timeout_ms=5000
    ):
        """
        Play the audio countdown for the given number of seconds
        :param seconds: Seconds to countdown, 0 to stop
        """
        if not self.can_control:
            return False

        # self.log("Playing countdown audio for " + str(seconds) + " seconds")

        if audio_seconds != 0 and audio_seconds < 5:
            audio_seconds = 5
            visual_seconds = 5

        audio_countdown_command = botengine.form_command(
            "ppc.countdown", str(audio_seconds)
        )
        visual_countdown_command = botengine.form_command(
            "ppc.visualCountdown", str(visual_seconds)
        )

        botengine.send_commands(
            self.device_id,
            [audio_countdown_command, visual_countdown_command],
            command_timeout_ms=command_timeout_ms,
        )
        return True

    def play_sound_and_countdown(
        self, botengine, sound, audio_seconds, visual_seconds, command_timeout_ms=5000
    ):
        """
        Play both a sound and the countdown
        :param sound: Sound file to play, i.e. "beep.mp3".  "" to silence
        :param audio_seconds: Audio countdown in seconds. 0 to silence.
        :param visual_seconds: Visual countdown in seconds. 0 for no visuals.
        """
        if not self.can_control:
            return False

        sound_command = botengine.form_command("ppc.playSound", sound)

        if audio_seconds != 0 and audio_seconds < 5:
            audio_seconds = 5
            visual_seconds = 5

        botengine.get_logger().info(
            "Playing countdown audio for "
            + str(audio_seconds)
            + " seconds; visual countdown for "
            + str(visual_seconds)
            + "; Playing sound "
            + sound
            + ": on "
            + self.description
        )

        audio_countdown_command = botengine.form_command(
            "ppc.countdown", str(audio_seconds)
        )
        visual_countdown_command = botengine.form_command(
            "ppc.visualCountdown", str(visual_seconds)
        )

        botengine.send_commands(
            self.device_id,
            [sound_command, audio_countdown_command, visual_countdown_command],
            command_timeout_ms=command_timeout_ms,
        )
        return True

    def beep(self, botengine, times, command_timeout_ms=5000):
        """
        Make the camera beep
        :param times: 1, 2, or 3
        """
        if not self.can_control:
            return False

        botengine.send_command(
            self.device_id,
            "ppc.alarm",
            times + 1,
            command_timeout_ms=command_timeout_ms,
        )
        return True

    def alarm(self, botengine, on, command_timeout_ms=10000):
        """
        Turn the alarm on or off
        :param on: Boolean. True for on, False for complete silence including turning off the countdown
        """
        if not self.can_control:
            return False

        botengine.send_command(
            self.device_id,
            "ppc.alarm",
            str(int(on)),
            command_timeout_ms=command_timeout_ms,
        )
        return True

    def notify_mode_changed(self, botengine, mode, command_timeout_ms=10000):
        """
        Send a command to the Touchpad to declare that the mode has changed.
        :param botengine:
        :param mode: New mode
        :return:
        """
        botengine.send_command(
            self.device_id, "ppc.mode", str(mode), command_timeout_ms=command_timeout_ms
        )

    def notify(self, botengine, push_content, push_sound, command_timeout_ms=5000):
        """
        Send a manual push notification to this device
        :param botengine: BotEngine environment
        :param push_content: Push notification content
        """
        commands = [botengine.form_command("ppc.notification", push_content)]

        if push_sound is not None:
            commands.append(botengine.form_command("ppc.playSound", push_sound))

        botengine.send_commands(
            self.device_id, commands, command_timeout_ms=command_timeout_ms
        )
