'''
Created on October 21, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from filters.filter import Filter

import utilities.utilities as utilities

class FilterExampleMicroservice(Filter):
    """
    Example data filter.
    Pay attention to the filter_measurements() event which is unique to filters,
    see how to correct data in place before that data is absorbed into our device models and device+location microservices,
    and understand the get_parameter() helper method provided by the parent Filter class.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Filter.__init__(self, botengine, parent)

        # Recent RSSI values to create a low-pass filter (moving average)
        self.rssi = []

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        botengine.get_logger().info("Filter: new_version()")
        return

    def initialize(self, botengine):
        """
        Initialize on every bot execution.
        :param botengine: BotEngine environment
        """
        botengine.get_logger().info("Filter: initialize()")
        return

    def destroy(self, botengine):
        """
        This object is getting permanently deleted. Clean up.
        :param botengine: BotEngine environment
        """
        botengine.get_logger().info("Filter: destroy()")
        return

    def filter_measurements(self, botengine, device_object, measurements):
        """
        Optionally filter device measurement data before it reaches the upper layers of the stack.

        Use self.get_parameter(measurements, name, index=None) to extract a specific parameter, then
        edit the measurements_dict directly in place.

        Example measurements:
            [
                {
                    "deviceId": "63a5f00e006f0d00",
                    "name": "power",
                    "time": 1608748576694,
                    "updated": true,
                    "value": "0.2"
                },
                {
                    "deviceId": "63a5f00e006f0d00",
                    "name": "energy",
                    "time": 1634866106490,
                    "updated": false,
                    "value": "34.8459829801"
                }
            ]

        :param botengine: BotEngine environment
        :param device_object: Device object pending update
        :param measurements_dict: Measurements dictionary we're about to trigger off of, which is modified in place.
        """
        import json
        botengine.get_logger().info("Filter: filter_measurements()")
        botengine.get_logger().info("Filter: Original measurements = {}".format(json.dumps(measurements, sort_keys=True)))

        # EXAMPLE of changing a parameter's value. Here we apply a low-pass filter to the data.
        # This retrieves the measurement dictionary for this parameter name, using our super class's "get_parameter()" method.
        measured_rssi = self.get_parameter(measurements, "rssi")

        if measured_rssi is None:
            return

        # Here's the actual value. We'll print this out later and compare the original vs. new.
        rssi_value = measured_rssi['value']

        # Insert the current measurement into the beginning of our list
        self.rssi.insert(0, rssi_value)

        # Don't let the list get too long
        del self.rssi[20:]

        # Find the mean of the values in the list, round it to 1 decimal place.
        from statistics import mean
        measured_rssi['value'] = round(mean(self.rssi), 1)

        # Here's some output for you to look at when you --run a bot with this filter.
        botengine.get_logger().info(utilities.Color.GREEN + "Filter: Transformed measured RSSI {} into low-pass RSSI {}".format(rssi_value, measured_rssi['value']) + utilities.Color.END)
        botengine.get_logger().info("Filter: Corrected rssi = {}".format(json.dumps(self.get_parameter(measurements, "rssi"), sort_keys=True)))

        # EXAMPLE of ignoring a parameter's updated value completely.
        if self.get_parameter(measurements, "lqi"):
            self.get_parameter(measurements, "lqi")['updated'] = False

        return

    def data_request_ready(self, botengine, reference, csv_dict):
        """
        Edit the data request results directly in place.

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
        botengine.get_logger().info("Filter: data_request_ready()")
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