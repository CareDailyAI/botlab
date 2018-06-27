'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device


class LightDevice(Device):
    """Lighting Device"""

    # Measurement Names
    MEASUREMENT_NAME_STATUS = 'state'
    MEASUREMENT_NAME_BRIGHTNESS = 'currentLevel'
    MEASUREMENT_NAME_HUE = 'hue'
    MEASUREMENT_NAME_SATURATION = 'saturation'

    # Command Names
    COMMAND_NAME_STATUS = 'state'
    COMMAND_NAME_BRIGHTNESS = 'currentLevel'

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [10036]
    
    
    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # The boolean on/off state of this device that was saved
        self.saved_state = False

        # Saved brightess
        self.saved_brightness = None

        # Saved hue
        self.saved_hue = None

        # Saved saturation
        self.saved_saturation = None

        # Whether the saved_state is valid or not
        self.saved = False

            
    def initialize(self, botengine):
        Device.initialize(self, botengine)

        if not hasattr(self, 'saved_brightness'):
            self.saved_brightness = None

        if not hasattr(self, 'saved_hue'):
            self.saved_hue = None

        if not hasattr(self, 'saved_saturation'):
            self.saved_saturation = None

    #===========================================================================
    # Attributes
    #===========================================================================
    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Light")
    
    def get_image_name(self, botengine):
        """
        :return: the font icon name of this device type
        """
        return "bulb"
    
    def is_command(self, measurement_name):
        """
        :param measurement_name: Name of a local measurement name
        :return: True if the given parameter name is a command
        """
        return measurement_name == LightDevice.COMMAND_NAME_STATUS
    
    def is_light(self):
        """
        :return: True if this is a light
        """
        return True

    def can_control_brightness(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if we can control brightness on this device
        """
        return self.MEASUREMENT_NAME_BRIGHTNESS in self.measurements

    def can_control_color(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if we can control brightness on this device
        """
        return self.MEASUREMENT_NAME_HUE in self.measurements and self.MEASUREMENT_NAME_SATURATION in self.measurements

    def current_brightness(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if we can control brightness on this device
        """
        if self.MEASUREMENT_NAME_BRIGHTNESS in self.measurements:
            # ASYMMETRIC NON-SENSE.
            # The measurements are raw, 0-254.
            # The display formula is math:ceil(math:sqrt(39.37*value)).intValue()
            # This applies to the currentLevel parameter in general, apparently.
            import math
            return int(math.ceil(math.sqrt(self.measurements[self.MEASUREMENT_NAME_BRIGHTNESS][0][0] * 39.37)))

        return 100

    def current_hue(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: The current hue. None if this parameter doesn't exist.
        """
        if self.MEASUREMENT_NAME_HUE in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_HUE][0][0]

        return None

    def current_saturation(self, botengine=None):
        """
        :param botengine:
        :return: The current saturation. None if the parameter doesn't exist
        """
        if self.MEASUREMENT_NAME_SATURATION in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_SATURATION][0][0]

        return None

    def is_on(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if this light is on
        """
        if self.MEASUREMENT_NAME_STATUS in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_STATUS][0][0]

        return False

    def is_off(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if this light is on
        """
        if self.MEASUREMENT_NAME_STATUS in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_STATUS][0][0] == False

        return False

    def did_turn_on(self, botengine=None):
        """
        Did the light just turn on in the last execution
        :param botengine: BotEngine environment
        :return: True if the light turned on in the last execution
        """
        if self.MEASUREMENT_NAME_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_STATUS in self.last_updated_params:
                return self.measurements[self.MEASUREMENT_NAME_STATUS][0][0] == True

        return False

    def did_turn_off(self, botengine=None):
        """
        Did the light just turn off in the last execution
        :param botengine: BotEngine environment
        :return: True if the light turned off in the last execution
        """
        if self.MEASUREMENT_NAME_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_STATUS in self.last_updated_params:
                return self.measurements[self.MEASUREMENT_NAME_STATUS][0][0] == False

        return False

    #===========================================================================
    # Commands
    #===========================================================================
    def save(self, botengine):
        """Save the status of this device"""
        if not self.is_connected or not self.can_control:
            return False
        
        try:
            self.saved_state = self.measurements[self.MEASUREMENT_NAME_STATUS][0][0]
        except:
            self.saved_state = False

        self.saved_brightness = self.current_brightness(botengine)
        self.saved_hue = self.current_hue(botengine)
        self.saved_saturation = self.current_saturation(botengine)
        self.saved = True
        return True
        
    def restore(self, botengine):
        """
        Restore the status of the device from the save point
        :return: True if the lights were restored, False if there was nothing to restore
        """
        if not self.is_connected or not self.can_control:
            return False

        if not self.saved:
            return False
        
        self.saved = False
            
        if self.saved_state:
            self.on(botengine)
        else:
            self.off(botengine)

        # TODO : The DSR gateway does not support multiple parameters in a single command
        # Really this should be handled underneath this application layer, by the JEXL abstraction layer in the cloud.
        if self.saved_saturation:
            #self.set_saturation(botengine, self.saved_saturation)
            self.saved_saturation = None

        if self.saved_brightness:
            #self.set_brightness(botengine, self.saved_brightness)
            self.saved_brightness = None

        if self.saved_hue:
            #self.set_hue(botengine, self.saved_hue)
            self.saved_hue = None

        return True

    def toggle(self, botengine):
        """
        Toggle the light on or off
        :param botengine:
        :return:
        """
        if self.is_on(botengine):
            self.off(botengine)
        else:
            self.on(botengine)

    def on(self, botengine):
        """
        Turn on
        :param botengine: BotEngine environment
        :return: True if the command will attempt to be delivered
        """
        if not self.is_connected or not self.can_control:
            return False

        botengine.get_logger().info("Switch ON " + str(self.description))

        # Turning on and off requires 2 commands
        commands = [
            botengine.form_command(self.COMMAND_NAME_STATUS, True)  # This does accept True
        ]

        botengine.send_commands(self.device_id, commands)
        return True

    def off(self, botengine):
        """
        Turn off
        :param botengine: BotEngine environment
        :return: True if the command will attempt to be delivered
        """
        if not self.is_connected or not self.can_control:
            return False

        botengine.get_logger().info("Switch OFF " + str(self.description))

        # Turning on and off requires 2 commands
        commands = [
            botengine.form_command(self.COMMAND_NAME_STATUS, False)   # TODO this should accept False but does not
        ]

        botengine.send_commands(self.device_id, commands)
        return True

    def set_brightness(self, botengine, percent):
        """
        Set the brightness level between 0 - 100%
        :param botengine: BotEngine environment
        :param percent: 0-100% brightness
        :return: True if the command will attempt to be delivered
        """
        if not self.is_connected or not self.can_control:
            return False

        botengine.get_logger().info("Set brightness of " + str(self.description) + " to " + str(percent) + "%")

        # Adjusting the brightness requires 2 parameters for compatibility with our partners gateways
        commands = [
            botengine.form_command(LightDevice.COMMAND_NAME_BRIGHTNESS, percent)
        ]

        botengine.send_commands(self.device_id, commands)

    def set_saturation(self, botengine, saturation):
        """
        Set the saturation of the light. 254 is most saturated (colored) and 0 is the least saturated (white)
        :param botengine: BotEngine environment
        :param saturation: Saturation between 0 - 254
        :return:
        """
        if saturation < 0:
            saturation = 0

        elif saturation > 254:
            saturation = 254

        if self.MEASUREMENT_NAME_SATURATION in self.measurements:
            botengine.send_command(self.device_id, self.MEASUREMENT_NAME_SATURATION, saturation)

    def set_hue(self, botengine, hue):
        """
        Hue of the light. This is a wrapping value between 0 - 65535.
        Note that hue and saturation values are hardware dependent which means that programming two devices with the same value does not guarantee they will be the same color.
        Values 0 and 65535 would mean the light will resemble the color red.
        Value 21845 for green
        Value 43690 for blue

        :param botengine:
        :param hue: Hue of the light between 0 - 65535 (wrapping color spectrum, 0 is about equal to 65535 which is red)
        :return:
        """
        if hue < 0:
            hue = 0

        elif hue > 65535:
            hue = 65535

        if self.MEASUREMENT_NAME_HUE in self.measurements:
            botengine.send_command(self.device_id, self.MEASUREMENT_NAME_HUE, hue)

    def set_red(self, botengine):
        """
        Set the color to red. This does not control brightness or on/off state.
        :param botengine:
        :return:
        """
        self.set_saturation(botengine, 254)
        self.set_hue(botengine, 0)

    def set_green(self, botengine):
        """
        Set the color to green. This does not control brightness or on/off state.
        :param botengine:
        :return:
        """
        self.set_saturation(botengine, 254)
        self.set_hue(botengine, 21845)

    def set_blue(self, botengine):
        """
        Set the color to blue. This does not control brightness or on/off state.
        :param botengine:
        :return:
        """
        self.set_saturation(botengine, 254)
        self.set_hue(botengine, 43690)