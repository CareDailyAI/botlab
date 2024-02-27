'''
Created on January 23, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence

# State variabe name
MULTISTREAM_STATE_VARIABLE = "multistream"

class LocationMultistreamMicroservice(Intelligence):
    """
    Implements a multi-stream message - a single data stream message containing multiple data stream messages.
    Including the ability to time-shift the delivery and execution of the messages until later.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # Initialize our 'multistream' state variable
        self.parent.set_location_property_separately(botengine, MULTISTREAM_STATE_VARIABLE, {}, overwrite=True)


    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        return

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        return

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        return

    def occupancy_status_updated(self, botengine, status, reason, last_status, last_reason):
        """
        AI Occupancy Status updated
        :param botengine: BotEngine
        :param status: Current occupancy status
        :param reason: Current occupancy reason
        :param last_status: Last occupancy status
        :param last_reason: Last occupancy reason
        """
        return

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
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

    def device_added(self, botengine, device_object):
        """
        A new Device was added to this Location
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting added
        """
        return

    def device_deleted(self, botengine, device_object):
        """
        Device is getting deleted
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting deleted
        """
        return

    def question_answered(self, botengine, question_object):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question_object: Question object
        """
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
        return

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        multistream_queue = botengine.get_state(MULTISTREAM_STATE_VARIABLE)

        for id in list(multistream_queue.keys()):
            if multistream_queue[id]['timestamp'] <= botengine.get_timestamp():
                # Add the ID back into the content before submitting the multistream message again
                # These will get automatically deleted from our queue as they execute in self.multistream()
                content = multistream_queue[id]
                content['id'] = id
                self.multistream(botengine, content)

        self._set_alarm(botengine)

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

    def user_role_updated(self, botengine, user_id, role, alert_category, location_access, previous_alert_category, previous_location_access):
        """
        A user changed roles
        :param botengine: BotEngine environment
        :param user_id: User ID that changed roles
        :param alert_category: User's current alert/communications category (1=resident; 2=supporter)
        :param location_access: User's access to the location and devices. (0=None; 10=read location/device data; 20=control devices and modes; 30=update location info and manage devices)
        :param previous_alert_category: User's previous category, if any
        :param previous_location_access: User's previous access to the location, if any
        """
        return

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
        return

    def multistream(self, botengine, content):
        """
        Accepts a 'multistream' message and either queues it up for delivery later, or delivers it now.

        {
          "timestamp": Optional timestamp in milliseconds to queue these messages up for later,
          "id": Optional unique ID to later update/edit/delete queued messages. If this is left out, then queued messages will generate their own ID
          "address_0": { content_0 },    # Data stream message
          "address_1": { content_1 },    # Data stream message
        }

        :param botengine:
        :param content:
        :return:
        """
        if content is None:
            return

        id = None
        if 'id' in content:
            id = str(content['id'])
            del(content['id'])

        if 'timestamp' in content:
            timestamp_ms = int(content['timestamp'])
            if timestamp_ms > botengine.get_timestamp():
                # Queue it up for later
                if id is None:
                    import uuid
                    id = str(uuid.uuid4())
                    # The ID is not stored in the content, it's stored as the key in the multistream_queue dictionary.

                multistream_queue = botengine.get_state(MULTISTREAM_STATE_VARIABLE)
                if multistream_queue is None:
                    multistream_queue = {}

                multistream_queue[id] = content

                # Save the state variable
                self.parent.set_location_property_separately(botengine, MULTISTREAM_STATE_VARIABLE, multistream_queue, overwrite=True)
                self._set_alarm(botengine)
                return

        # Deliver immediately
        # First delete the object from our queue if the ID exists in our queue
        if id is not None:
            multistream_queue = botengine.get_state(MULTISTREAM_STATE_VARIABLE)
            if multistream_queue is not None:
                if id in multistream_queue:
                    del multistream_queue[id]
                    self.parent.set_location_property_separately(botengine, MULTISTREAM_STATE_VARIABLE, multistream_queue, overwrite=True)

        for address in content:
            if address != "timestamp" and address != "id":
                botengine.get_logger().info("location_multistream_microservice: Delivering data stream message '{}'".format(address))
                self.parent.distribute_datastream_message(botengine, address, content[address], internal=True, external=False)

    def _set_alarm(self, botengine):
        """
        Find the next queued event to trigger and set an alarm for it.
        :param botengine:
        :return:
        """
        multistream_queue = botengine.get_state(MULTISTREAM_STATE_VARIABLE)

        # Pick the next closest timestamp
        next_timestamp_ms = None
        for queue_id in list(multistream_queue.keys()):
            if 'timestamp' not in multistream_queue[queue_id]:
                botengine.get_logger().error("location_multistream_microservice: Found a saved multistream queue element that doesn't have a timestamp: {}".format(multistream_queue[queue_id]))
                del multistream_queue[queue_id]
                self.parent.set_location_property_separately(botengine, MULTISTREAM_STATE_VARIABLE, multistream_queue, overwrite=True)

            if next_timestamp_ms is None:
                next_timestamp_ms = multistream_queue[queue_id]['timestamp']

            elif multistream_queue[queue_id]['timestamp'] < next_timestamp_ms:
                next_timestamp_ms = multistream_queue[queue_id]['timestamp']

        if next_timestamp_ms is not None:
            self.set_alarm(botengine, next_timestamp_ms)

