'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 7 - MACHINE LEARNING
# Up until now, your bots have been executing, and at the end of execution all of
# the local variables are completely deleted.
#
# Now it's time to persist variables across multiple bot triggers and executions.
#
# This lesson will demonstrate how to manage variables that persist across executions.
# We will listen to door/window sensors, and virtual light switches, and give you a
# report about how many times they were opened or turned on, and for how long, on
# schedule every 30 seconds.
#
# Imagine this is a paid service that is running in a user's account, and once per week
# you'd like to send that user an email summary of all the things that happened
# in their account. That's what we're creating here.
#
# With the ability to save memory, we have the ability to transform the very
# primitive classes we defined below into classes and objects that perform
# very complex machine learning algorithms. The limits of what you can create
# are found at the boundaries of the Python programming language capabilities.
#
# To add real machine learning libraries to your project like scikit-learn, open the structure.json
# and add the Python package dependencies to the "pip_install" list. This will download and install those dependencies
# locally into the bot's directory on your computer during the bot generation process while committing and running.
#
# structure.json:
#
#     "pip_install": [
#        "scipy",
#        "numpy"
#     ],
#
#
# VARIABLES
# The BotEngine bot pickles all variables coming in, and unpickles them coming out.
# That means you can store everything that can be pickled.
# Integers. Strings. Floats. Tuples. Arrays. Objects. Everything.
#
# According to https://docs.python.org/3/library/pickle.html, the following can be pickled:
#   * None, True, and False
#   * Integers, floating point numbers, complex numbers
#   * Strings, bytes, bytearrays
#   * Tuples, lists, sets, and dictionaries containing only picklable objects
#   * Functions defined at the top level of a module (using def, not lambda)
#   * Built-in functions defined at the top level of a module
#   * Classes that are defined at the top level of a module
#   * Instances of such classes whose __dict__ or the result of calling __getstate__() is
#     picklable (see section Pickling Class Instances for details).
#
# The BotEngine framework will automatically load all variables before your bot starts,
# and it will flush all variables when your bot exits.  When you save and load variables
# while the bot is running, no API calls are made until the very end of execution. This makes
# the load() and save() operations extremely efficient while your bot is running.
#
# When the bot finishes executing, any variables that were saved during execution will
# be flushed to non-volatile memory on the server. This requires an API call to be made
# to synchronize your local BotEngine bot with the server.
#
# You should never have to flush variables yourself. Just load() and save(), and let the
# framework do its job.
#
# The available methods are:
#
#   - save_variable(name, value)             # For example, save_variable("helloWorld", True)
#   - save_variables(variables_dictionary)   # In the form of {"variable1": "value1", "variable2": "value2"}
#   - clear_variable(name)                   # The equivalent of save_variable("yourVariable", None)
#   - flush_variables()                      # It's available, but you should never call this.
#                                              It is called automatically each time your bot exits.
#   - load_variable(name)                    # Returns the object you saved last time, or None.
#
#
# HOMEWORK EXERCISE
#   * The framework can save objects. Objects are instantiated from classes.
#     As you evolve your code, under what circumstances can you safely
#     update the definition of your class while loading into that new definition an object created from
#     an older definition?  How do you future-proof your code?
#
#

# RUNNING THIS APP
# First, create a user account at http://app.presencepro.com.
#
# This bot will require a device to be connected to your account:
#    Option A:  Buy a Presence Security Pack (http://presencepro.com/store).
#               This is recommended because it will give you a lot more tools
#               to create cool bots with.
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
# There are several steps needed to run this :
#    1. Create a new directory for your , with your own unique bundle ID. Copy all the files into it.
#       Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourBot) and cannot
#       be deleted or edited once created.
#    2. Create a new -- on the server with botengine
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



def run(botengine):
    """
    Starting point of execution
    :param botengine: BotEngine environment - your link to the outside world
    """

    # Initialize
    inputs = botengine.get_inputs()                  # Information input into the
    trigger_type = botengine.get_trigger_type()      # What type of trigger caused the bot to execute this time
    triggers = botengine.get_triggers()              # Get the information about the trigger
    measures = botengine.get_measures_block()        # Capture new measurements, if any
    access = botengine.get_access_block()            # Capture info about all things this bot has permission to access
    timestamp_ms = botengine.get_timestamp()          # Get the timestamp of execution

    # Let's figure out what triggered us, and therefore what we should do next.
    if trigger_type == botengine.TRIGGER_SCHEDULE:
        print("\nExecuting on schedule")
        print("---------")
        door_object = botengine.load_variable("door_object")
        if door_object == None:
            # This has never been run before - go ahead and create the DoorTracker() object for the first time.
            door_object = DoorTracker(timestamp_ms, False)

            # Here we demonstrate the 'required_for_each_execution' flag inside of the save_variable(..) method.
            # If you use this flag, then your variable will be downloaded before your bot executes, every time.
            # It will increase performance if you know your variable will definitely be used on every execution.
            #
            # If you use this flag but do not end up using this variable on every execution, then you might end
            # up decreasing performance due to the extra overhead of loading it on each execution.
            botengine.save_variable("door_object", door_object, required_for_each_execution=True)

        switch_object = botengine.load_variable("switch_object")
        if switch_object == None:
            # This has never been run before - go ahead and create the SwitchTracker() object for the first time.
            switch_object = SwitchTracker(timestamp_ms, False)
            botengine.save_variable("switch_object", switch_object)

        # Get our objects ready for reporting
        opens = door_object.total_opens()
        open_ms = door_object.total_time_open_ms(timestamp_ms)

        on = switch_object.total_on()
        on_ms = switch_object.total_time_on_ms(timestamp_ms)

        # This would be our "daily report"
        print("Your door opened " + str(opens) + " times in the past 30 seconds")
        print("Your door spent " + str(open_ms / 1000) + " seconds open")
        print("")
        print("Your switch turned on " + str(on) + " times in the past 30 seconds")
        print("Your switch spent " + str(on_ms / 1000) + " seconds on")

        # Create new objects to start accumulating data fresh for the next report
        # If you use 'required_for_each_execution' once, then try to use it every time on when saving that variable name.
        botengine.save_variable("door_object", DoorTracker(timestamp_ms, door_object.was_open), required_for_each_execution=True)
        botengine.save_variable("switch_object", SwitchTracker(timestamp_ms, switch_object.was_switched_on))


    elif trigger_type == botengine.TRIGGER_DEVICE_MEASUREMENT:
        # There can be multiple devices that trigger simultaneously (for example, a parent and child)
        for trigger in triggers:
            print("\nExecuting on a new device measurement")
            print("---------")
            device_type = trigger['device']['deviceType']
            device_name = trigger['device']['description']

            if device_type == 10014:
                # This is a door/window entry sensor.

                # See if we previously stored a DoorTracker() object - if not, initialize it.
                door_object = botengine.load_variable("door_object")
                if door_object == None:
                    # This has never been run before - go ahead and create the DoorTracker() object for the first time.
                    door_object = DoorTracker(timestamp_ms, False)

                    # If you use 'required_for_each_execution' once, then try to use it every time you save that variable name
                    botengine.save_variable("door_object", door_object, required_for_each_execution=True)

                # Retrieve from the input measurements the "value" for the parameter with the "name" = "doorStatus"
                door_status = botengine.get_property(measures, "name", "doorStatus", "value")

                if door_status == "true":
                    print("=> Your '" + device_name + "' opened")
                    door_object.opened(timestamp_ms)

                else:
                    print("=> Your '" + device_name + "' closed")
                    door_object.closed(timestamp_ms)

                # Print out some status
                opens = door_object.total_opens()
                open_ms = door_object.total_time_open_ms(timestamp_ms)

                print("Your door opened " + str(opens) + " times so far")
                print("Your door spent " + str(open_ms / 1000) + " seconds open")

                # Save!
                botengine.save_variable("door_object", door_object, required_for_each_execution=True)


            elif device_type == 10072:
                # This is a Virtual Light Switch

                # See if we previously stored a SwitchTracker() object - if not, initialize it.
                switch_object = botengine.load_variable("switch_object")
                if switch_object == None:
                    # This has never been run before - go ahead and create the SwitchTracker() object for the first time.
                    switch_object = SwitchTracker(timestamp_ms, False)
                    botengine.save_variable("switch_object", switch_object)

                # Now augment our saved variables
                switch_status = botengine.get_property(measures, "name", "ppc.switchStatus", "value")

                if int(switch_status) > 0:
                    print("Your '" + device_name + "' switched on")
                    switch_object.did_switch_on(timestamp_ms)

                else:
                    print("Your '" + device_name + "' switched off")
                    switch_object.did_switch_off(timestamp_ms)


                # Print out some status
                on = switch_object.total_on()
                on_ms = switch_object.total_time_on_ms(timestamp_ms)

                print("Your switch turned on " + str(on) + " times so far")
                print("Your switch spent " + str(on_ms / 1000) + " seconds on")

                # Save!
                botengine.save_variable("switch_object", switch_object)






class DoorTracker:
    '''This class will track how many times the door opened, and how long it was opened'''
    def __init__(self, timestamp, doorWasOpen):
        """Constructor"""

        self.opens = 0;
        self.open_ms = 0;
        self.was_open_on_init = doorWasOpen
        self.was_open = doorWasOpen
        self.opened_timestamp = timestamp

    def opened(self, timestamp):
        '''The door opened'''
        if self.was_open:
            return

        self.opens = self.opens + 1
        self.opened_timestamp = timestamp
        self.was_open_on_init = False
        self.was_open = True

    def closed(self, timestamp):
        '''The door closed'''
        if not self.was_open:
            return

        self.open_ms = self.open_ms + (timestamp - self.opened_timestamp)
        self.was_open = False

    def total_opens(self):
        '''Return the total number of times the door opened'''
        return self.opens

    def total_time_open_ms(self, timestamp):
        '''Return the total amount of time the door spent open, in milliseconds'''
        if self.opens == 0 and not self.was_open_on_init:
            return 0

        total_time_open_ms = self.open_ms

        if self.was_open:
            total_time_open_ms = total_time_open_ms + (timestamp - self.opened_timestamp)

        return total_time_open_ms



class SwitchTracker:
    '''This class will track how many times the switch turned on, and how long it was on for'''
    def __init__(self, timestamp, switchWasOn):
        """Constructor"""

        self.switched_on = 0;
        self.on_ms = 0;
        self.switched_on_timestamp = timestamp
        self.was_on_on_init = switchWasOn
        self.was_switched_on = switchWasOn

    def did_switch_on(self, timestamp):
        '''Switched on'''
        if self.was_switched_on:
            return

        self.switched_on = self.switched_on + 1
        self.switched_on_timestamp = timestamp
        self.was_on_on_init = False
        self.was_switched_on = True

    def did_switch_off(self, timestamp):
        '''Switched off'''
        if not self.was_switched_on:
            return

        self.on_ms = self.on_ms + (timestamp - self.switched_on_timestamp)
        self.was_switched_on = False

    def total_on(self):
        '''Return the total number of times the switch turned on'''
        return self.switched_on

    def total_time_on_ms(self, timestamp):
        '''Return the total amount of time the switch turned off, in milliseconds'''
        if self.switched_on == 0 and not self.was_on_on_init:
            return 0

        total_time_open_ms = self.on_ms

        if self.was_switched_on:
            total_time_open_ms = total_time_open_ms + (timestamp - self.switched_on_timestamp)

        return total_time_open_ms
