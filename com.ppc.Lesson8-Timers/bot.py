'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 8 - TIMERS
# Bots can set a timer to execute themselves again in the future.
#
# To start a timer, first define a function in your bot.py file to execute:
#
#     def my_timer_fired(botengine, argument):
#
# Since this is a new entry point to your bot, it includes the 'botengine' environment, and
# it includes a single argument.  You can name that argument variable whatever you want.
# This function should be provided in your bot.py file and not any other file, and it
# should never be a class method.
#
# To start the timer, just use the start_timer(..) method in the botengine:
#
#     botengine.start_timer(seconds, function, argument=None, reference=None)
#
# To make your 'my_timer_fired' timer fire in 10 seconds with the argument "Hello!":
#
#     botengine.start_timer(10, my_timer_fired, "Hello!")
#
# To set an absolute timer:
#
#     timestamp = botengine.get_timestamp()
#     milliseconds_from_now = 5000
#     botengine.set_timer(timestamp + milliseconds_from_now, my_timer_fired)
#
# To cancel a timer, you must create a timer with a reference. The reference can be whatever
# you want. Numbers are most efficient if you can remember/specify what they mean.
#
#     MY_TIMER_REFERENCE = 1
#     botengine.start_timer(300, my_timer_fired, "Hello!", MY_TIMER_REFERENCE)
#
#     # ... later ...
#     botengine.cancel_timers(MY_TIMER_REFERENCE)
#
#
# You can pass whatever you want into the timer, but consider the arguments you get when
# the timer fires to be an exact copy of the arguments going in. In other words,
# avoid passing in any object that could have been edited between the time you start the
# timer and the time the timer executes. Best practice, when dealing with device objects for
# example, is to pass in a reference to the device object and then use load_variable(..) to
# load the latest version of that object.
#
# Note that while a timer will never execute early, it is almost always guaranteed to execute
# a little late. Do not expect a timer to execute right on time. Use your timestamps to get a
# sense of the data you should be evaluating.
#
# You can set as many timers as you want. Avoid setting timers faster than 2 seconds.
#
#
# This bot will demonstration initially triggers off of a door/window sensor or a virtual light switch.
# We'll show how to debounce these devices in software.
#
# Now, normal 'debouncing' is done at the microsecond level on physical circuitry. This is
# a similar concept, but across a magnitude of seconds.
#
# When a door opens, we'll execute the bot again in a few seconds to see if the door remained open for
# longer than 2 seconds. If the door was open for less than 2 seconds, then it's likely
# nobody actually made it through the door. Try it yourself and see if you can get through a closed
# door in less than 2 seconds.
#
# We'll do the same thing with the light switch to demonstrate concepts. If the virtual switch
# is on for less than 2 seconds, we'll call the final state OFF.  If it's on for longer than
# 2 seconds, we'll call the final state ON.
#

# RUNNING THIS BOT
# First, register your developer account at http://presto.peoplepowerco.com.
#
# This bot will require a device to be connected to your account:
#    Option A:  Buy a Presence Security Pack (http://presencepro.com/store).
#               This is recommended because it will give you a lot more tools
#               to create cool botswith.
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

# Make it easier to read our if-statements and avoid typos
ENTRY_SENSOR_DEVICE_TYPE = 10014
VIRTUAL_LIGHT_SWITCH_DEVICE_TYPE = 10072


def run(botengine):
    # Initialize
    logger = botengine.get_logger()                  # Debug logger
    inputs = botengine.get_inputs()                  # Information input into the bot
    triggerType = botengine.get_trigger_type()       # What type of trigger caused the bot to execute this time
    trigger = botengine.get_trigger_info()           # Get the information about the trigger
    measures = botengine.get_measures_block()        # Capture new measurements, if any
    access = botengine.get_access_block()            # Capture info about all things this bot has permission to access
    timestamp = botengine.get_timestamp()            # Capture the timestamp of execution

# This is what our inputs look like when we receive a new measurement
#{
#  "access": [
#    {
#      "category": 4,
#      "control": false,
#      "device": {
#        "description": "Virtual Light Switch",
#        "deviceId": "moss-switch1",
#        "device_type": 10072,
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


    # Trigger type 8 is a device measurement
    if triggerType == botengine.TRIGGER_MODE:
        print("\n[" + str(timestamp) + "] Executing on a change of mode, canceling any previous mode timers and starting new ones (10, 15, 20 second timers)")

        # Cancel any previous mode timers
        botengine.cancel_timers("mode")

        # Again, I recommend using an integer for the reference, but I'll use a string here for readability.
        botengine.start_timer(-1, mode_timer_fired, "Minus One Second", "mode")
        botengine.start_timer(0, mode_timer_fired, "Zero Second", "mode")
        botengine.start_timer(1, mode_timer_fired, "One Second", "mode")
        botengine.start_timer(2, mode_timer_fired, "Two Second", "mode")
        botengine.start_timer(3, mode_timer_fired, "Three Second", "mode")
        botengine.start_timer(4, mode_timer_fired, "Four Second", "mode")
        botengine.start_timer(5, mode_timer_fired, "Five Second", "mode")
        botengine.start_timer(6, mode_timer_fired, "Six Second", "mode")
        botengine.start_timer(7, mode_timer_fired, "Seven Second", "mode")
        botengine.start_timer(8, mode_timer_fired, "Eight Second", "mode")
        botengine.start_timer(9, mode_timer_fired, "Nine Second", "mode")
        botengine.start_timer(10, mode_timer_fired, "Ten Second", "mode")
        botengine.start_timer(15, mode_timer_fired, "Fifteen Second", "mode")
        botengine.set_timer(timestamp + 20000, mode_timer_fired, "Twenty Second Absolute", "mode")


    # Trigger type 8 is a device measurement
    elif triggerType == botengine.TRIGGER_DEVICE_MEASUREMENT:
        print("\n[" + str(timestamp) + "] Executing on a new device measurement")

        device_type = trigger['device']['deviceType']
        device_name = trigger['device']['description']
        device_id = str(trigger['device']['deviceId'])

        # Load or create the appropriate object, with the device ID as part of the variable name to track multiple devices.
        focused_object = botengine.load_variable("sensor_object_" + str(device_id))
        if focused_object == None:
            focused_object = Sensor(device_id, device_type, device_name)
            botengine.save_variable(device_id, focused_object)

        # Find out what type of sensor it was.
        if int(device_type) == ENTRY_SENSOR_DEVICE_TYPE:
            # Retrieve from the input measurements the "value" for the parameter with the "name" = "doorStatus"
            doorStatus = botengine.get_property(measures, "name", "doorStatus", "value")
            time = botengine.get_property(measures, "name", "doorStatus", "time")
            state = (doorStatus.lower() == "true") or (doorStatus == "1")
            focused_object.update_state(state, time)

            if state:
                print("[" + str(timestamp) + "] Your '" + device_name + "' opened! Executing this bot again in 3 seconds...")
                botengine.start_timer(3, entry_sensor_timer_fired, device_id)
            else:
                print("[" + str(timestamp) + "] Your '" + device_name + "' closed.")


        if int(device_type) == VIRTUAL_LIGHT_SWITCH_DEVICE_TYPE:
            switchStatus = botengine.get_property(measures, "name", "ppc.switchStatus", "value")
            time = botengine.get_property(measures, "name", "ppc.switchStatus", "time")
            state = (switchStatus == "1")
            focused_object.update_state(state, time)

            if state:
                print("[" + str(timestamp) + "] Your '" + device_name + "' switched on! Executing this bot at a specific timestamp 3 seconds from now...")
                botengine.start_timer(3, virtual_light_switch_timer_fired, device_id)
            else:
                print("[" + str(timestamp) + "] Your '" + device_name + "' switched off.")

        # Make sure you save your variables when you're done, or you'll get strange behaviors!
        botengine.save_variable("sensor_object_" + str(device_id), focused_object)




def entry_sensor_timer_fired(botengine, device_id):
    """
    Entry Sensor timer fired

    Note that the 2 arguments passed in here are always required.
    You can name them whatever you want, but we always need 2 arguments.
    The timer function should always be a base function inside of bot.py, as this is an entry point for execution.
    It is never a function in a different file, and can never be a class method either.

    :param botengine: Execution environment
    :param device_id: Device ID we should be paying attention to inside this timer
    """

    print("\n\n=> Entry Sensor timer fired!")

    # You can't get here without saving these variables from another execution up above.
    # But we'll check their existence anyway for good practice.
    # We never pass in objects that could have been edited in between the time the timer started and when the timer fired,
    # because the timer will always pass in a copy of the argument that was given back when the timer was started, not
    # a reference to the newest objects. Save and load the objects using a reference to them, so you always know what to trust.
    focused_object = botengine.load_variable(device_id)

    if focused_object.was_active_longer_than_x_seconds(1):
        print("\t[" + str(botengine.get_timestamp()) + "]=> OPENED. The last time your '" + focused_object.device_name + "' opened, it was open for longer than 2 seconds.")
    else:
        print("\t[" + str(botengine.get_timestamp()) + "]=> FALSE POSITIVE DETECTED. Your '" + focused_object.device_name + "' wasn't open long enough for someone to get through.")


def virtual_light_switch_timer_fired(botengine, device_id):
    """
    Virtual Light Switch timer fired
    :param botengine: Execution environment
    :param device_id: Device ID we should be paying attention to inside this timer
    """
    focused_object = botengine.load_variable(device_id)

    if focused_object.was_active_longer_than_x_seconds(2):
        print("\t[" + str(botengine.get_timestamp()) + "]=> SWITCHED ON. The last time your '" + focused_object.device_name + "' switched on, it was on for longer than 2 seconds.")
    else:
        print("\t[" + str(botengine.get_timestamp()) + "]=> FALSE POSITIVE DETECTED. Your '" + focused_object.device_name + "' wasn't on for longer than 2 seconds.")


def mode_timer_fired(botengine, name):
    """
    Mode Timer Fired
    :param botengine: Execution environment
    :param name: Name of this timer
    """
    print("\n[" + str(botengine.get_timestamp()) + "] => '" + name + "' mode timer fired!")



class Sensor():
    '''Generic sensor class to store timestamps and states'''

    def __init__(self, device_id, device_type, device_name):
        print("INIT")
        self.device_id = device_id
        self.device_type = device_type
        self.device_name = device_name

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

    def was_active_longer_than_x_seconds(self, seconds):
        '''Find if the sensor was really active for longer than X seconds'''
        print("self.timestamp = " + str(self.timestamp))
        print("self.lastTimestamp = " + str(self.lastTimestamp))
        print("self.timestamp - self.lastTimestamp = " + str(self.timestamp - self.lastTimestamp))
        return self.state or ((self.timestamp - self.lastTimestamp) >= (seconds * 1000))
