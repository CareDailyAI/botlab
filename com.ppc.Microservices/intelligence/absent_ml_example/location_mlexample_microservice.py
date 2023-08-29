'''
Created on March 1, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence
from devices.motion.motion import MotionDevice
from devices.entry.entry import EntryDevice
import utilities

# You would have your own machine learning implementation here.
import intelligence.ml_example.ml_engine_example as ml

# List of minutes that we should evaluate for away mode activity
EVALUATION_INTERVALS_IN_MINUTES = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

# Minimum confidence threshold that must be met to go into internal AWAY mode
# This should ideally be different for different users, based on feedback.
# If we predict that the user is away and then it turns out they're not, turn this up.
# If we constantly hit the max amount of time before predicting the user is away, turn this down.
AWAY_CONFIDENCE_THRESHOLD = 0.7

# Maximum confidence threshold
MAX_AWAY_CONFIDENCE_THRESHOLD = 0.85

# Minimum confidence threshold
MIN_AWAY_CONFIDENCE_THRESHOLD = 0.4

# Minimum confidence threshold that must be met to go into internal H2A mode
H2A_CONFIDENCE_THRESHOLD = 0.1

# Amount to adjust the away mode confidence threshold by when we make a mistake or reach the peak
AWAY_CONFIDENCE_THRESHOLD_INCREMENT = 0.05

# Minimum number of motion sensors required for away mode machine learning algorithms to work and be applied. Otherwise we have to wait for the final length of time defined in EVALUATION_INTERVALS_IN_MINUTES.
MINIMUM_NUMBER_OF_MOTION_SENSORS_FOR_AWAY_ML_ALGORITHMS = 2

# Non-volatile variable name used to store the ML model
VARIABLE_ABSENT_MODELS = "absent_models"

# Timer reference - evaluate whether the family is absent.
HOME_AWAY_EVALUATION_REFERENCE = "ha"

# Timer reference - force the location into an absent state.
FORCE_AWAY_REFERENCE = "fa"

# Data stream message reason why the mode changed - ML algorithm made the change
ML_ALGORITHM_MODE_CHANGE = "ML"

# The user changed the mode
USER_ALGORITHM_MODE_CHANGE = "USER"

# Data stream message reason why the mode changed - The last mode change was a mistake and the ML algorithm is trying to fix that mistake
ML_ALGORITHM_FIXING_MISTAKE = "MISTAKE"


# We rely upon Space identification to classify and ignore 'naughty' sensors, defined at installation of the sensor.
# But we also don't always trust end users to set up the service correctly.
# So as a fallback, we use the descriptive names of the sensors as context to
# ignore blatently obvious entry sensors that are not on the perimeter of the home.
NAUGHTY_ENTRY_SENSOR_NAMES = ['fridge', 'cabinet', 'bath', 'refri', 'freez']

# Location Tags for customer support activities
AWAY_ML_SUCCESS = "away_ml_success"
AWAY_ML_FAILURE = "away_ml_fail"
NOT_ENOUGH_MOTION_SENSOR_TAG = "not_enough_motion_sensors"

class LocationMlExampleMicroservice(Intelligence):
    """
    Example machine learning algorithm infrastructure.

    This will show some basic infrastructure around an ABSENT detection occupancy sensing machine learning service.

    The basic concept behind ABSENT classification is this:  assume the primary entrances to the home are instrumented
    with entry sensors, and assume there are a couple motion sensors in the home to detect activity. When a door
    closes, either there's someone in the house or there's not. Spend about 15 minutes seeing if there's motion
    activity. Then, if there's no motion to indicate the house is occupied, start asking the machine learning
    algorithm what it thinks on the schedule defined by the EVALUATION_INTERVALS_IN_MINUTES variable above.
    There could be someone asleep in bed where there are no sensors, so the machine learning algorithms fill in the
    gaps in the data.

    IMPORTANT: This microservice is not meant to be completely functional, but serves as a reference of what we should
    think about and how we should structure code as we develop machine learning services. We're simply showing the base
    infrastructure and best practices to implement machine learning algorithms that safely regenerate models each week,
    custom-tailored for the specific family that lives at this Location.

    Your bot should include the 'data_request' microservice package in its structure.json. This will wake up about
    once per week and download all data from a Location. The data is then passed around to all microservices through the
    data_request_ready() event.  The 'data_request' microservice package uses a reference 'all' for its data requests,
    so when the data_request_ready() event fires, you can check the reference to see if this data request includes
    all data from the location as requested by the 'data_request' microservice package.

    Some machine learning developers choose to preprocess the raw CSV data before building models. For example,
    you may take the data you're interested in, and merge it together into a single chronological narrative. While
    we're not showing this preprocess step here, you could assume it would take place in the ml_engine_example.py.

    Note the structure.json file in this microservice package includes scipy, numpy, and sklearn packages, which
    would normally be an important set of tools for most machine learning services.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # List of durations, in minutes, that were used in the generation of our decision models. For example, [15, 30, 45]
        # These are the amounts of time after a door closes that we wait to evaluate whether the house is occupied.
        self.durations = None

        # Specific duration index we're focused on right now
        self.focused_duration_index = 0

        # Away confidence threshold which we can dial up and down like a knob to make the ML algorithms more discerning
        self.away_confidence_threshold = AWAY_CONFIDENCE_THRESHOLD

        # Reference the the last door closed object
        self.last_door_closed_object = None

        # First boot - request all existing data from this location to generate initial models.
        # This data stream message is picked up by the 'data_request' microservice package, and will later
        # result in the data_request_ready() event triggering below.
        self.parent.distribute_datastream_message(botengine, 'download_data')

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
        # This microservice is getting destroyed, so remove its non-volatile memory so we don't end up
        # with zombie wasted space.
        botengine.delete_variable(VARIABLE_ABSENT_MODELS)

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
        if isinstance(device_object, EntryDevice):
            # Door opened or closed
            if not self._is_entry_sensor_naughty(botengine, device_object):
                if device_object.did_close(botengine):
                    # Door closed
                    self.focused_duration_index = 0
                    self.door_closed_timestamps_ms = botengine.get_timestamp()
                    self.last_door_closed_object = device_object
                    self.start_timer_s(botengine, self._calculate_next_duration(botengine), argument=[HOME_AWAY_EVALUATION_REFERENCE, device_object], reference=HOME_AWAY_EVALUATION_REFERENCE)

        elif isinstance(device_object, MotionDevice):
            # Motion detected or not
            if device_object.did_start_detecting_motion(botengine):
                # Motion detected
                if self.is_timer_running(botengine, reference=HOME_AWAY_EVALUATION_REFERENCE) or self.is_timer_running(botengine, reference=FORCE_AWAY_REFERENCE):
                    botengine.get_logger().info("location_mlexample_microservice: '{}' detected motion. Canceling the away detection timer.".format(device_object.description))
                    self.cancel_timers(botengine, reference=HOME_AWAY_EVALUATION_REFERENCE)
                    self.cancel_timers(botengine, reference=FORCE_AWAY_REFERENCE)

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

        # First we're going to tag accounts that don't have enough sensors for this machine learning service to operate.
        motion_devices = 0
        for device_id in self.parent.devices:
            motion_devices += isinstance(self.parent.devices[device_id], MotionDevice)

        if motion_devices < MINIMUM_NUMBER_OF_MOTION_SENSORS_FOR_AWAY_ML_ALGORITHMS:
            if not NOT_ENOUGH_MOTION_SENSOR_TAG in self.tags:
                # Not enough motion sensors for away mode detection - Tag it and end
                botengine.tag_location(NOT_ENOUGH_MOTION_SENSOR_TAG)
                self.tags.append(NOT_ENOUGH_MOTION_SENSOR_TAG)
                return

            elif NOT_ENOUGH_MOTION_SENSOR_TAG in self.tags:
                # There are enough motion sensors and it was previously tagged - remove the tag and continue
                botengine.delete_location_tag(NOT_ENOUGH_MOTION_SENSOR_TAG)
                self.tags.remove(NOT_ENOUGH_MOTION_SENSOR_TAG)

        # Next let's evaluate whether the occupant is home or away.
        # Note that there are 2 arguments passed into the timer in this case,
        # so we're looking to argument[0] for the action we want to perform, and argument[1] is extra context.
        if argument[0] == HOME_AWAY_EVALUATION_REFERENCE:
            # Evaluate whether the user is absent
            import numpy as np

            # Extract a relative hour of the day feature for our ML prediction
            relative_hour_of_day = self.parent.get_local_hour_of_day(botengine)

            # Extract a day-of-the-week feature for our ML prediction
            day_of_week = self.parent.get_local_day_of_week(botengine)

            # Download our absent models from non-volatile memory
            absent_models = botengine.load_variable(VARIABLE_ABSENT_MODELS)

            # The argument[1] contains the last door closed object
            last_door_closed_object = argument[1]

            # Grab a specific model for the amount of time that has elapsed
            focused_model = absent_models[self.focused_duration_index]

            # Initial probability that this user is absent - set low but greater than 0.0.
            probability_absent = H2A_CONFIDENCE_THRESHOLD

            try:
                # Call your machine learning algorithm with the latest features and the model we're comparing against.
                probability_absent = ml.get_prediction_value(
                    relative_hour_of_day,
                    day_of_week,
                    last_door_closed_object,
                    focused_model)

                # Track the results in your favorite analytics tool
                self.parent.track(botengine, 'probability_absent', properties={"probability": probability_absent})

                # See the results on your command line terminal
                botengine.get_logger().info("location_mlexample_microservice: {} probability that the user is absent".format(probability_absent))

            except Exception as e:
                botengine.get_logger().warn("location_mlexample_microservice : Cannot get absent prediction. " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

            # Is the probability that the user is away greater than our current confidence threshold?
            # The confidence threshold acts like a knob that can go up and down to tune itself to this
            # user's account as we learn whether our predictions were right or wrong.
            if probability_absent >= self.away_confidence_threshold:
                # You appear to be away now
                if "ABSENT" not in self.parent.occupancy_status:
                    self._announce_occupancy(botengine, "ABSENT", ML_ALGORITHM_MODE_CHANGE)
                    return

            elif probability_absent >= H2A_CONFIDENCE_THRESHOLD:
                # You might be transitioning into absent mode
                # Check again soon.
                # We use the term "H2A" as a transitionary state to represent home-to-absent.
                # It's to say 'We're not really sure if the person is away yet, but maybe.."
                # There are some useful things that can be done here, like slowly dialing down the thermostat to
                # save energy.
                if "H2A" not in self.parent.occupancy_status:
                    self._announce_occupancy(botengine, "H2A", ML_ALGORITHM_MODE_CHANGE)


            # If we got this far, we're still evaluating whether the person is home or away.
            # We increase the index of which self.durations interval we're going to evaluate next, so
            # we can go from 15 minutes to 20 minutes to 25 minutes, etc. and test the the model each step of the way.
            self.focused_duration_index += 1

            if self.focused_duration_index <= len(self.durations) - 1:
                # Set a timer to keep evaluating at the next prescribed duration of time.
                self.start_timer_s(botengine, self._calculate_next_duration(botengine),
                                   argument=[HOME_AWAY_EVALUATION_REFERENCE, last_door_closed_object],
                                   reference=HOME_AWAY_EVALUATION_REFERENCE)

            else:
                # Okay, we ran out of machine learning models (or never had any to begin with).
                #
                # It's been a really long time. We haven't seen any activity in the home to indicate someone is there.
                # Let's make an application-layer decision to force this location into an 'absent' occupancy status
                # after another 15 minutes passes with no activity.
                self.start_timer_s(botengine, 60 * 15, argument=[FORCE_AWAY_REFERENCE], reference=FORCE_AWAY_REFERENCE)

        elif argument[0] == FORCE_AWAY_REFERENCE:
            # We've gone over our limit to evaluate if the user is home or absent.
            # We gave up. The machine learning algorithms weren't able to make a decision.
            # Let's make an application-layer decision to just force this user into an absent occupancy status because
            # it has been so long...
            if "ABSENT" not in self.parent.occupancy_status:
                # Dial down the threshold for next time so we can try to be more aggressive.
                self.away_confidence_threshold -= AWAY_CONFIDENCE_THRESHOLD_INCREMENT
                if self.away_confidence_threshold < MIN_AWAY_CONFIDENCE_THRESHOLD:
                    self.away_confidence_threshold = MIN_AWAY_CONFIDENCE_THRESHOLD

                self._announce_occupancy(botengine, "ABSENT", ML_ALGORITHM_MODE_CHANGE)

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

    def user_role_updated(self, botengine, user_id, alert_category, location_access, previous_alert_category,
                          previous_location_access):
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
        if reference == "all":
            # This is a data request response that was driven by the 'data_request' microservice package.
            # This typically fires once per week, but could fire more often if requested through
            # a data stream message with the 'download_data'.

            # We can update the definition of EVALUATION_INTERVALS_IN_MINUTES any time, without
            # affecting the operation of ML models that have already been generated. Here, we take
            # a snapshot of the current evaluation intervals we're going to be building machine learning
            # models around.
            self.durations = EVALUATION_INTERVALS_IN_MINUTES

            try:
                # Here we calculate the models based on all the data passed in.
                # There is effectively one model calculated per duration of time.
                # Underneath, you would implement algorithms to take this raw data and convert it into
                # models, using whatever machine learning tools you believe are appropriate for this task.
                absent_models = ml.generate_prediction_models(csv_dict, self.durations)

                # Now save the model. The model can potentially get quite large, and we do not need it for every
                # execution of the bot. Therefore it's a perfect candidate to store in its own variable direct
                # through the botengine environment, instead of as a class variable locally here which would
                # have to get downloaded with every trigger and execution of the bot.
                botengine.save_variable(VARIABLE_ABSENT_MODELS, absent_models)

                # Let's see how big the model got.
                size = utilities.getsize(absent_models)
                botengine.get_logger().info("sizeof(home_away_model) = {}".format(size))

                # Let's track the results to our analytics tools of choice.
                self.parent.track(botengine, 'away_model_calculated', properties={"sizeof": size, "durations": self.durations})

                # Let's tag this Location so we can see as administrators through the Maestro Command Center
                # whether this Location was successful at generating models or not.
                botengine.delete_location_tag(AWAY_ML_FAILURE)
                botengine.tag_location(AWAY_ML_SUCCESS)

            except utilities.MachineLearningError as e:
                # Your ML tools down below should raise a MachineLearningError when they can't converge on a solution,
                # possibly because there's not enough data.

                # Tag the Location as having a problem generating models.
                botengine.delete_location_tag(AWAY_ML_SUCCESS)
                botengine.tag_location(AWAY_ML_FAILURE)
                return

            except Exception as e:
                # Some strange exception
                # Look for errors like this so you can fix them:  ./botengine --errors com.you.Bot
                botengine.get_logger().warn("location_mlexample_microservice : Cannot create absent model. " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())

                # Tag the Location as having a problem generating models.
                botengine.delete_location_tag(AWAY_ML_SUCCESS)
                botengine.tag_location(AWAY_ML_FAILURE)
                return

            botengine.get_logger().info("location_mlexample_microservice: Done generating absent models")

        return

    def _is_entry_sensor_naughty(self, botengine, device_object):
        """
        Return True if the entry sensor device is naughty and should be ignored
        :param device_object:
        :return:
        """
        if not device_object.is_goal_id(EntryDevice.GOAL_PERIMETER_NORMAL) and not device_object.is_goal_id(EntryDevice.GOAL_PERIMETER_ALERT_ALWAYS):
            botengine.get_logger().info("location_mlexample_microservice: Entry sensor {} is not on the perimeter and will be ignored.".format(device_object.description))
            return True

        for name in NAUGHTY_ENTRY_SENSOR_NAMES:
            if name in device_object.description.lower():
                botengine.get_logger().info("location_mlexample_microservice: Entry sensor {} has a naughty name and will be ignored.".format(device_object.description))
                return True

        return False

    def _calculate_next_duration(self, botengine):
        """
        Calculate the next duration of time, in seconds, that we wait before re-evaluating whether the family is away.
        :param botengine:
        :return: relative time in seconds to wait
        """
        if self.focused_duration_index == 0:
            return self.durations[0] * 60

        return (self.durations[self.focused_duration_index] - self.durations[self.focused_duration_index - 1]) * 60

    def _announce_occupancy(self, botengine, status, reason):
        """
        Announce the mode change internally to other microservices
        :param botengine: BotEngine environment
        :param mode: New mode
        :param reason: "ML" if the machine learning algorithm changed the mode, or "MISTAKE" if the machine learning algorithm is correcting its mistake in the previous state change
        """
        # This would go to another service that arbitrates between multiple individual microservice's recommendations
        # about what the occupancy status should be.
        self.parent.distribute_datastream_message(botengine, "occupancy_recommendation", { "status": status, "reason": reason, "source": "AWAY" }, internal=True, external=False)
