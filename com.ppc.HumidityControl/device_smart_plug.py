'''
Created on June 28, 2016

@author: David Moss
'''

from device import Device

# Smart Plug Device Type
DEVICE_TYPE = 10035

class SmartPlugDevice(Device):
    """Smart Plug Device"""
    

    def save(self):
        """Save the status of this device"""
        if not self.is_connected:
            return False
        
        try:
            self.saved_state = self.history[0]
        except:
            self.saved_state = False
        
        self.saved = True
        return True
        
    def restore(self):
        """
        Restore the status of the device from the save point
        :return: True if the smart plug was restored, False if there was nothing to restore
        """
        if not self.is_connected or not self.can_control:
            return False
        
        self.log(">restore(" + str(self.device_id) + ")")
        if not self.saved:
            self.log("<restore() : Nothing to restore")
            return False
        
        self.saved = False
            
        if self.saved_state:
            self.on()
        else:
            self.off()
            
        self.log("<restore() : Restored")
        return True
    
    def on(self):
        """Turn on"""
        if not self.is_connected or not self.can_control:
            return False
        
        self.log(">on(" + str(self.device_id) + ")")
        self.botengine.send_command(self.device_id, "outletStatus", "true")
        return True
    
    
    def off(self):
        """Turn off"""
        if not self.is_connected or not self.can_control:
            return False
        
        self.log(">off(" + str(self.device_id) + ")")
        self.botengine.send_command(self.device_id, "outletStatus", "false")
        return True
    