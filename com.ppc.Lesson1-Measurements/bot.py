'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 1 - MEASUREMENTS
# You must use Python 3.0 or newer to run BotEngine.
# 
# This lesson demonstrates how to listen and do processing on real-time data flowing
# through a cloud server from a door/window Entry Sensor.  This example will require you to
# have a device of type 10014 or 10072 connected to your account.
#
# Device type 10014 is an Entry Sensor found in a standard Presence Security pack.
# http://presencepro.com/store.
# 
# Device type 10072 is a virtual light switch. Run the "lightSwitch.py" application in this 
# bot's local directory to attach a virtual light switch to your account.
# 
# 
# VERSION.JSON
# First, open up version.json. This file drives the behavior of when this bot runs,
# and it's updated with every new version of the bot. One of the most important
# lines in this version.json file is here:
# 
#     "trigger": 8,
#
# This is the trigger that causes this bot to run. Trigger 8 means "Run this bot when a new device measurement comes in."
#
# Here are some other triggers, for your information. These are found in the BotEngine API documentation.
#   * Trigger 1 = Schedule (based off a cron schedule inside the version.json file)
#   * Trigger 2 = Location Event (switching between home / away / etc.)
#   * Trigger 4 = Device Alert
#   * Trigger 8 = Device Measurements
#   * Trigger 16 = Question Answered
#   * Trigger 32 = New device file (like a video or picture)
#   * Trigger 64 = Execute again
#
# 
# Because we picked Trigger 8 in our version.json, we need to specify a device type to be the trigger.
# You can see this in the next section:
# 
#     "deviceTypes": [{
#       "id": 10014,                           <-- Device type 10014 is a Door/Window sensor
#       "minOccurrence": 1,                    <-- You need at least one device of this type
#       "trigger": true,                       <-- This device type is the trigger
#       "read": true,                          <-- We're going to read from the device
#       "control": false,                      <-- There's nothing to control
#       "triggerParamName": "doorStatus",      <-- We'll trigger off of parameter 'doorStatus' ...
#       "triggerParamValues": "true",          <-- ... whenever that trigger says only "true" (the door opened).
#       "reason": {
#         "en": "We're going to monitor your doors and windows."  <-- This is what we tell the end user about why we want access to this device, in English.
#       }
#     },
#
#     {
#       "id": 10072,                           <-- Device type 10072 is a Virtual Light Switch
#       "trigger": true,                       <-- Trigger off this device
#       "read": true,
#       "control": false,
#       "triggerParamName": "ppc.switchStatus", <-- Listen for the parameter 'ppc.switchStatus'
#       "triggerParamValues": "0,1",            <-- Only fire the bot when the parameter is a 0 or a 1
#       "reason": {
#         "en": "Monitor your virtual light switches."
#       }
#     }
#   ],
# 
# One very important thing to note:  If you want to make changes to the way your bot executes:
# first you should first edit the version.json file to describe how you want it to execute,
# then you should COMMIT your bot to the cloud.  
#
#     botengine --commit <your bot bundle>
# 
# You may want to reconfigure your purchased bot instance after that to give your bot access
# to anything else in your account:
#
#     botengine --configure <your bot instance ID or bundle ID>
# 
# 
# BOT.PY
# The run(..) function in this file executes exactly 1 time, every time the bot is triggered.
# When the run() function exits, this bot completely exits. Completely Exits! Gone! Poof. 
# All your local variables - evaporated! So if you want to persist some variables, you'll
# need to ask BotEngine to store them for you.
#
# The 'botengine' object is our window into the user's account. It provides access to things like:
#    * Logger, to capture debug output
#    * The user's info, including language preference, Locations in the user's account, timezones for each location, and Home/Away/Sleep/Vacation modes for each location
#    * Ability to store and load variables - remember, your local variables evaporate every time your bot runs
#    * Measurements from devices
#    * Ability to communicate with users, professional monitoring services, etc.
# 

# RUNNING THIS BOT
# First, register your developer account at http://presto.peoplepowerco.com.
#
# This bot will require a device to be connected to your account:
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
#    account before you can purchase this bot to run it (see below). Otherwise,
#    this bot will be incompatible with your account.
# 
# 
# There are several steps needed to run this bot:
#    1. Create a new directory for your bot, with your own unique bundle ID. Copy all the files into it.
#       Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourApp) and cannot
#       be deleted or edited once created.
#    2. Create a new --bot on the server with botengine
#    3. Commit your bot to the server with botengine
#    4. Purchase your bot with botengine
#    5. Run your bot locally
# 
#
# We've automated this for you with a script, 'runlesson.sh'. Run it from your terminal window:
# 
#    $ ./runlesson.sh
#
# 
# This script will automatically do the following for you. 
# From a terminal window *above* this bot's current directory:
# 
# 1. Create a new directory for your bot with your given bundle ID, and copy all the files from this
#    lesson into that new directory.
#
# 
# 2. Create a new bot in your user account with the given bundle ID.
#    
#    botengine --new com.yourname.YourApp
#    
# 
# 3. Commit your bot to the server. 
#    This will push all the code, version information, marketing information, and icon to the server. 
#    The bot will become privately available.
#
#    botengine --commit com.yourname.YourApp
#
# 
# 4. Purchase the bot as if you're an end-user. Note that because your bot is privately available, other end users
#    will not be able to see or access it.
#
#    botengine --purchase com.yourname.YourApp
# 
#    This will return a unique instance ID for your purchased bot, which you may reference to reconfigure the bot instance later.
#    
#    
# 5. Run the bot locally.
#    
#    botengine --run com.yourname.YourApp
#    
#    This will automatically look up your bot instance ID and run the bot, using the real-time streaming data from the server
#    and the code that is on your local computer.
# 


def run(botengine):
    '''This is the execution starting point of your bot
    
    @param botengine: Instance of the BotEngine object, which provides built-in functions for you to privately interact with this user's data
    @param initialize: True if we should initialize this bot for the given deviceId, and perhaps clear variables
    '''
    
    # Initialize the bot by grabbing access to all the important information
    logger = botengine.get_logger()                  # Debug logger, this will capture logged output to an external 'bot.log' file
    inputs = botengine.get_inputs()                  # Information input into the bot
    triggerType = botengine.get_trigger_type()       # What type of trigger caused the bot to execute this time
    trigger = botengine.get_trigger_info()           # Get the information about the trigger
    measures = botengine.get_measures_block()        # Capture new measurements, if any
    access = botengine.get_access_block()            # Capture info about all things this bot has permission to access
    
# Below is what the inputs look like when I run this on my account with only a Virtual Light Switch.
# 
# You'll see the 'access' block tells us which device triggered this execution.
# The 'measures' block tells us all the latest parameters for this device.
# 
#{
#    'access': [{                             <-- These are all the things we have access to in this user's account.
#        'read': True,
#        'category': 4,                       <-- In 'access', category 4 means this particular block represents a device.
#        'trigger': True,
#        'device': {
#            'measureDate': 1467589363000,
#            'updateDate': 1467589363000,
#            'locationId': 205,
#            'deviceId': 'moss-switch1',
#            'description': 'Virtual Light Switch',
#            'startDate': 1467588763000,
#            'deviceType': 10072
#        },
#        'control': False
#    }],
#    'measures': [{                           <-- Here are all the latest measurements from the device that caused this execution
#        'prevTime': 0,
#        'value': '1',
#        'prevValue': '0',
#        'updated': True,
#        'deviceId': 'moss-switch1',
#        'name': 'ppc.switchStatus',
#        'time': 1467589363000
#        'prevTime': 1467589362000
#    }],
#    'trigger': 8,                            <-- Trigger 8 = "This triggered from a device measurement"
#    'time': 1467589363290
#}
    
    
    deviceName = trigger['device']['description']
    deviceType = trigger['device']['deviceType']
    
    if deviceType == 10014:
        # This is a door/window entry sensor.
        
        # Retrieve from the input measurements the "value" for the parameter with the "name" = "doorStatus"
        doorStatus = botengine.get_property(measures, "name", "doorStatus", "value")
        
        # Do something with this value
        if doorStatus == "true":
            print("Your '" + deviceName + "' opened!")        # print(), to make it easier for you
        
        else:
            # Notice that this should never execute, because our version.json specifies the triggering device have param name 'doorStatus' equal to 'true'
            print("Your '" + deviceName + "' closed!")        # print(), to make it easier for you
        
        
    elif deviceType == 10072:
        # This is a Virtual Light Switch
        
        switchStatus = botengine.get_property(measures, "name", "ppc.switchStatus", "value")
        
        if int(switchStatus) > 0:
            print("Your '" + deviceName + "' switched on")
            
        else:
            print("Your '" + deviceName + "' switched off")
            
            
    # That's it!  Your bot is complete, demonstrating you can get real-time data from Ensemble-connected devices for processing in Python,
    # on your local computer, or pushed to a cloud server to run 24/7 in the background of your life.
    
    




    
    

