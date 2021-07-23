'''
Created on August 21, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.light.light import LightDevice


class LevitonDecoraLightswitchDevice(LightDevice):
    """Leviton Decora in-wall switch lighting device"""

    # Measurement Names
    MEASUREMENT_NAME_STATUS = 'state'

    # Command Names
    COMMAND_NAME_STATUS = 'outletStatus'

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9001]
    
    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        LightDevice.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)

        if not hasattr(self, "saved_state"):
            self.saved_state = False

        if not hasattr(self, "saved"):
            self.saved = False

    #===========================================================================
    # Attributes
    #===========================================================================
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Leviton Decora In-Wall Switch")
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "light-switch"

    def get_icon_font(self):
        """
        Get the icon font package from which to render an icon
        :return: The name of the icon font package
        """
        import utilities.utilities as utilities
        return utilities.ICON_FONT_FONTAWESOME_REGULAR

    def is_command(self, measurement_name):
        """
        :param measurement_name: Name of a local measurement name
        :return: True if the given parameter name is a command
        """
        return measurement_name == self.COMMAND_NAME_STATUS
    
    def is_light(self):
        """
        :return: True if this is a light
        """
        return True
    
    #===========================================================================
    # Commands
    #===========================================================================
    def save(self, botengine):
        """Save the status of this device"""
        if not self.is_connected or not self.can_control:
            return False
        
        try:
            self.saved_state = (int(self.measurements[self.MEASUREMENT_NAME_STATUS][0][0]) == 1)
        except:
            self.saved_state = False
        
        #botengine.get_logger().info("Light Switch [" + str(self.device_id) + "] saved state = " + str(self.saved_state))
        
        self.saved = True
        return True
        
    def restore(self, botengine):
        """
        Restore the status of the device from the save point
        :return: True if the lights were restored, False if there was nothing to restore
        """
        #botengine.get_logger().info("GE Light Switch: Restore")
        if not self.is_connected or not self.can_control:
            #botengine.get_logger().info("\t=> Can't control or not connected")
            return False
        
        #botengine.get_logger().info("\t>restore(" + str(self.device_id) + ")")
        if not self.saved:
            botengine.get_logger().info("\t<restore() : Nothing to restore")
            return False
        
        self.saved = False
            
        if self.saved_state:
            self.on(botengine)
        else:
            self.off(botengine)
            
        #self.log("<restore() : Restored")
        return True
    
    def raw_command(self, botengine, name, value):
        """
        Send a command for the given local measurement name
        """
        if name == self.COMMAND_NAME_STATUS:
            if value:
                self.on(botengine)
            else:
                self.off(botengine)
        
    def on(self, botengine):
        """Turn on"""
        if not self.is_connected or not self.can_control:
            return False
        
        botengine.get_logger().info(">on(lightswitch " + str(self.device_id) + ")")
        botengine.send_command(self.device_id, self.COMMAND_NAME_STATUS, "1")
        return True
    
    
    def off(self, botengine):
        """Turn off"""
        if not self.is_connected or not self.can_control:
            return False
        
        botengine.get_logger().info(">off(lightswitch " + str(self.device_id) + ")")
        botengine.send_command(self.device_id, self.COMMAND_NAME_STATUS, "0")
        return True
    
    