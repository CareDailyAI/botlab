'''
Created on January 23, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''
# TODO: Add "messaging" signal class to com.ppc.Bot/signals/messaging/messaging.py
# TODO: Add documentation to github docs.


from intelligence.intelligence import Intelligence

class LocationMessagingMicroservice(Intelligence):
    """
    Transform a data stream message into communications that are delivered to the users.
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

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
        :param alert_category: User's current alert/communications category (1=resident; 2=supporter)
        :param location_access: User's access to the location and devices. (0=None; 10=read location/device data; 20=control devices and modes; 30=update location info and manage devices)
        :param previous_alert_category: User's previous category, if any
        :param previous_location_access: User's previous access to the location, if any
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

    def message(self, botengine, content):
        """
        Data stream message to communicate to the user(s).

        All fields are optional
        {
          "push_content": None,
          "push_sound": None,
          "push_sms_fallback_content": None,

          "email_subject": None,
          "email_content": None,
          "email_html": False,
          "email_template_filename": None,
          "email_template_model": None,

          "sms_content": None,
          "sms_group_chat": True,

          "admin_domain_name": None,
          "brand": None,

          "user_id": None,
          "user_id_list": None,

          "to_residents": False,
          "to_supporters": False,
          "to_admins": False
        }

        SMS content will be delivered via "send_sms" to add delays between individual SMS messages.

        :param botengine:
        :param content:
        :return:
        """
        push_content = None
        if 'push_content' in content:
            push_content = content['push_content']

        push_sound = None
        if 'push_sound' in content:
            push_sound = content['push_sound']

        push_sms_fallback_content = None
        if 'push_sms_fallback_content' in content:
            push_sms_fallback_content = content['push_sms_fallback_content']

        email_subject = None
        if 'email_subject' in content:
            email_subject = content['email_subject']

        email_content = None
        if 'email_content' in content:
            email_content = content['email_content']

        email_html = False
        if 'email_html' in content:
            email_html = content['email_html']

        email_template_filename = None
        if 'email_template_filename' in content:
            email_template_filename = content['email_template_filename']

        email_template_model = None
        if 'email_template_model' in content:
            email_template_model = content['email_template_model']

        sms_group_chat = True
        if 'sms_group_chat' in content:
            sms_group_chat = content['sms_group_chat']

        admin_domain_name = None
        if 'admin_domain_name' in content:
            admin_domain_name = content['admin_domain_name']

        brand = None
        if 'brand' in content:
            brand = content['brand']

        user_id = None
        if 'user_id' in content:
            user_id = content['user_id']

        user_id_list = None
        if 'user_id_list' in content:
            user_id_list = content['user_id_list']

        to_residents = False
        if 'to_residents' in content:
            to_residents = content['to_residents']

        to_supporters = False
        if 'to_supporters' in content:
            to_supporters = content['to_supporters']

        to_admins = False
        if 'to_admins' in content:
            to_admins = content['to_admins']

        sms_content = None
        if 'sms_content' in content:
            sms_content = content['sms_content']
            self.parent.distribute_datastream_message(botengine, 'send_sms',
                                                      {
                                                          "sms_content": sms_content,
                                                          "to_residents": to_residents,
                                                          "to_supporters": to_supporters,
                                                          "sms_group_chat": sms_group_chat,
                                                          "user_id": user_id,
                                                          "add_delay": True
                                                      },
                                                      internal=True,
                                                      external=False)
        
        if to_admins:
            import utilities.utilities as utilities
            import properties

            url = utilities.get_admin_url_for_location(botengine)

            if url is not None:
                # Send the email to admins.
                botengine.get_logger().info("location_messaging_microservice: Sending email notification to admins.")

                # Notify Organization Users
                botengine.email_admins(
                    email_subject=email_subject,
                    email_content=email_content,
                    email_html=email_html,
                    email_template_filename=email_template_filename,
                    email_template_model=email_template_model,
                    brand=properties.get_property(botengine, "ORGANIZATION_BRAND"),
                    categories=utilities.get_organization_user_notification_categories(botengine, self.parent))
            return
        
        import signals.analytics as analytics
        analytics.track_and_notify(botengine, self.parent, 'send_message',
                              push_content=push_content,
                              push_sound=push_sound,
                              push_sms_fallback_content=push_sms_fallback_content,
                              email_subject=email_subject,
                              email_content=email_content,
                              email_html=email_html,
                              email_template_filename=email_template_filename,
                              email_template_model=email_template_model,
                              admin_domain_name=admin_domain_name,
                              brand=brand,
                              user_id=user_id,
                              user_id_list=user_id_list,
                              to_residents=to_residents,
                              to_supporters=to_supporters,
                              to_admins=to_admins)



