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
from devices.health.health_withings_sleep import WithingsSleepHealthDevice
from devices.health.health import HealthDevice

# For debugging, export CSV data to local files
EXPORT_CSV_TO_LOCAL_FILES = False

# Timer reference to avoid overlapping timers
TIMER_REFERENCE = "dr"

# Version
VERSION = 1.0

# Only download device types that our machine learning services currently do something with.
DOWNLOAD_FOCUSED_DEVICES_ONLY = True

class LocationDataRequestMicroservice(Intelligence):
    """
    This module is responsible for waking up at least once weekly, downloading data, and distributing the shared data
    throughout the various microservices to allow machine learning models to be created efficiently.

    The result will be a data_request_ready() event with a reference "all", which other microservices can listen for
    to reproduce machine learning models.
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
                
            self.start_timer_ms(botengine, random.randint(0, utilities.ONE_HOUR_MS * 12), reference=TIMER_REFERENCE)

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
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

                if DOWNLOAD_FOCUSED_DEVICES_ONLY:
                    # Download focused devices only based on the list below.
                    if isinstance(focused_object, MotionDevice) or isinstance(focused_object, EntryDevice) or isinstance(focused_object, PressurePadDevice) or isinstance(focused_object, RadarDevice) or isinstance(focused_object, HealthDevice) or isinstance(focused_object, WithingsSleepHealthDevice):
                        focused_object.request_data(botengine, param_name_list=focused_object.MEASUREMENT_PARAMETERS_LIST, oldest_timestamp_ms=oldest_timestamp_ms, reference=reference)

                else:
                    # Download any device with a focused measurements parameters list.
                    if hasattr(focused_object, 'MEASUREMENT_PARAMETERS_LIST'):
                        focused_object.request_data(botengine, param_name_list=focused_object.MEASUREMENT_PARAMETERS_LIST, oldest_timestamp_ms=oldest_timestamp_ms, reference=reference)

        else:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|download_data() Attempted to download_data(), but we just did so recently so skipping this request.")
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<download_data()")

    def data_request_ready(self, botengine, reference, csv_dict):
        """
        A botengine.request_data() asynchronous request for CSV data is ready.

        This is part of a very scalable method to extract large amounts of data from the server for the purpose of
        machine learning services. If a service needs to extract a large amount of data for one or multiple devices,
        the developer should call botengine.request_data(..) and also allow the bot to trigger off of trigger type 2048.
        The bot can exit its current execution. The server will independently gather all the necessary data and
        capture it into a LZ4-compressed CSV file on the server which is available for one day and accessible only by
        the bot through a public HTTPS URL identified by a cryptographic token. The bot then gets triggered and
        downloads the CSV data, passing the data throughout the environment with this data_request_ready()
        event-driven method.

        Developers are encouraged to use the 'reference' argument inside calls to botengine.request_data(..). The
        reference is passed back out at the completion of the request, allowing the developer to ensure the
        data request that is now available was truly destined for their microservice.

        CRITICALLY IMPORTANT:
        Data Request triggers operate *concurrently* with other triggers, because typically machine learning
        algorithms take their sweet, sweet time and life must go on. Therefore, **the core variable is not saved** during
        execution of a data request trigger (because otherwise, it would stomp all over the other trigger executions that are
        taking place in the background). That means: YOU CANNOT SAVE CLASS VARIABLES DURING A DATA REQUEST TRIGGER. You must
        save all memory inside explicitly separate variables with botengine.save_variable(..) or botengine.save_shared_variable(..).


        Your bots will need to include the following configuration for data requests to operate:
        * runtime.json should include trigger 2048
        * structure.json should include inside 'pip_install_remotely' a reference to the "lz4" Python package

        :param botengine: BotEngine environment
        :param reference: Optional reference passed into botengine.request_data(..)
        :param csv_dict: { device_object: 'csv data string' }
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">data_request_ready() reference={}".format(reference))
        
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
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|data_request_ready() {} = {} bytes".format(d, len(csv_dict[d])))

            if EXPORT_CSV_TO_LOCAL_FILES:
                filename = "{}_{}.csv".format(d.device_id, d.device_type)
                with open(filename, "w") as text_file:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|data_request_ready() Saving CSV data to {} ...".format(filename))
                    text_file.write(csv_dict[d])


        # It is up to the developer to capture the data_request_ready(..) event in their own microservice
        # and verify the reference is 'all', then do something with all this data.
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<data_request_ready()")