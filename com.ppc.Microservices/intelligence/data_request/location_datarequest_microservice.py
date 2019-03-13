'''
Created on February 1, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence
import utilities

# Reference to use when requesting data so we know the response is ours
DATA_REQUEST_REFERENCE = "all"

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

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        if self.last_download == 0:
            self.request_all_data(botengine)

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
            self.start_timer_ms(botengine, random.randint(0, utilities.ONE_HOUR_MS * 6))

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        self.request_all_data(botengine)

    def download_data(self, botengine, content=None):
        """
        This is data stream message friendly to allow external microservices to request all data for recalculating
        models.

        :param botengine:
        :param content:
        :return:
        """
        self.last_recalculation = botengine.get_timestamp()
        botengine.get_logger().info("location_datarequest_microservice.download_data() - Requesting data")

        # Request all data from devices that capture interesting information
        for device_id in self.parent.devices:
            focused_object = self.parent.devices[device_id]
            if hasattr(focused_object, 'MEASUREMENT_PARAMETERS_LIST'):
                focused_object.request_data(botengine, param_name_list=focused_object.MEASUREMENT_PARAMETERS_LIST, reference=DATA_REQUEST_REFERENCE)

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

        Your bots will need to include the following configuration for data requests to operate:
        * runtime.json should include trigger 2048
        * structure.json should include inside 'pip_install_remotely' a reference to the "lz4" Python package

        :param botengine: BotEngine environment
        :param reference: Optional reference passed into botengine.request_data(..)
        :param csv_dict: { device_object: 'csv data string' }
        """
        if reference == DATA_REQUEST_REFERENCE:
            botengine.get_logger().info("Data request received. reference={}".format(reference))

            for d in csv_dict:
                botengine.get_logger().info("{} = {} bytes".format(d, len(csv_dict[d])))

        # It is up to the developer to capture the data_request_ready(..) event in their own microservice
        # and verify the reference is 'all', then do something with all this data.