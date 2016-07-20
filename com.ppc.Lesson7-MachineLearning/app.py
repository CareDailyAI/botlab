'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 8 - MACHINE LEARNING
# Up until now, your apps have been executing, and at the end of execution all of
# the local variables are completely deleted. 
# 
# Now it's time to persist variables across multiple app triggers and executions.
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
# 
# VARIABLES
# The Composer app pickles all variables coming in, and unpickles them coming out.
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
# The Composer framework will automatically load all variables before your app starts,
# and it will flush all variables when your app exits.  When you save and load variables
# while the app is running, no API calls are made until the very end of execution. This makes
# the load() and save() operations extremely efficient while your app is running. 
#
# When the app finishes executing, any variables that were saved during execution will
# be flushed to non-volatile memory on the server. This requires an API call to be made 
# to synchronize your local Composer app with the server. 
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
#                                              It is called automatically each time your app exits.
#   - load_variable(name)                    # Returns the object you saved last time, or None.
# 
# 
# HOMEWORK EXERCISE
#   * The framework can save objects. Objects are instantiated from classes.
#     As you evolve your code, under what circumstances can you safely
#     modify the definition of your class?  How do you future-proof your code?
#     What guidelines or best practices can you offer?
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



def run(composer, initialize=False):
    # Initialize
    logger = composer.get_logger()                  # Debug logger
    inputs = composer.get_inputs()                  # Information input into the app
    triggerType = composer.get_trigger_type()       # What type of trigger caused the app to execute this time
    trigger = composer.get_trigger_info()           # Get the information about the trigger
    measures = composer.get_measures_block()        # Capture new measurements, if any
    access = composer.get_access_block()            # Capture info about all things this app has permission to access
    timestampMs = composer.get_timestamp()          # Get the timestamp of execution
    
    # Let's figure out what triggered us, and therefore what we should do next.
    if triggerType == 1:
        print("\nExecuting on schedule")
        print("---------")
        doorObject = composer.load_variable("doorObject")
        if doorObject == None:
            # This has never been run before - go ahead and create the DoorTracker() object for the first time.
            doorObject = DoorTracker(timestampMs, False)
            composer.save_variable("doorObject", doorObject)
                
        switchObject = composer.load_variable("switchObject")
        if switchObject == None:
            # This has never been run before - go ahead and create the SwitchTracker() object for the first time.
            switchObject = SwitchTracker(timestampMs, False)
            composer.save_variable("switchObject", switchObject)
        
        # Get our objects ready for reporting
        opens = doorObject.totalOpens()
        openMs = doorObject.totalTimeOpenMs(timestampMs)
        
        on = switchObject.totalOn()
        onMs = switchObject.totalTimeOnMs(timestampMs)
        
        # This would be our "daily report"
        print("Your door opened " + str(opens) + " times in the past 30 seconds")
        print("Your door spent " + str(openMs / 1000) + " seconds open")
        print()
        print("Your switch turned on " + str(on) + " times in the past 30 seconds")
        print("Your switch spent " + str(onMs / 1000) + " seconds on")
        
        # Create new objects to start accumulating data fresh for the next report
        composer.save_variable("doorObject", DoorTracker(timestampMs, doorObject.wasOpen))
        composer.save_variable("switchObject", SwitchTracker(timestampMs, switchObject.wasSwitchedOn))
        
        
    elif triggerType == 8:
        print("\nExecuting on a new device measurement")
        print("---------")
        deviceType = trigger['device']['deviceType']
        deviceName = trigger['device']['description']
        
        if deviceType == 10014:
            # This is a door/window entry sensor.
            
            # See if we previously stored a DoorTracker() object - if not, initialize it.
            doorObject = composer.load_variable("doorObject")
            if doorObject == None:
                # This has never been run before - go ahead and create the DoorTracker() object for the first time.
                doorObject = DoorTracker(timestampMs, False)
                composer.save_variable("doorObject", doorObject)
            
            # Retrieve from the input measurements the "value" for the parameter with the "name" = "doorStatus"
            doorStatus = composer.get_property(measures, "name", "doorStatus", "value")
            
            if doorStatus == "true":
                print("\t=> Your '" + deviceName + "' opened")
                doorObject.opened(timestampMs)
                    
            else:
                print("\t=> Your '" + deviceName + "' closed")
                doorObject.closed(timestampMs)
                
            # Print out some status
            opens = doorObject.totalOpens()
            openMs = doorObject.totalTimeOpenMs(timestampMs)
            
            print("Your door opened " + str(opens) + " times so far")
            print("Your door spent " + str(openMs / 1000) + " seconds open")
            
            # Save!
            composer.save_variable("doorObject", switchObject)
            
            
        elif deviceType == 10072:
            # This is a Virtual Light Switch
            
            # See if we previously stored a SwitchTracker() object - if not, initialize it.
            switchObject = composer.load_variable("switchObject")
            if switchObject == None:
                # This has never been run before - go ahead and create the SwitchTracker() object for the first time.
                switchObject = SwitchTracker(timestampMs, False)
                composer.save_variable("switchObject", switchObject)
            
            # Now augment our saved variables
            switchStatus = composer.get_property(measures, "name", "ppc.switchStatus", "value")
            
            if int(switchStatus) > 0:
                print("Your '" + deviceName + "' switched on")
                switchObject.didSwitchOn(timestampMs)
                
            else:
                print("Your '" + deviceName + "' switched off")
                switchObject.didSwitchOff(timestampMs)
                
                
            # Print out some status
            on = switchObject.totalOn()
            onMs = switchObject.totalTimeOnMs(timestampMs)
            
            print("Your switch turned on " + str(on) + " times so far")
            print("Your switch spent " + str(onMs / 1000) + " seconds on")
            
            # Save!
            composer.save_variable("switchObject", switchObject)
            
            
                
                
        
        
class DoorTracker:
    '''This class will track how many times the door opened, and how long it was opened'''
    def __init__(self, timestamp, doorWasOpen):
        """Constructor"""
        
        self.opens = 0;
        self.openMs = 0;
        self.wasOpenOnInit = doorWasOpen
        self.wasOpen = doorWasOpen
        self.openedTimestamp = timestamp
        
    def opened(self, timestamp):
        '''The door opened'''
        if self.wasOpen:
            return
        
        self.opens = self.opens + 1
        self.openedTimestamp = timestamp
        self.wasOpenOnInit = False
        self.wasOpen = True
        
    def closed(self, timestamp):
        '''The door closed'''
        if not self.wasOpen:
            return
        
        self.openMs = self.openMs + (timestamp - self.openedTimestamp)
        self.wasOpen = False
    
    def totalOpens(self):
        '''Return the total number of times the door opened'''
        return self.opens
    
    def totalTimeOpenMs(self, timestamp):
        '''Return the total amount of time the door spent open, in milliseconds'''
        if self.opens == 0 and not self.wasOpenOnInit:
            return 0
        
        totalTimeOpenMs = self.openMs
        
        if self.wasOpen:
            totalTimeOpenMs = totalTimeOpenMs + (timestamp - self.openedTimestamp)
            
        return totalTimeOpenMs
    

        
class SwitchTracker:
    '''This class will track how many times the switch turned on, and how long it was on for'''
    def __init__(self, timestamp, switchWasOn):
        """Constructor"""
        
        self.switchedOn = 0;
        self.onMs = 0;
        self.switchedOnTimestamp = timestamp
        self.wasOnOnInit = switchWasOn
        self.wasSwitchedOn = switchWasOn
        
    def didSwitchOn(self, timestamp):
        '''Switched on'''
        if self.wasSwitchedOn:
            return
        
        self.switchedOn = self.switchedOn + 1
        self.switchedOnTimestamp = timestamp
        self.wasOnOnInit = False
        self.wasSwitchedOn = True
        
    def didSwitchOff(self, timestamp):
        '''Switched off'''
        if not self.wasSwitchedOn:
            return
        
        self.onMs = self.onMs + (timestamp - self.switchedOnTimestamp)
        self.wasSwitchedOn = False
    
    def totalOn(self):
        '''Return the total number of times the switch turned on'''
        return self.switchedOn
    
    def totalTimeOnMs(self, timestamp):
        '''Return the total amount of time the switch turned off, in milliseconds'''
        if self.switchedOn == 0 and not self.wasOnOnInit:
            return 0
        
        totalTimeOpenMs = self.onMs
        
        if self.wasSwitchedOn:
            totalTimeOpenMs = totalTimeOpenMs + (timestamp - self.switchedOnTimestamp)
        
        return totalTimeOpenMs
    
