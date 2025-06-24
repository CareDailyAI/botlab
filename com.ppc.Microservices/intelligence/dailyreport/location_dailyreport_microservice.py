'''
Created on November 20, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''
# TODO: Create a datastream address to "configure" the daily report by changing the level of detail for a given location: Low, Medium, High
from intelligence.intelligence import Intelligence
import random
import properties
import json
import utilities.utilities as utilities
import signals.analytics as analytics
import signals.dailyreport as dailyreport
import signals.dashboard as dashboard

# Current version
VERSION = 1.2

# Section Properties
DEFAULT_SECTION_PROPERTIES = {
    dailyreport.SECTION_ID_WELLNESS: {
        dailyreport.SECTION_KEY_WEIGHT: -5,
        dailyreport.SECTION_KEY_TITLE: _("Wellness"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Overall physical and mental health status."),
        dailyreport.SECTION_KEY_ICON: "heart",
        dailyreport.SECTION_KEY_COLOR: "F47174",
        dailyreport.SECTION_KEY_TREND_IDS: [
            # "trend.sleep_score", 
            # "trend.bedtime_score", 
            # "trend.wakeup_score", 
            # "trend.restlessness_score", 
            #"trend.wellness_score", 
            # "trend.mobility_score",
            # "trend.stability_score",
            # "trend.hygiene_score", 
            # "trend.bathroom_score",
            # "trend.social_score", 
            # "trend.care_score",
            # "trend.illbeing_score",
            # "trend.positivity_score",
            # "trend.sleep_diary",
            # "trend.percieved_stress_scale",
        ],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
    },
    dailyreport.SECTION_ID_ALERTS: {
        dailyreport.SECTION_KEY_WEIGHT: 0,
        dailyreport.SECTION_KEY_TITLE: _("Today's Alerts"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Urgent notifications and reminders for the day."),
        dailyreport.SECTION_KEY_ICON: "comment-exclamation",
        dailyreport.SECTION_KEY_COLOR: "D0021B",
        dailyreport.SECTION_KEY_TREND_IDS: [
            "trend.total_falls", 
            "trend.fall_duration",
        ],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [
            # "care.inactivity.bedtime_awake_too_late", 
            # "sleep.low_sleep_quality.warning", 
            # "sleep.too_many_bathrooms.warning", 
            # "care.inactivity.time_to_stretch", 
            # "care.inactivity.warning", 
            # "care.inactivity.good_morning_sleeping_in", 
            # "care.inactivity.good_morning_problem_critical", 
            # "care.inactivity.good_morning_problem", 
            # "care.inactivity.not_back_home.warning", 
            # "request_assistance", 
            # "care.sms_sos", 
            # "health_high_heart_rate_warning", 
            # "health_movement_confirmed_alert", 
            # "vayyar.fall_confirmed_alert", 
            # "vayyar.stability_event_confirmed_alert",
        ],
    },
    dailyreport.SECTION_ID_NOTES: {
        dailyreport.SECTION_KEY_WEIGHT: 5,
        dailyreport.SECTION_KEY_TITLE: _("Today's Notes"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Observations and reflections noted today."),
        dailyreport.SECTION_KEY_ICON: "clipboard",
        dailyreport.SECTION_KEY_COLOR: "530F8B",
        dailyreport.SECTION_KEY_TREND_IDS: [],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
    },
    dailyreport.SECTION_ID_TASKS: {
        dailyreport.SECTION_KEY_WEIGHT: 10,
        dailyreport.SECTION_KEY_TITLE: _("Today's Tasks"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("List of to-do items scheduled for today."),
        dailyreport.SECTION_KEY_ICON: "clipboard-list-check",
        dailyreport.SECTION_KEY_COLOR: "00AD9D",
        dailyreport.SECTION_KEY_TREND_IDS: [],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
    },
    dailyreport.SECTION_ID_SLEEP: {
        dailyreport.SECTION_KEY_WEIGHT: 15,
        dailyreport.SECTION_KEY_TITLE: _("Sleep"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Sleep quality and other insightful information."),
        dailyreport.SECTION_KEY_ICON: "moon",
        dailyreport.SECTION_KEY_COLOR: "946C49",
        dailyreport.SECTION_KEY_TREND_IDS: [
            "trend.bedtime", 
            "trend.sleep_bathroom_visits", 
            "trend.sleep_duration", 
            "trend.wakeup", 
            "trend.sleep_movement", 
            "trend.nap_duration",
        ],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [
            # "sleep.duration_ms", 
            # "sleep.bedtime_ms", 
            # "sleep.wakeup_ms", 
            # "sleep.sleep_score", 
            # "sleep.underslept", 
            # "sleep.overslept", 
            # "sleep.bedtime_score", 
            # "sleep.wakeup_ms", 
            # "sleep.restlessness_score", 
            # "sleep.sleep_prediction_ms", 
            # "sleep.wake_prediction_ms",
        ],
    },
    dailyreport.SECTION_ID_ACTIVITIES: {
        dailyreport.SECTION_KEY_WEIGHT: 20,
        dailyreport.SECTION_KEY_TITLE: _("Activities"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Physical or leisure activities undertaken."),
        dailyreport.SECTION_KEY_ICON: "walking",
        dailyreport.SECTION_KEY_COLOR: "27195F",
        dailyreport.SECTION_KEY_TREND_IDS: [
            "trend.mobility_duration", 
            # "trend.mobility_rooms", 
            "sitting"
        ],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
    },
    dailyreport.SECTION_ID_MEALS: {
        dailyreport.SECTION_KEY_WEIGHT: 25,
        dailyreport.SECTION_KEY_TITLE: _("Meals"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Details of food and drink consumed."),
        dailyreport.SECTION_KEY_ICON: "utensils",
        dailyreport.SECTION_KEY_COLOR: "C1006E",
        dailyreport.SECTION_KEY_TREND_IDS: [],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
    },
    dailyreport.SECTION_ID_MEDICATION: {
        dailyreport.SECTION_KEY_WEIGHT: 30,
        dailyreport.SECTION_KEY_TITLE: _("Medication"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("List of medicines taken or due today."),
        dailyreport.SECTION_KEY_ICON: "pills",
        dailyreport.SECTION_KEY_COLOR: "1E6601",
        dailyreport.SECTION_KEY_TREND_IDS: [],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
    },
    dailyreport.SECTION_ID_BATHROOM: {
        dailyreport.SECTION_KEY_WEIGHT: 35,
        dailyreport.SECTION_KEY_TITLE: _("Bathroom"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Frequency and nature of bathroom visits."),
        dailyreport.SECTION_KEY_ICON: "toilet",
        dailyreport.SECTION_KEY_COLOR: "17A5F6",
        dailyreport.SECTION_KEY_TREND_IDS: [
            "trend.bathroom_visits", 
            # "trend.bathroom_duration", 
            # "trend.shower_visits", 
        ],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
    },
    dailyreport.SECTION_ID_SOCIAL: {
        dailyreport.SECTION_KEY_WEIGHT: 40,
        dailyreport.SECTION_KEY_TITLE: _("Social"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Interactions with friends, family, or others."),
        dailyreport.SECTION_KEY_ICON: "user-friends",
        dailyreport.SECTION_KEY_COLOR: "B6B038",
        dailyreport.SECTION_KEY_TREND_IDS: [
            "trend.absent", 
            "trend.checkedin", 
            "trend.visitor", 
            "trend.together"
        ],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
    },
    dailyreport.SECTION_ID_MEMORIES: {
        dailyreport.SECTION_KEY_WEIGHT: 45,
        dailyreport.SECTION_KEY_TITLE: _("Memories"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Noteworthy or cherished moments from today."),
        dailyreport.SECTION_KEY_ICON: "camera-retro",
        dailyreport.SECTION_KEY_COLOR: "600000",
        dailyreport.SECTION_KEY_TREND_IDS: [],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
    },
    dailyreport.SECTION_ID_SYSTEM: {
        dailyreport.SECTION_KEY_WEIGHT: 50,
        dailyreport.SECTION_KEY_TITLE: _("System Status"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Current functioning and updates of the system."),
        dailyreport.SECTION_KEY_ICON: "brain",
        dailyreport.SECTION_KEY_COLOR: "787F84",
        dailyreport.SECTION_KEY_TREND_IDS: [],
        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
    }
}

# TODO: Really?
WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Reasons why the occupancy status would have changed
REASON_ML = "ML"
REASON_USER = "USER"

# State UI content address
DAILY_REPORT_ADDRESS = "dailyreport"
WEEKLY_REPORT_ADDRESS = "weeklyreport"
MONTHLY_REPORT_ADDRESS = "monthlyreport"

# Trend metadata state address
TRENDS_METADATA_NAME = "trends_metadata"

# Datastream message to add a new entry to the daily report
DATASTREAM_DAILY_REPORT_ENTRY = "daily_report_entry"

# Datastream message to notify other microservices that a report has been updated
DATASTREAM_DAILY_REPORT_STATUS_UPDATED = "daily_report_status_updated"

# Daily Report State Variable
DAILYREPORT_STATE_VARIABLE_NAME = "dailyreport"

# Services and Alerts Question Settings
_("Daily Report Settings")
SERVICES_COLLECTION_NAME    = "Daily Report Settings"
SERVICES_COLLECTION_WEIGHT  = 0

# Enable or disable daily report services
SERVICE_SECTION_ID         = 0
SERVICE_KEY_ACTIVE         = "dailyreport.is_enabled"
SERVICE_WEIGHT_ACTIVE      = 0

class LocationDailyReportMicroservice(Intelligence):
    """
    Create a daily report

    This microservice creates a daily report for the user.
    A signal can be received notifying this microservice that a new entry should be added to the daily report.
    A signal is sent to notify other microservices that the daily report updated.
    A signal can be received describing new configurations for the daily report.
    
    See README.md for more information.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # Timestamp at which the current report was created
        self.current_report_ms = None

        # Timestamp at which the current weekly report was created
        self.current_weekly_report_ms = None
        
        # Timestamp at which the current monthly report was created
        self.current_monthly_report_ms = None

        # Timestamp at which the home went into SLEEP mode
        self.started_sleeping_ms = None

        # Last report we emailed
        self.last_emailed_report_ms = None

        # Weekly report {"2021_week1":{"sleep.duration_ms":[8, 7.5], xxx}, "2021_week2":{}}
        self.weekly_reports = {}

        # Monthly report {"2021_month1":{"sleep.duration_ms":[8, 7.5], xxx}, "2021_month2":{}}
        self.monthly_reports = {}

        # Version
        self.version = None

        # Section Config
        self.section_config = None

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        if not hasattr(self, 'last_emailed_report_ms'):
            self.last_emailed_report_ms = None
        
        # Added: 9/14/2023
        if not hasattr(self, 'current_weekly_report_ms'):
            self.current_weekly_report_ms = None
        
        if not hasattr(self, 'current_monthly_report_ms'):
            self.current_monthly_report_ms = None

        if not hasattr(self, 'weekly_reports'):
            self.weekly_reports = {}

        if not hasattr(self, 'monthly_reports'):
            self.monthly_reports = {}

        if not hasattr(self, 'version'):
            self.version = None

        if not hasattr(self, 'section_config'):
            self.section_config = None
        return

    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        if self.version != VERSION:
            self.version = VERSION
            # Retreive location state
            daily_report_state = self.parent.get_location_property(botengine, DAILYREPORT_STATE_VARIABLE_NAME)
            if daily_report_state is None:
                daily_report_state = {}

            # Update the version
            daily_report_state['version'] = VERSION
            self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, daily_report_state)

            # Set configuration
            if self.section_config is None:
                self.section_config = daily_report_state.get("section_config", None)

            self._ask_questions(botengine)
            
        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">destroy()")
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
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">occupancy_status_updated()")
        if 'SLEEP' in status and REASON_ML in reason and self.started_sleeping_ms is None:
            # Started sleeping
            self.started_sleeping_ms = botengine.get_timestamp()

            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">occupancy_status_updated() started_sleeping_ms={} rh={}".format(self.started_sleeping_ms, self.parent.get_relative_time_of_day(botengine)))
            if self.parent.get_relative_time_of_day(botengine) > 12.0:
                # Went to sleep before midnight - send out the daily report now.
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|occupancy_status_updated() - Send completion status for todays report: {}".format(self.current_report_ms))
                self.last_emailed_report_ms = self.current_report_ms
                report = botengine.get_state(DAILY_REPORT_ADDRESS, timestamp_ms=self.current_report_ms)
                if report is not None:
                    # Notify that the daily report has completed
                    dailyreport.report_status_updated(botengine, self.parent, report, status=dailyreport.REPORT_STATUS_COMPLETED)

        if 'SLEEP' not in status and 'S2H' not in status and self.started_sleeping_ms is not None:
            # Stopped sleeping
            self.started_sleeping_ms = None
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<occupancy_status_updated()")
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

        name = botengine.get_formatted_name_by_user_id(question_object.user_id)
        if name is not None:
            # NOTE: 'This service has been turned on by ___'
            message = " " + _("by {}").format(name)
        else:
            message = ""

        if question_object.key_identifier == SERVICE_KEY_ACTIVE:

            # Services are turned on
            if utilities.get_answer(question_object):
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|question_answered() Enabled")
                analytics.track(botengine, self.parent, "service_dailyreport_activated")
                self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, {SERVICE_KEY_ACTIVE: True})
                # NOTE: GPT service turned on.
                self.parent.narrate(botengine,
                                    title=_("Daily Report services activated."),
                                    description=_("Daily Reports have been turned on{}.").format(message),
                                    priority=botengine.NARRATIVE_PRIORITY_INFO,
                                    icon="file-alt",
                                    icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                                    question_key=SERVICE_KEY_ACTIVE,
                                    event_type="dailyreport.activated")
            else:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|question_answered() disabled")
                analytics.track(botengine, self.parent, "service_dailyreport_deactivated")
                self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, {SERVICE_KEY_ACTIVE: False})
                # NOTE: GPT service turned off.
                self.parent.narrate(botengine,
                                    title=_("Daily Report services deactivated."),
                                    description=_("Daily Reports have been turned off{}.").format(message),
                                    priority=botengine.NARRATIVE_PRIORITY_INFO,
                                    icon="file-alt",
                                    icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                                    question_key=SERVICE_KEY_ACTIVE,
                                    event_type="dailyreport.deactivated")
        else:
            return
        self._ask_questions(botengine)
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
    
    def capture_insight(self, botengine, insight_json):
        """
        Capture an insight

            {
                "insight_id": "id",
                "value": value,
                "title": "Human readable title for end-users",
                "description": "Human readable description for end-users",
                "device_id": "device_id_reference_if_available",
                "device_desc": "device nickname",
                "updated_ms": timestamp_ms
            }

        If value is None, then the insight gets deleted if it exists.

        :param botengine:
        :param insight_json:
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">capture_insight() insight_json={}".format(json.dumps(insight_json)))
        if not self._is_active(botengine):
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<capture_insight() Service is not enabled")
            return
        if len(self.parent.devices) == 0 and not self.parent.deviceless_trends:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<capture_insight() No devices or deviceless trends")
            return

        insight_id = insight_json.get('insight_id', None)
        if insight_id is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("<capture_insight() Missing insight_id: insight_json={}".format(json.dumps(insight_json)))
            return
        
        section_id = self._section_id_for_insight(botengine, insight_id)

        if section_id is None:
            # This insight is not reported in the daily report
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<capture_insight() section_id is None")
            return
        # This insight is associated with this section

        week_key = self._report_key(botengine, report_address=WEEKLY_REPORT_ADDRESS, date=self.parent.get_local_datetime(botengine))
        month_key = self._report_key(botengine, report_address=MONTHLY_REPORT_ADDRESS, date=self.parent.get_local_datetime(botengine))
        
        if self._weekly_reports_enabled(botengine):
            if week_key not in self.weekly_reports:
                self.weekly_reports[week_key] = {}
        if self._monthly_reports_enabled(botengine):
            if month_key not in self.monthly_reports:
                self.monthly_reports[month_key] = {}

        value = insight_json.get('value', None)
        if value is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|capture_insight() Remove insight: insight_id={}".format(insight_id))

            self._add_entry(botengine, section_id, comment=None, identifier=f"insight-{insight_id}")
            
            # # Remove it from the report
            # if insight_id in self.weekly_reports[week_key]:
            #     del self.weekly_reports[week_key][insight_id]
            # if insight_id in self.monthly_reports[month_key]:
            #     del self.monthly_reports[month_key][insight_id]

            # # Remove the key if it's empty
            # if len(self.weekly_reports[week_key]) == 0:
            #     del self.weekly_reports[week_key]
            # if len(self.monthly_reports[month_key]) == 0:
            #     del self.monthly_reports[month_key]
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<capture_insight() value is None")
            return
        
        description = insight_json.get('description', None)
        if description is not None:
            self._add_entry(botengine, section_id, comment=description, identifier=f"insight-{insight_id}")
        
        if self._weekly_reports_enabled(botengine):
            if f"insight-{insight_id}" not in self.weekly_reports[week_key]:
                self.weekly_reports[week_key][f"insight-{insight_id}"] = {
                    "title": insight_json.get('title', "Insight"),
                    "values": {},
                }

        if self._monthly_reports_enabled(botengine):
            if f"insight-{insight_id}" not in self.monthly_reports[month_key]:
                self.monthly_reports[month_key][f"insight-{insight_id}"] = {
                    "title": insight_json.get('title', "Insight"),
                    "values": {},
                }

        # Extrapolate some trend data into a format that is more useful for the report
        # Assign the data to the appropriate day of the week
        day_of_week = self.parent.get_local_datetime(botengine).weekday()
        day = self.parent.get_local_datetime(botengine).day

        if insight_id in ['sleep.duration_ms']:
            # Milliseconds are represented in hours
            value = round(value / 1000.0 / 60 / 60, 1)
        elif insight_id in ['sleep.bedtime_ms', 'sleep.wakeup_ms', 'sleep.sleep_prediction_ms', 'sleep.wake_prediction_ms']:
            # Relative time calculations will be constrained between 12.0 and 36.0 to allow for statistical analysis
            relative_time = self.parent.get_relative_time_of_day(botengine, value)
            if 12 >= relative_time >= 0:
                relative_time += 24
                day_of_week == day_of_week - 1 if day_of_week > 0 else 6

            value = relative_time

        if self._weekly_reports_enabled(botengine):
            if day_of_week not in self.weekly_reports[week_key][f"insight-{insight_id}"]["values"]:
                self.weekly_reports[week_key][f"insight-{insight_id}"]["values"][day_of_week] = []
            self.weekly_reports[week_key][f"insight-{insight_id}"]["values"][day_of_week].append(value)
        if self._monthly_reports_enabled(botengine):
            if day not in self.monthly_reports[month_key][f"insight-{insight_id}"]["values"]:
                self.monthly_reports[month_key][f"insight-{insight_id}"]["values"][day] = []
            self.monthly_reports[month_key][f"insight-{insight_id}"]["values"][day].append(value)

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<capture_insight()")
        return
    
    def trend_processed(self, botengine, trend_info):
        """
        Announce to all microservices that a trend was processed for a given ID, with computed results.

        In a typical implementation, a microservice might capture a trend and then listen for the processed results which allow the microservice
        to generate an alert if multiple trends have not been going in the correct direction lately.

        This will distribute the following type of information locally (where everything but the 'trend_id' is coming from the trend_info dictionary)
            {
                "trend_id": trend_id,
                "value": value,
                "std": float(std),
                "avg": float(avg),
                "zscore": float(zscore),
                "display": display,
                "updated_ms": int(botengine.get_timestamp())
            }
        :param botengine: BotEngine environment
        :param trend_info: Trend information
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(">trend_processed() trend_info={}".format(json.dumps(trend_info)))

        if not self._is_active(botengine):
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<trend_processed() Service is not enabled")
            return
        # Trends are dependent upon the device being present or by the parent location.
        # TODO: Deprecated deviceless_trends
        if len(self.parent.devices) == 0 and not self.parent.deviceless_trends:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<trend_processed() No devices or deviceless trends")
            return
        
        # Ignore midnight trends + 30 minute buffer to avoid double reporting and zerod trends
        if self.parent.get_relative_time_of_day(botengine) <= 0.5:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<trend_processed() Midnight trend")
            return
        
        # Check for required fields
        trend_id = trend_info.get('trend_id', None)
        value = trend_info.get('value', None)
        if trend_id is None or value is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|trend_processed() Missing fields in trend data: {}".format(trend_info))
            return
        
        # Get the section ID for this trend
        section_id = self._section_id_for_trend(botengine, trend_id)
        if section_id is None:
            # This trend is not reported in the daily report
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|trend_processed() Trend is not reported in the daily report: {}".format(trend_id))
            return

        # Get the trend metadata and check for required fields
        trends_metadata = botengine.get_state(TRENDS_METADATA_NAME)
        if trends_metadata is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|trend_processed() Missing trend metadata: {}".format(trend_id))
            return
        
        metadata = trends_metadata.get(trend_id, None)
        if metadata is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|trend_processed() Missing metadata for trend: {}".format(trend_id))
            return
        
        if metadata.get("hidden", False):
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|trend_processed() Trend is hidden: {}".format(trend_id))
            return

        # This trend is associated with this section
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|trend_processed() Reporting trend: {}".format(trend_info))

        # Include in daily report
        # Check this
        # TODO: Some trends are represented through insights or other means, and should not be included in the daily report
        if trend_info.get('daily', False) or True:
            # This trend is a daily trend
            display = trend_info.get('display', None)
                
            if display is None:
                # No comment, remove trend

                self._add_entry(botengine, section_id, comment=None, identifier=f"trend-{trend_id}")
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("<trend_processed() Missing comment for trend: {}".format(trend_id))
                return

            # Create a comment based on the trend data
            comment = None
            if not self.parent.is_on_vacation(botengine):
                comment = self.get_daily_comment(botengine, trend_info)
            

            # Ignore any trends where comments are excluded
            if comment is not None:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|trend_processed() comment={}".format(comment))
                # If not given a prescribed comment, and has a title, use the title and display value as the comment
                if len(comment) == 0 and metadata.get("title", None) is not None:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|trend_processed() metadata title={}".format(metadata.get("title", None)))
                    comment = "{}: {}".format(metadata.get("title", None), display)
            
                self._add_entry(botengine, section_id, comment=comment, identifier=f"trend-{trend_id}")
            else:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|trend_processed() No comment for trend: {}".format(trend_id))
        
        # Track this trend for weekly and monthly reports
        timestamp = trend_info.get('updated_ms', botengine.get_timestamp())
        daily_key = self._report_key(botengine, report_address=DAILY_REPORT_ADDRESS, date=self.parent.get_local_datetime_from_timestamp(botengine, timestamp))
        weekly_key = self._report_key(botengine, report_address=WEEKLY_REPORT_ADDRESS, date=self.parent.get_local_datetime_from_timestamp(botengine, timestamp))
        monthly_key = self._report_key(botengine, report_address=MONTHLY_REPORT_ADDRESS, date=self.parent.get_local_datetime_from_timestamp(botengine, timestamp))

        if self._weekly_reports_enabled(botengine):
            if weekly_key not in self.weekly_reports:
                self.weekly_reports[weekly_key] = {}
            if f"trend-{trend_id}" not in self.weekly_reports[weekly_key]:
                self.weekly_reports[weekly_key][f"trend-{trend_id}"] = {}

        if self._monthly_reports_enabled(botengine):
            if monthly_key not in self.monthly_reports:
                self.monthly_reports[monthly_key] = {}
            if f"trend-{trend_id}" not in self.monthly_reports[monthly_key]:
                self.monthly_reports[monthly_key][f"trend-{trend_id}"] = {}
                
        updated_ms = trend_info.get('updated_ms', None)
        if updated_ms is None:
            updated_ms = botengine.get_timestamp()
        
        # Store daily trends for weekly report metrics
        if self._weekly_reports_enabled(botengine):
            self.weekly_reports[weekly_key][f"trend-{trend_id}"][daily_key] = trend_info

        # Store weekly trends for monthly report metrics
        if self._monthly_reports_enabled(botengine):
            self.monthly_reports[monthly_key][f"trend-{trend_id}"][weekly_key] = trend_info
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<trend_processed()")

    def get_daily_comment(self, botengine, trend_info):
        """
        Get comment for daily report
        :param botengine: BotEngine environment
        :param trend_info: Trend information
        :return: comment
        """
        trend_id = trend_info.get('trend_id', None)

        value = trend_info.get('value', None)
        std = trend_info.get('std', None)
        avg = trend_info.get('avg', None)
        zscore = trend_info.get('zscore', None)
        comment = None
 
        #All possible comments
        possible_comments = {
            "trend.total_falls": {
                "value > 0": [
                    _("A fall might have occurred today."),
                    _("Possibly, a tumble was taken today."),
                    _("It’s likely that a fall happened today.")
                ]
            },
            "trend.bedtime": {
                "std < 600000 and zscore > 2": [
                    _("Went to bed later than usual."),
                    _("Stayed up later last night."),
                    _("Stayed up past normal bedtime."),
                ],
                "std < 600000 and zscore < -2": [
                    _("Went to bed earlier than usual."),
                    _("Bedtime was earlier than normal."),
                    _("Went to bed a little before the usual time.")
                ],
                "zscore > 2": [
                    _("Went to bed much later than usual."),
                    _("Stayed up significantly later last night."),
                    _("Stayed up well past normal bedtime."),
                    _("Went to bed much later than usual.")
                ],
                "2 >= zscore > 0.5": [
                    _("Went to bed a bit later than usual last night."),
                    _("Bedtime was slightly delayed last night."),
                    _("Stayed up a tad past the usual bedtime."),
                    _("Went to bed shortly after normal time.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("Went to bed at the usual time."),
                    _("Turned in for the night at the regular time."),
                    _("Bedtime was the same as usual last night.")
                ],
                "-0.5 >= zscore > -2": [
                    _("Went to bed a bit earlier last night."),
                    _("Turned in slightly earlier than normal."),
                    _("Went to bed a little earlier last night."),
                    _("Bedtime was just before the usual time.")
                ],
                "-2 >= zscore": [
                    _("Went to bed much earlier last night."),
                    _("Bedtime was significantly earlier last night."),
                    _("Turned in much earlier than usual."),
                    _("Went to bed well before the regular time.")
                ]
            },
            "trend.sleep_bathroom_visits": {
                "value == 0 and avg >= 1": [
                    _("Did not use the bathroom last night."),
                    _("No bathroom visits occurred last night."),
                    _("No bathroom break was needed last night.")
                ],
                "value > 0": [
                    _("Got up to use the bathroom last night."),
                    _("Made a trip to the bathroom last night."),
                    _("Took a bathroom break last night.")
                ]
            },
            "trend.sleep_duration": {
                "zscore > 2": [
                    _("Slept much longer than usual last night."),
                    _("Had significantly more sleep last night."),
                    _("Slept for a much longer duration than usual."),
                    _("Sleep was considerably longer last night."),
                    _("Had an extended sleep last night."),
                    _("Slept well beyond the usual time."),
                    _("Sleep duration was much longer than normal."),
                    _("Had a significantly longer sleep last night."),
                    _("Slept for a far longer period than usual.")
                ],
                "2 >= zscore > 0.5": [
                    _("Slept longer than usual."),
                    _("Had a slightly longer sleep than normal."),
                    _("Sleep duration was longer than usual."),
                    _("Enjoyed a longer rest than normal."),
                    _("Slept a bit longer than the usual time."),
                    _("Experienced an extended sleep period."),
                    _("Rest lasted longer than normal."),
                    _("Slept for a longer time than usual."),
                    _("Sleep was somewhat longer than usual."),
                    _("Had a longer sleep than normal.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("Slept the usual amount."),
                    _("Had the regular amount of sleep."),
                    _("Sleep duration was normal."),
                    _("Enjoyed the typical amount of rest."),
                    _("Slept the same amount as usual."),
                    _("Experienced the usual sleep period."),
                    _("Rest time was as expected."),
                    _("Slept for the usual duration."),
                    _("Sleep was just as normal."),
                    _("Had the standard amount of sleep.")
                ],
                "-0.5 >= zscore > -2": [
                    _("Slept less than usual."),
                    _("Had a shorter sleep than normal."),
                    _("Sleep duration was shorter than usual."),
                    _("Got less rest than usual."),
                    _("Slept for a shorter time than normal."),
                    _("Experienced a reduced sleep period."),
                    _("Rest time was less than normal."),
                    _("Slept for less time than usual."),
                    _("Sleep was shorter than usual."),
                    _("Had less sleep than the usual amount.")
                ]
            },
            "trend.wakeup": {
                "std < 600000 and zscore > 2": [
                    _("Woke up later than usual."),
                    _("Got up later than typical."),
                    _("Wake-up time was later than usual."),
                    _("Woke up a bit later than normal."),
                    _("Arose later than usual."),
                    _("Woke up past the usual hour."),
                    _("Got up later than typical."),
                    _("Morning started later than usual."),
                    _("Wake-up was delayed compared to usual."),
                    _("Got out of bed later than usual.")
                ],
                "std < 600000 and zscore < -2": [
                    _("Woke up earlier than usual."),
                    _("Got up earlier than typical."),
                    _("Wake-up time was earlier than usual."),
                    _("Woke up a bit earlier than normal."),
                    _("Arose earlier than usual."),
                    _("Woke up before the usual hour."),
                    _("Got up earlier than typical."),
                    _("Morning started earlier than usual."),
                    _("Wake-up was ahead of schedule compared to usual."),
                    _("Got out of bed earlier than usual.")
                ],
                "zscore > 2": [
                    _("Woke up much later than usual."),
                    _("Got up significantly later than typical."),
                    _("Wake-up time was much later than usual."),
                    _("Woke up far later than normal."),
                    _("Arose much later than usual."),
                    _("Woke up well past the usual hour."),
                    _("Got up much later than typical."),
                    _("Morning started much later than usual."),
                    _("Wake-up was considerably delayed compared to usual."),
                    _("Got out of bed much later than usual.")
                ],
                "2 >= zscore > 0.5": [
                    _("Woke up later than usual."),
                    _("Got up later than typical."),
                    _("Wake-up time was later than usual."),
                    _("Woke up a bit later than normal."),
                    _("Arose later than usual."),
                    _("Woke up past the usual hour."),
                    _("Got up later than typical."),
                    _("Morning started later than usual."),
                    _("Wake-up was delayed compared to usual."),
                    _("Got out of bed later than usual.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("Woke up around the usual amount."),
                    _("Got up at the typical time."),
                    _("Wake-up time was about the usual."),
                    _("Woke up approximately at the normal hour."),
                    _("Arose around the usual time."),
                    _("Wake-up was typical."),
                    _("Got up at the usual hour."),
                    _("Morning started around the usual time."),
                    _("Wake-up was standard."),
                    _("Got out of bed at the usual time.")
                ],
                "-0.5 >= zscore > -2": [
                    _("Woke up earlier than usual."),
                    _("Got up earlier than typical."),
                    _("Wake-up time was earlier than usual."),
                    _("Woke up a bit earlier than normal."),
                    _("Arose earlier than usual."),
                    _("Woke up before the usual hour."),
                    _("Got up earlier than typical."),
                    _("Morning started earlier than usual."),
                    _("Wake-up was ahead of schedule compared to usual."),
                    _("Got out of bed earlier than usual.")
                ],
                "-2 >= zscore": [
                    _("Woke up much earlier than usual."),
                    _("Got up significantly earlier than typical."),
                    _("Wake-up time was much earlier than usual."),
                    _("Woke up far earlier than normal."),
                    _("Arose much earlier than usual."),
                    _("Woke up well before the usual hour."),
                    _("Got up much earlier than typical."),
                    _("Morning started much earlier than usual."),
                    _("Wake-up was considerably earlier compared to usual."),
                    _("Got out of bed much earlier than usual.")
                ]
            },
            "trend.sleep_movement": {
                "zscore > 2": [
                    _("Experienced much more movement in sleep than usual."),
                    _("There was significantly more movement in sleep than usual."),
                    _("Had much more movement during sleep than usual."),
                    _("The amount of movement in sleep was significantly higher."),
                    _("Experienced a much greater degree of movement in sleep than usual."),
                    _("There was much more movement in sleep."),
                    _("Sleep featured much more movement than usual."),
                    _("Sleep included significantly more movement than usual."),
                    _("Experienced increased movement in sleep."),
                    _("Had much more movement in sleep than usual.")
                ],
                "2 >= zscore > 0.5": [
                    _("Experienced more movement in sleep than usual."),
                    _("There was more movement in sleep."),
                    _("Had more movement during sleep than usual."),
                    _("The amount of movement in sleep was higher than usual."),
                    _("Experienced a greater degree of movement in sleep than usual."),
                    _("There was more movement during sleep last night."),
                    _("Sleep featured more movement than usual."),
                    _("Sleep included more movement than usual."),
                    _("Experienced increased movement in sleep than usual."),
                    _("Had more movement in sleep.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("Experienced the normal amount of movement in sleep."),
                    _("There was the usual amount of movement in sleep."),
                    _("Had the typical amount of movement during sleep."),
                    _("The amount of movement in sleep was normal."),
                    _("Experienced the regular level of movement during sleep."),
                    _("Sleep featured the standard amount of movement."),
                    _("Sleep included the expected amount of movement."),
                    _("Had the usual degree of movement in sleep."),
                    _("Experienced the customary amount of movement in sleep."),
                    _("Had the normal amount of movement in sleep.")
                ],
                "-0.5 >= zscore > -2": [
                    _("Experienced less movement during sleep than usual."),
                    _("There was reduced movement during sleep compared to usual."),
                    _("Had less movement during sleep than normal."),
                    _("The amount of movement during sleep was lower than usual."),
                    _("Experienced a decrease in movement during sleep."),
                    _("There was less movement during sleep than typical."),
                    _("Sleep featured decreased movement compared to usual."),
                    _("Sleep included less movement than normal."),
                    _("Experienced reduced movement during sleep."),
                    _("Had less movement during sleep than usual.")

                ],
                "-2 >= zscore": [
                    _("Experienced much less movement during sleep than usual."),
                    _("There was significantly less movement during sleep than normal."),
                    _("Had much less movement during sleep than typical."),
                    _("The amount of movement during sleep was significantly lower than usual."),
                    _("Experienced a much lower degree of movement during sleep."),
                    _("There was much less movement during sleep than usual."),
                    _("Sleep featured much reduced movement compared to usual."),
                    _("Sleep included significantly less movement than normal."),
                    _("Experienced much decreased movement during sleep."),
                    _("Had much less movement during sleep than usual.")
                ]
            },
            "trend.nap_duration": {
                "zscore > 2": [
                    _("Spent much more time napping than usual."),
                    _("Significantly more time was spent napping compared to usual."),
                    _("Napped for a much longer duration than usual."),
                    _("The amount of time spent napping was much greater than usual."),
                    _("Indulged in much more nap time than usual."),
                    _("Nap duration was much longer than usual."),
                    _("Took significantly more naps than usual."),
                    _("Had much more frequent naps than usual.")
                ],
                "2 >= zscore > 0.5": [
                    _("Spent more time napping than usual."),
                    _("There was increased time spent napping compared to usual."),
                    _("Napped for a longer duration than usual."),
                    _("The amount of time spent napping was greater than usual."),
                    _("Indulged in more nap time than usual."),
                    _("There was an increase in nap time compared to usual."),
                    _("Nap duration was longer than usual."),
                    _("Took more naps than usual."),
                    _("Spent extra time napping compared to usual."),
                    _("Had more frequent naps than usual.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("Napping time was around the usual amount."),
                    _("Nap duration was typical."),
                    _("The amount of time spent napping was about the usual."),
                    _("Napping followed the usual pattern."),
                    _("Nap time was regular."),
                    _("Had the usual nap duration."),
                    _("Napping routine was standard."),
                    _("Nap frequency was normal."),
                    _("The time spent napping was typical."),
                    _("Nap schedule was as expected.")
                ],
                "-0.5 >= zscore > -2": [
                    _("Spent less time napping than usual."),
                    _("There was reduced time spent napping compared to usual."),
                    _("Napped for a shorter duration than usual."),
                    _("The amount of time spent napping was less than usual."),
                    _("Indulged in less nap time than usual."),
                    _("There was a decrease in nap time compared to usual."),
                    _("Nap duration was shorter than usual."),
                    _("Took fewer naps than usual."),
                    _("Spent less time napping compared to usual."),
                    _("Had less frequent naps than usual.")
                ],
                "-2 >= zscore": [
                    _("Spent much less time napping than usual."),
                    _("Significantly less time was spent napping compared to usual."),
                    _("Napped for a much shorter duration than usual."),
                    _("The amount of time spent napping was much less than usual."),
                    _("Indulged in much less nap time than usual."),
                    _("There was a considerable decrease in nap time compared to usual."),
                    _("Nap duration was much shorter than usual."),
                    _("Took significantly fewer naps than usual."),
                    _("Spent much less time napping compared to usual."),
                    _("Had much less frequent naps than usual.")
                ]
            },
            "trend.mobility_duration": {
                "zscore > 2": [
                    _("Moved much more than usual."),
                    _("Exhibited significantly more movement than usual."),
                    _("Had a much higher amount of movement than usual."),
                    _("Experienced much more activity than usual."),
                    _("Showed much increased movement compared to usual."),
                    _("Movement was much more pronounced than usual."),
                    _("Engaged in much more activity than usual."),
                    _("Had much increased movement compared to usual."),
                    _("Experienced much more activity than usual."),
                    _("Had much more movement than usual.")
                ],
                "2 >= zscore > 0.5": [
                    _("Moved more than usual."),
                    _("Exhibited more movement than usual."),
                    _("Had a higher amount of movement than usual."),
                    _("Experienced more activity than usual."),
                    _("Showed increased movement compared to usual."),
                    _("Movement was more pronounced than usual."),
                    _("Engaged in more activity than usual."),
                    _("Had increased movement compared to usual."),
                    _("Experienced increased movement compared to usual."),
                    _("Had more movement than usual.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("Moved the usual amount."),
                    _("Exhibited typical movement."),
                    _("Had the usual amount of movement."),
                    _("Showed regular activity."),
                    _("Experienced the expected amount of movement."),
                    _("Movement was typical."),
                    _("Showed the usual amount of activity."),
                    _("Engaged in the customary amount of movement."),
                    _("Experienced the expected amount of activity."),
                    _("Had the expected amount of movement.")
                ],
                "-0.5 >= zscore > -2":[
                    _("There was reduced movement compared to usual."),
                    _("Had a lower amount of movement than usual."),
                    _("The amount of movement was less than usual."),
                    _("Experienced less activity than usual."),
                    _("There was a decrease in movement compared to usual."),
                    _("Movement was less pronounced than usual."),
                    _("Exhibited less movement than usual."),
                    _("Engaged in less activity than usual."),
                    _("Experienced decreased movement compared to usual.")
                ],
                "-2 >= zscore": [
                    _("Moved much less than usual."),
                    _("Exhibited much less movement than usual."),
                    _("Had a much lower amount of movement than usual."),
                    _("Experienced much less activity than usual."),
                    _("Showed decreased movement compared to usual."),
                    _("Movement was much less pronounced than usual."),
                    _("Engaged in much less activity than usual."),
                    _("Had decreased movement compared to usual."),
                    _("Experienced decreased movement compared to usual."),
                    _("Had much less movement than usual.")
                ]
            },
            "trend.mobility_rooms": {
                "zscore > 2": [
                    _("Moved between rooms much more than usual."),
                    _("Exhibited significantly more movement between rooms than usual."),
                    _("Had a much higher amount of room-to-room movement than usual."),
                    _("Experienced much more room-to-room activity than usual."),
                    _("Showed much increased movement between rooms compared to usual."),
                    _("Movement between rooms was much more pronounced than usual."),
                    _("Engaged in much more room-to-room activity than usual."),
                    _("Had much increased movement between rooms compared to usual."),
                    _("Experienced much increased movement between rooms compared to usual."),
                    _("Had much more room-to-room movement than usual.")
                ],
                "2 >= zscore > 0.5": [
                    _("Moved between rooms more than usual."),
                    _("Exhibited more movement between rooms than usual."),
                    _("Had a higher amount of room-to-room movement than usual."),
                    _("Experienced more room-to-room activity than usual."),
                    _("Showed increased movement between rooms compared to usual."),
                    _("Movement between rooms was more pronounced than usual."),
                    _("Engaged in more room-to-room activity than usual."),
                    _("Had increased movement between rooms compared to usual."),
                    _("Experienced increased movement between rooms compared to usual."),
                    _("Had more room-to-room movement than usual.")
                ],
                "0.5 >= zscore > -0.5":[
                    _("Moved between rooms the usual amount."),
                    _("There was typical movement between rooms."),
                    _("A usual amount of room-to-room movement occurred."),
                    _("The amount of movement between rooms was normal."),
                    _("The regular level of room-to-room activity took place."),
                    _("There was no change in the movement between rooms."),
                    _("The room-to-room movement was typical."),
                    _("The usual amount of room-to-room activity happened."),
                    _("The expected amount of movement between rooms was experienced.")
                ],
                "-0.5 >= zscore > -2": [
                    _("Moved between rooms less than usual."),
                    _("Exhibited less movement between rooms than usual."),
                    _("Had a lower amount of room-to-room movement than usual."),
                    _("Experienced less room-to-room activity than usual."),
                    _("Showed decreased movement between rooms compared to usual."),
                    _("Movement between rooms was less pronounced than usual."),
                    _("Engaged in less room-to-room activity than usual."),
                    _("Had decreased movement between rooms compared to usual."),
                    _("Experienced decreased movement between rooms compared to usual."),
                    _("Had less room-to-room movement than usual.")
                ],
                "-2 >= zscore": [
                    _("Moved between rooms much less frequently than usual."),
                    _("Exhibited much less movement between rooms than usual."),
                    _("Had much less frequent room-to-room movements than usual."),
                    _("Experienced much less frequent room-to-room activity than usual."),
                    _("Showed much less frequent movement between rooms than usual."),
                    _("Movement between rooms was much less frequent than usual."),
                    _("Engaged in much less frequent room-to-room activity than usual."),
                    _("Had much less frequent movement between rooms than usual."),
                    _("Experienced much less frequent room-to-room activity than usual."),
                    _("Had much less frequent room-to-room movements than usual.")
                ]
            },
            "sitting": {
                "zscore > 2": [
                    _("Spent much more time sitting down today."),
                    _("There was significantly more time spent sitting down today."),
                    _("Sat down for a much longer duration today."),
                    _("Spent a much longer duration sitting down today."),
                    _("Spent much extra time sitting down today."),
                    _("Considerably increased sitting time today."),
                    _("Sitting duration today was much longer."),
                    _("Sat down significantly more today."),
                    _("Spent much extra time sitting today."),
                    _("Had much more sitting time today.")
                ],
                "2 >= zscore > 0.5": [
                    _("Spent more time sitting down today."),
                    _("Increased time spent sitting down today."),
                    _("Sat down for a longer duration today."),
                    _("Spent a longer duration sitting down today."),
                    _("Spent extra time sitting down today."),
                    _("Increased sitting time today."),
                    _("Sitting duration today was longer."),
                    _("Sat down more today."),
                    _("Spent extra time sitting today."),
                    _("Had more sitting time today.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("Spent the usual amount of time sitting down today."),
                    _("Typical time spent sitting down today."),
                    _("Sat down for the usual duration today."),
                    _("Spent the usual amount of time sitting today."),
                    _("Sitting duration today was typical."),
                    _("No change in sitting time today."),
                    _("Sitting duration today was typical."),
                    _("Showed the usual amount of sitting time today."),
                    _("Engaged in the customary amount of sitting today."),
                    _("Expected amount of sitting time today.")
                ],
                "-0.5 >= zscore > -2": [
                    _("Spent less time sitting down today."),
                    _("Reduced time spent sitting down today."),
                    _("Sat down for a shorter duration today."),
                    _("Spent a shorter duration sitting down today."),
                    _("Spent less time sitting today."),
                    _("Decreased sitting time today."),
                    _("Sitting duration today was shorter."),
                    _("Sat down less today."),
                    _("Spent less time sitting today."),
                    _("Decrease in sitting time today.")
                ],
                "-2 >= zscore": [
                    _("Spent much less time sitting down today."),
                    _("Significantly less time spent sitting down today."),
                    _("Sat down for a much shorter duration today."),
                    _("Spent a much shorter duration sitting down today."),
                    _("Spent much less time sitting today."),
                    _("Considerable decrease in sitting time today."),
                    _("Sitting duration today was much shorter."),
                    _("Sat down much less today."),
                    _("Spent much less time sitting today."),
                    _("Significant decrease in sitting time today.")
                ]
            },
            "trend.bathroom_visits": {
                "value < 1": [
                    _("Did not appear to visit the bathroom today."),
                    _("No indication of visiting the bathroom today."),
                    _("Seemed not to have visited the bathroom today."),
                    _("No sign of using the bathroom today."),
                    _("Did not seem to have gone to the bathroom today."),
                    _("Did not appear to have gone to the bathroom today."),
                    _("No appearance of using the bathroom today."),
                    _("Did not appear to have used the bathroom today."),
                    _("No indication of using the bathroom today.")
                ],
                "value > 1": [
                    _("Bathroom was visited around {} times today.".format(value)),
                    _("Approximately {} visits to the bathroom today.".format(value)),
                    _("Bathroom saw about {} visits today.".format(value)),
                    _("Around {} visits to the bathroom were recorded today.".format(value)),
                    _("Approximately {} trips to the bathroom occurred today.".format(value)),
                    _("There were {} bathroom visits today.".format(value)),
                    _("Bathroom was used about {} times today.".format(value)),
                    _("There were about {} bathroom visits today.".format(value)),
                    _("Approximately {} bathroom trips today.".format(value)),
                    _("About {} bathroom visits occurred today.".format(value))
                ],
                "value == 1": [
                    _("Only one trip was made to the bathroom."),
                    _("The bathroom had a single visit."),
                    _("There was one visit to the bathroom.")
                ]
            },
            "trend.bathroom_duration": {
                "zscore > 2": [
                    _("Spent much more time than usual in the bathroom today."),
                    _("Stayed in the bathroom for significantly longer than usual today."),
                    _("Had a much longer bathroom duration today."),
                    _("Bathroom duration was much longer than usual today."),
                    _("Spent a considerable extra amount of time in the bathroom today."),
                    _("Considerably increased bathroom duration today."),
                    _("Bathroom stay today was much longer than usual."),
                    _("Spent significantly more time in the bathroom today."),
                    _("Had extra bathroom time today."),
                    _("Bathroom stay today was much longer than usual.")
                ],
                "2 >= zscore > 0.5": [
                    _("Spent more time than usual in the bathroom today."),
                    _("Stayed in the bathroom for longer than usual today."),
                    _("Had a longer bathroom duration today."),
                    _("Bathroom duration was longer than usual today."),
                    _("Spent extra time in the bathroom today."),
                    _("Increased bathroom duration today."),
                    _("Bathroom stay today was longer than usual."),
                    _("Spent more time in the bathroom today."),
                    _("Had extra bathroom time today."),
                    _("Bathroom stay today was longer than usual.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("Spent the usual amount of time in the bathroom today."),
                    _("Stayed in the bathroom for the usual duration today."),
                    _("Had the usual bathroom duration today."),
                    _("Bathroom duration was typical today."),
                    _("No change in bathroom time today."),
                    _("Bathroom stay today was typical."),
                    _("Showed the usual bathroom time today."),
                    _("Engaged in the customary bathroom duration today."),
                    _("Expected amount of bathroom time today."),
                    _("Experienced the expected bathroom duration today.")
                ],
                "-0.5 >= zscore > -2": [
                    _("Spent less time than usual in the bathroom today."),
                    _("Stayed in the bathroom for a shorter duration today."),
                    _("Had a shorter bathroom duration today."),
                    _("Bathroom duration was shorter than usual today."),
                    _("Spent less time in the bathroom today."),
                    _("Decreased bathroom duration today."),
                    _("Bathroom stay today was shorter than usual."),
                    _("Spent less time in the bathroom today."),
                    _("Had less bathroom time today.")
                ],
                "-2 >= zscore": [
                    _("Spent much less time than usual in the bathroom today."),
                    _("Stayed in the bathroom for significantly less time than usual today."),
                    _("Had a much shorter bathroom duration today."),
                    _("Bathroom duration was much shorter than usual today."),
                    _("Spent considerably less time in the bathroom today."),
                    _("Considerably decreased bathroom duration today."),
                    _("Bathroom stay today was much shorter than usual."),
                    _("Spent significantly less time in the bathroom today."),
                    _("Had much less bathroom time today."),
                    _("Bathroom stay today was much shorter than usual.")
                ]
            },
            "trend.shower_visits": {
                "value < 1": [
                    _("Did not appear to take a shower today."),
                    _("No indication of showering today."),
                    _("Seemed not to have taken a shower today."),
                    _("No sign of showering today."),
                    _("Did not seem to have showered today."),
                    _("Did not appear to have showered today."),
                    _("No appearance of showering today."),
                    _("Did not appear to have taken a shower today."),
                    _("No indication of taking a shower today.")
                ],
                "value > 1": [
                    _("Took approximately {} showers today.".format(int(value))),
                    _("Approximately {} showers were taken today.".format(int(value))),
                    _("Showered about {} times today.".format(int(value))),
                    _("Took {} showers today.".format(int(value))),
                    _("Had about {} shower visits today.".format(int(value))),
                    _("There were {} shower visits today.".format(int(value))),
                    _("Approximately {} showering instances today.".format(int(value))),
                    _("Took about {} showers today.".format(int(value))),
                    _("Approximately {} shower sessions today.".format(int(value))),
                    _("About {} shower visits occurred today.".format(int(value)))
                ],
                "value == 1": [
                    _("Enjoyed one shower today."),
                    _("Took a shower once today."),
                    _("Had a single shower today."),
                    _("Showered one time today.")
                ]
            },
            "trend.absent": {
                "value < 1000": [
                    _("No one appeared to leave the house."),
                    _("There was no indication that anyone left the house."),
                    _("It seemed like no one left the house."),
                    _("There was no sign of anyone leaving the house."),
                    _("No one seemed to have gone out of the house."),
                    _("It did not appear that anyone left the house."),
                    _("There was no appearance of anyone leaving the house."),
                    _("No one appeared to have gone out of the house."),
                    _("It seemed that no one left the house."),
                    _("There was no indication of anyone leaving the house.")
                ],
                "zscore > 2": [
                    _("Spent much more time away than usual."),
                    _("There was significantly more time spent away than usual."),
                    _("Spent a much longer duration away than usual."),
                    _("The amount of time spent away was much greater than usual."),
                    _("Spent much extra time away compared to usual."),
                    _("There was a considerable increase in time spent away compared to usual."),
                    _("Time away was much longer than usual."),
                    _("Spent significantly more time away than usual."),
                    _("Had much more time away than usual."),
                    _("Spent a significantly longer time away than usual.")
                ],
                "2 >= zscore > 0.5": [
                    _("Spent more time away than usual."),
                    _("There was increased time spent away compared to usual."),
                    _("Spent a longer duration away than usual."),
                    _("The amount of time spent away was greater than usual."),
                    _("Spent extra time away compared to usual."),
                    _("There was an increase in time spent away compared to usual."),
                    _("Time away was longer than usual."),
                    _("Spent more time away from home than usual."),
                    _("Had more time away than usual."),
                    _("Spent a longer time away than usual.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("Spent the usual amount of time away from home."),
                    _("The amount of time spent away from home was normal."),
                    _("Time away from home was the regular duration."),
                    _("There was no change in time away from home."),
                    _("Showed the usual amount of time away from home."),
                    _("Engaged in the customary time away from home."),
                    _("Experienced the expected amount of time away from home.")
                ],
                "-0.5 >= zscore > -2": [
                    _("Spent less time away from home than usual."),
                    _("There was reduced time spent away from home compared to usual."),
                    _("Spent a shorter duration away from home than usual."),
                    _("The amount of time spent away from home was less than usual."),
                    _("Spent less time away from home than typical."),
                    _("There was a decrease in time away from home compared to usual."),
                    _("Time away from home was shorter than usual."),
                    _("Had less time away from home than usual."),
                    _("Spent a lesser amount of time away from home than usual."),
                    _("Time away from home was reduced compared to usual.")
                ],
                "-2 >= zscore": [
                    _("Spent much less time away from home than usual."),
                    _("There was significantly less time spent away from home than usual."),
                    _("Spent a much shorter duration away from home than usual."),
                    _("The amount of time spent away from home was much less than usual."),
                    _("Spent much less time away from home compared to the usual routine."),
                    _("There was a considerable decrease in time away from home compared to usual."),
                    _("Time away from home was much shorter than usual."),
                    _("Had much less time away from home than usual."),
                    _("Spent a significantly lesser amount of time away from home than usual."),
                    _("Time away from home was significantly reduced compared to usual.")
                ]
            },
            "trend.checkedin": {
                "value < 1": [
                    _("No one has checked in today."),
                    _("There is no record of anyone being checked on today."),
                    _("No one checked in today."),
                    _("It appears that no one was checked on today."),
                    _("There was no check-in for anyone today."),
                    _("No one has checked in today."),
                    _("There was no indication of anyone checking in today."),
                    _("No one appeared to check in today."),
                    _("No check-in was recorded for anyone today."),
                    _("No one was checked on today.")
                ],
                "value == 1": [
                    _("There has been one check in."),
                    _("Just one check-in has been noted."),
                    _("Only one check-in happened."),
                    _("Only one check-in has occurred.")
                ],
                "value > 1": [
                    _("There has been {} check ins.".format(int(value))),
                    _("Today, there has been {} check ins.".format(int(value))),
                    _("It appears that there were {} check ins times today.".format(int(value))),
                    _("There were {} instances where someone checking in today.".format(int(value))),
                    _("There were {} occasions of check ins today.".format(int(value)))
                ]
            },
            "trend.visitor": {
                "zscore > 2": [
                    _("There were many more visitors than usual today."),
                    _("There were significantly more visitors today than usual."),
                    _("There were many more visitors today than usual."),
                    _("There were much more visitors today compared to usual."),
                    _("There was a considerable increase in visitors today."),
                    _("There were significantly more visitors than usual today."),
                    _("There was much more company today than usual."),
                    _("There were many more visitors than usual today."),
                    _("There was a substantial increase in visitors today."),
                    _("There was much more visitation than usual today.")
                ],
                "2 >= zscore > 0.5": [
                    _("There were more visitors than usual."),
                    _("There were increased visitors compared to usual."),
                    _("There was a higher number of visitors than usual."),
                    _("There were more visitors than usual."),
                    _("There was an increase in visitors compared to usual."),
                    _("There were additional visitors today."),
                    _("There were more visitors today than usual."),
                    _("There were more guests than usual."),
                    _("There was more visitation than usual."),
                    _("There were a greater number of visitors than usual.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("There were the usual amount of visitors."),
                    _("There were typical visitors."),
                    _("There were the usual visitors."),
                    _("The number of visitors was normal."),
                    _("There were the regular visitors."),
                    _("There was no change in visitors."),
                    _("Visitors were typical."),
                    _("There were the usual visitors."),
                    _("There were the customary visitors."),
                    _("There was the expected amount of visitors.")
                ],
                "-0.5 >= zscore > -2": [
                    _("There was less interaction with people today."),
                    _("There was reduced interaction with people today."),
                    _("There were fewer social interactions today."),
                    _("There was a lower level of interaction with people today."),
                    _("There was less interaction with others today."),
                    _("Today's interaction with people was lower."),
                    _("Interaction with others today was less than usual."),
                    _("There was less interaction with people today."),
                    _("There was a decrease in interaction with others today."),
                    _("There was a reduced amount of interaction with others today.")
                ],
                "-2 >= zscore": [
                    _("There was much less interaction with people today."),
                    _("There was significantly less interaction with people today."),
                    _("There were much fewer social interactions today."),
                    _("There was a considerable decrease in interaction with people today."),
                    _("There was much less interaction with others today."),
                    _("Today's interaction with people was much lower."),
                    _("Interaction with others today was much less than usual."),
                    _("There was a significant decrease in interaction with people today."),
                    _("There was a substantial reduction in interaction with others today."),
                    _("There was a markedly reduced amount of interaction with others today.")
                ]
            },
            "trend.together": {
                "zscore > 2": [
                    _("Interacted with people more than normal."),
                    _("There was increased interaction with people compared to normal."),
                    _("Had more social interaction than normal."),
                    _("There was a higher level of interaction with people than usual."),
                    _("Had more interaction with others than usual."),
                    _("There was an increase in social interactions compared to normal."),
                    _("Interaction with people was higher than normal."),
                    _("Engaged more with people than usual."),
                    _("Experienced more interaction with others than usual."),
                    _("There was greater interaction with people than normal.")
                ],
                "2 >= zscore > 0.5": [
                    _("Had an average amount of human interaction today."),
                    _("There was a moderate level of human interaction today."),
                    _("Had a typical amount of interaction with others today."),
                    _("The amount of human interaction today was average."),
                    _("Had a standard level of interaction with people today."),
                    _("Today's human interaction was average."),
                    _("Interaction with others today was typical."),
                    _("Experienced an average amount of human interaction today."),
                    _("There was a normal level of interaction with others today."),
                    _("Had a customary amount of interaction with others today.")
                ],
                "0.5 >= zscore > -0.5": [
                    _("Had an average amount of human interaction today."),
                    _("There was a moderate level of human interaction today."),
                    _("Had a typical amount of interaction with others today."),
                    _("The amount of human interaction today was average."),
                    _("Had a standard level of interaction with people today."),
                    _("Today's human interaction was average."),
                    _("Interaction with others today was typical."),
                    _("Experienced an average amount of human interaction today."),
                    _("There was a normal level of interaction with others today."),
                    _("Had a customary amount of interaction with others today.")
                ],
                "-0.5 >= zscore > -2": [
                    _("Interacted with people less today."),
                    _("There was reduced interaction with people today."),
                    _("Had fewer social interactions today."),
                    _("There was a lower level of interaction with people today."),
                    _("Had less interaction with others today."),
                    _("Today's interaction with people was lower."),
                    _("Interaction with others today was less than usual."),
                    _("Experienced less interaction with people today."),
                    _("There was a decrease in interaction with others today."),
                    _("Had a reduced amount of interaction with others today.")
                ],
                "-2 >= zscore": [
                    _("Interacted with people much less today."),
                    _("There was significantly less interaction with people today."),
                    _("Had much fewer social interactions today."),
                    _("There was a considerable decrease in interaction with people today."),
                    _("Had much less interaction with others today."),
                    _("Today's interaction with people was much lower."),
                    _("Interaction with others today was much less than usual."),
                    _("Experienced a significant decrease in interaction with people today."),
                    _("There was a substantial reduction in interaction with others today."),
                    _("Had a markedly reduced amount of interaction with others today.")
                ]
            }
        }

        if trend_id in possible_comments:
            for key in possible_comments[trend_id]:
                if eval(key):
                    comment = random.choice(possible_comments[trend_id][key])
                    break
        return comment


    def midnight_fired(self, botengine, content=None):
        """
        Data stream message - Midnight timer fired
        :param botengine:
        :param content:
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">midnight_fired()")
        self.process_report(botengine, report_address=DAILY_REPORT_ADDRESS)
        self.process_report(botengine, report_address=WEEKLY_REPORT_ADDRESS)
        self.process_report(botengine, report_address=MONTHLY_REPORT_ADDRESS)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<midnight_fired()")

    def process_report(self, botengine, report_address=DAILY_REPORT_ADDRESS):
        """
        Process a report
        Daily reports are completed when the location goes into SLEEP mode, or at midnight if it has not gone into SLEEP mode yet.
        Weekly reports are completed on Monday morning at midnight.
        Monthly reports are completed on the last day of the month at midnight.

        :param botengine: BotEngine environment
        :param report_address: Address of the report to process
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">process_report() check timestamps {} == {} | {} | {}".format(self._get_todays_timestamp(botengine), self.current_report_ms, self.current_weekly_report_ms, self.current_monthly_report_ms))
        if report_address == DAILY_REPORT_ADDRESS:
            # If we haven't notified yet because the person hasn't gone to sleep yet, notify now.
            if self.current_report_ms is not None:
                if self.last_emailed_report_ms != self.current_report_ms:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() Send completion status for todays report: {}".format(self.current_report_ms))
                    self.last_emailed_report_ms = self.current_report_ms
                    if "SLEEP" not in self.parent.occupancy_status and "VACATION" not in self.parent.occupancy_status:
                        self._add_entry(botengine, dailyreport.SECTION_ID_SLEEP, comment=_("Hasn't gone to sleep by midnight."), include_timestamp=True, force_previous=True)
                    
                    # Get the report or create our first one
                    report = botengine.get_state(DAILY_REPORT_ADDRESS, timestamp_ms=self.current_report_ms)
                    if report is None:
                        report = self._initialize_report(botengine, self.current_report_ms)

                    # Notify that the daily report has completed
                    dailyreport.report_status_updated(botengine, self.parent, report, status=dailyreport.REPORT_STATUS_COMPLETED)
                    
                    # Create a new daily report
                    self._initialize_report(botengine, self._get_todays_timestamp(botengine))

            if self._get_todays_timestamp(botengine) == self.current_report_ms:
                # Already processed today's report
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<process_report() Already processed today's report")
                return
            # Create a new daily report
            self._initialize_report(botengine, self._get_todays_timestamp(botengine))
        
        elif report_address == WEEKLY_REPORT_ADDRESS:
            # Create a new weekly report at Monday morning.
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() day of week {}".format(self.parent.get_local_day_of_week(botengine)))
            if self.parent.get_local_day_of_week(botengine) == 0:
                
                if self.current_weekly_report_ms is not None and self._get_todays_timestamp(botengine) == self.current_weekly_report_ms:
                    # Already processed this week's report
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<process_report() Already processed this week's report")
                    return
                import datetime
                from statistics import mean, stdev

                this_week = (self.parent.get_local_datetime(botengine) - datetime.timedelta(days=1))

                
                # Calculate the last week's average values
                last_week = (this_week - datetime.timedelta(weeks=1))
                last_key = self._report_key(botengine, report_address=WEEKLY_REPORT_ADDRESS, date=last_week)

                last_week_average_values = {}
                if last_key in self.weekly_reports:
                    for section_id in DEFAULT_SECTION_PROPERTIES.keys():
                        for id in DEFAULT_SECTION_PROPERTIES[section_id][dailyreport.SECTION_KEY_INSIGHT_IDS]:
                            if f"insight-{id}" in self.weekly_reports[last_key]:
                                
                                # Apply statistics
                                # If the values are not numeric, then we need to apply a different set of statistics
                                values = self.weekly_reports[last_key][f"insight-{id}"]["values"]
                                if any([any([isinstance(k,str) for k in j]) for j in [i for i in values.values()]]):
                                    # This metric is not numeric

                                    for day_of_week in values.keys():
                                        averages = {}
                                        for value in values:
                                            if value not in averages:
                                                averages[value] = 0
                                            averages[value] += 1
                                        if id not in last_week_average_values:
                                            last_week_average_values[id] = {}
                                        last_week_average_values[id][day_of_week] = averages
                                    
                                    continue
                                
                                try:
                                    for day_of_week in values.keys():
                                        if id not in last_week_average_values:
                                            last_week_average_values[id] = {}
                                        last_week_average_values[id][day_of_week] = mean(values[day_of_week])
                                except TypeError as e:
                                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|process_report() TypeError error={} id={} values={}".format(e, id, json.dumps(self.weekly_reports[last_key][id]["values"])))
                                    continue

                key = self._report_key(botengine, report_address=WEEKLY_REPORT_ADDRESS, date=this_week)
                if key in self.weekly_reports:
                    # Create a new weekly report
                    report = self._initialize_weekly_report(botengine, self._get_todays_timestamp(botengine))

                    # Add entry for each insight
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() Processing weekly report key '{}' for data: {}".format(key, json.dumps(self.weekly_reports)))
                    for id in self.weekly_reports[key]:
                        insight_id = id.split("-")[-1]
                        section_id = self._section_id_for_insight(botengine, insight_id)
                        if section_id is None:
                            # This metric is not an insight
                            continue
                               
                        title = self.weekly_reports[key][id]["title"]
                        values = self.weekly_reports[key][id]["values"]

                        if len(values) == 0:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|process_report() No values for id '{}'".format(id))
                            continue
                        
                        # Apply statistics
                        # If the values are not numeric, then we need to apply a different set of statistics
                        if any([any([isinstance(k,str) for k in j]) for j in [i for i in values.values()]]):
                            # This metric is not numeric
                            statistics = {}

                            for day_of_week in values.keys():
                                averages = {}
                                for value in values[day_of_week]:
                                    if value not in averages:
                                        averages[value] = 0
                                    averages[value] += 1
                                max_value = max(averages, key=averages.get)
                                min_value = min(averages, key=averages.get)
                                statistics[day_of_week] = {
                                    "max": max_value,
                                    "min": min_value,
                                }
                                last_week_max_value = None
                                last_week_min_value = None
                                if id in last_week_average_values and day_of_week in last_week_average_values[id]:
                                    statistics[day_of_week]["max_prev"] = max(last_week_average_values[id][day_of_week], key=last_week_average_values[id][day_of_week].get)
                                    statistics[day_of_week]["min_prev"] = min(last_week_average_values[id][day_of_week], key=last_week_average_values[id][day_of_week].get)
                        
                            self.weekly_reports[key][id]["statistics"] = statistics
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() This insight does not report numeric values. id={} values={} statistics={}".format(id, json.dumps(values), statistics))
                            continue

                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() Analyzing values: {}".format(json.dumps(values)))

                        daily_values = [mean(values[day_of_week]) for day_of_week in values.keys()]

                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() daily_values={}".format(daily_values))

                        try:
                            average_value = mean(daily_values)
                            std = stdev(daily_values) if len(daily_values) > 1 else 0
                        except TypeError as e:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() This insight does not report numeric values.")
                            continue
                        
                        max_index, max_value = max(enumerate(daily_values), key=lambda x: x[1] - average_value)
                        min_index, min_value = min(enumerate(daily_values), key=lambda x: x[1] - average_value)

                        # Update the day indexes in case the services was added mid-week
                        max_index += 7 - len(daily_values)
                        min_index += 7 - len(daily_values)

                        value = round(sum(daily_values) / len(daily_values), 2)

                        last_average_value = None
                        if id in last_week_average_values:
                            last_daily_values = [last_week_average_values[id][day_of_week] for day_of_week in last_week_average_values[id].keys()]
                            last_average_value = mean(last_daily_values)

                        # Reformat some of the data for the report
                        if insight_id in ['sleep.bedtime_ms', 'sleep.wakeup_ms', 'sleep.sleep_prediction_ms', 'sleep.wake_prediction_ms']:
                            average_value -= 24
                            if average_value < 0:
                                average_value += 24
                            min_value -= 24
                            if min_value < 0:
                                min_value += 24
                            max_value -= 24
                            if max_value < 0:
                                max_value += 24
                            value -= 24
                            if value < 0:
                                value += 24
                            if last_average_value:
                                last_average_value -= 24
                                if last_average_value < 0:
                                    last_average_value += 24

                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() id={} average_value={} max_value={} min_value={} std={} value={} last_average_value={}".format(id, average_value, max_value, min_value, std, value, last_average_value))

                        self.weekly_reports[key][id]["statistics"] = {
                            "average": round(average_value, 2),
                            "max": {
                                "value": round(max_value, 2),
                                "index": max_index
                            },
                            "min": {
                                "value": round(min_value, 2),
                                "index": min_index
                            }
                        }
                        

                        self.weekly_reports[key][id]["reported"] = round(value, 2)

                        # Comment for the report
                        comment = "{} - {}".format(title, value)
                        compare_comment = None

                        if insight_id in ["sleep.bedtime_ms", "sleep.wakeup_ms", "sleep.sleep_prediction_ms", "sleep.wake_prediction_ms"]:
                            # Calculate the time of day
                            min_timestamp_ms = self.parent.local_timestamp_ms_from_relative_hours(botengine, min_index, min_value, future=False)
                            max_timestamp_ms = self.parent.local_timestamp_ms_from_relative_hours(botengine, max_index, max_value, future=False)
                            average_timestamp_ms = self.parent.local_timestamp_ms_from_relative_hours(botengine, 0, average_value, future=False)
                            
                            # Convert to local time last week
                            min_dt = self.parent.get_local_datetime_from_timestamp(botengine, min_timestamp_ms - utilities.ONE_WEEK_MS)
                            max_dt = self.parent.get_local_datetime_from_timestamp(botengine, max_timestamp_ms - utilities.ONE_WEEK_MS)
                            average_dt = self.parent.get_local_datetime_from_timestamp(botengine, average_timestamp_ms - utilities.ONE_WEEK_MS)

                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() min_timestamp_ms={} min_dt={} max_timestamp_ms={} max_dt={} average_timestamp_ms={} average_dt={} std={}".format(min_timestamp_ms, min_dt, max_timestamp_ms, max_dt, average_timestamp_ms, average_dt, std))

                        if insight_id == "sleep.duration_ms":
                            if abs(max_value - average_value) < 1.0:
                                comment = "You slept for about {} hours each night this week".format(average_value)
                            elif abs(std) < 1.0:
                                comment = "On {}, you slept for {} hours, which is close to other days in the week".format(WEEK_DAYS[max_index], utilities.strftime(max_dt, "%-I:%M %p"))
                            else:
                                comment = "Your longest sleep was {} hours on {}.".format(max_value, WEEK_DAYS[max_index])
                            if last_average_value and average_value > last_average_value:
                                compare_comment = "You slept more on average this week."

                        elif insight_id == "sleep.bedtime_ms":
                            if abs(min_value - average_value) < 1.0:
                                comment = "On average, you went to sleep at {} this week".format(utilities.strftime(average_dt, "%-I:%M %p"))
                            elif abs(std) < 1.0:
                                comment = "On {}, you went to sleep at {}, which is close to other days in the week".format(WEEK_DAYS[min_index], utilities.strftime(min_dt, "%-I:%M %p"))
                            else:
                                comment = "On {}, you went to sleep at {}, which is earlier than other days in the week".format(WEEK_DAYS[min_index], utilities.strftime(min_dt, "%-I:%M %p"))
                            if last_average_value and average_value < last_average_value:
                                compare_comment = "You went to sleep earlier on average this week."

                        elif insight_id == "sleep.wakeup_ms":
                            if abs(max_value - average_value) < 1.0:
                                comment = "On average, you woke up at {} this week".format(utilities.strftime(average_dt, "%-I:%M %p"))
                            elif abs(std) < 1.0:
                                comment = "On {}, you went to sleep at {}, which is close to other days in the week".format(WEEK_DAYS[max_index], utilities.strftime(max_dt, "%-I:%M %p"))
                            else:
                                comment = "You woke up the latest on {} at {}.".format(WEEK_DAYS[max_index], utilities.strftime(max_dt, "%-I:%M %p"))
                            if last_average_value and average_value < last_average_value:
                                compare_comment = "You woke up later on average this week."
                                
                        elif insight_id == "sleep.sleep_score":
                            comment = "You slept the best on {}".format(WEEK_DAYS[max_index])
                            if last_average_value and average_value > last_average_value:
                                compare_comment = "You slept better this week."

                        elif insight_id == "sleep.sleep_prediction_ms":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.sleep_prediction_ms comments")
                            # min_timestamp_ms=1706065200000 min_dt=2024-01-16 22:00:00-05:00 
                            # max_timestamp_ms=1706503500000 max_dt=2024-01-21 23:45:00-05:00 
                            # average_timestamp_ms=1705982040000 average_dt=2024-01-15 22:54:00-05:00 
                            # std=0.7824936397800923

                            # min_timestamp_ms=1706676660000 min_dt=2024-01-23 23:51:00-05:00 
                            # max_timestamp_ms=1707025080000 max_dt=2024-01-28 00:38:00-05:00 
                            # average_timestamp_ms=1706505420000 average_dt=2024-01-22 00:17:00-05:00 
                            # std=0.3208371984924874


                        elif insight_id == "sleep.wake_prediction_ms":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.wake_prediction_ms comments")
                            # min_timestamp_ms=1706179200000 min_dt=2024-01-18 05:40:00-05:00 
                            # max_timestamp_ms=1706446140000 max_dt=2024-01-21 07:49:00-05:00
                            # average_timestamp_ms=1705924080000 average_dt=2024-01-15 06:48:00-05:00
                            # std=0.7689639494511785

                            # min_timestamp_ms=1706701740000 min_dt=2024-01-24 06:49:00-05:00 
                            # max_timestamp_ms=1707051900000 max_dt=2024-01-28 08:05:00-05:00 
                            # average_timestamp_ms=1706530500000 average_dt=2024-01-22 07:15:00-05:00 
                            # std=0.49679528535962847


                        elif insight_id == "sleep.underslept":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.underslept comments")
                        elif insight_id == "sleep.overslept":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.overslept comments")
                        elif insight_id == "sleep.bedtime_score":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.bedtime_score comments")
                        elif insight_id == "sleep.restlessness_score":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.restlessness_score comments")
                        elif insight_id == "care.inactivity.bedtime_awake_too_late":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.bedtime_awake_too_late comments")
                        elif insight_id == "sleep.low_sleep_quality.warning":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.low_sleep_quality.warning comments")
                        elif insight_id == "sleep.too_many_bathrooms.warning":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.too_many_bathrooms.warning comments")
                        elif insight_id == "care.inactivity.time_to_stretch":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.time_to_stretch comments")
                        elif insight_id == "care.inactivity.warning":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.warning comments")
                        elif insight_id == "care.inactivity.good_morning_sleeping_in":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.good_morning_sleeping_in comments")
                        elif insight_id == "care.inactivity.good_morning_problem_critical":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.good_morning_problem_critical comments")
                        elif insight_id == "care.inactivity.good_morning_problem":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.good_morning_problem comments")
                        elif insight_id == "care.inactivity.not_back_home.warning":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.not_back_home.warning comments")
                        elif insight_id == "request_assistance":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process request_assistance comments")
                        elif insight_id == "care.sms_sos":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.sms_sos comments")
                        elif insight_id == "health_high_heart_rate_warning":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process health_high_heart_rate_warning comments")
                        elif insight_id == "health_movement_confirmed_alert":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process health_movement_confirmed_alert comments")
                        elif insight_id == "vayyar.fall_confirmed_alert":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process vayyar.fall_confirmed_alert comments")
                        elif insight_id == "vayyar.stability_event_confirmed_alert":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process vayyar.stability_event_confirmed_alert comments")

                        # Add report entry
                        self._add_weekly_entry(botengine, section_id, comment=comment, identifier=id)

                        if compare_comment is not None:
                            self._add_weekly_entry(botengine, section_id, comment=compare_comment, identifier=f"{id}-comparison")

                    # Add an entry for each trend
                    for id in self.weekly_reports[key]:
                        trend_id = id.split("-")[-1]
                        section_id = self._section_id_for_trend(botengine, trend_id)
                        if section_id is None:
                            # This metric is not a trend
                            continue
                        if len(self.weekly_reports[key][id]) == 0:
                            # No trend data for this trend
                            continue

                        # Get the trend metadata and check for required fields
                        trends_metadata = botengine.get_state(TRENDS_METADATA_NAME)
                        if trends_metadata is None:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|process_report() Missing trend metadata: {}".format(trend_id))
                            break
                        
                        metadata = trends_metadata.get(trend_id, None)
                        if metadata is None:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|process_report() Missing metadata for trend: {}".format(trend_id))
                            continue
                        
                        if metadata.get("hidden", False):
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|process_report() Trend is hidden: {}".format(trend_id))
                            continue
        
                        # Pull the title into the trend metadata
                        title = metadata.get("title", None)
                        if title is None:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|process_report() Missing title for trend: {}".format(trend_id))
                            continue

                        latest_trend = list(self.weekly_reports[key][id].values())[-1]
                        value = latest_trend.get('value', None)
                        display = latest_trend.get("display", None)
                        std = latest_trend.get('std', None)
                        avg = latest_trend.get('avg', None)
                        zscore = latest_trend.get('zscore', None)

                        last_weeks_trend = {}
                        if last_key in self.weekly_reports:
                            if id in self.weekly_reports[last_key]:
                                last_weeks_trend = list(self.weekly_reports[last_key][id].values())[-1]

                        # Comment for the report
                        comment = "{} - {}".format(title, display)
                        compare_comment = None

                        if last_weeks_trend:
                            last_avg = last_weeks_trend.get('avg', None)

                            if trend_id == "trend.sleep_duration":
                                if avg > last_avg:
                                    compare_comment = "You slept more on average this week."
                            elif trend_id == "trend.bedtime":
                                if avg < last_avg:
                                    compare_comment = "You went to sleep earlier on average this week."
                            elif trend_id == "trend.wakeup":
                                if avg > last_avg:
                                    compare_comment = "You slept in longer this week."
                            elif trend_id == "sleep.sleep_score":
                                if avg > last_avg > 0:
                                    compare_comment = "You slept better this week."
                            elif trend_id == "trend.absent":
                                if avg > last_avg > 0:
                                    compare_comment = "You were absent more this week."


                        # Add report entry
                        self._add_weekly_entry(botengine, section_id, comment=comment, identifier=id)

                        if compare_comment is not None:
                            self._add_weekly_entry(botengine, section_id, comment=compare_comment)

                    
                    # Trim the weekly reports to keep only the last 7
                    keys = list(self.weekly_reports.keys())
                    keys.sort()
                    keys.reverse()
                    for _key in keys[7:]:
                        del self.weekly_reports[_key]
                    
                    report = botengine.get_state(WEEKLY_REPORT_ADDRESS, timestamp_ms=self.current_weekly_report_ms)

                    # Notify that the weekly report has completed
                    dailyreport.report_status_updated(botengine, self.parent, report, status=dailyreport.REPORT_STATUS_COMPLETED, metadata=self.weekly_reports[key])

        elif report_address == MONTHLY_REPORT_ADDRESS:
            # Create a new monthly report on the last day of the month
            if self.parent.is_last_day_of_month(botengine):

                if self.current_monthly_report_ms is not None and self._get_todays_timestamp(botengine) == self.current_monthly_report_ms:
                    # Already processed this week's report
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<process_report() Already processed this month's report")
                    return
                import datetime
                import calendar
                from statistics import mean, stdev
                date = self.parent.get_local_datetime(botengine)

                # Get a key for last month
                if date.month > 1:
                    last_month = date.replace(day=1).replace(month=date.month-1)
                else:
                    last_month = date.replace(day=1).replace(year=date.year-1, month=12)
                last_key = self._report_key(botengine, report_address=MONTHLY_REPORT_ADDRESS, date=last_month)
                
                last_month_average_values = {}
                if last_key in self.monthly_reports:
                    for section_id in DEFAULT_SECTION_PROPERTIES.keys():
                        for id in DEFAULT_SECTION_PROPERTIES[section_id][dailyreport.SECTION_KEY_INSIGHT_IDS]:
                            if f"insight-{id}" in self.monthly_reports[last_key]:
                                
                                # Apply statistics
                                # If the values are not numeric, then we need to apply a different set of statistics
                                values = self.monthly_reports[last_key][f"insight-{id}"]["values"]
                                if any([any([isinstance(k,str) for k in j]) for j in [i for i in values.values()]]):
                                    # This metric is not numeric
                                    for day_of_month in values.keys():
                                        averages = {}
                                        for value in values:
                                            if value not in averages:
                                                averages[value] = 0
                                            averages[value] += 1
                                        if id not in last_month_average_values:
                                            last_month_average_values[id] = {}
                                        last_month_average_values[id][day_of_month] = averages
                                    
                                    continue
                                
                                try:
                                    for day_of_month in values.keys():
                                        if id not in last_month_average_values:
                                            last_month_average_values[id] = {}
                                        last_month_average_values[id][day_of_month] = mean(values[day_of_month])
                                except TypeError as e:
                                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|process_report() TypeError error={} id={} values={}".format(e, id, json.dumps(self.monthly_reports[last_key][id]["values"])))
                                    continue

                key = self._report_key(botengine, report_address=MONTHLY_REPORT_ADDRESS, date=date)
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() Processing monthly report key '{}' for data: {}".format(key, json.dumps(self.monthly_reports)))
                if key in self.monthly_reports:
                    # Create a new monthly report
                    report = self._initialize_monthly_report(botengine, self._get_todays_timestamp(botengine))
                    
                    # Add entry for each insight
                    for id in self.monthly_reports[key]:
                        insight_id = id.split("-")[-1]
                        section_id = self._section_id_for_insight(botengine, insight_id)
                        if section_id is None:
                            # This metric is not an insight
                            continue
                        title = self.monthly_reports[key][id]["title"]
                        values = self.monthly_reports[key][id]["values"]

                        if len(values) == 0:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|process_report() No values for id '{}'".format(id))
                            continue

                        # Apply statistics
                        # If the values are not numeric, then we need to apply a different set of statistics
                        if any([any([isinstance(k,str) for k in j]) for j in [i for i in values.values()]]):
                            # This metric is not numeric
                            statistics = {}

                            for day_of_month in values.keys():
                                averages = {}
                                for value in values[day_of_month]:
                                    if value not in averages:
                                        averages[value] = 0
                                    averages[value] += 1
                                max_value = max(averages, key=averages.get)
                                min_value = min(averages, key=averages.get)
                                statistics[day_of_month] = {
                                    "max": max_value,
                                    "min": min_value,
                                }
                                last_month_max_value = None
                                last_month_min_value = None
                                if id in last_month_average_values and day_of_week in last_month_average_values[id]:
                                    statistics[day_of_month]["max_prev"] = max(last_month_average_values[id][day_of_month], key=last_month_average_values[id][day_of_month].get)
                                    statistics[day_of_month]["min_prev"] = min(last_month_average_values[id][day_of_month], key=last_month_average_values[id][day_of_month].get)
                        
                            self.monthly_reports[key][id]["statistics"] = statistics
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() This insight does not report numeric values. id={} values={} statistics={}".format(id, json.dumps(values), statistics))

                            # TODO: Add a comment for these insights
                            """
                            "security_mode", 
                            "occupancy.status"
                            """
                            continue

                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() Analyzing values: {}".format(json.dumps(values)))

                        daily_values = [mean(values[day_of_month]) for day_of_month in values.keys()]

                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() daily_values={}".format(daily_values))

                        try:
                            average_value = mean(values)
                            std = stdev(daily_values) if len(daily_values) > 1 else 0
                        except TypeError as e:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() This insight does not report numeric values.")
                            continue

                        max_index, max_value = max(enumerate(daily_values), key=lambda x: x[1] - average_value)
                        min_index, min_value = min(enumerate(daily_values), key=lambda x: x[1] - average_value)

                        # Update the day indexes in case the services was added mid-month
                        current_dt = self.parent.get_local_datetime(botengine)

                        max_index += calendar.monthrange(current_dt.year, current_dt.month)[1] - len(daily_values)
                        min_index += calendar.monthrange(current_dt.year, current_dt.month)[1] - len(daily_values)
                        
                        value = round(sum(daily_values) / len(daily_values), 2)

                        last_average_value = None
                        if id in last_month_average_values:
                            last_daily_values = [last_month_average_values[id][day_of_week] for day_of_week in last_month_average_values[id].keys()]
                            last_average_value = mean(last_daily_values)

                        # Reformat some of the data for the report
                        if insight_id in ['sleep.bedtime_ms', 'sleep.wakeup_ms', 'sleep.sleep_prediction_ms', 'sleep.wake_prediction_ms']:
                            average_value -= 24
                            if average_value < 0:
                                average_value += 24
                            min_value -= 24
                            if min_value < 0:
                                min_value += 24
                            max_value -= 24
                            if max_value < 0:
                                max_value += 24
                            value -= 24
                            if value < 0:
                                value += 24
                            if last_average_value:
                                last_average_value -= 24
                                if last_average_value < 0:
                                    last_average_value += 24
                        
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() id={} average_value={} max_value={} min_value={} std={} value={} last_average_value={}".format(id, average_value, max_value, min_value, std, value, last_average_value))
                        
                        self.monthly_reports[key][id]["statistics"] = {
                            "average": round(average_value, 2),
                            "max": {
                                "value": round(max_value, 2),
                                "index": max_index
                            },
                            "min": {
                                "value": round(min_value, 2),
                                "index": min_index
                            }
                        }

                        self.monthly_reports[key][id]["reported"] = round(value, 2)

                        # Comment for the report
                        comment = "{} - {}".format(title, value)
                        compare_comment = None

                        if insight_id in ["sleep.bedtime_ms", "sleep.wakeup_ms", "sleep.sleep_prediction_ms", "sleep.wake_prediction_ms"]:
                            # Calculate the time of day
                            min_timestamp_ms = self.parent.local_timestamp_ms_from_relative_hours(botengine, min_index, min_value, future=False)
                            max_timestamp_ms = self.parent.local_timestamp_ms_from_relative_hours(botengine, max_index, max_value, future=False)
                            average_timestamp_ms = self.parent.local_timestamp_ms_from_relative_hours(botengine, 0, average_value, future=False)
                            
                            # Convert to local time last month
                            min_dt = self.parent.get_local_datetime_from_timestamp(botengine, min_timestamp_ms - calendar.monthrange(current_dt.year, current_dt.month)[1] * utilities.ONE_DAY_MS)
                            max_dt = self.parent.get_local_datetime_from_timestamp(botengine, max_timestamp_ms - calendar.monthrange(current_dt.year, current_dt.month)[1] * utilities.ONE_DAY_MS)
                            average_dt = self.parent.get_local_datetime_from_timestamp(botengine, average_timestamp_ms - calendar.monthrange(current_dt.year, current_dt.month)[1] * utilities.ONE_DAY_MS)

                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() min_timestamp_ms={} min_dt={} max_timestamp_ms={} max_dt={} average_timestamp_ms={} average_dt={} std={}".format(min_timestamp_ms, min_dt, max_timestamp_ms, max_dt, average_timestamp_ms, average_dt, std))

                        if insight_id == "sleep.duration_ms":
                            if abs(max_value - average_value) < 1.0:
                                comment = "You slept for about {} hours each night this month".format(average_value)
                            elif abs(std) < 1.0:
                                comment = "On {}, you slept for {} hours, which is close to other days in the month".format(utilities.strftime(max_dt, "%A, %B %-d"), utilities.strftime(max_dt, "%-I:%M %p"))
                            else:
                                comment = "Your longest sleep was {} hours on {}.".format(max_value, utilities.strftime(max_dt, "%A, %B %-d"))
                            if last_average_value and average_value > last_average_value:
                                compare_comment = "You slept more on average this month."

                        elif insight_id == "sleep.bedtime_ms":
                            if abs(min_value - average_value) < 1.0:
                                comment = "On average, you went to sleep at {} this month".format(utilities.strftime(average_dt, "%-I:%M %p"))
                            elif abs(std) < 1.0:
                                comment = "On {}, you went to sleep at {}, which is close to other days in the month".format(utilities.strftime(min_dt, "%A, %B %-d"), utilities.strftime(min_dt, "%-I:%M %p"))
                            else:
                                comment = "On {}, you went to sleep at {}, which is earlier than other days in the month".format(utilities.strftime(min_dt, "%A, %B %-d"), utilities.strftime(min_dt, "%-I:%M %p"))
                            if last_average_value and average_value < last_average_value:
                                compare_comment = "You went to sleep earlier on average this month."

                        elif insight_id == "sleep.wakeup_ms":
                            if abs(max_value - average_value) < 1.0:
                                comment = "On average, you woke up at {} this month".format(utilities.strftime(average_dt, "%-I:%M %p"))
                            elif abs(std) < 1.0:
                                comment = "On {}, you went to sleep at {}, which is close to other days in the month".format(utilities.strftime(max_dt, "%A, %B %-d"), utilities.strftime(max_dt, "%-I:%M %p"))
                            else:
                                comment = "You woke up the latest on {} at {}.".format(utilities.strftime(max_dt, "%A, %B %-d"), utilities.strftime(max_dt, "%-I:%M %p"))
                            if last_average_value and average_value < last_average_value:
                                compare_comment = "You woke up later on average this month."
                                
                        elif insight_id == "sleep.sleep_score":
                            comment = "You slept the best on {}".format(utilities.strftime(max_dt, "%A, %B %-d"))
                            if last_average_value and average_value > last_average_value:
                                compare_comment = "You slept better this month."

                        elif insight_id == "sleep.sleep_prediction_ms":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.sleep_prediction_ms comments")

                            # min_timestamp_ms=1707966000000 min_dt=2024-01-14 22:00:00-05:00 
                            # max_timestamp_ms=1708925880000 max_dt=2024-01-26 00:38:00-05:00 
                            # average_timestamp_ms=1706587200000 average_dt=2023-12-29 23:00:00-05:00 
                            # std=0.8908975320980596


                        elif insight_id == "sleep.wake_prediction_ms":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.wake_prediction_ms comments")

                            # min_timestamp_ms=1708339200000 min_dt=2024-01-19 05:40:00-05:00 
                            # max_timestamp_ms=1709039100000 max_dt=2024-01-27 08:05:00-05:00 
                            # average_timestamp_ms=1706585880000 average_dt=2023-12-29 22:38:00-05:00 
                            # std=0.6298856183910626

                        elif insight_id == "sleep.underslept":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.underslept comments")
                        elif insight_id == "sleep.overslept":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.overslept comments")
                        elif insight_id == "sleep.bedtime_score":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.bedtime_score comments")
                        elif insight_id == "sleep.restlessness_score":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.restlessness_score comments")
                        elif insight_id == "care.inactivity.bedtime_awake_too_late":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.bedtime_awake_too_late comments")
                        elif insight_id == "sleep.low_sleep_quality.warning":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.low_sleep_quality.warning comments")
                        elif insight_id == "sleep.too_many_bathrooms.warning":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process sleep.too_many_bathrooms.warning comments")
                        elif insight_id == "care.inactivity.time_to_stretch":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.time_to_stretch comments")
                        elif insight_id == "care.inactivity.warning":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.warning comments")
                        elif insight_id == "care.inactivity.good_morning_sleeping_in":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.good_morning_sleeping_in comments")
                        elif insight_id == "care.inactivity.good_morning_problem_critical":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.good_morning_problem_critical comments")
                        elif insight_id == "care.inactivity.good_morning_problem":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.good_morning_problem comments")
                        elif insight_id == "care.inactivity.not_back_home.warning":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.inactivity.not_back_home.warning comments")
                        elif insight_id == "request_assistance":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process request_assistance comments")
                        elif insight_id == "care.sms_sos":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process care.sms_sos comments")
                        elif insight_id == "health_high_heart_rate_warning":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process health_high_heart_rate_warning comments")
                        elif insight_id == "health_movement_confirmed_alert":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process health_movement_confirmed_alert comments")
                        elif insight_id == "vayyar.fall_confirmed_alert":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process vayyar.fall_confirmed_alert comments")
                        elif insight_id == "vayyar.stability_event_confirmed_alert":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|process_report() TODO: Process vayyar.stability_event_confirmed_alert comments")

                        # Add report entry
                        self._add_monthly_entry(botengine, section_id, comment=comment, identifier=id)

                        if compare_comment is not None:
                            self._add_monthly_entry(botengine, section_id, comment=compare_comment, identifier=f"{id}-comparison")

                    # Add an entry for each trend
                    for id in self.monthly_reports[key]:
                        trend_id = id.split("-")[-1]
                        section_id = self._section_id_for_trend(botengine, trend_id)
                        if section_id is None:
                            # This metric is not a trend
                            continue
                        if len(self.monthly_reports[key][id]) == 0:
                            # No trend data for this trend
                            continue

                        # Get the trend metadata and check for required fields
                        trends_metadata = botengine.get_state(TRENDS_METADATA_NAME)
                        if trends_metadata is None:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|process_report() Missing trend metadata: {}".format(trend_id))
                            break
                        
                        metadata = trends_metadata.get(trend_id, None)
                        if metadata is None:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|process_report() Missing metadata for trend: {}".format(trend_id))
                            continue
                        
                        if metadata.get("hidden", False):
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|process_report() Trend is hidden: {}".format(trend_id))
                            continue
        
                        # Pull the title into the trend metadata
                        title = metadata.get("title", None)
                        if title is None:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|process_report() Missing title for trend: {}".format(trend_id))
                            continue

                        latest_trend = list(self.monthly_reports[key][id].values())[-1]
                        value = latest_trend.get('value', None)
                        display = latest_trend.get("display", None)
                        std = latest_trend.get('std', None)
                        avg = latest_trend.get('avg', None)
                        zscore = latest_trend.get('zscore', None)

                        last_months_trend = {}
                        if last_key in self.monthly_reports:
                            if id in self.monthly_reports[last_key]:
                                last_months_trend = list(self.monthly_reports[last_key][id].values())[-1]

                        # Comment for the report
                        comment = "{} - {}".format(title, display)
                        compare_comment = None

                        if last_months_trend:
                            last_avg = last_months_trend.get('avg', None)

                            if trend_id == "trend.sleep_duration":
                                if avg > last_avg:
                                    compare_comment = "You slept more on average this month."
                            elif trend_id == "trend.bedtime":
                                if avg < last_avg:
                                    compare_comment = "You went to sleep earlier on average this month."
                            elif trend_id == "trend.wakeup":
                                if avg > last_avg:
                                    compare_comment = "You slept in longer this month."
                            elif trend_id == "sleep.sleep_score":
                                if avg > last_avg > 0:
                                    compare_comment = "You slept better this month."
                            elif trend_id == "trend.absent":
                                if avg > last_avg > 0:
                                    compare_comment = "You were absent more this month."

                        # Add report entry
                        self._add_monthly_entry(botengine, section_id, comment=comment, identifier=id)

                        if compare_comment is not None:
                            self._add_monthly_entry(botengine, section_id, comment=compare_comment)
                    
                    # Trim the monthly reports to keep only the last 7
                    keys = list(self.monthly_reports.keys())
                    keys.sort()
                    keys.reverse()
                    for key in keys[7:]:
                        del self.monthly_reports[key]

                    report = botengine.get_state(MONTHLY_REPORT_ADDRESS, timestamp_ms=self.current_monthly_report_ms)
                    
                    # Notify that the monthly report has completed
                    dailyreport.report_status_updated(botengine, self.parent, report, status=dailyreport.REPORT_STATUS_COMPLETED, metadata=self.monthly_reports[key])
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<process_report()")

    def daily_report_entry(self, botengine, content):
        """
        Data stream message to add content to our daily report
        :param botengine: BotEngine environment
        :param content: Data Stream Content
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">daily_report_entry() data stream message received {}".format(json.dumps(content)))
        if 'section_id' not in content:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<daily_report_entry() Section ID not found in data stream message {}".format(json.dumps(content)))
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

        self._add_entry(botengine, section_id, comment=comment, subtitle=subtitle, identifier=identifier, include_timestamp=include_timestamp, timestamp_override_ms=timestamp_override_ms)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<daily_report_entry()")

    def daily_report_weekly_entry(self, botengine, content):
        """
        Data stream message to add content to our weekly report
        :param botengine: BotEngine environment
        :param content: Data Stream Content
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">daily_report_weekly_entry() data stream message received {}".format(json.dumps(content)))
        if 'section_id' not in content:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<daily_report_weekly_entry() Section ID not found in data stream message {}".format(json.dumps(content)))
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

        self._add_weekly_entry(botengine, section_id, comment=comment, subtitle=subtitle, identifier=identifier, include_timestamp=include_timestamp, timestamp_override_ms=timestamp_override_ms)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<daily_report_weekly_entry()")
    
    def daily_report_monthly_entry(self, botengine, content):
        """
        Data stream message to add content to our monthly report
        :param botengine: BotEngine environment
        :param content: Data Stream Content
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">daily_report_monthly_entry() data stream message received {}".format(json.dumps(content)))
        if 'section_id' not in content:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<daily_report_monthly_entry() Section ID not found in data stream message {}".format(json.dumps(content)))
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

        self._add_monthly_entry(botengine, section_id, comment=comment, subtitle=subtitle, identifier=identifier, include_timestamp=include_timestamp, timestamp_override_ms=timestamp_override_ms)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<daily_report_monthly_entry()")

    def daily_report_set_config(self, botengine, content):
        """
        Set the daily report configuration

        Section content can be configured in the following ways:
        - Add a new section with specified properties
        - Remove an existing default section by setting the section id value to empty dict {}
        - Sort sections by weight
        - Set the title, description, icon, and color of a section
        - Describe trend IDs to include for a given section
        - Describe insight IDs to include for a given section

        To remove a configuration provide an empty string ("") or "null" as a value for the key

        :param botengine: BotEngine environment
        :param content: Data Stream Content
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">daily_report_set_config() data stream message received {}".format(json.dumps(content)))
        if 'section_config' in content: 
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|daily_report_set_config() Updating section configuration.")
            dailyreport_state =  botengine.get_state(DAILYREPORT_STATE_VARIABLE_NAME)
            if dailyreport_state is None:
                dailyreport_state = {}

            section_config = dailyreport_state.get("section_config", {})
            supported_params = ['title', 'description', 'icon', 'color', 'weight', 'insight_ids', 'trend_ids']

            for section_id in content['section_config']:
                if content['section_config'][section_id] == "null" or content['section_config'][section_id] == "":
                    section_config.pop(section_id, None)
                    continue
                if section_id not in section_config:
                    new_section = {param: content['section_config'][section_id].get(param, None) for param in supported_params}
                    section_config[section_id] = {k: v for k, v in new_section.items() if v is not None}
                    continue
                updated_section = {param: content['section_config'][section_id].get(param, None) for param in supported_params}
                params_to_remove = [param for param in supported_params.keys() if supported_params[param] == "" or supported_params[param] == "null"]
                for param in params_to_remove:
                    updated_section.pop(param, None)
                    section_config[section_id].pop(param, None)
                section_config[section_id] = {k: v for k, v in updated_section.items() if v is not None}

            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|daily_report_set_config() section_config={}".format(json.dumps(section_config)))
            
            # Set the section configuration
            self.section_config = section_config

            # Save the section configuration to the location
            self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, {"section_config": section_config})

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<daily_report_set_config()")

    def _add_entry(self, botengine, section_id, comment=None, subtitle=None, identifier=None, include_timestamp=False, timestamp_override_ms=None, force_previous=False):
        """
        Add a section and bullet point the current daily report
        :param botengine: BotEngine environment
        :param comment: Comment like "Woke up."
        :param subtitle: Subtitle comment like "Consistent sleep schedule and good quality sleep last night."
        :param identifier: Optional identifier to come back and edit this entry later.
        :param include_timestamp: True to include a timestamp like "7:00 AM - <comment>" (default is False)
        :param timestamp_override_ms: Optional timestamp in milliseconds to override the current time when citing the timestamp with include_timestamp=True
        :param force_previous: Internal argument to add an entry to the previous day's daily report, even if today is a different day than the current report.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_add_entry() section_id={} comment={} subtitle={} identifier={} include_timestamp={} timestamp_override_ms={} force_previous={}".format(section_id, comment, subtitle, identifier, include_timestamp, timestamp_override_ms, force_previous))
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_add_entry() Current report timestamp is {}".format(self.current_report_ms))

        if self.current_report_ms is None:
            self._initialize_report(botengine, self._get_todays_timestamp(botengine))

        # Make sure our midnight schedule fired properly.
        elif self._get_todays_timestamp(botengine) != self.current_report_ms and not force_previous:
            # Create a new daily report
            self._initialize_report(botengine, self._get_todays_timestamp(botengine))

        report = botengine.get_state(DAILY_REPORT_ADDRESS, timestamp_ms=self.current_report_ms)
        # if report is None:
        #     botengine.get_logger(f"{__name__}.{__class__.__name__}").info("There is currently no active daily report.")
        #     self.midnight_fired(botengine)
        #     report = botengine.get_state(DAILY_REPORT_ADDRESS, self.current_report_ms)
        #     if report is None:
        #         return
        #     else:
        #         botengine.get_logger(f"{__name__}.{__class__.__name__}").info("Successfully created and loaded a new report.")
        # else:
        #     botengine.get_logger(f"{__name__}.{__class__.__name__}").info("Successfully loaded an existing report.")

        focused_section = self._get_section_object(botengine, report, section_id)
        if focused_section is None:
            if comment is None:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_add_entry() No comment, and no section found. Nothing to do.")
                return
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() Need to create a new section for section_id '{}'.".format(section_id))
            section_properties = None
            # Check if the section is a default section
            if section_id in DEFAULT_SECTION_PROPERTIES:
                section_properties = DEFAULT_SECTION_PROPERTIES[section_id]
            # Check if the section is a custom section
            if self.section_config is not None and self.section_config.get(section_id, None) is not None:
                if self.section_config[section_id] == {}:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_add_entry() Section ignored by custom configuration '{}'".format(section_id))
                    return
                if section_properties is None:
                    section_properties = {
                        dailyreport.SECTION_KEY_WEIGHT: 0,
                        dailyreport.SECTION_KEY_TITLE: "", 
                        dailyreport.SECTION_KEY_DESCRIPTION: "",
                        dailyreport.SECTION_KEY_ICON: "",
                        dailyreport.SECTION_KEY_COLOR: "",
                        dailyreport.SECTION_KEY_TREND_IDS: [],
                        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
                    }
                section_properties.update(self.section_config[section_id])
            if section_properties is None:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("<_add_entry() No section properties found for section '{}'".format(section_id))
                return
            focused_section = {
                dailyreport.SECTION_KEY_ID: section_id,
                dailyreport.SECTION_KEY_WEIGHT: section_properties[dailyreport.SECTION_KEY_WEIGHT],
                dailyreport.SECTION_KEY_TITLE: section_properties[dailyreport.SECTION_KEY_TITLE],
                dailyreport.SECTION_KEY_DESCRIPTION: section_properties[dailyreport.SECTION_KEY_DESCRIPTION],
                dailyreport.SECTION_KEY_ICON: section_properties[dailyreport.SECTION_KEY_ICON],
                dailyreport.SECTION_KEY_COLOR: section_properties[dailyreport.SECTION_KEY_COLOR],
                dailyreport.SECTION_KEY_ITEMS: []
            }

            if section_id == dailyreport.SECTION_ID_WELLNESS:
                if self.section_config is None or self.section_config.get(section_id, {}).get('title', None) is None:
                    # Wellness is a special case because it has a dynamic title
                    focused_section[dailyreport.SECTION_KEY_TITLE] = self._get_wellness_title(botengine, section_properties[dailyreport.SECTION_KEY_TITLE])

            if 'sections' not in report:
                report['sections'] = []

            report['sections'].append(focused_section)
            report['sections'] = sorted(report['sections'], key=lambda k: k['weight'])

        if comment is not None or identifier is not None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() Adding a new item to section_id '{}'".format(section_id))
            # Backwards compatibility with older app versions that exclusively used a comment modified with the timestamp.
            timeless_comment = comment
            timeful_comment = comment
            timestamp_str = None

            if include_timestamp and comment is not None:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() Including a timestamp in the comment")
                if timestamp_override_ms is not None:
                    dt = self.parent.get_local_datetime_from_timestamp(botengine, timestamp_override_ms)
                else:
                    dt = self.parent.get_local_datetime(botengine)

                if section_id == dailyreport.SECTION_ID_SLEEP:
                    # Sleep timestamps include the day
                    timestamp_str = utilities.strftime(dt, "%-I:%M %p %A")

                    # Backwards compatibility with previous apps that use a 'comment' field which included the timestamp in the field.
                    timeful_comment = "{} - {}".format(timestamp_str, comment)
                else:
                    # Other timestamps don't include the day
                    timestamp_str = utilities.strftime(dt, "%-I:%M %p")
                    timeful_comment = "{} - {}".format(timestamp_str, comment)

            if identifier is None and comment is not None:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() Adding an unidentified item to section_id '{}'".format(section_id))
                ts = botengine.get_timestamp()
                if timestamp_override_ms is not None:
                    ts = timestamp_override_ms

                focused_item = {
                    "timestamp_ms": ts,
                    "comment": timeful_comment,
                    "comment_raw": timeless_comment
                }
                if timestamp_str is not None:
                    focused_item['timestamp_str'] = timestamp_str
                focused_section['items'].append(focused_item)
                focused_section['items'] = sorted(focused_section['items'], key=lambda k: k['timestamp_ms'])

            else:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() Managing an identified item '{}' for section_id '{}'".format(identifier, section_id))
                # Try to overwrite any previous entry with this identifier
                focused_item = None
                for item in focused_section['items']:
                    if 'id' in item:
                        if item['id'] == identifier:
                            focused_item = item

                if focused_item is not None:
                    # Edit the item in place
                    if comment is not None:
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() Modifying the existing item with identifier '{}'".format(identifier))
                        # Modify the item
                        ts = botengine.get_timestamp()
                        if timestamp_override_ms is not None:
                            ts = timestamp_override_ms

                        focused_item['timestamp_ms'] = ts
                        focused_item['comment'] = comment
                        focused_item['comment_raw'] = timeless_comment
                        if timestamp_str is not None:
                            focused_item['timestamp_str'] = timestamp_str
                        focused_section['items'] = sorted(focused_section['items'], key=lambda k: k['timestamp_ms'])

                    else:
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() Deleting the existing item with identifier '{}'".format(identifier))
                        # Delete the item
                        focused_section['items'].remove(focused_item)
                        focused_section['items'] = sorted(focused_section['items'], key=lambda k: k['timestamp_ms'])

                        if len(focused_section['items']) == 0:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() No more items in section_id '{}', removing it.".format(section_id))
                            # Delete the entire section
                            report['sections'].remove(focused_section)
                elif comment is None:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() No comment, and no item found with identifier '{}'".format(identifier))
                    return
                else:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() Adding a new item with identifier '{}'".format(identifier))
                    # Add the item
                    ts = botengine.get_timestamp()
                    if timestamp_override_ms is not None:
                        ts = timestamp_override_ms

                    focused_item = {
                        "timestamp_ms": ts,
                        "comment": timeful_comment,
                        "comment_raw": timeless_comment,
                        "id": identifier
                    }
                    if timestamp_str is not None:
                        focused_item['timestamp_str'] = timestamp_str
                    focused_section['items'].append(focused_item)
                    focused_section['items'] = sorted(focused_section['items'], key=lambda k: k['timestamp_ms'])

        if subtitle is not None:
            # Manually defined subtitle for this section
            focused_section['subtitle'] = subtitle

        else:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_entry() Generating the subtitle for section_id '{}'".format(section_id))
            # Auto-generated subtitles for specific sections that support it
            if section_id == dailyreport.SECTION_ID_NOTES:
                if len(focused_section['items']) == 0:
                    focused_section['subtitle'] = _("No notes captured today.")

                elif len(focused_section['items']) == 1:
                    focused_section['subtitle'] = _("Captured one note today.")

                elif len(focused_section['items']) > 1:
                    focused_section['subtitle'] = _("Captured {} notes today.").format(len(focused_section['items']))

            elif section_id == dailyreport.SECTION_ID_TASKS:
                if len(focused_section['items']) == 0:
                    focused_section['subtitle'] = _("No tasks updated today.")

                elif len(focused_section['items']) == 1:
                    focused_section['subtitle'] = _("Updated one task today.")

                elif len(focused_section['items']) > 1:
                    focused_section['subtitle'] = _("Updated {} tasks today.").format(len(focused_section['items']))

            # TODO: This does not make sense
            elif section_id == dailyreport.SECTION_ID_MEDICATION:
                if len(focused_section['items']) == 0:
                    focused_section['subtitle'] = _("No medication accessed today.")

                elif len(focused_section['items']) == 1:
                    focused_section['subtitle'] = _("Accessed medicine once today.")

                elif len(focused_section['items']) > 1:
                    focused_section['subtitle'] = _("Accessed medicine {} times today.").format(len(focused_section['items']))

            # TODO: This does not make sense
            elif section_id == dailyreport.SECTION_ID_BATHROOM:
                if len(focused_section['items']) == 0:
                    focused_section['subtitle'] = _("No bathroom visits observed today.")

                elif len(focused_section['items']) == 1:
                    focused_section['subtitle'] = _("Visited the bathroom once today.")

                elif len(focused_section['items']) > 1:
                    focused_section['subtitle'] = _("Visited the bathroom {} times today.").format(len(focused_section['items']))
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_add_daily_entry() Setting daily report to {}".format(json.dumps(report, indent=2, sort_keys=True)))
        self.parent.set_location_property_separately(botengine, DAILY_REPORT_ADDRESS, report, overwrite=True, timestamp_ms=self.current_report_ms)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_add_daily_entry()")
        
    def _add_weekly_entry(self, botengine, section_id, comment=None, subtitle=None, identifier=None, include_timestamp=False, timestamp_override_ms=None):
        """
        Add a section and bullet point the current daily report
        :param botengine: BotEngine environment
        :param comment: Comment like "Woke up."
        :param subtitle: Subtitle comment like "Consistent sleep schedule and good quality sleep last night."
        :param identifier: Optional identifier to come back and edit this entry later.
        :param include_timestamp: True to include a timestamp like "7:00 AM - <comment>" (default is False)
        :param timestamp_override_ms: Optional timestamp in milliseconds to override the current time when citing the timestamp with include_timestamp=True
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_add_weekly_entry() section_id={} comment={} subtitle={} identifier={} include_timestamp={} timestamp_override_ms={}".format(section_id, comment, subtitle, identifier, include_timestamp, timestamp_override_ms))
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_weekly_entry() Current report timestamp is {}".format(self.current_weekly_report_ms))

        if self.current_weekly_report_ms is None:
            self._initialize_weekly_report(botengine, self._get_todays_timestamp(botengine))

        report = botengine.get_state(WEEKLY_REPORT_ADDRESS, timestamp_ms=self.current_weekly_report_ms)
        
        focused_section = self._get_section_object(botengine, report, section_id)
        if focused_section is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_weekly_entry() Need to create a new section for section_id '{}'.".format(section_id))
            section_properties = None
            # Check if the section is a default section
            if section_id in DEFAULT_SECTION_PROPERTIES:
                section_properties = DEFAULT_SECTION_PROPERTIES[section_id]
            # Check if the section is a custom section
            if self.section_config is not None and self.section_config.get(section_id, None) is not None:
                if self.section_config[section_id] == {}:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_add_weekly_entry() Section ignored by custom configuration '{}'".format(section_id))
                    return
                if section_properties is None:
                    section_properties = {
                        dailyreport.SECTION_KEY_WEIGHT: 0,
                        dailyreport.SECTION_KEY_TITLE: "", 
                        dailyreport.SECTION_KEY_DESCRIPTION: "",
                        dailyreport.SECTION_KEY_ICON: "",
                        dailyreport.SECTION_KEY_COLOR: "",
                        dailyreport.SECTION_KEY_TREND_IDS: [],
                        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
                    }
                section_properties.update(self.section_config[section_id])
            if section_properties is None:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("<_add_weekly_entry() No section properties found for section '{}'".format(section_id))
                return
            focused_section = {
                dailyreport.SECTION_KEY_ID: section_id,
                dailyreport.SECTION_KEY_WEIGHT: section_properties[dailyreport.SECTION_KEY_WEIGHT],
                dailyreport.SECTION_KEY_TITLE: section_properties[dailyreport.SECTION_KEY_TITLE],
                dailyreport.SECTION_KEY_DESCRIPTION: section_properties[dailyreport.SECTION_KEY_DESCRIPTION],
                dailyreport.SECTION_KEY_ICON: section_properties[dailyreport.SECTION_KEY_ICON],
                dailyreport.SECTION_KEY_COLOR: section_properties[dailyreport.SECTION_KEY_COLOR],
                dailyreport.SECTION_KEY_ITEMS: []
            }

            if section_id == dailyreport.SECTION_ID_WELLNESS:
                if self.section_config is None or self.section_config.get(section_id, {}).get('title', None) is None:
                    # Wellness is a special case because it has a dynamic title
                    focused_section[dailyreport.SECTION_KEY_TITLE] = self._get_wellness_title(botengine, section_properties[dailyreport.SECTION_KEY_TITLE])

            if 'sections' not in report:
                report['sections'] = []

            report['sections'].append(focused_section)
            report['sections'] = sorted(report['sections'], key=lambda k: k['weight'])

        if comment is not None or identifier is not None:
            # Backwards compatibility with older app versions that exclusively used a comment modified with the timestamp.
            timeless_comment = comment
            timeful_comment = comment
            timestamp_str = None

            if include_timestamp and comment is not None:
                if timestamp_override_ms is not None:
                    dt = self.parent.get_local_datetime_from_timestamp(botengine, timestamp_override_ms)
                else:
                    dt = self.parent.get_local_datetime(botengine)

                if section_id == dailyreport.SECTION_ID_SLEEP:
                    # Sleep timestamps include the day
                    timestamp_str = utilities.strftime(dt, "%-I:%M %p %A")

                    # Backwards compatibility with previous apps that use a 'comment' field which included the timestamp in the field.
                    timeful_comment = "{} - {}".format(timestamp_str, comment)
                else:
                    # Other timestamps don't include the day
                    timestamp_str = utilities.strftime(dt, "%-I:%M %p")
                    timeful_comment = "{} - {}".format(timestamp_str, comment)

            if identifier is None and comment is not None:
                ts = botengine.get_timestamp()
                if timestamp_override_ms is not None:
                    ts = timestamp_override_ms

                focused_item = {
                    "timestamp_ms": ts,
                    "comment": timeful_comment,
                    "comment_raw": timeless_comment
                }
                if timestamp_str is not None:
                    focused_item['timestamp_str'] = timestamp_str
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
                        focused_item['comment_raw'] = timeless_comment
                        if timestamp_str is not None:
                            focused_item['timestamp_str'] = timestamp_str
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
                        "comment": timeful_comment,
                        "comment_raw": timeless_comment,
                        "id": identifier
                    }
                    if timestamp_str is not None:
                        focused_item['timestamp_str'] = timestamp_str
                    focused_section['items'].append(focused_item)
                    focused_section['items'] = sorted(focused_section['items'], key=lambda k: k['timestamp_ms'])

        if subtitle is not None:
            # Manually defined subtitle for this section
            focused_section['subtitle'] = subtitle

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_add_weekly_entry() Setting weekly report to {}".format(json.dumps(report)))
        self.parent.set_location_property_separately(botengine, WEEKLY_REPORT_ADDRESS, report, overwrite=True, timestamp_ms=self.current_weekly_report_ms)
        
        # Track analytics
        analytic_properties = {
            "timestamp_ms": self.current_weekly_report_ms,
            "section_id": section_id,
            "period": WEEKLY_REPORT_ADDRESS
        }
        if identifier is not None:
            analytic_properties['id'] = identifier
        if comment is not None:
            analytic_properties['comment'] = comment
        analytics.track(botengine,
                        self.parent,
                        "daily_report_entry_added",
                        properties=analytic_properties)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_add_weekly_entry()")
        
    def _add_monthly_entry(self, botengine, section_id, comment=None, subtitle=None, identifier=None, include_timestamp=False, timestamp_override_ms=None):
        """
        Add a section and bullet point the current daily report
        :param botengine: BotEngine environment
        :param comment: Comment like "Woke up."
        :param subtitle: Subtitle comment like "Consistent sleep schedule and good quality sleep last night."
        :param identifier: Optional identifier to come back and edit this entry later.
        :param include_timestamp: True to include a timestamp like "7:00 AM - <comment>" (default is False)
        :param timestamp_override_ms: Optional timestamp in milliseconds to override the current time when citing the timestamp with include_timestamp=True
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_add_monthly_entry() section_id={} comment={} subtitle={} identifier={} include_timestamp={} timestamp_override_ms={}".format(section_id, comment, subtitle, identifier, include_timestamp, timestamp_override_ms))
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_monthly_entry() Current report timestamp is {}".format(self.current_monthly_report_ms))

        if self.current_monthly_report_ms is None:
            self._initialize_monthly_report(botengine, self._get_todays_timestamp(botengine))

        report = botengine.get_state(MONTHLY_REPORT_ADDRESS, timestamp_ms=self.current_monthly_report_ms)
        
        focused_section = self._get_section_object(botengine, report, section_id)
        if focused_section is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_monthly_entry() Need to create a new section for section_id '{}'.".format(section_id))
            section_properties = None
            # Check if the section is a default section
            if section_id in DEFAULT_SECTION_PROPERTIES:
                section_properties = DEFAULT_SECTION_PROPERTIES[section_id]
            # Check if the section is a custom section
            if self.section_config is not None and self.section_config.get(section_id, None) is not None:
                if self.section_config[section_id] == {}:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_add_monthly_entry() Section ignored by custom configuration '{}'".format(section_id))
                    return
                if section_properties is None:
                    section_properties = {
                        dailyreport.SECTION_KEY_WEIGHT: 0,
                        dailyreport.SECTION_KEY_TITLE: "", 
                        dailyreport.SECTION_KEY_DESCRIPTION: "",
                        dailyreport.SECTION_KEY_ICON: "",
                        dailyreport.SECTION_KEY_COLOR: "",
                        dailyreport.SECTION_KEY_TREND_IDS: [],
                        dailyreport.SECTION_KEY_INSIGHT_IDS: [],
                    }
                section_properties.update(self.section_config[section_id])
            if section_properties is None:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("<_add_monthly_entry() No section properties found for section '{}'".format(section_id))
                return
            focused_section = {
                dailyreport.SECTION_KEY_ID: section_id,
                dailyreport.SECTION_KEY_WEIGHT: section_properties[dailyreport.SECTION_KEY_WEIGHT],
                dailyreport.SECTION_KEY_TITLE: section_properties[dailyreport.SECTION_KEY_TITLE],
                dailyreport.SECTION_KEY_DESCRIPTION: section_properties[dailyreport.SECTION_KEY_DESCRIPTION],
                dailyreport.SECTION_KEY_ICON: section_properties[dailyreport.SECTION_KEY_ICON],
                dailyreport.SECTION_KEY_COLOR: section_properties[dailyreport.SECTION_KEY_COLOR],
                dailyreport.SECTION_KEY_ITEMS: []
            }

            if section_id == dailyreport.SECTION_ID_WELLNESS:
                if self.section_config is None or self.section_config.get(section_id, {}).get('title', None) is None:
                    # Wellness is a special case because it has a dynamic title
                    focused_section[dailyreport.SECTION_KEY_TITLE] = self._get_wellness_title(botengine, section_properties[dailyreport.SECTION_KEY_TITLE])

            if 'sections' not in report:
                report['sections'] = []

            report['sections'].append(focused_section)
            report['sections'] = sorted(report['sections'], key=lambda k: k['weight'])

        if comment is not None or identifier is not None:
            # Backwards compatibility with older app versions that exclusively used a comment modified with the timestamp.
            timeless_comment = comment
            timeful_comment = comment
            timestamp_str = None

            if include_timestamp and comment is not None:
                if timestamp_override_ms is not None:
                    dt = self.parent.get_local_datetime_from_timestamp(botengine, timestamp_override_ms)
                else:
                    dt = self.parent.get_local_datetime(botengine)

                if section_id == dailyreport.SECTION_ID_SLEEP:
                    # Sleep timestamps include the day
                    timestamp_str = utilities.strftime(dt, "%-I:%M %p %A")

                    # Backwards compatibility with previous apps that use a 'comment' field which included the timestamp in the field.
                    timeful_comment = "{} - {}".format(timestamp_str, comment)
                else:
                    # Other timestamps don't include the day
                    timestamp_str = utilities.strftime(dt, "%-I:%M %p")
                    timeful_comment = "{} - {}".format(timestamp_str, comment)

            if identifier is None and comment is not None:
                ts = botengine.get_timestamp()
                if timestamp_override_ms is not None:
                    ts = timestamp_override_ms

                focused_item = {
                    "timestamp_ms": ts,
                    "comment": timeful_comment,
                    "comment_raw": timeless_comment
                }
                if timestamp_str is not None:
                    focused_item['timestamp_str'] = timestamp_str
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
                        focused_item['comment_raw'] = timeless_comment
                        if timestamp_str is not None:
                            focused_item['timestamp_str'] = timestamp_str
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
                        "comment": timeful_comment,
                        "comment_raw": timeless_comment,
                        "id": identifier
                    }
                    if timestamp_str is not None:
                        focused_item['timestamp_str'] = timestamp_str
                    focused_section['items'].append(focused_item)
                    focused_section['items'] = sorted(focused_section['items'], key=lambda k: k['timestamp_ms'])

        if subtitle is not None:
            # Manually defined subtitle for this section
            focused_section['subtitle'] = subtitle

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_add_monthly_entry() Setting monthly report to {}".format(json.dumps(report)))
        self.parent.set_location_property_separately(botengine, MONTHLY_REPORT_ADDRESS, report, overwrite=True, timestamp_ms=self.current_monthly_report_ms)

        # Track analytics
        analytic_properties = {
            "timestamp_ms": self.current_monthly_report_ms,
            "section_id": section_id,
            "period": MONTHLY_REPORT_ADDRESS
        }
        if identifier is not None:
            analytic_properties['id'] = identifier
        if comment is not None:
            analytic_properties['comment'] = comment
        analytics.track(botengine,
                        self.parent,
                        "daily_report_entry_added",
                        properties=analytic_properties)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_add_monthly_entry()")

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
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_get_todays_timestamp() Midnight last night = {}; Today's timestamp = {}".format(self.parent.get_midnight_last_night(botengine), self.parent.timezone_aware_datetime_to_unix_timestamp(botengine, self.parent.get_midnight_last_night(botengine))))
        return self.parent.timezone_aware_datetime_to_unix_timestamp(botengine, self.parent.get_midnight_last_night(botengine))

    def _initialize_report(self, botengine, timestamp):
        """
        Create a new report

        :param botengine: BotEngine environment
        :param timestamp: Timestamp in milliseconds
        :return: Report object
        """
        self.current_report_ms = timestamp
        report = {}

        name = self._get_resident_name(botengine)
        if name is not None:
            report['title'] = name.upper()
        else:
            report['title'] = _("DAILY REPORT")

        report['subtitle'] = _("Daily Report for {}").format(utilities.strftime(self.parent.get_local_datetime(botengine), "%A %B %-d, %Y"))
        report['created_ms'] = self.current_report_ms
        report['sections'] = []
        report['period'] = DAILY_REPORT_ADDRESS
        self.parent.set_location_property_separately(botengine, DAILY_REPORT_ADDRESS, report, overwrite=True, timestamp_ms=self.current_report_ms)

        # Track analytics
        analytics.track(botengine,
                        self.parent,
                        "daily_report_initialized",
                        properties={
                            "timestamp_ms": self.current_report_ms,
                            "period": DAILY_REPORT_ADDRESS
                        })
        
        # Add our first entry if possible.
        if self.started_sleeping_ms is not None and "SLEEP" in self.parent.occupancy_status:
            self._add_entry(botengine, dailyreport.SECTION_ID_SLEEP, comment=_("Went to sleep."), subtitle=_("Currently sleeping."), include_timestamp=True, timestamp_override_ms=self.started_sleeping_ms)

        # Notify that a new daily report has been created
        dailyreport.report_status_updated(botengine, self.parent, report, status=dailyreport.REPORT_STATUS_CREATED)

        return report
    
    def _initialize_weekly_report(self, botengine, timestamp):
        """
        Create a new report

        :param botengine: BotEngine environment
        :param timestamp: Timestamp in milliseconds
        :return: Report object
        """
        self.current_weekly_report_ms = timestamp
        report = {}

        name = self._get_resident_name(botengine)
        if name is not None:
            report['title'] = name.upper()
        else:
            report['title'] = _("WEEKLY REPORT")

        report['subtitle'] = _("Weekly Report for {}").format(utilities.strftime(self.parent.get_local_datetime(botengine), "%A %B %-d, %Y"))
        report['created_ms'] = self.current_weekly_report_ms
        report['sections'] = []
        report['period'] = WEEKLY_REPORT_ADDRESS
        self.parent.set_location_property_separately(botengine, WEEKLY_REPORT_ADDRESS, report, overwrite=True, timestamp_ms=timestamp)

        # Track analytics
        analytics.track(botengine,
                        self.parent,
                        "daily_report_initialized",
                        properties={
                            "timestamp_ms": timestamp,
                            "period": WEEKLY_REPORT_ADDRESS
                        })
        
        # Notify that a new weekly report has been created
        dailyreport.report_status_updated(botengine, self.parent, report, status=dailyreport.REPORT_STATUS_CREATED)

        return report
    
    def _initialize_monthly_report(self, botengine, timestamp):
        """
        Create a new report

        :param botengine: BotEngine environment
        :param timestamp: Timestamp in milliseconds
        :return: Report object
        """
        self.current_monthly_report_ms = timestamp
        report = {}

        name = self._get_resident_name(botengine)
        if name is not None:
            report['title'] = name.upper()
        else:
            report['title'] = _("MONTHLY REPORT")

        report['subtitle'] = _("Monthly Report for {}").format(utilities.strftime(self.parent.get_local_datetime(botengine), "%B %Y"))
        report['created_ms'] = self.current_monthly_report_ms
        report['sections'] = []
        report['period'] = MONTHLY_REPORT_ADDRESS
        self.parent.set_location_property_separately(botengine, MONTHLY_REPORT_ADDRESS, report, overwrite=True, timestamp_ms=timestamp)

        # Track analytics
        analytics.track(botengine,
                        self.parent,
                        "daily_report_initialized",
                        properties={
                            "timestamp_ms": timestamp,
                            "period": MONTHLY_REPORT_ADDRESS
                        })

        # Notify that a new monthly report has been created
        dailyreport.report_status_updated(botengine, self.parent, report, status=dailyreport.REPORT_STATUS_CREATED)

        return report
    
    def _report_key(self, botengine, report_address=DAILY_REPORT_ADDRESS, date=None):
        """
        Generate a key to manage data for a specific report.
        
        :param botengine: BotEngine environment
        :param report_address: Report address
        :param date: Date object
        :return: Key string
        """
        if report_address == WEEKLY_REPORT_ADDRESS:
            # Weekly reports are stored by year and week number
            # Note: Respects iso/gregorian calendar, so the first few days of a year might be in the last week of the previous year.
            return "{}_{}".format(f"{date.isocalendar()[0]:02}", f"{date.isocalendar()[1]:02}")
        elif report_address == MONTHLY_REPORT_ADDRESS:
            # Monthly reports are stored by year and month number
            return "{}_{}".format(date.year, f"{date.month:02}")
        # Daily reports are stored by year and day number
        return "{}_{}_{}".format(date.year, f"{date.month:02}", f"{date.day:02}")

                
    def _section_id_for_insight(self, botengine, id):
        """
        Section ID for an insight
        :param botengine: BotEngine environment
        :param id: Insight ID
        :return: Section ID if we should process this event, or None if we shouldn't
        """
        if self.section_config is not None:
            for section_id in self.section_config.keys():
                if any(insight_id in id for insight_id in self.section_config[section_id].get(dailyreport.SECTION_KEY_INSIGHT_IDS, [])):
                    return section_id
        for section_id in DEFAULT_SECTION_PROPERTIES.keys():
            if self.section_config is not None and section_id in self.section_config and self.section_config[section_id] is {}:
                # Disabled by custom configuration
                continue
            if any(insight_id in id for insight_id in DEFAULT_SECTION_PROPERTIES[section_id][dailyreport.SECTION_KEY_INSIGHT_IDS]):
                return section_id
        return None


    def _section_id_for_trend(self, botengine, id):
        """
        Section ID for a trend
        :param botengine: BotEngine environment
        :param id: Trend ID
        :return: Section ID if we should process this event, or None if we shouldn't
        """
        if self.section_config is not None:
            for section_id in self.section_config.keys():
                if any(trend_id in id for trend_id in self.section_config[section_id].get(dailyreport.SECTION_KEY_TREND_IDS, [])):
                    return section_id
        for section_id in DEFAULT_SECTION_PROPERTIES.keys():
            if self.section_config is not None and section_id in self.section_config and self.section_config[section_id] is {}:
                # Disabled by custom configuration
                continue
            if any(trend_id in id for trend_id in DEFAULT_SECTION_PROPERTIES[section_id][dailyreport.SECTION_KEY_TREND_IDS]):
                return section_id
        return None
    
    def _get_wellness_title(self, botengine, title):
        """
        Get the wellness title
        :param botengine: BotEngine environment
        :return: Wellness title
        """
        service_name = properties.get_property(botengine, "SERVICE_NAME")
        if service_name is None:
            return title
        else:
            return "{} {}".format(service_name, title)
        
    def _ask_questions(self, botengine):
        """
        Refresh questions
        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">ask_question()")

        try:
            from localization import get_translations
        except ImportError:
            get_translations = None

        botengine.set_collection(name=SERVICES_COLLECTION_NAME,
                                 icon="file-alt", 
                                 description="Daily Report Settings",
                                 weight=SERVICES_COLLECTION_WEIGHT,
                                 ml_name=get_translations(botengine, SERVICES_COLLECTION_NAME) if get_translations else None,
                                 ml_description=get_translations(botengine, "Daily Report Settings") if get_translations else None)

        dailyreport_state =  botengine.get_state(DAILYREPORT_STATE_VARIABLE_NAME)
        if dailyreport_state is None:
            dailyreport_state = {}

        # DAILY REPORT ACTIVATION
        is_enabled = dailyreport_state.get(SERVICE_KEY_ACTIVE, None)
        if is_enabled is None:
            # On by default
            is_enabled = True

        # Create a new question if needed
        is_enabled_question_object = botengine.retrieve_question(SERVICE_KEY_ACTIVE)

        if is_enabled_question_object is None:
            is_enabled_question_object = botengine.generate_question(SERVICE_KEY_ACTIVE,
                                                                            botengine.QUESTION_RESPONSE_TYPE_BOOLEAN,
                                                                            collection=SERVICES_COLLECTION_NAME,
                                                                            icon="file-alt",
                                                                            display_type=botengine.QUESTION_DISPLAY_BOOLEAN_ONOFF,
                                                                            default_answer=is_enabled,
                                                                            editable=True,
                                                                            section_id=SERVICE_SECTION_ID,
                                                                            question_weight=SERVICE_WEIGHT_ACTIVE)
            is_enabled_question_object.set_section_title(_("Wellness Reports"))
        
        is_enabled_question_object.editable = True
        is_enabled_question_object.answer = self.parent.get_location_property(botengine, SERVICE_KEY_ACTIVE)
        is_enabled_question_object.default_answer = is_enabled
        botengine.ask_question(is_enabled_question_object)
        
        framed_question = _("Automated Daily Reports Services")
        if 'en' not in is_enabled_question_object.question:
            is_enabled_question_object.frame_question(framed_question, 'en')
            botengine.ask_question(is_enabled_question_object)

        if is_enabled_question_object.question['en'] != framed_question:
            is_enabled_question_object.frame_question(framed_question, "en")
            botengine.ask_question(is_enabled_question_object)

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|ask_question() services enabled: {}".format(is_enabled))
        self._set_service(botengine, 
                          comment=_("Automated reporting of insights and statistical analysis for Daily, Weekly, and Monthly Reports for the Trusted Circle."), 
                          status=dashboard.STATUS_GOOD if is_enabled else dashboard.STATUS_CRITICAL, 
                          percent=100, 
                          active=is_enabled, 
                          status_text=_("RUNNING") if is_enabled else _("DISABLED"), 
                          context=None)
    
    def _is_active(self, botengine):
        """
        Is the service active?
        :param botengine: BotEngine environment
        :return: True if the service is active
        """
        if botengine.playback:
            return True
        dailyreport_state =  botengine.get_state(DAILYREPORT_STATE_VARIABLE_NAME)
        if dailyreport_state is None:
            dailyreport_state = {}

        is_enabled = dailyreport_state.get(SERVICE_KEY_ACTIVE, None)
        if is_enabled is None:
            # On by default
            is_enabled = True
        return is_enabled
    
    def _weekly_reports_enabled(self, botengine):
        """
        Are weekly reports enabled?
        :param botengine: BotEngine environment
        :return: True if weekly reports are enabled
        """
        weekly_reports_enabled = properties.get_property(botengine, "WEEKLY_REPORTS_ENABLED", complain_if_missing=False)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_weekly_reports_enabled() weekly_reports_enabled={}".format(weekly_reports_enabled))
        if weekly_reports_enabled is None:
            return True
        return weekly_reports_enabled
    
    def _monthly_reports_enabled(self, botengine):
        """
        Are monthly reports enabled?
        :param botengine: BotEngine environment
        :return: True if monthly reports are enabled
        """
        monthly_reports_enabled = properties.get_property(botengine, "MONTHLY_REPORTS_ENABLED", complain_if_missing=False)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_monthly_reports_enabled() monthly_reports_enabled={}".format(monthly_reports_enabled))
        if monthly_reports_enabled is None:
            return True
        return monthly_reports_enabled

    def _set_service(self, botengine, comment, status, percent, active, status_text, context):
        """
        Set the service in the dashboard
        :param botengine: BotEngine environment
        :param comment: Comment
        :param status: Status
        :param percent: Percent
        :param active: Active
        :param status_text: Status text
        :param context: Context
        """
        description = _("""**Daily Reports:**

Our "Daily Reports" service is designed to transform statistical data into personalized insights for care providers within the Trusted Circle. 

- **Automated Daily Reports**: This feature automatically generates daily, weekly, and monthly reports, providing a comprehensive overview of relevant information.
                                                
- **Wellness Reports**: Utilize the Wellness Report services to receive insights and analysis for Weekly and Monthly Reports directly over email.
                        
- **Report Summaries**: Receive daily summaries over email and SMS of the most important insights and statistical data, ensuring that you stay informed and up-to-date with the latest information.
                        
Tailoring content to the specific needs of the Trusted Circle ensures that care providers receive accurate and targeted insights, facilitating informed decision-making and enhancing the overall quality of care. Stay connected and well-informed with Daily Reports, your personalized window into meaningful statistical data.""")
        
        if context:
            description += "\n\n" + context
        dashboard.set_service(
            botengine, 
            self.parent,
            unique_identifier=SERVICE_KEY_ACTIVE,
            title=_("Daily Reports"),
            comment=comment,
            icon="calendar",
            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
            status=status,
            percent=percent,
            active=active,
            description=description,
            status_text=status_text,
            collection_id=SERVICES_COLLECTION_NAME,
            comment_weight=SERVICES_COLLECTION_WEIGHT)