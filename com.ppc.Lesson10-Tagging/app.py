'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 10 - TAGGING
# Tags can be applied to users, locations, devices, and files.
# 
# Tags enable use to categorize these objects.  Tags can also surface into the Maestro
# Command Center to help us proactively enhance the customer experience.
# 
# The tags that a Composer app applies are only available within that Composer app 
# instance, and the Maestro Command Center.  No other Composer apps can see the tags
# this app applies.
#
# Here are some examples of where you'd consider using Tags:
# 
#    * Tag devices with bad batteries, so the Maestro administrator can 
#      select all the users with bad batteries and send those people new batteries
#      to keep the service running.
#
#    * Identify devices with poor signal strength and flag these devices in the Maestro
#      Command Center, so technical support can see right away there are connectivity issues.
#
#    * Tag users who have #pets. If the user goes away from home and they have pets, then
#      we should not let the thermostat get too hot or cold.
#
#    * Tag locations in an office building that have poor energy performance, 
#      allowing the administrators to focus their attention where it's needed.
#
#    * Apply OpenCV-Python to a video file to identify objects in the video, then
#      tag the file with the object names we see. For example #blue #truck. This
#      allows end users to search their videos with text and tagging.
#
# The methods we have available to us are:
#
#     composer.tag_user(<tag>) - Tag this user's account
#     composer.tag_location(<tag>, <location_id>) - Tag a location
#     composer.tag_device(<tag>, <device_id>) - Tag a device
#     composer.tag_file(<tag>, <file_id>) - Tag a file
#
#     composer.delete_user_tag(<tag>) - Delete a tag for a user
#     composer.delete_location_tag(<tag>, <location_id>) - Delete a tag for a location
#     composer.delete_device_tag(<tag>, <device_id>) - Delete a device tag
#     composer.delete_file_tag(<tag>, <file_id>) - Delete a file tag
# 
#     composer.get_tags(type=None, id=None) - Get tags, where 'type' and 'id' are optional
#         type 1 = User tag
#         type 2 = Location tag (id = location ID)
#         type 3 = Device tag (id = device ID)
#         type 4 = File tag (id = file ID)
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

# Declare our virtual light switch device type, to avoid typos and gain clarity in the code
ENTRY_SENSOR_DEVICE_TYPE = 10014
VIRTUAL_LIGHT_SWITCH_DEVICE_TYPE = 10072

# Declare our triggers to make the code more readable
TRIGGER_MODE = 2
TRIGGER_MEASUREMENT = 8

def run(composer, initialize=False):
    # Initialize
    logger = composer.get_logger()                  # Debug logger
    inputs = composer.get_inputs()                  # Information input into the app
    triggerType = composer.get_trigger_type()       # What type of trigger caused the app to execute this time
    trigger = composer.get_trigger_info()           # Get the information about the trigger
    measures = composer.get_measures_block()        # Capture new measurements, if any
    access = composer.get_access_block()            # Capture info about all things this app has permission to access
    
    logger.debug("Inputs: " + str(inputs));     # Save it to our logging debug file, just to show you what's going on. You'll have to run with --console to see this.
    
    # Scroll down past this commentary for the rest of the example code ...


# INPUTS WHEN THE ENTRY SENSOR TRIGGERS:
# Scroll down past this commentary for the rest of the example code ...
#{
#   'access':[
#      {
#         'category':4,
#         'control':True,
#         'trigger':True,
#         'device':{
#            'deviceId':'FFFFFFFF00600a70',
#            'deviceType':10014,
#            'measureDate':1467061017000,
#            'updateDate':1467061018000,
#            'description':'Practice\xa0Entry\xa0Sensor'
#         },
#         'read':True
#      },
#      {
#         'category':1,
#         'control':False,
#         'location':{
#            'locationId':660432,
#            'event':'HOME'
#         },
#         'trigger':False,
#         'read':True
#      },
#      {
#         'category':4,
#         'trigger':False,
#         'control':False,
#         'device':{
#            'deviceId':'FFFFFFFF00612088',
#            'deviceType':10017,
#            'measureDate':0,
#            'updateDate':0,
#            'description':'Water Sensor'
#         },
#         'read':False
#      }
#   ],
#   'measures':[
#      {
#         'deviceId':'FFFFFFFF00600a70',
#         'name':'doorStatus',
#         'value':'false',
#         'prevValue':'true',
#         'prevTime':1467060993000,
#         'time':1467061017000,
#         'updated':True
#      },
#      {
#         'deviceId':'FFFFFFFF00600a70',
#         'name':'lqi',
#         'value':'136',
#         'prevValue':'188',
#         'prevTime':1467060993000,
#         'time':1467061017000,
#         'updated':True
#      },
#      {
#         'deviceId':'FFFFFFFF00600a70',
#         'name':'rssi',
#         'value':'-68',
#         'prevValue':'-60',
#         'prevTime':1467060993000,
#         'time':1467061017000,
#         'updated':True
#      }
#   ],
#   'trigger':8,
#   'time':1467061018591
#}
    
    print("Executing")
    print("-----")
    
    # Tag the user account
    composer.tag_user("developer")
    
    if triggerType == TRIGGER_MODE:
        # Executing on a change of mode
        mode = trigger['location']['event']
        locationId = trigger['location']['locationId']
        
        new_tag = mode.lower()
        last_tag = composer.load_variable("last_mode_tag")
    
        if last_tag:
            composer.delete_user_tag("user" + last_tag)
            composer.delete_location_tag("location" + last_tag, locationId)
            
        composer.tag_user("user" + new_tag)
        composer.tag_location("location" + new_tag, locationId)
        composer.save_variable("last_mode_tag", new_tag)
        
        
    elif triggerType == TRIGGER_MEASUREMENT:
        # Executing on a device measurement
        deviceType = trigger['device']['deviceType']
        deviceName = trigger['device']['description']
        deviceId = trigger['device']['deviceId']
        
        if deviceType == ENTRY_SENSOR_DEVICE_TYPE:
            batteryLevel = composer.get_property(measures, "name", "batteryLevel", "value")
            
            if batteryLevel is not None:
                if int(batteryLevel) > 20:
                    composer.delete_device_tag("badBattery", deviceId)
                    composer.tag_device("goodBattery", deviceId)
                
                else:
                    composer.delete_device_tag("goodBattery", deviceId)
                    composer.tag_device("badBattery", deviceId)
        
        if deviceType == VIRTUAL_LIGHT_SWITCH_DEVICE_TYPE:
            switchStatus = composer.get_property(measures, "name", "ppc.switchStatus", "value")
            
            if int(switchStatus) == 1:
                new_tag = "switchOn"
            else:
                new_tag = "switchOff"
                
            last_tag = composer.load_variable("last_device_tag_" + str(deviceId))
            last_device_id = composer.load_variable("last_device_id")
            
            if last_tag and last_device_id:
                composer.delete_device_tag(last_tag, last_device_id)
                
            composer.tag_device(new_tag, deviceId)
            composer.save_variable("last_device_tag_" + str(deviceId), new_tag)
            composer.save_variable("last_device_id", str(deviceId))
            
    
    # Show you our existing tags
    import json
    existingTags = composer.get_tags()
    print("Existing Tags: " + json.dumps(existingTags, indent=2, sort_keys=True))
    print()
        
