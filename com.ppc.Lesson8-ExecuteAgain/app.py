'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 8 - EXECUTE AGAIN
# Apps can decide to execute themselves again at an absolute time, or a relative time from now.
# 
# This demonstration initially triggers off of a door/window sensor or a virtual light switch.
# We'll show how to debounce these devices in software.
#
# Now, normal 'debouncing' is done at the microsecond level on physical circuitry. This is
# a similar concept, but across a magnitude of seconds.
# 
# When a door opens, we'll execute the app again in a few seconds to see if the door remained open for 
# longer than 2 seconds. If the door was open for less than 2 seconds, then it's likely 
# nobody actually made it through the door. Try it yourself and see if you can get through a closed
# door in less than 2 seconds.
#
# We'll do the same thing with the light switch to demonstrate concepts. If the virtual switch
# is on for less than 2 seconds, we'll call the final state OFF.  If it's on for longer than 
# 2 seconds, we'll call the final state ON.
#
# There can only be 1 "execute again" timer running on the server. So if you call
# "execute_again_in_n_seconds" multiple times, you'll keep overriding the sensor
# until it finally has a chance to play out and execute.
#
# There are 2 methods available to make an app execute again:
#
#   composer.execute_again_in_n_seconds(<seconds>)
#   composer.execute_again_at_timestamp(<timestamp in unix milliseconds>)
#
# In this app, the Entry Sensor will execute the app again in N seconds,
# and the Virtual Light Switch will execute the app again at a fixed timestamp.
# 
#

# RUNNING THIS APP
# First, register your developer account at http://presto.peoplepowerco.com.
#
# This app will require a device to be connected to your account:
#    Option A:  Buy a Presence Security Pack (http://presencepro.com/store).
#               This is recommended because it will give you a lot more tools
#               to create cool apps with.
#
#    Option B:  Create a virtual light switch locally.
#               Open up another terminal window. In this lesson's directory, run
#               
#               $ python lightSwitch.py
#
#               This will register a new 'Virtual Light Switch' into your account,
#               which you can control manually from its command line.
#               It uses the Device API, and from the point of view of the Ensemble
#               software suite server, is a real device.
# 
#    You will need to have at least 1 entry sensor OR 1 virtual light switch in your
#    account before you can purchase this app to run it (see below). Otherwise,
#    this app will be incompatible with your account.
# 
# 
# There are several steps needed to run this app:
#    1. Create a new directory for your app, with your own unique bundle ID. Copy all the files into it.
#       Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourApp) and cannot
#       be deleted or edited once created.
#    2. Create a new --app on the server with composer
#    3. Commit your app to the server with composer
#    4. Purchase your app with composer
#    5. Run your app locally
# 
#
# We've automated this for you with a script, 'runlesson.sh'. Run it from your terminal window:
# 
#    $ ./runlesson.sh
#
# 
# This script will automatically do the following for you. 
# From a terminal window *above* this app's current directory:
# 
# 1. Create a new directory for your app with your given bundle ID, and copy all the files from this
#    lesson into that new directory.
#
# 
# 2. Create a new app in your user account with the given bundle ID.
#    
#    composer --new com.yourname.YourApp
#    
# 
# 3. Commit your app to the server. 
#    This will push all the code, version information, marketing information, and icon to the server. 
#    The app will become privately available.
#
#    composer --commit com.yourname.YourApp
#
# 
# 4. Purchase the app as if you're an end-user. Note that because your app is privately available, other end users
#    will not be able to see or access it.
#
#    composer --purchase com.yourname.YourApp
# 
#    This will return a unique instance ID for your purchased app, which you may reference to reconfigure the app instance later.
#    
#    
# 5. Run the app locally.
#    
#    composer --run com.yourname.YourApp
#    
#    This will automatically look up your app instance ID and run the app, using the real-time streaming data from the server
#    and the code that is on your local computer.
# 

# Make it easier to read our if-statements and avoid typos
ENTRY_SENSOR_DEVICE_TYPE = 10014
VIRTUAL_LIGHT_SWITCH_DEVICE_TYPE = 10072

# Trigger declarations
TRIGGER_TYPE_MEASUREMENT = 8
TRIGGER_TYPE_EXECUTE_AGAIN = 64


def run(composer, initialize=False):
    # Initialize
    logger = composer.get_logger()                  # Debug logger
    inputs = composer.get_inputs()                  # Information input into the app
    triggerType = composer.get_trigger_type()       # What type of trigger caused the app to execute this time
    trigger = composer.get_trigger_info()           # Get the information about the trigger
    measures = composer.get_measures_block()        # Capture new measurements, if any
    access = composer.get_access_block()            # Capture info about all things this app has permission to access
    timestampMs = composer.get_timestamp()          # Capture the timestamp of execution
  
# This is what our inputs look like when we receive a new measurement
#{
#  "access": [
#    {
#      "category": 4,
#      "control": false,
#      "device": {
#        "description": "Virtual Light Switch",
#        "deviceId": "moss-switch1",
#        "deviceType": 10072,
#        "locationId": 205,
#        "measureDate": 1467736972000,
#        "startDate": 1467588763000,
#        "updateDate": 1467736972000
#      },
#      "read": true,
#      "trigger": true
#    }
#  ],
#  "measures": [
#    {
#      "deviceId": "moss-switch1",
#      "name": "ppc.switchStatus",
#      "prevTime": 1467736893000,
#      "prevValue": "0",
#      "time": 1467736972000,
#      "updated": true,
#      "value": "1"
#    }
#  ],
#  "time": 1467736972636,
#  "trigger": 8
#}

# This is what our inputs look like when the app executes again
#{
#  "access": [
#    {
#      "category": 4,
#      "control": false,
#      "device": {
#        "description": "Virtual Light Switch",
#        "deviceId": "moss-switch1",
#        "deviceType": 10072,
#        "locationId": 205,
#        "measureDate": 1467736972000,
#        "startDate": 1467588763000,
#        "updateDate": 1467736972000
#      },
#      "read": true,
#      "trigger": false
#    }
#  ],
#  "time": 1467736975575,
#  "trigger": 64
#}

    
    # Trigger type 8 is a device measurement
    if triggerType == TRIGGER_TYPE_MEASUREMENT:
        print("\nExecuting on a new device measurement")
        
        deviceType = trigger['device']['deviceType']
        deviceName = trigger['device']['description']
        deviceId = trigger['device']['deviceId']
        
        # Remember, on the next execution, which device ID triggered last.  
        composer.save_variable("last_device_id", str(deviceId))
        composer.save_variable("last_device_type", str(deviceType))
        composer.save_variable("last_device_name", str(deviceName))
        
        # Load or create the appropriate object, with the device ID as part of the variable name to track multiple devices.
        focused_object = composer.load_variable("sensor_object_" + str(deviceId))
        if focused_object == None:
            focused_object = Sensor()
            composer.save_variable("sensor_object_" + str(deviceId), focused_object)
        
        if int(deviceType) == ENTRY_SENSOR_DEVICE_TYPE:
            # Retrieve from the input measurements the "value" for the parameter with the "name" = "doorStatus"
            doorStatus = composer.get_property(measures, "name", "doorStatus", "value")
            time = composer.get_property(measures, "name", "doorStatus", "time")
            state = (doorStatus.lower() == "true")
            focused_object.update_state(state, time)
            
            if state:
                print("Your '" + deviceName + "' opened! Executing this app again in 2 seconds...")
                composer.execute_again_in_n_seconds(2)
            else:
                print("Your '" + deviceName + "' closed.")
                
            
        if int(deviceType) == VIRTUAL_LIGHT_SWITCH_DEVICE_TYPE:
            switchStatus = composer.get_property(measures, "name", "ppc.switchStatus", "value")
            time = composer.get_property(measures, "name", "ppc.switchStatus", "time")
            state = (switchStatus == "1")
            focused_object.update_state(state, time)
            
            if state:
                print("Your '" + deviceName + "' switched on! Executing this app at a specific timestamp 2 seconds from now...")
                composer.execute_again_at_timestamp(int(timestampMs) + 2000)
            else:
                print("Your '" + deviceName + "' switched off.")
                
        # Make sure you save your variables when you're done, or you'll get strange behaviors!
        composer.save_variable("sensor_object_" + str(deviceId), focused_object)
            

    # Trigger Type 64 is from executing again
    if triggerType == TRIGGER_TYPE_EXECUTE_AGAIN:
        print("\n\n=> Executing again!")
        
        # You can't get here without saving these variables from another execution up above.
        # But we'll check their existence anyway for good practice.
        deviceId = composer.load_variable("last_device_id")
        deviceType = composer.load_variable("last_device_type")
        deviceName = composer.load_variable("last_device_name")
        focused_object = composer.load_variable("sensor_object_" + str(deviceId))
        
        if deviceId is None or deviceType is None or deviceName is None or focused_object is None:
            # This should never execute in a normal environment.
            print("??? What happened to all our variables ???")
            return
        
        if int(deviceType) == ENTRY_SENSOR_DEVICE_TYPE:
            if focused_object.was_active_longer_than_x_milliseconds(2000):
                print("\t=> OPENED. The last time your '" + deviceName + "' opened, it was open for longer than 2 seconds.")
            else:
                print("\t=> FALSE POSITIVE DETECTED. Your '" + deviceName + "' wasn't open long enough for someone to get through.")
        
        if int(deviceType) == VIRTUAL_LIGHT_SWITCH_DEVICE_TYPE:
            if focused_object.was_active_longer_than_x_milliseconds(2000):
                print("\t=> SWITCHED ON. The last time your '" + deviceName + "' switched on, it was on for longer than 2 seconds.")
            else:
                print("\t=> FALSE POSITIVE DETECTED. Your '" + deviceName + "' wasn't on for longer than 2 seconds.")
            
    

class Sensor():
    '''Generic sensor class to store timestamps and states'''
    
    def __init__(self):
        print("INIT")
        self.state = True
        self.timestamp = 0
        
        self.lastState = True
        self.lastTimestamp = 0
        
    def update_state(self, state, timestamp):
        '''Update the status of this sensor'''
        print("Updating state to " + str(state) + " at timestamp " + str(timestamp))
        self.lastState = self.state
        self.lastTimestamp = self.timestamp
        
        self.state = state
        self.timestamp = timestamp
        print("Timestamp is now " + str(self.timestamp))
        print("Last timestamp is now " + str(self.lastTimestamp))
        
    def was_active_longer_than_x_milliseconds(self, milliseconds):
        '''Find if the sensor was really active for longer than X milliseconds'''
        print("self.timestamp = " + str(self.timestamp))
        print("self.lastTimestamp = " + str(self.lastTimestamp))
        print("self.timestamp - self.lastTimestamp = " + str(self.timestamp - self.lastTimestamp))
        return self.state or ((self.timestamp - self.lastTimestamp) >= milliseconds)
    
