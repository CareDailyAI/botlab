'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.camera.camera import CameraDevice


# Motion status values
MOTION_STATUS_DISABLED_BY_RULE = -1
MOTION_STATUS_DISABLED_MANUALLY = 0
MOTION_STATUS_ENABLED_MANUALLY = 1
MOTION_STATUS_ENABLED_BY_RULE = 2

# Motion sensitivity values
MOTION_SENSITIVITY_TINY = 0
MOTION_SENSITIVITY_SMALL = 10
MOTION_SENSITIVITY_NORMAL = 20
MOTION_SENSITIVITY_LARGE = 30
MOTION_SENSITIVITY_HUGE = 40


class PeoplePowerPresenceCameraDevice(CameraDevice):
    """Camera Device"""
    
    # Robot types, stored in the ppc.robotConnected parameter
    ROBOT_NOT_CONNECTED = 0
    ROBOT_GALILEO = 1
    ROBOT_KUBI = 2
    ROBOT_ROMO = 3
    ROBOT_GALILEO_BLE = 4
    ROBOT_PRESENCE_360 = 5
    
    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        CameraDevice.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)
        
    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: This is an abstract name of a camera device that doesn't show up in end-user documentation.
        return _("Presence Camera")
    
    
    #===========================================================================
    # Commands
    #===========================================================================
    def is_audible(self, botengine):
        """
        :return: True, this is an audible device
        """
        return True
    
    def play_sound(self, botengine, sound):
        """
        :param sound: Play the given sound file, for example "beep.mp3" or "alarm.mp3"
        """
        if not self.is_connected:
            return False
        
        botengine.get_logger().info("Playing file " + sound + " on camera " + self.description)
        
        botengine.send_command(self.device_id, "ppc.playSound", sound)
        return True

    def play_countdown(self, botengine, audio_seconds, visual_seconds):
        """
        Play the audio countdown for the given number of seconds
        :param seconds: Seconds to countdown, 0 to stop
        """
        if not self.is_connected or not self.can_control:
            return False
        
        if audio_seconds != 0 and audio_seconds < 5:
            audio_seconds = 5
            visual_seconds = 5
            
        botengine.get_logger().info("Playing countdown audio for " + str(audio_seconds) + " seconds; visual countdown for " + str(visual_seconds) + ": on " + self.description)
        
        audio_countdown_command = botengine.form_command("ppc.countdown", str(audio_seconds))
        visual_countdown_command = botengine.form_command("ppc.visualCountdown", str(visual_seconds))
        
        botengine.send_commands(self.device_id, [audio_countdown_command, visual_countdown_command])
        return True

    def play_sound_and_countdown(self, botengine, sound, audio_seconds, visual_seconds):
        """
        Play both a sound and the countdown
        :param sound: Sound file to play, i.e. "beep.mp3".  "" to silence
        :param audio_seconds: Audio countdown in seconds. 0 to silence.
        :param visual_seconds: Visual countdown in seconds. 0 for no visuals.
        """
        if not self.is_connected or not self.can_control:
            
            #===================================================================
            # if not self.is_connected:
            #     botengine.get_logger().info("This device " + str(self.device_id) + " is not connected")
            # else:
            #     botengine.get_logger().info("This device " + str(self.device_id) + " cannot be controlled")
            #===================================================================

            return False
        
        sound_command = botengine.form_command("ppc.playSound", sound)

        if audio_seconds != 0 and audio_seconds < 5:
            audio_seconds = 5
            visual_seconds = 5
        
        botengine.get_logger().info("Playing countdown audio for " + str(audio_seconds) + " seconds; visual countdown for " + str(visual_seconds) + "; Playing sound " + sound + ": on camera " + self.description)
        
        audio_countdown_command = botengine.form_command("ppc.countdown", str(audio_seconds))
        visual_countdown_command = botengine.form_command("ppc.visualCountdown", str(visual_seconds))
        
        botengine.send_commands(self.device_id, [sound_command, audio_countdown_command, visual_countdown_command])
        return True

    def beep(self, botengine, times):
        """
        Make the camera beep
        :param times: 1, 2, or 3
        """
        if not self.is_connected or not self.can_control:
            return False

        botengine.send_command(self.device_id, "ppc.alarm", times + 1)
        return True

    def alarm(self, botengine, on):
        """
        Turn the alarm on or off
        :param on: Boolean. True for on, False for complete silence including turning off the countdown
        """
        if not self.is_connected or not self.can_control:
            return False

        botengine.send_command(self.device_id, "ppc.alarm", str(int(on)))
        return True

    def capture_image(self, botengine, send_alert=False):
        """
        Make the camera capture an image
        :param send_alert: True to make the camera send an alert
        """
        value = 2
        if send_alert:
            value = 1
        
        botengine.send_command(self.device_id, "ppc.captureImage", str(value))
    
    
    def set_motion_detection(self, botengine, on):
        """
        Set motion detection on or off
        :param on: True for on, False for OFF
        """
        motion_status = MOTION_STATUS_DISABLED_BY_RULE
        if on:
            motion_status = MOTION_STATUS_ENABLED_BY_RULE
            
        botengine.send_command(self.device_id, "motionStatus", motion_status)
    
    
    def set_motion_sensitivity(self, botengine, sensitivity):
        """
        Set the motion sensitivity - see the MOTION_SENSITIVITY_* enums for values
        :param sensitivity: Sensitivity values between 0 - 40
        """
        botengine.send_command(self.device_id, "ppc.motionSensitivity", sensitivity)
        
    