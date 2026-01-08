'''
Created on August 23, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence

import utilities.utilities as utilities
import signals.analytics as analytics
import properties

# Timer references
TIMER_REFERENCE_BIRTH = "birth"
TIMER_REFERENCE_INSTALL = "install"

# Total number of devices we expect you to have minimum before we suggest you reach out to customer support for an assisted install session
TOTAL_MINIMUM_DEVICES = 4

class LocationWelcomeMicroservice(Intelligence):
    """
    Add a narrative (history) that welcomes people to the app.
    Send a welcome SMS with instructions on how to download the app 5 minutes after creation.

    We can customize the welcome message per brand by adding an "IN_APP_WELCOME_MESSAGE" to the domain.py file.

    This stores the state in the location_properties so this message is only injected once over the lifetime of the location, even if the bot gets swapped out multiple times.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # NOTE: AI Bot started / rebooted. (machine readable)
        analytics.track(botengine, self.parent, "reset")

        # NOTE: AI Bot started / rebooted. (human readable)
        self.parent.narrate(botengine,
                            title=_("Reset"),
                            description=_("The AI bot has rebooted."),
                            priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                            icon="power-off",
                            event_type="welcome.reset")

        welcomed = self.parent.get_location_property(botengine, "welcomed")

        if welcomed is None:
            welcomed = False

        if not welcomed:
            if properties.get_property(botengine, "SERVICE_NAME") is not None:
                title = _("Welcome to {}").format(properties.get_property(botengine, "SERVICE_NAME"))
            else:
                title = _("Welcome")

            if properties.get_property(botengine, "IN_APP_WELCOME_MESSAGE", complain_if_missing=False) is not None:
                description = properties.get_property(botengine, "IN_APP_WELCOME_MESSAGE", False)
            else:
                description = _("This screen will capture the history of events that are happening in your home. Please remember to add other people to help watch over your home inside the Trusted Circle tab.")

            # NOTE: Log that the user welcomed for the first and only time. (human readable)
            self.parent.narrate(botengine,
                                title=title,
                                description=description,
                                icon="comment-smile",
                                priority=botengine.NARRATIVE_PRIORITY_INFO,
                                event_type="welcome.welcomed")

            # NOTE: Log that the user welcomed for the first and only time. (machine readable)
            analytics.track(botengine, self.parent, "welcomed")

            self.parent.set_location_property(botengine, "welcomed", True)

            # Send welcome SMS/push notifications to download the app.
            self.start_timer_ms(botengine, utilities.ONE_MINUTE_MS * 5, reference=TIMER_REFERENCE_BIRTH, argument=TIMER_REFERENCE_BIRTH)

            delay_ms = properties.get_property(botengine, "CS_VIRTUAL_CONNECT_SMS_DELAY_MS", False)
            if delay_ms is None:
                delay_ms = utilities.ONE_HOUR_MS * 4

            self.start_timer_ms(botengine, delay_ms, reference=TIMER_REFERENCE_INSTALL, argument=TIMER_REFERENCE_INSTALL)


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
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
        :param alert_params: Alert parameters as key/value dictionary
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
        if argument == TIMER_REFERENCE_BIRTH:
            # This fires one time, 5 minutes after birth
            ios_url = properties.get_property(botengine, "APP_IOS_URL", False)
            android_url = properties.get_property(botengine, "APP_ANDROID_URL", False)
            ios_store_name = properties.get_property(botengine, "APP_IOS_STORE_NAME", False)
            android_store_name = properties.get_property(botengine, "APP_ANDROID_STORE_NAME", False)

            # Check if we have either URLs or store names available
            has_ios_info = ios_url is not None or ios_store_name is not None
            has_android_info = android_url is not None or android_store_name is not None

            if has_ios_info or has_android_info:
                message = _("Thanks for signing up! Here's how to download {}.").format(properties.get_property(botengine, "SERVICE_NAME"))

                if ios_url is not None:
                    # Note: iOS app download URL qualifier
                    message += "\n\n{}: {}".format(_("iPhone / iPad"), ios_url)
                elif ios_store_name is not None:
                    # Note: iOS app store name when URL not available
                    message += "\n\n{}: Search for '{}' in the App Store".format(_("iPhone / iPad"), ios_store_name)

                if android_url is not None:
                    # Note: Android download URL qualifier
                    message += "\n\n{}: {}".format(_("Android"), android_url)
                elif android_store_name is not None:
                    # Note: Android app store name when URL not available
                    message += "\n\n{}: Search for '{}' in the Play Store".format(_("Android"), android_store_name)

                # Add instructions to sign in with phone number
                message += "\n\n" + _("After downloading, open the app and sign in with your phone number.")

                analytics.track_and_notify(botengine, self.parent, 'services_activated', push_content=_("{} services are activated at \"{}\"!").format(properties.get_property(botengine, "SERVICE_NAME"), self.parent.get_location_name(botengine)), push_sms_fallback_content=message, to_residents=True)

        elif argument == TIMER_REFERENCE_INSTALL:
            # This is a recommendation to schedule time with customer support for an assisted connect session
            
            # Check if any device is a BedDevice
            from devices.bed.bed import BedDevice
            from devices.radar.radar import RadarDevice
            for device_id in self.parent.devices:
                if utilities._isinstance(self.parent.devices[device_id], BedDevice):
                    return

                if utilities._isinstance(self.parent.devices[device_id], RadarDevice):
                    return
            
            # Else let's check for a smattering of device sources available to round out a solution from
            # a standard Activities of Daily Living style pack of products.
            device_count = len(self.parent.devices)
            if 0 < device_count < TOTAL_MINIMUM_DEVICES:
                support_email = properties.get_property(botengine, "CS_EMAIL_ADDRESS")
                service_name = properties.get_property(botengine, "SERVICE_NAME")
                if support_email is not None and service_name is not None:
                    if len(support_email) > 0:
                        # Notify: Want a person to help you set up?
                        message = _("Want a real person to help you set up {} at {}? Email -> {}.").format(service_name, botengine.get_location_name(), support_email)

                        import signals.sms as sms
                        sms.send(botengine,
                                 self.parent,
                                 sms_content=message,
                                 to_residents=True,
                                 to_supporters=False,
                                 sms_group_chat=False,
                                 user_id=None,
                                 add_delay=False)

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

        To return to a synchronous environment where you can use timers and manage state, call:
        botengine.async_execute_again_in_n_seconds(seconds)

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
