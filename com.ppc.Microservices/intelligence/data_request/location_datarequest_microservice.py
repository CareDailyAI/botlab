'''
Created on February 1, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence
import utilities.utilities as utilities
import signals.analytics as analytics
import signals.machinelearning as machinelearning
import properties

from devices.entry.entry import EntryDevice
from devices.motion.motion import MotionDevice
from devices.radar.radar import RadarDevice
from devices.pressure.pressure import PressurePadDevice
from devices.bed.bed import BedDevice
from devices.health.health import HealthDevice

# For debugging, export CSV data to local files
EXPORT_CSV_TO_LOCAL_FILES = False

# Timer reference to avoid overlapping timers
TIMER_REFERENCE = "dr"

# Data request postprocess variable name for split-phase processing
DATA_REQUEST_POSTPROCESS = "data_request_postprocess"

# Version
VERSION = 1.0


class LocationDataRequestMicroservice(Intelligence):
    """
    This module is responsible for waking up at least once weekly, downloading data, and distributing the shared data
    throughout the various microservices to allow machine learning models to be created efficiently.

    The result will be a async_data_request_ready() event with a reference "all", which other microservices can listen for
    to reproduce machine learning models.

    CRITICAL WARNING ABOUT ASYNC_DATA_REQUEST_READY() EXECUTION:
    Data Request triggers operate *concurrently* with other triggers, because typically machine learning
    algorithms take their sweet, sweet time and life must go on. Therefore, **the core variable is not saved** during
    execution of a data request trigger (because otherwise, it would stomp all over the other trigger executions that are
    taking place in the background). That means: YOU CANNOT SAVE CLASS VARIABLES DURING A DATA REQUEST TRIGGER. You must
    save all memory inside explicitly separate variables with botengine.save_variable() or botengine.save_shared_variable().

    PROPER PRACTICE FOR DATA REQUEST PROCESSING:
    1. During async_data_request_ready() execution, process your data and store conclusions in explicit non-volatile variables
       using botengine.save_variable() or botengine.save_shared_variable(). DO NOT use class variables to store state.
    2. Implement the data_request_postprocess() event handler in your microservice to safely interact with the user,
       set timers, update class variables, and perform any other operations that require core variable access.
    3. This microservice implements a split-phase operation through the use of the non-volatile variable
       "data_request_postprocess" and data stream delivery architecture, overcoming the limitations of parallel
       execution and avoiding core variable and timer conflicts.

    SPLIT-PHASE ARCHITECTURE:
    - async_data_request_ready() processes data and stores references for post-processing
    - initialize() checks for pending post-processing and schedules it
    - timer_fired() distributes data_request_postprocess signals to microservices
    - Microservices receive data_request_postprocess() and can safely interact with the system
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # Last recalculation timestamp
        self.last_download = 0

        # When was this microservice born on
        self.born_on = botengine.get_timestamp()

        # Version
        self.version = None

        # Download data
        machinelearning.request_data(botengine, location_object=self.parent)

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        if self.version != VERSION:
            machinelearning.request_data(botengine, location_object=self.parent, force=True)

        return

    def initialize(self, botengine):
        """
        Initialize the microservice
        :param botengine: BotEngine environment
        """
        # Check for pending data request postprocessing
        postprocess_list = botengine.load_variable(DATA_REQUEST_POSTPROCESS)
        if postprocess_list is not None and len(postprocess_list) > 0:
            # We have previous data request references to post-process
            # Set a timer for 10 seconds to process them
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(utilities.Color.PURPLE + ">initialize() Post-processing {} data request references".format(len(postprocess_list)) + utilities.Color.END)
            self.start_timer_ms(botengine, utilities.ONE_SECOND_MS * 10, reference="postprocess", argument=postprocess_list)
            # Clear the variable so we don't set another timer next time
            botengine.save_variable(DATA_REQUEST_POSTPROCESS, None)

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        if hasattr(self, address):
            getattr(self, address)(botengine, content)

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """
        if schedule_id == "ML":
            import random
            if botengine.playback:
                # Reduce the strain on the playback system by calculating on a weekly basis
                if self.parent.get_local_datetime(botengine).weekday() > 0:
                    return
                
            self.start_timer_ms(botengine, random.randint(0, utilities.ONE_HOUR_MS * 12), reference="schedule_ml", argument="schedule")

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        # Check if this is a postprocess timer
        if isinstance(argument, list):
            # This is a postprocess timer - distribute data_request_postprocess signals
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(utilities.Color.PURPLE + ">timer_fired() DATA REQUEST POST-PROCESSING START: Processing {} data request references for postprocessing".format(len(argument)) + utilities.Color.END)
            for reference in argument:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(utilities.Color.PURPLE + "|timer_fired() Processing data request reference {}".format(reference) + utilities.Color.END)
                machinelearning.data_request_postprocess(botengine, self.parent, reference)
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(utilities.Color.PURPLE + "<timer_fired() DATA REQUEST POST-PROCESSING COMPLETE: Processing {} data request references for postprocessing".format(len(argument)) + utilities.Color.END)
        
        elif argument == "schedule":
            # This is the schedule-fired data request timer
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">timer_fired() Requesting data from schedule...")
            machinelearning.request_data(botengine, location_object=self.parent)
        
        else:
            # This is the original data request timer (fallback)
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">timer_fired() Requesting data...")
            machinelearning.request_data(botengine, location_object=self.parent)

    def download_data(self, botengine, content):
        """
        This is data stream message friendly to allow external microservices to request all data for recalculating
        models.

        :param botengine:
        :param content:
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">download_data() content={}".format(content))
        self.version = VERSION

        force = False
        try:
            if 'force' in content:
                force = content['force']
        except:
            pass

        reference = machinelearning.DATAREQUEST_REFERENCE_ALL

        oldest_timestamp_ms = botengine.get_timestamp() - utilities.ONE_MONTH_MS * 6
        if botengine.playback:
            # Reduce the strain on the playback system
            oldest_timestamp_ms = botengine.get_timestamp() - utilities.ONE_WEEK_MS
        if 'oldest_timestamp_ms' in content:
            if content['oldest_timestamp_ms'] is not None:
                oldest_timestamp_ms = int(content['oldest_timestamp_ms'])

                if 'reference' in content:
                    if content['reference'] == machinelearning.DATAREQUEST_REFERENCE_ALL:
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<download_data() oldest_timestamp_ms={} but the reference={}; we won't process this data request because it's dangerous.".format(oldest_timestamp_ms, content['reference']))
                        return

        if 'reference' in content:
            reference = content['reference']

        if (self.last_download < botengine.get_timestamp() - utilities.ONE_HOUR_MS) or (reference != machinelearning.DATAREQUEST_REFERENCE_ALL) or force:
            if reference == machinelearning.DATAREQUEST_REFERENCE_ALL:
                self.last_download = botengine.get_timestamp()

            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|download_data() - Requesting data for reference {}".format(reference))

            # Request all data from devices that capture interesting information
            for device_id in self.parent.devices:
                focused_object = self.parent.devices[device_id]

                # Download any device with a focused measurements parameters list.
                if hasattr(focused_object, 'MEASUREMENT_PARAMETERS_LIST'):
                    focused_object.request_data(botengine, param_name_list=focused_object.MEASUREMENT_PARAMETERS_LIST, oldest_timestamp_ms=oldest_timestamp_ms, reference=reference)

        else:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|download_data() Attempted to download_data(), but we just did so recently so skipping this request.")
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<download_data()")

    def data_request_postprocess(self, botengine, content):
        """
        Data stream message for post-processing data request results.
        
        This method is called when it's safe to post-process data request results.
        During async_data_request_ready() execution, we cannot save class variables, update the dashboard,
        set timers, or do anything that requires core variable access. This data_request_postprocess
        internal data stream message exists to provide a safe environment for post-processing any data
        and drawing conclusions from it, setting timers, updating class variables, etc.
        
        :param botengine: BotEngine environment
        :param content: Reference string for post-processing
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">data_request_postprocess() content={}".format(content))
        
        # The content is the reference string directly
        reference = content
        
        # This is where you can safely post-process the data request results
        # You can now save class variables, set timers, update the dashboard, etc.
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|data_request_postprocess() Post-processing data for reference: {}".format(reference))
        
        # Example: You could set timers, update class variables, or trigger other microservices here
        # self.some_class_variable = some_value
        # self.start_timer_ms(botengine, utilities.ONE_MINUTE_MS * 5, reference="postprocess_followup")
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<data_request_postprocess()")

    def async_data_request_ready(self, botengine, reference, csv_dict):
        """
        A botengine.request_data() asynchronous request for CSV data is ready.

        This is part of a very scalable method to extract large amounts of data from the server for the purpose of
        machine learning services. If a service needs to extract a large amount of data for one or multiple devices,
        the developer should call botengine.request_data(..) and also allow the bot to trigger off of trigger type 2048.
        The bot can exit its current execution. The server will independently gather all the necessary data and
        capture it into a LZ4-compressed CSV file on the server which is available for one day and accessible only by
        the bot through a public HTTPS URL identified by a cryptographic token. The bot then gets triggered and
        downloads the CSV data, passing the data throughout the environment with this async_data_request_ready()
        event-driven method.


        IMPORTANT: This method executes in an asynchronous environment where you are NOT allowed to:
        - Set timers or alarms
        - Manage class variables that persist across executions
        - Perform other stateful operations

        Developers are encouraged to use the 'reference' argument inside calls to botengine.request_data(..). The
        reference is passed back out at the completion of the request, allowing the developer to ensure the
        data request that is now available was truly destined for their microservice.

        CRITICALLY IMPORTANT:
        Data Request triggers operate *concurrently* with other triggers, because typically machine learning
        algorithms take their sweet, sweet time and life must go on. Therefore, **the core variable is not saved** during
        execution of a data request trigger (because otherwise, it would stomp all over the other trigger executions that are
        taking place in the background). That means: YOU CANNOT SAVE CLASS VARIABLES DURING A DATA REQUEST TRIGGER. You must
        save all memory inside explicitly separate variables with botengine.save_variable(..) or botengine.save_shared_variable(..),
        or use tags or states.

        Your bots will need to include the following configuration for data requests to operate:
        * runtime.json should include trigger 2048
        * structure.json should include inside 'pip_install_remotely' a reference to the "lz4" Python package

        :param botengine: BotEngine environment
        :param reference: Optional reference passed into botengine.request_data(..)
        :param csv_dict: { device_object: 'csv data string' }
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">async_data_request_ready() reference={}".format(reference))
        
        if reference == machinelearning.DATAREQUEST_REFERENCE_ALL:
            self.parent.narrate(botengine,
                                title=_("Learning"),
                                description=_("{} is reviewing everything it observed recently and is learning from it.").format(properties.get_property(botengine, "SERVICE_NAME")),
                                priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                                extra_json_dict={ "timestamp_ms": botengine.get_timestamp() },
                                icon="brain",
                                event_type="data_request.ready")

        botengine.save_variable("data_request_timestamp", botengine.get_timestamp())
        analytics.track(botengine, self.parent, "data_request_ready", properties={"reference": reference})

        for d in csv_dict:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|async_data_request_ready() {} = {} bytes".format(d, len(csv_dict[d])))

            if EXPORT_CSV_TO_LOCAL_FILES:
                filename = "{}_{}.csv".format(d.device_id, d.device_type)
                with open(filename, "w") as text_file:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|async_data_request_ready() Saving CSV data to {} ...".format(filename))
                    text_file.write(csv_dict[d])

        # Split-phase logic: Store reference for post-processing
        # Load existing postprocess list (might be None or a list)
        postprocess_list = botengine.load_variable(DATA_REQUEST_POSTPROCESS)
        if postprocess_list is None:
            postprocess_list = []
        
        # Add the current reference if it's not already in the list (no duplicates)
        if reference not in postprocess_list:
            postprocess_list.append(reference)
        
        # Save the updated list for post-processing
        botengine.save_variable(DATA_REQUEST_POSTPROCESS, postprocess_list)
        botengine.async_execute_again_in_n_seconds(90)

        # It is up to the developer to capture the async_data_request_ready(..) event in their own microservice
        # and verify the reference is 'all', then do something with all this data.
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<async_data_request_ready()")