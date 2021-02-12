'''
Created on November 20, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence

import domain
import json
import utilities.utilities as utilities
import signals.analytics as analytics

# Section weights
WEIGHT_ALERTS = 0
WEIGHT_NOTES = 5
WEIGHT_TASKS = 10
WEIGHT_SLEEP = 15
WEIGHT_ACTIVITIES = 20
WEIGHT_MEALS = 25
WEIGHT_MEDICATION = 30
WEIGHT_BATHROOM = 35
WEIGHT_SOCIAL = 40
WEIGHT_MEMORIES = 45
WEIGHT_SYSTEM = 50

# Section ID's
SECTION_ID_ALERTS = "alerts"
SECTION_ID_NOTES = "notes"
SECTION_ID_TASKS = "tasks"
SECTION_ID_SLEEP = "sleep"
SECTION_ID_ACTIVITIES = "activities"
SECTION_ID_MEALS = "meals"
SECTION_ID_MEDICATION = "medication"
SECTION_ID_BATHROOM = "bathroom"
SECTION_ID_SOCIAL = "social"
SECTION_ID_MEMORIES = "memories"
SECTION_ID_SYSTEM = "system"

# Section Colors
SECTION_COLOR_ALERTS = "D0021B"
SECTION_COLOR_NOTES = "530F8B"
SECTION_COLOR_TASKS = "00AD9D"
SECTION_COLOR_SLEEP = "946C49"
SECTION_COLOR_ACTIVITIES = "27195F"
SECTION_COLOR_MEALS = "C1006E"
SECTION_COLOR_MEDICATION = "1E6601"
SECTION_COLOR_BATHROOM = "17A5F6"
SECTION_COLOR_SOCIAL = "B6B038"
SECTION_COLOR_MEMORIES = "600000"
SECTION_COLOR_SYSTEM = "787F84"

# Reasons why the occupancy status would have changed
REASON_ML = "ML"
REASON_USER = "USER"

# Timer references
TIMER_REFERENCE_ADVANCE_REPORTS = "new"

# State UI content address
DAILY_REPORT_ADDRESS = "dailyreport"

class LocationDailyReportMicroservice(Intelligence):
    """
    Create a daily report
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # Timestamp at which the current report was created
        self.current_report_ms = None

        # Timestamp at which the home went into SLEEP mode
        self.started_sleeping_ms = None

        # Last report we emailed
        self.last_emailed_report_ms = None


    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        if not hasattr(self, 'last_emailed_report_ms'):
            self.last_emailed_report_ms = None

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

    def occupancy_status_updated(self, botengine, status, reason, last_status, last_reason):
        """
        AI Occupancy Status updated
        :param botengine: BotEngine
        :param status: Current occupancy status
        :param reason: Current occupancy reason
        :param last_status: Last occupancy status
        :param last_reason: Last occupancy reason
        """
        if 'SLEEP' in status and REASON_ML in reason and self.started_sleeping_ms is None:
            # Started sleeping
            self.started_sleeping_ms = botengine.get_timestamp()

            if self.parent.get_relative_time_of_day(botengine) > 12.0:
                # Went to sleep before midnight - send out the daily report now.
                self.last_emailed_report_ms = self.current_report_ms
                self.email_report(botengine)

        if 'SLEEP' not in status and 'S2H' not in status and self.started_sleeping_ms is not None:
            # Stopped sleeping
            self.started_sleeping_ms = None

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

    def user_role_updated(self, botengine, user_id, alert_category, location_access, previous_alert_category, previous_location_access):
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

    def midnight_fired(self, botengine, content=None):
        """
        Data stream message - Midnight timer fired
        :param botengine:
        :param content:
        :return:
        """
        # If we haven't emailed the daily report yet because the person hasn't gone to sleep yet, email it now.
        if self.current_report_ms is not None:
            if self.last_emailed_report_ms != self.current_report_ms:
                self.last_emailed_report_ms = self.current_report_ms
                if "SLEEP" not in self.parent.occupancy_status and "VACATION" not in self.parent.occupancy_status:
                    self.add_entry(botengine, SECTION_ID_SLEEP, comment=_("Hasn't gone to sleep by midnight."), include_timestamp=True)
                self.email_report(botengine)

        # Create a new report
        self.current_report_ms = self._get_todays_timestamp(botengine)
        report = {}

        name = self._get_resident_name(botengine)
        if name is not None:
            report['title'] = name.upper()
        else:
            report['title'] = _("DAILY REPORT")

        report['subtitle'] = _("Daily Report for {}").format(self.parent.get_local_datetime(botengine).strftime("%A %B %-d, %Y"))
        report['created_ms'] = botengine.get_timestamp()
        report['sections'] = []
        self.parent.set_location_property_separately(botengine, DAILY_REPORT_ADDRESS, report, overwrite=True, timestamp_ms=self.current_report_ms)

        analytics.track(botengine,
                        self.parent,
                        "daily_report_initialized",
                        properties={
                            "timestamp_ms": self.current_report_ms
                        })

        # Add our first entry if possible.
        if self.started_sleeping_ms is not None and "SLEEP" in self.parent.occupancy_status:
            self.add_entry(botengine, SECTION_ID_SLEEP, comment=_("Went to sleep."), subtitle=_("Currently sleeping."), include_timestamp=True, timestamp_override_ms=self.started_sleeping_ms)

    def daily_report_entry(self, botengine, content):
        """
        Data stream message to add content to our daily report
        :param botengine: BotEngine environment
        :param content: Data Stream Content
        :return:
        """
        botengine.get_logger().info("location_dailyreport_microservice: 'daily_report_entry' data stream message received.")
        if 'section_id' not in content:
            botengine.get_logger().error("location_dailyreport_microservice: Section ID not found in data stream message {}".format(content))
            return

        section_id = content['section_id']
        comment = None
        subtitle = None
        identifier = None
        include_timestamp = False
        timestamp_override_ms = None

        if 'comment' in content:
            comment = content['comment']

        if 'subtitle' in content:
            subtitle = content['subtitle']

        if 'identifier' in content:
            identifier = content['identifier']

        if 'include_timestamp' in content:
            include_timestamp = content['include_timestamp']

        if 'timestamp_override_ms' in content:
            timestamp_override_ms = content['timestamp_override_ms']

        self.add_entry(botengine, section_id, comment=comment, subtitle=subtitle, identifier=identifier, include_timestamp=include_timestamp, timestamp_override_ms=timestamp_override_ms)

    def add_entry(self, botengine, section_id, comment=None, subtitle=None, identifier=None, include_timestamp=False, timestamp_override_ms=None):
        """
        Add a section and bullet point the current daily report
        :param botengine: BotEngine environment
        :param comment: Comment like "Woke up."
        :param subtitle: Subtitle comment like "Consistent sleep schedule and good quality sleep last night."
        :param identifier: Optional identifier to come back and edit this entry later.
        :param include_timestamp: True to include a timestamp like "7:00 AM - <comment>" (default is False)
        :param timestamp_override_ms: Optional timestamp in milliseconds to override the current time when citing the timestamp with include_timestamp=True
        """
        botengine.get_logger().info("location_dailyreport_microservice.add_entry(): Current report timestamp is {}".format(self.current_report_ms))

        # Make sure our midnight schedule fired properly.
        # We added a 1 hour buffer for backwards compatibility, because the self.current_report_ms was previously being set to the current botengine.get_timestamp()
        # which was some time after midnight.
        if self.current_report_ms is None:
            self.midnight_fired(botengine)

        if self._get_todays_timestamp(botengine) < (self.current_report_ms - utilities.ONE_HOUR_MS):
            self.midnight_fired(botengine)

        report = botengine.get_ui_content(DAILY_REPORT_ADDRESS, timestamp_ms=self.current_report_ms)
        if report is None:
            botengine.get_logger().info("location_dailyreport_microservice: There is currently no active daily report.")
            self.midnight_fired(botengine)
            report = botengine.get_ui_content(DAILY_REPORT_ADDRESS, self.current_report_ms)
            if report is None:
                return
            else:
                botengine.get_logger().info("location_dailyreport_microservice: Successfully created and loaded a new report.")
        else:
            botengine.get_logger().info("location_dailyreport_microservice: Successfully loaded an existing report.")

        focused_section = self._get_section_object(botengine, report, section_id)
        if focused_section is None:
            botengine.get_logger().info("location_dailyreport_microservice: Need to create a new section for section_id '{}'.".format(section_id))
            if section_id == SECTION_ID_ALERTS:
                focused_section = {
                    "weight": WEIGHT_ALERTS,
                    "id": SECTION_ID_ALERTS,
                    "title": _("Today's Alerts"),
                    "icon": "comment-exclamation",
                    "color": SECTION_COLOR_ALERTS,
                    "items": []
                }

            elif section_id == SECTION_ID_NOTES:
                focused_section = {
                    "weight": WEIGHT_NOTES,
                    "id": SECTION_ID_NOTES,
                    "title": _("Today's Notes"),
                    "icon": "clipboard",
                    "color": SECTION_COLOR_NOTES,
                    "items": []
                }

            elif section_id == SECTION_ID_TASKS:
                focused_section = {
                    "weight": WEIGHT_TASKS,
                    "id": SECTION_ID_TASKS,
                    "title": _("Today's Tasks"),
                    "icon": "clipboard-list-check",
                    "color": SECTION_COLOR_TASKS,
                    "items": []
                }

            elif section_id == SECTION_ID_SLEEP:
                focused_section = {
                    "weight": WEIGHT_SLEEP,
                    "id": SECTION_ID_SLEEP,
                    "title": _("Sleep"),
                    "icon": "moon",
                    "color": SECTION_COLOR_SLEEP,
                    "items": []
                }

            elif section_id == SECTION_ID_BATHROOM:
                focused_section = {
                    "weight": WEIGHT_BATHROOM,
                    "id": SECTION_ID_BATHROOM,
                    "title": _("Bathroom"),
                    "icon": "toilet",
                    "color": SECTION_COLOR_BATHROOM,
                    "items": []
                }

            elif section_id == SECTION_ID_ACTIVITIES:
                focused_section = {
                    "weight": WEIGHT_ACTIVITIES,
                    "id": SECTION_ID_ACTIVITIES,
                    "title": _("Activities"),
                    "icon": "walking",
                    "color": SECTION_COLOR_ACTIVITIES,
                    "items": []
                }

            elif section_id == SECTION_ID_MEALS:
                focused_section = {
                    "weight": WEIGHT_MEALS,
                    "id": SECTION_ID_MEALS,
                    "title": _("Meals"),
                    "icon": "utensils",
                    "color": SECTION_COLOR_MEALS,
                    "items": []
                }

            elif section_id == SECTION_ID_MEDICATION:
                focused_section = {
                    "weight": WEIGHT_MEDICATION,
                    "id": SECTION_ID_MEDICATION,
                    "title": _("Medication"),
                    "icon": "pills",
                    "color": SECTION_COLOR_MEDICATION,
                    "items": []
                }

            elif section_id == SECTION_ID_SOCIAL:
                focused_section = {
                    "weight": WEIGHT_SOCIAL,
                    "id": SECTION_ID_SOCIAL,
                    "title": _("Social"),
                    "icon": "user-friends",
                    "color": SECTION_COLOR_SOCIAL,
                    "items": []
                }

            elif section_id == SECTION_ID_MEMORIES:
                focused_section = {
                    "weight": WEIGHT_MEMORIES,
                    "id": SECTION_ID_MEMORIES,
                    "title": _("Memories"),
                    "icon": "camera-retro",
                    "color": SECTION_COLOR_MEMORIES,
                    "items": []
                }

            elif section_id == SECTION_ID_SYSTEM:
                focused_section = {
                    "weight": WEIGHT_SYSTEM,
                    "id": SECTION_ID_SYSTEM,
                    "title": _("System Status"),
                    "icon": "brain",
                    "color": SECTION_COLOR_SYSTEM,
                    "items": []
                }

            else:
                botengine.get_logger().error("location_dailyreport_microservice: Unknown section '{}'".format(section_id))
                return

            if 'sections' not in report:
                report['sections'] = []

            report['sections'].append(focused_section)
            report['sections'] = sorted(report['sections'], key=lambda k: k['weight'])

        if comment is not None or identifier is not None:
            if include_timestamp and comment is not None:
                if timestamp_override_ms is not None:
                    dt = self.parent.get_local_datetime_from_timestamp(botengine, timestamp_override_ms)
                else:
                    dt = self.parent.get_local_datetime(botengine)

                if section_id == SECTION_ID_SLEEP:
                    # Sleep timestamps include the day
                    comment = "{} - {}".format(dt.strftime("%-I:%M %p %A"), comment)
                else:
                    # Other timestamps don't include the day
                    comment = "{} - {}".format(dt.strftime("%-I:%M %p"), comment)

            if identifier is None and comment is not None:
                ts = botengine.get_timestamp()
                if timestamp_override_ms is not None:
                    ts = timestamp_override_ms

                focused_item = {
                    "timestamp_ms": ts,
                    "comment": comment
                }
                focused_section['items'].append(focused_item)
                focused_section['items'] = sorted(focused_section['items'], key=lambda k: k['timestamp_ms'])

            else:
                # Try to overwrite any previous entry with this identifier
                focused_item = None
                for item in focused_section['items']:
                    if 'id' in item:
                        if item['id'] == identifier:
                            focused_item = item

                if focused_item is not None:
                    # Edit the item in place
                    if comment is not None:
                        # Modify the item
                        ts = botengine.get_timestamp()
                        if timestamp_override_ms is not None:
                            ts = timestamp_override_ms

                        focused_item['timestamp_ms'] = ts
                        focused_item['comment'] = comment
                        focused_section['items'] = sorted(focused_section['items'], key=lambda k: k['timestamp_ms'])

                    else:
                        # Delete the item
                        focused_section['items'].remove(focused_item)
                        focused_section['items'] = sorted(focused_section['items'], key=lambda k: k['timestamp_ms'])

                        if len(focused_section['items']) == 0:
                            # Delete the entire section
                            report['sections'].remove(focused_section)

                else:
                    # Add the item
                    ts = botengine.get_timestamp()
                    if timestamp_override_ms is not None:
                        ts = timestamp_override_ms

                    focused_item = {
                        "timestamp_ms": ts,
                        "comment": comment,
                        "id": identifier
                    }
                    focused_section['items'].append(focused_item)
                    focused_section['items'] = sorted(focused_section['items'], key=lambda k: k['timestamp_ms'])

        if subtitle is not None:
            # Manually defined subtitle for this section
            focused_section['subtitle'] = subtitle

        else:
            # Auto-generated subtitles for specific sections that support it
            if section_id == SECTION_ID_NOTES:
                if len(focused_section['items']) == 0:
                    focused_section['subtitle'] = _("No notes captured today.")

                elif len(focused_section['items']) == 1:
                    focused_section['subtitle'] = _("Captured one note today.")

                elif len(focused_section['items']) > 1:
                    focused_section['subtitle'] = _("Captured {} notes today.").format(len(focused_section['items']))

            elif section_id == SECTION_ID_TASKS:
                if len(focused_section['items']) == 0:
                    focused_section['subtitle'] = _("No tasks updated today.")

                elif len(focused_section['items']) == 1:
                    focused_section['subtitle'] = _("Updated one task today.")

                elif len(focused_section['items']) > 1:
                    focused_section['subtitle'] = _("Updated {} tasks today.").format(len(focused_section['items']))

            elif section_id == SECTION_ID_MEDICATION:
                if len(focused_section['items']) == 0:
                    focused_section['subtitle'] = _("No medication accessed today.")

                elif len(focused_section['items']) == 1:
                    focused_section['subtitle'] = _("Accessed medicine once today.")

                elif len(focused_section['items']) > 1:
                    focused_section['subtitle'] = _("Accessed medicine {} times today.").format(len(focused_section['items']))

            elif section_id == SECTION_ID_BATHROOM:
                if len(focused_section['items']) == 0:
                    focused_section['subtitle'] = _("No bathroom visits observed today.")

                elif len(focused_section['items']) == 1:
                    focused_section['subtitle'] = _("Visited the bathroom once today.")

                elif len(focused_section['items']) > 1:
                    focused_section['subtitle'] = _("Visited the bathroom {} times today.").format(len(focused_section['items']))

        self.parent.set_location_property_separately(botengine, DAILY_REPORT_ADDRESS, report, overwrite=True, timestamp_ms=self.current_report_ms)

    def email_report(self, botengine):
        """
        Email the current report
        :param botengine:
        :return:
        """
        return

    def _get_section_object(self, botengine, report, section_id):
        """
        Find and return a section object out of all the sections in the report dictionary that is passed in
        :param botengine:
        :param report: report dictionary object
        :param section_id: section ID to return
        :return: section object dictionary, or None if it doesn't exist
        """
        if report is not None:
            if 'sections' in report:
                for section in report['sections']:
                    if section['id'] == section_id:
                        return section

        return None

    def _get_resident_name(self, botengine):
        """
        Get the name of the resident in a way that we can use this in a sentence
        :param botengine:
        :return:
        """
        residents = botengine.get_location_user_names(to_residents=True, to_supporters=False, sms_only=False)
        name = ""
        if len(residents) == 0:
            # Nobody lives here, nothing to do
            return None

        elif len(residents) == 1:
            name = "{} {}".format(residents[0]['firstName'], residents[0]['lastName']).strip()

        elif len(residents) == 2:
            a = _("and")

            # a and b
            name = "{} {} {}".format(residents[0]['firstName'], a, residents[1]['firstName'])

        elif len(residents) > 2:
            # So, we only list 3 names max just because we don't want to waste a ton of SMS space.
            a = _("and")

            # a, b, and c
            name = "{}, {}, {} {}".format(residents[0]['firstName'], residents[1]['firstName'], a, residents[2]['firstName'])

        return name

    def _get_todays_timestamp(self, botengine):
        """
        Get the timestamp for midnight last night
        :param botengine:
        :return:
        """
        return self.parent.timezone_aware_datetime_to_unix_timestamp(botengine, self.parent.get_midnight_last_night(botengine))
