'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 9 -COMMANDS
# This lesson will show how to send commands to devices.
# The user gives the app permission to manage any number of lights in the user's account.
# The user can also give the app permission to listen to any number of light switches.
# In this way, virtual light switches can bind to control a group of lights.
# 
# 
# VERSION.JSON
# The trigger indicates we'll be listening for device measurements only:
# 
#     "trigger": 8,
#
# The specific device measurement we'll trigger off of is from a light switch,
# on both on and off.
#
# The app will also be compatible with light bulbs of type 10036. These are 
# recognized by the Ensemble software suite as GE LED light bulbs, capable of 
# turning on and off with the 'state' parameter set to 'true' or 'false', and
# also capable of dimming with the 'currentLevel' parameter between 0 to 100.
# 
# 


# RUNNING THIS APP
# First, register your developer account at http://presto.peoplepowerco.com.
#

#   Create virtual light switch(es) locally.
#               Open up another terminal window. In this lesson's directory, run
#               
#               $ python lightSwitch.py
#
#               This will register a new 'Virtual Light Switch' into your account,
#               which you can control manually from its command line.
#               It uses the Device API, and from the point of view of the Ensemble
#               software suite server, is a real device.
#
#   Create virtual light bulb(s) locally
#               Open a terminal window. In this lesson's directory, run
#               
#               $ python lightBulb.py
#
#               This will register a new 'Virtual Light Bulb' into your account,
#               which will simply declare its status on the command line.
# 
#    You will need to have at least 1 virtual light switch AND 1 virtual light bulb
#    in your account before you can successfully run this app.
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
VIRTUAL_LIGHT_SWITCH_DEVICE_TYPE = 10072
VIRTUAL_LIGHT_BULB_DEVICE_TYPE = 10071


def run(composer):
    # Initialize
    logger = composer.get_logger()                  # Debug logger
    inputs = composer.get_inputs()                  # Information input into the app
    triggerType = composer.get_trigger_type()       # What type of trigger caused the app to execute this time
    trigger = composer.get_trigger_info()           # Get the information about the trigger
    measures = composer.get_measures_block()        # Capture new measurements, if any
    access = composer.get_access_block()            # Capture info about all things this app has permission to access
    
# Here's what my inputs look like when running locally:    
#{
#  "access": [
#    {
#      "category": 4,
#      "control": true,
#      "device": {
#        "description": "Virtual Light Bulb",
#        "deviceId": "moss-light1",
#        "deviceType": 10071,
#        "locationId": 205,
#        "measureDate": 0,
#        "startDate": 1468028907000,
#        "updateDate": 0
#      },
#      "read": true,
#      "trigger": false
#    },
#    {
#      "category": 4,
#      "control": true,
#      "device": {
#        "description": "Virtual Light Bulb",
#        "deviceId": "moss-light2",
#        "deviceType": 10071,
#        "locationId": 205,
#        "measureDate": 0,
#        "startDate": 1468028934000,
#        "updateDate": 0
#      },
#      "read": true,
#      "trigger": false
#    },
#    {
#      "category": 4,
#      "control": false,
#      "device": {
#        "description": "Virtual Light Switch",
#        "deviceId": "moss-switch1",
#        "deviceType": 10072,
#        "locationId": 205,
#        "measureDate": 1468029417000,
#        "startDate": 1467588763000,
#        "updateDate": 1468029417000
#      },
#      "read": true,
#      "trigger": true
#    }
#  ],
#  "measures": [
#    {
#      "deviceId": "moss-switch1",
#      "name": "ppc.switchStatus",
#      "prevTime": 0,
#      "time": 1468029417000,
#      "updated": false,
#      "value": "1"
#    }
#  ],
#  "time": 1468029417687,
#  "trigger": 8
#}
# 



    if composer.load_variable("lightsOn") == None:
        # Initialize the 'lightsOn' variable
        composer.save_variable("lightsOn", False)
        
    lightsOn = composer.load_variable("lightsOn")
    lightsOn = not lightsOn
    
    # Get list of all accessible (device ID, device type pairs) relevant to Pro Security
    lights = []

    # For your convenience to see what's going on
    logger.info("Light switch toggled")
    print("Light switch toggled")
    
    # Send the command to all the lights we're given permission to access
    for item in access:
        try:
            device_type = item['device']['deviceType']
            
            if device_type == VIRTUAL_LIGHT_BULB_DEVICE_TYPE:
                print("Commanding '" + item['device']['deviceId'] + "' to switch to " + str(lightsOn).lower())
                composer.send_command(device_id=item['device']['deviceId'], param_name="outletStatus", value=str(lightsOn).lower())
                
        except KeyError:
            pass
    
    composer.save_variable("lightsOn", lightsOn)
    




    
    

