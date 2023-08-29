'''
Created on August 19, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence

import signals.dashboard as dashboard
import utilities.utilities as utilities
import properties

# Name of the UI state variable
DASHBOARD_HEADER_VARIABLE_NAME = "dashboard_header"


class LocationDashboardHeaderMicroservice(Intelligence):
    """
    Quantify the home health metrics for end-users and display the most prominent one on the end-user's app dashboard for this location.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # Dashboard headers to automatically apply in the future. { 'name' : [ list, of, future, timer, references ] }
        self.futures = {}

        # Backlog of saved headers that haven't made it out to the UI.
        self.saved_headers = {}

        # CRC32 of the last saved state
        self.last_crc32 = None

        # True if the last narration we made on a dashboard update was for a "lastseen" header, so we don't overdo it
        self.last_seen = False

        self.is_service_running = True

        self.clear_dashboard_headers(botengine)
    
    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        # Added September 4, 2020
        if not hasattr(self, 'last_crc32'):
            self.last_crc32 = None

        # Added December 8, 2020
        if not hasattr(self, 'last_seen'):
            self.last_seen = False

        # Added October 11, 2021
        if not hasattr(self, 'is_service_running'):
            self.is_service_running = True

        if len(self.saved_headers) == 0:
            self.clear_dashboard_headers(botengine)
        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
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

    def timer_fired(self, botengine, dashboard_header):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        self.update_dashboard_header(botengine, dashboard_header)

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

    def clear_dashboard_headers(self, botengine, content=None):
        """
        Clear all dashboard headers.
        :param botengine:
        :param content:
        :return:
        """
        botengine.get_logger().info("location_dashboardheader_microservice: clearing all dashboard headers")
        self.saved_headers = {}

        # Keep in mind that on __init__(), our microservices are not stitched together or fully initialized.
        # So the signals do not work during an __init__() method.
        # Since this method is called from __init__(), we skip the signal and go straight to the internal function.
        default_header = {
            "name": "default",
            "priority": dashboard.DASHBOARD_PRIORITY_EMPTY,
            "percent": 100,
            "updated_ms": botengine.get_timestamp(),
            "icon": "cogs",
            "icon_font": utilities.ICON_FONT_FONTAWESOME_REGULAR,
            "title": properties.get_property(botengine, "SERVICE_NAME"),
            "comment": _("Listening for activity")
        }
        self.update_dashboard_header(botengine, default_header)

    def resolve_dashboard_header(self, botengine, content):
        """
        Data stream message from a one-shot resolution object to resolve a dashboard item

        content = {
            "name": <dashboard header to delete>,
            "answer": 0
        }

        :param botengine:
        :param content:
        :return:
        """
        if 'name' not in content:
            self.update_dashboard_header(botengine, {})
            return

        self.update_dashboard_header(botengine, {"name": content['name']})

    def update_dashboard_header(self, botengine, dashboard_header):
        """
        Update the dashboard header : Data Stream Message

            {
                # Unique identifying name
                "name": name,

                # Priority of this dashboard header, which dictates color
                "priority": priority,

                # Title at the top of the dashboard
                "title": title,

                # Comment to display under the title
                "comment": comment,

                # Icon
                "icon": icon,

                # Icon font package
                "icon_font": icon_font,

                # Auto-Populated by a Conversation: True to show the emergency call button
                "call": False,

                # If the emergency call button is present, this flag allows the user to contact the emergency call center.
                "ecc": False,

                # Question ID for the resolution question
                "resolution": {
                    "question": "CHANGE STATUS >",

                    # Title at the top of the action sheet
                    "title": "Change Status",

                    # To answer this question, send a data stream message to this address ...
                    "datastream_address": "conversation_resolved",

                    # ... and include this content merged with the 'content' from the selected option
                    "content": {
                        "microservice_id": "26e636d2-c9e6-4caa-a2dc-a9738505c9f2",
                        "conversation_id": "68554d0f-da4a-408c-80fb-0c8f60b0ebc3",
                    }

                    # The options are already ordered by virtue of being in a list.
                    "response_options": [
                        {
                            "text": "Resolved",
                            "ack": "Okay, resolving the notification...",
                            "icon": "thumbs-up",
                            "icon_font": "far",
                            "content": {
                                "answer": 0
                            },
                        },
                        {
                            "text": "False Alarm",
                            "ack": "Okay, marking this a false alarm...",
                            "icon": "thumbs-up",
                            "icon_font": "far",
                            "content": {
                                "answer": 1
                            },
                        }
                    ]
                },

                # Question IDs for feedback
                "feedback": {
                    # Question for quantified thumbs-up / thumbs-down feedback
                    "quantified": "Did we do a good job?",

                    # Question for the open-ended text box
                    "verbatim": "What do you think caused the alert?",

                    # To answer this question, send a data stream message to this address ...
                    "datastream_address": "conversation_feedback_quantified",

                    # ... and include this content - you fill in the 'quantified', 'verbatim', and optional 'user_id' fields.
                    "content": {
                        "microservice_id": "26e636d2-c9e6-4caa-a2dc-a9738505c9f2",
                        "conversation_id": "68554d0f-da4a-408c-80fb-0c8f60b0ebc3",

                        # You'll fill these fields out in the app.
                        "quantified": <0=bad; 1=good>,
                        "verbatim": "Open-ended text field.",
                        "user_id": 1234
                    }
                },

                # Internal usage: Future timestamp to apply this header
                "future_timestamp_ms": <timestamp in milliseconds>

                # Internal usage only: Conversation object reference, so we don't keep a dashboard header around for a conversation that expired.
                "conversation_object": <conversation_object>,

                # Internal usage only: Percentage good, to help rank two identical priority headers against each other. Lower percentages get shown first because they're not good.
                "percent": <0-100 weight>
            }


        REFRESH:
        You can pass nothing into the 'dashboard_header' (content) field and this will simply refresh/resync the published state variable
        status based on the saved dashboard UI state variable, which could have been updated by the app.

        DELETE:
        You can delete the metric by passing in a 'name' and no 'priority'. Anytime the 'priority' is present, that means we want to update the dashboard.

        FUTURES:
        If you pass in 'future_timestamp_ms' and the timestamp is indeed in the future, then this dashboard_header
        (and any others you add to the future timestamp pile) will be applied at that future timestamp.

        If you do not pass in 'future_timestamp_ms' then it will erase all future timestamped metrics and start fresh.

        You can automatically delete this dashboard_header in the future by passing in a future_timestamp_ms, a name, and no priority.

        :param botengine: BotEngine environment
        :param dashboard_header: Dashboard header dictionary object
        :return:
        """
        if 'priority' in dashboard_header:
            if dashboard_header['priority'] is None:
                del(dashboard_header['priority'])

        if 'name' in dashboard_header:
            name = dashboard_header['name']

            # Update the current metrics table
            if 'future_timestamp_ms' in dashboard_header:

                # Make sure the developer was paying attention.
                if dashboard_header['future_timestamp_ms'] < botengine.get_timestamp() - utilities.ONE_WEEK_MS:
                    botengine.get_logger().warn("location_dashboardheader_microservice: Really old future_timestamp_ms at {} for {} - are you sure you're using absolute time instead of relative time? Trying to fix it by transforming relative->absolute time in ms".format(dashboard_header['future_timestamp_ms'], name))
                    dashboard_header['future_timestamp_ms'] = dashboard_header['future_timestamp_ms'] + botengine.get_timestamp()

                if dashboard_header['future_timestamp_ms'] > botengine.get_timestamp():
                    # Apply this in the future
                    reference = "{}:{}".format(dashboard_header['name'], dashboard_header['future_timestamp_ms'])

                    if name not in self.futures:
                        self.futures[name] = []

                    self.futures[name].append(reference)
                    self.set_alarm(botengine, dashboard_header['future_timestamp_ms'], argument=dashboard_header, reference=reference)
                    return

            else:
                # If there's no 'future_timestamp_ms' then delete all future metrics of this type and start fresh.
                if name in self.futures:
                    for reference in self.futures[name]:
                        self.cancel_alarms(botengine, reference)
                    del (self.futures[name])

            # Apply it now.
            if 'priority' in dashboard_header:
                # The 'priority' field exists - so don't delete, instead update the dashboard
                if 'future_timestamp_ms' in dashboard_header:
                    del(dashboard_header['future_timestamp_ms'])

                if dashboard_header['priority'] < 0:
                    dashboard_header['priority'] = 0
                elif dashboard_header['priority'] > 100:
                    dashboard_header['priority'] = 100

                # Make sure our app-required fields are present, or make something up.
                if name in self.saved_headers:
                    if 'title' not in dashboard_header:
                        dashboard_header['title'] = self.saved_headers[name]['title']

                    if 'comment' not in dashboard_header:
                        dashboard_header['comment'] = self.saved_headers[name]['comment']

                    if 'icon' not in dashboard_header:
                        dashboard_header['icon'] = self.saved_headers[name]['icon']

                else:
                    if 'title' not in dashboard_header:
                        dashboard_header['title'] = _("Hello")

                    if 'comment' not in dashboard_header:
                        dashboard_header['comment'] = _("Hope you're having a good day.")

                    if 'icon' not in dashboard_header:
                        dashboard_header['icon'] = "smile"

                self.saved_headers[name] = dashboard_header

            else:
                # Delete everything about this dashboard header
                botengine.get_logger().info("location_dashboardheader_microservice: Delete dashboard header {}".format(name))
                self._delete_all(botengine, name)

        # Refresh the overall health of the home
        highest_priority = dashboard.DASHBOARD_PRIORITY_EMPTY
        highest_priority_header = None
        for name in list(self.saved_headers.keys()):
            botengine.get_logger().debug("location_dashboard_header possibility: {}".format(self.saved_headers[name]))
            # Delete dashboard headers related to active conversations
            if highest_priority_header is None:
                highest_priority_header = self.saved_headers[name]
                highest_priority = self.saved_headers[name]['priority']

            if self.saved_headers[name]['priority'] > highest_priority:
                highest_priority = self.saved_headers[name]['priority']
                highest_priority_header = self.saved_headers[name]

            elif self.saved_headers[name]['priority'] == highest_priority:
                if 'conversation_object' not in highest_priority_header and 'conversation_object' in self.saved_headers[name]:
                    # Pick the one that is managing an active conversation (inactive conversations got deleted above, and there can only be 1 conversation at a time)
                    highest_priority_header = self.saved_headers[name]

                elif self.saved_headers[name]['percent'] < highest_priority_header['percent']:
                    # This header has a lower "good-ness" percentage than the leading contender, so pick it instead.
                    highest_priority_header = self.saved_headers[name]

        # Remove no-no items from the publishable header.
        if highest_priority_header is not None:
            publish_header = dict(highest_priority_header)

            # We update the dashboard header with the current state of its converastion here at the end to keep it all in sync.
            if 'conversation_object' in publish_header:
                botengine.get_logger().info("location_dashboardheader_microservice: 'conversation_object' exists in the header we're about to publish.")
                conversation_object = publish_header['conversation_object']
                if conversation_object is not None:
                    publish_header['call'] = conversation_object.contact_homeowners or conversation_object.contact_supporters
                    publish_header['ecc'] = not conversation_object.is_contacting_ecc(botengine)

                    if 'resolution' not in publish_header:
                        # If our dashboard header doesn't already contain a resolution object, try the conversation's resolution object.
                        if conversation_object.resolution_object is not None:
                            publish_header['resolution'] = conversation_object.resolution_object

                    if conversation_object.ask_for_feedback:
                        publish_header['feedback'] = conversation_object.feedback_object
            else:
                botengine.get_logger().info("location_dashboardheader_microservice: No conversation object in the header we're about to publish.")

            if 'conversation_object' in publish_header:
                del(publish_header['conversation_object'])

            if 'future_timestamp_ms' in publish_header:
                del(publish_header['future_timestamp_ms'])

            percent = 100
            if 'percent' in publish_header:
                percent = publish_header['percent']
                del(publish_header['percent'])

            import copy
            announcement_header = copy.copy(publish_header)
            announcement_header['percent'] = percent

            import binascii
            crc32 = binascii.crc32(str(publish_header).encode('utf-8'))

            if self.last_crc32 != crc32:
                self.last_crc32 = crc32
                self.parent.set_location_property_separately(botengine, DASHBOARD_HEADER_VARIABLE_NAME, publish_header, overwrite=True)
                dashboard.updated_dashboard_headers(botengine, self.parent, announcement_header, self.saved_headers)

                # Don't narrate every time a person is last seen.
                # Do narrate when the dashboard changes from something else back to 'lastseen'.
                if publish_header['name'] == "lastseen":
                    if self.last_seen:
                        return

                    self.last_seen = True

                else:
                    self.last_seen = False

                # NOTE: Update dashboard header.
                self.parent.narrate(botengine,
                                    title=_("Dashboard: {}").format(publish_header['title']),
                                    description=publish_header['comment'],
                                    priority=botengine.NARRATIVE_PRIORITY_DETAIL,
                                    icon=publish_header['icon'],
                                    icon_font=publish_header['icon_font'],
                                    event_type="dashboard.update_header")

            else:
                botengine.get_logger().info("location_dashboardheader_microservice: Duplicate header content, skip publishing...")



    def _delete_all(self, botengine, name):
        """
        Delete everything about this dashboard header
        :param botengine:
        :param name:
        :return:
        """
        if name in self.futures:
            for reference in self.futures[name]:
                self.cancel_alarms(botengine, reference)
            del (self.futures[name])

        # Delete the saved header
        if name in self.saved_headers:
            del (self.saved_headers[name])
