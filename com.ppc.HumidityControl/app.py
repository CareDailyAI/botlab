'''
Created on September 16, 2016

@author: David Moss

Email support@peoplepowerco.com if you have questions!
'''

# Import our device models
from device_smart_plug import SmartPlugDevice
from device_humidity import HumiditySensorDevice

import utilities

# Humidity threshold, above which we'll turn on the smart plug
HUMIDITY_THRESHOLD = 60

# Trigger types
TRIGGER_TYPE_SCHEDULE = 1
TRIGGER_TYPE_MODE = 2
TRIGGER_TYPE_ALERT = 4
TRIGGER_TYPE_MEASUREMENT = 8
TRIGGER_TYPE_QUESTION = 16
TRIGGER_TYPE_FILES = 32
TRIGGER_TYPE_EXECUTE_AGAIN = 64

# Access types
ACCESS_CATEGORY_LOCATION = 1
ACCESS_CATEGORY_DEVICE = 4


def run(composer):
    '''This is the execution starting point of your app
    
    @param composer: Instance of the Composer object, which provides built-in functions for you to privately interact with this user's data
    '''
    
    # Initialize the app by grabbing access to all the important information
    logger = composer.get_logger()                  # Debug logger, this will capture logged output to an external 'app.log' file
    inputs = composer.get_inputs()                  # Information input into the app
    triggerType = composer.get_trigger_type()       # What type of trigger caused the app to execute this time
    trigger = composer.get_trigger_info()           # Get the information about the trigger
    measures = composer.get_measures_block()        # Capture new measurements, if any
    access = composer.get_access_block()            # Capture info about all things this app has permission to access
    timestamp = composer.get_timestamp()            # Get the current UNIX epoch timestamp in milliseconds
    
    if triggerType == TRIGGER_DEVICE_MEASUREMENT:
        
        if deviceType == HumiditySensorDevice.DEVICE_TYPE:
            current_humidity = composer.get_property(measures, "name", "relativeHumidity", "value")
                
            # Blindly turn all the smart plugs we have permission to access either on or off each humidity trigger.
            # This could be made more intelligent by using save_variable() and load_variable(), 
            # but that's a little bit overkill for the simple use case we're trying to fulfill here.
            if current_humidity >= HUMIDITY_THRESHOLD:
                
                # When was the last time we turned on the plug?
                on_timestamp = composer.load_variable("on_timestamp", on_timestamp)
                if on_timestamp is None:
                    # Initialize it
                    on_timestamp = 0
                    
                # Let's not turn it on more than once ever 30 minutes
                if timestamp - on_timestamp > (utilities.ONE_MINUTE_MS * 30):
                    toggle_all_smart_plugs(composer, True)
                    on_timestamp = timestamp
                    composer.save("on_timestamp", on_timestamp)
                    
                    # Turn it back off again in 15 minutes.
                    composer.execute_again_in_n_sec(utilities.ONE_MINUTE_MS * 15)
                
                
    elif triggerType == TRIGGER_EXECUTE_AGAIN:
        # It must have been 15 minutes since we last turned on the plug, now turn it off.
        toggle_all_smart_plugs(composer, False)
        
    # The composer app completely exits at this point.
    
    

def toggle_all_smart_plugs(composer, turn_on):
    """
    Function to turn on all the smart plugs.
    
    Pass in the composer object. We extract all the devices we have access to.
    For every device that's a smart plug that we have access to, we turn it on or off.
    :param composer: Composer object that is executing this app
    :param turn_on: True to turn on all smart plugs, False to turn them all off.
    """
    access = composer.get_access_block()            # Capture info about all things this app has permission to access
    
    for item in access:
        if item['category'] == ACCESS_CATEGORY_DEVICE:
            # Some of these are just to show you some of the information we can get access to about this device
            device_id = item['device']['deviceId']
            device_type = item['device']['deviceType']
            device_desc = item['device']['description']
            location_id = item['device']['locationId']
            is_connected = item['device']['connected']
            can_control = item['control']
            can_read = item['read']
            
            if device_type == SmartPlugDevice.DEVICE_TYPE and is_connected and can_control:
                device_object = SmartPlugDevice(device_id, device_type, device_desc)
                device_object.initialize(composer)
                if turn_on:
                    device_object.on()
                else:
                    device_object.off()
                device_object.terminate(composer)
        
    
    

