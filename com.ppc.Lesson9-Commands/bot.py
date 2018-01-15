'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 9 - COMMANDS
# This lesson will show how to send commands to devices.
# By default, the bot will access all devices it is requesting access to in the runtime.json file.
# Users can opt-out of sharing devices with the bot.
#
# In this example bot, the user can also the bot permission to listen to any number of light switches and light bulbs.
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
#
# HOMEWORK: LIGHTING BOT
#   Make a version of this bot that is compatible with real in-wall switches, light bulbs, and motion detectors.
#   When motion is detected by any motion sensor accessible by the bot, turn on all the lights.
#   When a light switch is toggled on, turn on all the other lights accessible by the bot.
#   If bots turned on from motion detection, then when no motion is detected for 5 minutes, turn off the lights.
#
#   Use "botengine --device_types" to find the correct device type ID's for light bulbs, switches, and motion sensors.
#


# RUNNING THIS BOT
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
#    in your account before you can successfully run this bot.
#
#
# There are several steps needed to run this bot:
#    1. Create a new directory for your bot, with your own unique bundle ID. Copy all the files into it.
#       Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourBot) and cannot
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
# 2. Commit your bot to the server.
#    This will push all the code, version information, marketing information, and icon to the server.
#    The bot will become privately available.
#
#    This will also purchase the bot for you.
#
#    botengine --commit com.yourname.YourBot
#
#
# 3. Run the bot locally.
#
#    botengine --run com.yourname.YourBot
#
#    This will automatically look up your bot instance ID and run the bot, using the real-time streaming data from the server
#    and the code that is on your local computer.
#

# Declare our virtual light switch device type, to avoid typos and gain clarity in the code
VIRTUAL_LIGHT_SWITCH_DEVICE_TYPE = 10072
VIRTUAL_LIGHT_BULB_DEVICE_TYPE = 10071


def run(botengine):
    """
    Starting point of execution
    :param botengine: BotEngine environment - your link to the outside world
    """

    # Initialize
    inputs = botengine.get_inputs()                  # Information input into the bot
    trigger_type = botengine.get_trigger_type()       # What type of trigger caused the bot to execute this time
    measures = botengine.get_measures_block()        # Capture new measurements, if any
    access = botengine.get_access_block()            # Capture info about all things this bot has permission to access

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

    if botengine.load_variable("lights_on") == None:
        # Initialize the 'lights_on' variable
        botengine.save_variable("lights_on", False)

    lights_on = botengine.load_variable("lights_on")
    lights_on = not lights_on

    # For your convenience to see what's going on
    botengine.get_logger().info("Light switch toggled")

    # Send the command to all the lights we're given permission to access
    for item in access:
        try:
            device_type = item['device']['deviceType']

            if device_type == VIRTUAL_LIGHT_SWITCH_DEVICE_TYPE:
                print("Commanding '" + item['device']['deviceId'] + "' to switch to " + str(lights_on).lower())
                botengine.send_command(device_id=item['device']['deviceId'], param_name="outletStatus", value=str(lights_on).lower())

        except KeyError:
            pass

    botengine.save_variable("lights_on", lights_on)
