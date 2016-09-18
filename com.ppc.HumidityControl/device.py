'''
Created on June 28, 2016

@author: David Moss
'''

import utilities

# Low signal strength threshold
LOW_RSSI_THRESHOLD = -80

# Low signal strength tag
LOW_SIGNAL_STRENGTH_TAG = "weak_signal"

# This is the maximum number of elements we'll average over for RSSI and LQI readings
MAXIMUM_AVERAGING_ELEMENTS = 25
    

class Device:
    """This is a base class for each of our devices"""
    
    def __init__(self, device_id, device_type, device_description):
        """Constructor"""
        self.device_id = device_id
        self.device_type = device_type
        self.description = device_description
        
    def initialize(self, composer):
        """
        Initialize
        
        This is the proper way to initialize an object in Composer.
        Because your class can be instantiated used object data that was
        created from a previous version of this class.
        """
        self.composer = composer
        
        try:
            self.battery_tag
        except:
            self.battery_tag = None
            
        try:
            self.signal_strength_tag
        except:
            self.signal_strength_tag = None
            
        try:
            self._batteryLevel
        except:
            self._batteryLevel = 100
            
        try:
            self._rssiElements
        except:
            self._rssiElements = []
            
        try:
            self._lqiElements
        except:
            self._lqiElements = []
            
        try:
            self.tags
        except:
            self.tags = []
            
        try:
            self.history
        except:
            self.history = []
            
        try:
            self.is_connected
        except:
            self.is_connected = False
            
        try:
            self.can_control
        except:
            self.can_control = False
            
        try:
            self.can_read
        except:
            self.can_read = False
            
        try:
            self.born_on
        except:
            self.born_on = composer.get_timestamp()
            
        try:
            self.email_priority
        except:
            self.email_priority = self.device_type
        
    
    def terminate(self):
        """Terminate
        
        You terminate this class to wipe the Composer object before saving,
        so you aren't saving excess fat you won't use again in the next execution.
        """
        self.composer = None
    
    def log(self, message):
        """Log some info output"""
        if self.composer:
            self.composer.get_logger().info(message)
        
    def update_battery_level(self, batteryLevel):
        """Update the battery level
        :param batteryLevel
        """
        raise NotImplementedError
        
    def update_rssi(self, rssi):
        """Update our RSSI readings
        :param rssi
        """
        #self.log(">update_rssi(" + str(rssi) + ")")
        self._rssiElements.append(int(rssi))
        
        if len(self._rssiElements) > MAXIMUM_AVERAGING_ELEMENTS:
            del self._rssiElements[0]
            
        rssi_average = int(sum(self._rssiElements) / len(self._rssiElements))
        
        self.log("\taverage rssi = " + str(rssi_average))
        
        if rssi_average < LOW_RSSI_THRESHOLD:
            # Low average signal strength, #tag it
            if self.signal_strength_tag is not None:
                if self.signal_strength_tag == LOW_SIGNAL_STRENGTH_TAG:
                    # Already tagged it
                    return
                
                else:
                    self.composer.delete_device_tag(self.signal_strength_tag, self.device_id)
                    self.signal_strength_tag = None
                    
            self.log("\tTagging device " + str(self.device_id) + " #" + LOW_SIGNAL_STRENGTH_TAG)
            self.composer.tag_device(LOW_SIGNAL_STRENGTH_TAG, self.device_id)
            self.signal_strength_tag = LOW_SIGNAL_STRENGTH_TAG
            
        elif self.signal_strength_tag is not None:
            # High average signal strength and a tag exists, remove the #tag
            self.log("\tRemoving #" + self.signal_strength_tag + " from device " + str(self.device_id))
            self.composer.delete_device_tag(self.signal_strength_tag, self.device_id)
            self.signal_strength_tag = None
        
        #self.log("<update_rssi()")
        
    def rssi_status_quo(self):
        """RSSI reading didn't change from last time, duplicate the last reading"""
        self.log(">rssi_status_quo()")
        if len(self._rssiElements) > 0:
            self.update_rssi(self._rssiElements[-1])
        self.log("<rssi_status_quo()")
      
    def update_lqi(self, lqi):
        """Update our LQI readings
        :param lqi
        """
        #self.log(">update_lqi(" + str(lqi) + ")")
        self.log("\tlqi = " + str(lqi))
        self._lqiElements.append(int(lqi))
        if len(self._lqiElements) > MAXIMUM_AVERAGING_ELEMENTS:
            del self._lqiElements[0]
        #self.log("<update_lqi()")
        
    def lqi_status_quo(self):
        """LQI reading didn't change from last time, duplicate the last reading"""
        self.log(">lqi_status_quo()")
        if len(self._lqiElements) > 0:
            self.update_lqi(self._rssiElements[-1])
        self.log("<lqi_status_quo()")
    
    def add_measurement(self, status, timestamp):
        """Update the device's status"""
        self.composer.get_logger().info(">add_measurement(" + str(status) + ", " + str(timestamp) + ")")
        booleanStatus = (str(status).lower() == "true") or (str(status) == "1") or (status == True)
        self.history.insert(0, (booleanStatus, timestamp))
        self.composer.get_logger().info("<add_measurement")
    
    
    def garbage_collect(self, current_timestamp):
        """
        Clean up the garbage
        :param current_timestamp: Current timestamp in ms
        """
        i = 0
        for (value, timestamp) in self.history:
            i += 1
            if timestamp <= current_timestamp - (utilities.ONE_MONTH_MS * 2):
                del self.history[i:]
                break
    
    