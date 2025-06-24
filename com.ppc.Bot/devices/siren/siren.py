"""
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.device import Device


class SirenDevice(Device):
    """
    Siren
    """

    def __init__(
        self,
        botengine,
        location_object,
        device_id,
        device_type,
        device_description,
        precache_measurements=True,
    ):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        Device.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )

        # Microservice this siren is locked to
        self.locked_microservice = None

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Siren")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "siren"

    def get_icon_font(self):
        """
        Get the icon font package from which to render an icon
        :return: The name of the icon font package
        """
        import utilities.utilities as utilities

        return utilities.ICON_FONT_FONTAWESOME_REGULAR

    # ===========================================================================
    # Capabilities
    # ===========================================================================
    def has_dogbark(self, botengine):
        """
        Determine if this siren supports a dog bark sound
        :param botengine:
        :return: True if this siren supports a dog bark sound
        """
        return False

    def has_doorbell(self, botengine):
        """
        Determine if this siren supports a doorbell sound
        :param botengine:
        :return:
        """
        return False

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
        raise NotImplementedError

    def force_silence(self, botengine):
        """
        Force silence, even if this is locked by some other service.
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def silence(self, botengine, microservice_identifier=""):
        """
        Silence
        :param botengine:
        :return:
        """
        raise NotImplementedError

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

    def disarmed(self, botengine, microservice_identifier=""):
        """
        Make a sound that the home is disarmed
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def short_warning(self, botengine, microservice_identifier=""):
        """
        Make a sound that the home is disarmed
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def about_to_arm(self, botengine, seconds_left, microservice_identifier=""):
        """
        Make a unique aggressive warning noise for the amount of time remaining
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def armed(self, botengine, microservice_identifier=""):
        """
        Make a sound that the home is disarmed
        :param botengine:
        :return:
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def lock(self, botengine, microservice_identifier):
        """
        Lock the siren to some microservice - for example to use the siren exclusively for security purposes.
        :param botengine:
        :param microservice_identifier:
        :return:
        """
        if self.locked_microservice is None:
            botengine.get_logger().info(
                "Siren: LOCKING SIREN TO MICROSERVICE {}".format(
                    microservice_identifier
                )
            )
            self.locked_microservice = microservice_identifier
        else:
            botengine.get_logger().info(
                "Siren: Cannot lock siren again - siren is currently locked by {}".format(
                    self.locked_microservice
                )
            )

    def unlock(self, botengine):
        """
        Unlock the siren
        :param botengine:
        :param microservice_identifier:
        :return:
        """
        self.locked_microservice = None
