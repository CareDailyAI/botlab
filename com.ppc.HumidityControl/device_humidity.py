'''
Created on September 16, 2016

@author: David Moss
'''

from device import Device

# Humidity Sensor Device Type
DEVICE_TYPE = 10034

# Low battery tag
LOW_BATTERY_TAG = "lowbattery_CR2032"

class HumiditySensorDevice(Device):
    """Low Cost Gateway"""
    
    def initialize(self, botengine):
        """
        Initialize this object
        """
        super(HumiditySensorDevice, self).initialize(botengine)
        
        
    def update_battery_level(self, batteryLevel):
        """Update the battery level
        :param batteryLevel
        """
        self.log("\tbattery = " + str(batteryLevel))
        self._batteryLevel = batteryLevel
        
        if self._batteryLevel <= LOW_BATTERY_THRESHOLD:
            # Tag it
            if self.battery_tag is not None:
                if self.battery_tag != LOW_BATTERY_TAG:
                    self.botengine.delete_device_tag(self.battery_tag, self.device_id)
                
            elif self.battery_tag != LOW_BATTERY_TAG:
                self.log("\tTagging device " + str(self.device_id) + " #" + LOW_BATTERY_TAG)
                self.botengine.tag_device(LOW_BATTERY_TAG, self.device_id)
                self.battery_tag = LOW_BATTERY_TAG
                
        elif self.battery_tag is not None:
            # Remove the battery tag
            self.log("\tRemoving #" + self.battery_tag + " from device " + str(self.device_id))
            self.botengine.delete_device_tag(self.battery_tag, self.device_id)
            self.battery_tag = None
        