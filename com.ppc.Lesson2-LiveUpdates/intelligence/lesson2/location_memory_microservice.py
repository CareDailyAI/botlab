'''
Created on June 27, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence

class LocationMemoryMicroservice(Intelligence):
    """
    When your bot begins running in someone's account, it's live. But you - the developer - want to update it and add features. It's like changing a car tire while it's barreling down the road while trying not to crash.

    In live bots, microservice objects have already been instantiated and their constructor methods have already been called, so how do you add more features and variables to these objects?

    It turns out **the main thing you need to worry about are the class variables.** You can change the logic in your methods and nothing bad will happen (assuming you didn't add bugs to your code), but any new class variables you want to add to an already-running bot need to be properly instantiated. Failure to properly instantiate new class variables will crash live bots when your new logic attempts to access a variable that isn't there.

    Let's cut straight to the point.

    ## Use initialize() to add new variables to bots that are running live
    If there's anything to get out of this lesson, it's this one rule.

    When you need to add a new class variable to a microservice that may already be running inside a user's account,
    use the `initialize()` method to dynamically instantiate that new variable and add it to the class. Remember, the
    standardized `initialize(...)` method is called at the start of each execution in every microservice. Follow this template:

        def initialize(self, botengine):
            if not hasattr(self, 'new_variable'):
                self.new_variable = None

    If you don't do this, existing bot instances running in users' accounts may crash. It's not the end of the world: you can use `botengine --errors com.yourname.YourBot` to see errors from your bots running live on the server. In this world, you can fix the error and redeploy the bot instantaneously to fix the crasher.


    ### Explaining why: Old objects in new classes

    Class variables store memory that persists across multiple executions of the microservice. Class variables
    are typically defined in the `__init__()` method. But there's an important behavior to note: the `__init__()` method only gets called
    one time, only when the microservice is instantiated for the very first time. But your class definition for the microservice may
    continue to evolve over time as you continue to make improvements on an already-running bot.

    Let's say you are working on a bot microservice and run it in your account. When you run it for the first time, the framework
    will instantiate copies of all the microservices. The `__init__()` method is called one time per microservice, and class variables
    are created. Each future trigger of your bot will keep using the same objects that were already instantiated on each execution,
    and the `__init__()` method will never get called again on any existing microservice, even though you keep evolving the code.

    So, each time you modify the definition of the class and run the bot, something crazy happens: you're actually running a new
    definition of the class, against an object that already existed in memory which was instantiated from an older and now deprecated
    version of that class! How do you ensure, if your latest class requires a new class variable, that this new class variable is actually
    instantiated in memory before your new logic starts to try to access it?

    The `initialize()` method gets called every time the bot triggers and before anything else executes, and that's where we check to see
    if the class variable exists. If it doesn't, we create it. Now any logic in the new definition of your class that may reference
    `self.new_variable` will be able to see and interact with that variable with no problem, as if it existed all along.


    ## Best practices for commercial grade bot services

    While the code above is sufficient to solve most problems you'll run into as a developer, there are a few more concepts to internalize if you're going to deploy and manage commercial grade bots.

    Since the initialize() method gets called on every trigger and in every microservice, it is inefficient (on the order of nanoseconds, but still, don't write inefficient code...) so you should have a plan to
    someday back off the dynamic initialization of this class variable in a future bot update (perhaps a few weeks from now) by adding
    the new variable definition to the `__init__()` method, and also commenting a timestamp recommendation of when you can safely remove
    the dynamically initialized variable.

    Everyone's bot just needs to be triggered a single time for the new variable to become initialized, so
    if your bot triggers on schedule once a week to send out an email, then you should let a minimum of 1 week pass to ensure everyone's
    bot has initialized the new variable.

    For the `self.new_variable` described above, here are some best practices:

    Add the self.new_variable definition directly into the `__init__()` method:

        def __init__(self, botengine, parent):
            # New variable definition
            self.new_variable = None

    Add a comment to the dynamically initialized variable in the `initialize()` method:

        def initialize(self, botengine):
            # Remove after August 2, 20__
            if not hasattr(self, 'new_variable'):
                self.new_variable = None

    Now, any newly instantiated microservice simply starts out with this variable already declared one time. And later, you'll
    be reminded that it's safe to remove the dynamically instantiated class variable from the `initialize()` method, making
    your bot execute that much faster.

    ### Careful renaming or deleting microservice files

    When your bot executes, it downloads your serialized working environment from the server and uses the Python library `dill`
    to unpack and setup your whole environment. If a previous running version of your bot created a microservice, and then
    your latest version of the bot renames or deletes the microservice file, the `dill` library will choke and won't be able to unpack your
    environment. The result is it will give up, and all memory will be lost. The bot will start all over again as if it were
    just added to the user's account fresh.

    If you need to delete a microservice file, it's a 2-step process:

    1. Remove the microservice reference from `index.py`. Commit / publish the bot. When the bot runs in users' accounts, it
    will dynamically remove the microservice from memory.

    2. After the new bot has executed at least one time in everyone's account (wait a few weeks), the old microservice is now
    gone from memory. You can safely delete or rename the microservice file if you'd like.


    ### Deleting class variables
    If you need to get rid of a class variable, you will improve the execution speed. Remove the initialization of the variable
    from the `__init__()` and `initialize()` methods, and delete the variable in your `initialize()` method:

        def initialize(self, botengine):
            if hasattr(self, 'variable_to_delete'):
                del(self.variable_to_delete)


    ### Large variables
    If you have a large amount of data (>500kB) like a machine learning model or a picture, and if that data is not
    required on every execution of your bot, then you could further optimize your performance by placing that data into
    a separately stored botengine variable and avoid using class variables.

    At a mechanical level, every time your bot executes, the class variables have to first get downloaded into the bot from the
    server and populated. And when your bot gets done executing, all your class variables are saved back up to the server for
    next time. No need to include a large chunk of data in that process if you don't need to access that data on each execution.
    That's when you switch strategies and leverage two useful methods:

        botengine.save_variable(name, value)
        value = botengine.load_variable(name)

    The `name` argument is a string, and the `value` can be anything. When using this method, the botengine will save and load your
    variables extremely efficiently, flushing them to the server automatically when your bot gets done executing the current trigger.
    If you load_variable() multiple times on the same `name`, only 1 API call is made to the server to retrieve the variable.

    ## Protected variables
    If you have a small variable that must absolutely be protected against dumb errors you might make in the future,
    save it into a separate botengine variable space so it can remain intact - even if you break rule #1 or #2.

        botengine.save_variable("protected_variable", value)

    If you need that variable on every execution of the bot, then add the `required_for_each_execution` flag when you save the
    variable. The variable will be available when the bot executes, which means the bot doesn't need to make an additional API
    call to the server to retrieve it:

        botengine.save_variable("protected_variable", value, required_for_each_execution=True)


    ## Examples
    See the code below for examples.
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        # Always initialize your superclass first.
        Intelligence.__init__(self, botengine, parent)

        # This is how we store memory. Just define a class variable. The microservices framework takes care of the rest automatically.
        self.total_mode_updates = 0

        # This represents a variable that you created a long time ago, but now that you've updated this microservice, maybe you want to get rid of this class variable.
        # Check out the initialize() method to see how to remove a deprecated class variable.
        self.delete_this_class_variable = "Old, deprecated Variable - get rid of me"


    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """

        # Whoops! Your bot is already running and we need to add a new variable. Here's how to do it.
        # It's a good idea to add a comment like: "Remove on August 2, 20__" (after the bot triggers at least 1 time in every user's account)
        # so your bot will eventually execute a little more efficiently.
        if not hasattr(self, 'total_measurements'):
            self.total_measurements = 0

        # Delete an existing class variable that's no longer needed, to make your bot save and load more efficiently.
        if hasattr(self, 'delete_this_class_variable'):
            del(self.delete_this_class_variable)

        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        return

    def get_html_summary(self, botengine, oldest_timestamp_ms, newest_timestamp_ms, test_mode=False):
        """
        Return a human-friendly HTML summary of insights or status of this intelligence module to report in weekly and test mode emails
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: Oldest timestamp in milliseconds to summarize
        :param newest_timestamp_ms: Newest timestamp in milliseconds to summarize
        :param test_mode: True to add or modify details for test mode, instead of a general weekly summary
        """
        return ""

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        self.total_mode_updates += 1
        botengine.get_logger().info("You have updated your mode {} times".format(self.total_mode_updates))
        return

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        # Notice that even though self.total_measurements was not defined in the __init__() method, because it's
        # defined in the initialize method we can just start using it and make the correct assumption that it actually exists.
        self.total_measurements += 1
        botengine.get_logger().info("Class variable: This bot has heard {} device measurements and heartbeats.".format(self.total_measurements))

        # PROTECTED VARIABLE
        # Here's an example of a protected variable stored in a separate memory space, not required for each execution.
        measurements = botengine.load_variable("measurements")
        if measurements is None:
            # Initialize the protected variable
            measurements = 0

        measurements += 1
        botengine.get_logger().info("Protected variable: This bot has heard {} device measurements and heartbeats.".format(measurements))
        botengine.save_variable("measurements", measurements)
        return

    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        return

    def device_alert(self, botengine, device_object, alert_type, alert_params):
        """
        Device sent an alert.
        When a device disconnects, it will send an alert like this:  [{u'alertType': u'status', u'params': [{u'name': u'deviceStatus', u'value': u'2'}], u'deviceId': u'eb10e80a006f0d00'}]
        When a device reconnects, it will send an alert like this:  [{u'alertType': u'on', u'deviceId': u'eb10e80a006f0d00'}]
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
        """
        return

    def device_deleted(self, botengine, device_object):
        """
        Device is getting deleted
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting deleted
        """
        return

    def question_answered(self, botengine, question):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question: Question object
        """
        return

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        return

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """
        return

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        return

    def file_uploaded(self, botengine, device_object, file_id, filesize_bytes, content_type, file_extension):
        """
        A device file has been uploaded
        :param botengine: BotEngine environment
        :param device_object: Device object that uploaded the file
        :param file_id: File ID to reference this file at the server
        :param filesize_bytes: The file size in bytes
        :param content_type: The content type, for example 'video/mp4'
        :param file_extension: The file extension, for example 'mp4'
        """
        return

    def coordinates_updated(self, botengine, latitude, longitude):
        """
        Approximate coordinates of the parent proxy device object have been updated
        :param latitude: Latitude
        :param longitude: Longitude
        """
        return

