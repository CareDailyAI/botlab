'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device
import utilities.utilities as utilities

# Here are a list of .mp3 files that *should be* pre-installed on smartphone-as-camera devices:
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
# And new ones from our siren:
#   * alarm2.mp3
#   * dog.mp3
#   * warning.mp3
#   * bling.mp3
#   * bird.mp3
#   * droid.mp3
#   * lock.mp3
#   * phaser.mp3
#   * doorbell.mp3
#   * guncock.mp3
#   * gunshot.mp3
#   * switch.mp3
#   * trumpet.mp3
#   * whistle.mp3
#   * whoops.mp3
#
# Enjoy.


class PeoplePowerPictureFrameDevice(Device):
    """
    Picture Frame Device
    """

    # Alert priorities for asking questions
    ALERT_PRIORITY_DEBUG = 0
    ALERT_PRIORITY_INFO = 1
    ALERT_PRIORITY_WARNING = 2
    ALERT_PRIORITY_CRITICAL = 3

    # Blackout screen parameter name
    BLACKOUT_SCREEN_PARAM = "ppc.blackoutScreenOn"

    # Device types
    DEVICE_TYPES = []
    
    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)
        
        
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Picture Frame")
    
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "touchpad"
    
    #===========================================================================
    # Commands - Save for later
    #===========================================================================
    # def play_sound(self, botengine, sound, command_timeout_ms=5000):
    #     """
    #     :param sound: Play the given sound file, for example "beep.mp3" or "alarm.mp3"
    #     """
    #     if not self.is_connected:
    #         return False
    #
    #     #self.log("Playing " + sound + " on touchpad " + self.description)
    #     botengine.send_command(self.device_id, "ppc.playSound", sound, command_timeout_ms=command_timeout_ms)
    #     return True
    #
    # def play_countdown(self, botengine, audio_seconds, visual_seconds, command_timeout_ms=5000):
    #     """
    #     Play the audio countdown for the given number of seconds
    #     :param seconds: Seconds to countdown, 0 to stop
    #     """
    #     if not self.can_control:
    #         return False
    #
    #     #self.log("Playing countdown audio for " + str(seconds) + " seconds")
    #
    #     if audio_seconds != 0 and audio_seconds < 5:
    #         audio_seconds = 5
    #         visual_seconds = 5
    #
    #     audio_countdown_command = botengine.form_command("ppc.countdown", str(audio_seconds))
    #     visual_countdown_command = botengine.form_command("ppc.visualCountdown", str(visual_seconds))
    #
    #     botengine.send_commands(self.device_id, [audio_countdown_command, visual_countdown_command], command_timeout_ms=command_timeout_ms)
    #     return True
    #
    #
    # def play_sound_and_countdown(self, botengine, sound, audio_seconds, visual_seconds, command_timeout_ms=5000):
    #     """
    #     Play both a sound and the countdown
    #     :param sound: Sound file to play, i.e. "beep.mp3".  "" to silence
    #     :param audio_seconds: Audio countdown in seconds. 0 to silence.
    #     :param visual_seconds: Visual countdown in seconds. 0 for no visuals.
    #     """
    #     if not self.can_control:
    #         return False
    #
    #     sound_command = botengine.form_command("ppc.playSound", sound)
    #
    #     if audio_seconds != 0 and audio_seconds < 5:
    #         audio_seconds = 5
    #         visual_seconds = 5
    #
    #     botengine.get_logger().info("Playing countdown audio for " + str(audio_seconds) + " seconds; visual countdown for " + str(visual_seconds) + "; Playing sound " + sound + ": on " + self.description)
    #
    #     audio_countdown_command = botengine.form_command("ppc.countdown", str(audio_seconds))
    #     visual_countdown_command = botengine.form_command("ppc.visualCountdown", str(visual_seconds))
    #
    #     botengine.send_commands(self.device_id, [sound_command, audio_countdown_command, visual_countdown_command], command_timeout_ms=command_timeout_ms)
    #     return True
    #
    # def beep(self, botengine, times, command_timeout_ms=5000):
    #     """
    #     Make the camera beep
    #     :param times: 1, 2, or 3
    #     """
    #     if not self.can_control:
    #         return False
    #
    #     botengine.send_command(self.device_id, "ppc.alarm", times + 1, command_timeout_ms=command_timeout_ms)
    #     return True
    #
    # def alarm(self, botengine, on, command_timeout_ms=10000):
    #     """
    #     Turn the alarm on or off
    #     :param on: Boolean. True for on, False for complete silence including turning off the countdown
    #     """
    #     if not self.can_control:
    #         return False
    #
    #     botengine.send_command(self.device_id, "ppc.alarm", str(int(on)), command_timeout_ms=command_timeout_ms)
    #     return True
    #

    def notify_mode_changed(self, botengine, mode, command_timeout_ms=10000):
        """
        Send a command to the Touchpad to declare that the mode has changed.
        :param botengine:
        :param mode: New mode
        :return:
        """
        botengine.send_command(self.device_id, "ppc.mode", str(mode), command_timeout_ms=command_timeout_ms)

    #
    # def notify(self, botengine, push_content, push_sound, command_timeout_ms=5000):
    #     """
    #     Send a manual push notification to this device
    #     :param botengine: BotEngine environment
    #     :param push_content: Push notification content
    #     """
    #     commands = [botengine.form_command("ppc.notification", push_content)]
    #
    #     if push_sound is not None:
    #         commands.append(botengine.form_command("ppc.playSound", push_sound))
    #
    #     botengine.send_commands(self.device_id, commands, command_timeout_ms=command_timeout_ms)
    #


    def play_sound(self, botengine, sound):
        """
        :param sound: Play the given sound file, for example "beep.mp3" or "alarm.mp3"
        """
        if not self.is_connected:
            return False

        botengine.get_logger().info("Playing file " + sound + " on camera " + self.description)

        botengine.send_command(self.device_id, "ppc.playSound", sound)

    #===========================================================================
    # Status
    #===========================================================================
    def is_screen_blacked_out(self, botengine):
        """
        Is the screen blacked out?
        :param botengine:
        :return: True if the screen is blacked out
        """
        if PeoplePowerPictureFrameDevice.BLACKOUT_SCREEN_PARAM in self.measurements:
            return self.measurements[PeoplePowerPictureFrameDevice.BLACKOUT_SCREEN_PARAM][0][0]

        return False

    #===========================================================================
    # Commands
    #===========================================================================
    def blackout(self, botengine, on):
        """
        Blackout the screen or not
        :param botengine: BotEngine environment
        :param on: True to blackout the screen
        """
        if on:
            botengine.send_command(self.device_id, PeoplePowerPictureFrameDevice.BLACKOUT_SCREEN_PARAM, 1)
        else:
            botengine.send_command(self.device_id, PeoplePowerPictureFrameDevice.BLACKOUT_SCREEN_PARAM, 0)

    def dismiss_question(self, botengine, question_object, command_timeout_ms=60000):
        """
        Dismiss a question that was asked that may or may not be rendered on the screen
        :param botengine:
        :param question_object:
        :return:
        """
        if question_object._question_id is None:
            botengine.get_logger().warn("Attempted to dismiss questions, but couldn't find a question ID")
            return

        commands = []

        commands.append(botengine.form_command("ppc.alertStatus", 2))
        commands.append(botengine.form_command("ppc.alertQuestionId", question_object._question_id))

        botengine.send_commands(self.device_id, commands, command_timeout_ms=command_timeout_ms)



    def ask_question(self, botengine, title, subtitle, question_object, duration_ms=utilities.ONE_HOUR_MS, priority=1, play_sound=None):
        """
        Ask a question through the digital picture frame
        :param botengine:
        :param title:
        :param subtitle:
        :param question_object:
        :param icon:
        :param duration_ms:
        :param priority:
        :param sound_file:
        :return:
        """
        # Flush questions to get a definitive question ID for the question object asked
        botengine.ask_question(question_object)
        botengine.flush_questions()

        if question_object._question_id is None:
            botengine.get_logger().warn("Attempted to flush questions, but didn't get a question ID")
            return

        commands = []

        # Title
        commands.append(botengine.form_command("ppc.alertTitle", title))

        # Subtitle
        if subtitle is not None:
            commands.append(botengine.form_command("ppc.alertSubtitle", subtitle))

        # Question ID
        commands.append(botengine.form_command("ppc.alertQuestionId", question_object._question_id))

        # Absolute start timestamp in ms
        commands.append(botengine.form_command("ppc.alertTimestampMs", botengine.get_timestamp()))

        # Relative duration time in ms
        if duration_ms is not None:
            commands.append(botengine.form_command("ppc.alertDurationMs", duration_ms))

        # Priority of the alert
        if priority is not None:
            commands.append(botengine.form_command("ppc.alertPriority", priority))

        # Play sound
        if play_sound is not None:
            commands.append(botengine.form_command("ppc.playSound", play_sound))


        if duration_ms is None:
            duration_ms = 60000

        botengine.send_commands(self.device_id, commands, command_timeout_ms=duration_ms)