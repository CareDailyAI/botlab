
from botengine_pytest import BotEnginePyTest

from devices.motion.motion import MotionDevice
from devices.entry.entry import EntryDevice
from devices.vayyar.vayyar import VayyarDevice

from locations.location import Location

CURRENT_TEST_DOOR_OPEN = 0
CURRENT_TEST_MOTION_DETECT = 1
CURRENT_TEST_DOOR_CLOSE = 2
CURRENT_TEST_VAYYAR = 3

class TestLastSeenMicroservice():

    def setup_method(self):
        # Current test we're running
        self.current_test = None

        self.botengine = BotEnginePyTest({})

        self.botengine.reset()
        self.botengine.set_trigger_type(1)

        # Initialize the location
        self.location = Location(self.botengine, 0)

        self.motion = MotionDevice(self.botengine, self.location, "motion_id_1", 0, "Test Toilet Motion")
        self.motion.initialize(self.botengine)

        self.entry = EntryDevice(self.botengine, self.location, "entry_id_1", "10014", "Test Entry")
        self.entry.initialize(self.botengine)

        self.vayyar = VayyarDevice(self.botengine, self.location, "vayyar_id_1", 0, "Vayyar Device", precache_measurements=False)
        self.vayyar.born_on = 0
        self.location.devices[self.entry.device_id] = self.entry
        self.location.devices[self.motion.device_id] = self.motion
        self.location.devices[self.vayyar.device_id] = self.vayyar

        # Start up the bot
        self.location.new_version(self.botengine)
        self.location.initialize(self.botengine)

        # Add our custom microservices after we initialize the location so these don't get auto-deleted...
        self.location.intelligence_modules["unit_test_module"] = self

        self.lastseen_intelligence = self.location.intelligence_modules["intelligence.last_seen.location_lastseen_microservice"]

    def test_door_open_lastseen(self):
        self.current_test = CURRENT_TEST_DOOR_OPEN
        measurements = [{'deviceId': 'entry_id_1', 'updated': True, 'name': 'doorStatus', 'value': True, 'time': self.botengine.get_timestamp() - 1000}]
        self.entry.update(self.botengine, measurements)

    def test_motion_detect_lastseen(self):
        self.current_test = CURRENT_TEST_MOTION_DETECT
        measurements = [{'deviceId': 'motion_id_1', 'updated': True, 'name': 'motionStatus', 'value': 1, 'time': self.botengine.get_timestamp() - 1000}]
        self.motion.update(self.botengine, measurements)

    def test_door_close_lastseen(self):
        self.current_test = CURRENT_TEST_DOOR_CLOSE
        measurements = [{'deviceId': 'entry_id_1', 'updated': True, 'name': 'doorStatus', 'value': False, 'time': self.botengine.get_timestamp() - 1000}]
        self.entry.update(self.botengine, measurements)

    def test_vayyar_lastseen(self):
        self.current_test = CURRENT_TEST_VAYYAR
        self.lastseen_intelligence.knowledge_did_update_vayyar_occupants(self.botengine, self.vayyar, None)

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        if hasattr(self, address):
            getattr(self, address)(botengine, content)

    def capture_insight(self, botengine, insight_json):
        botengine.get_logger().info("location_lastseen_microservice: test {}".format(insight_json))

        if self.current_test == CURRENT_TEST_DOOR_OPEN or self.current_test == CURRENT_TEST_DOOR_CLOSE:
            assert self.lastseen_intelligence.last_observed_motion_object == self.entry

        elif self.current_test == CURRENT_TEST_MOTION_DETECT:
            assert self.lastseen_intelligence.last_observed_motion_object == self.motion

        elif self.current_test == CURRENT_TEST_VAYYAR:
            assert insight_json["device_id"] == self.vayyar.device_id

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

    def user_role_updated(self, botengine, user_id, role, alert_category, location_access, previous_alert_category, previous_location_access):
        """
        A user changed roles
        :param botengine: BotEngine environment
        :param user_id: User ID that changed roles
        :param role: Application-layer agreed upon role integer which may auto-configure location_access and alert category
        :param alert_category: User's current alert/communications category (1=resident; 2=supporter)
        :param location_access: User's access to the location and devices. (0=None; 10=read location/device data; 20=control devices and modes; 30=update location info and manage devices)
        :param previous_alert_category: User's previous category, if any
        :param previous_location_access: User's previous access to the location, if any
        """
        return

    def call_center_updated(self, botengine, user_id, status):
        """
        Emergency call center status has changed.

            0 = Unavailable
            1 = Available, but the user does not have enough information to activate
            2 = Registration pending
            3 = Registered and activated
            4 = Cancellation pending
            5 = Cancelled

        :param botengine: BotEngine environment
        :param user_id: User ID that made the change
        :param status: Current call center status
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


    def track_statistics(self, botengine, time_elapsed_ms):
        pass