'''
Created on November 20, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence

import properties
import json
import utilities.utilities as utilities
import signals.analytics as analytics
import signals.dailyreport as dailyreport
import signals.dashboard as dashboard

# Current version
VERSION = 1.1

# Section Properties
DEFAULT_SECTION_PROPERTIES = {
    dailyreport.SECTION_ID_WELLNESS: {
        dailyreport.SECTION_KEY_WEIGHT: -5,
        dailyreport.SECTION_KEY_TITLE: _("Wellness"),
        dailyreport.SECTION_KEY_DESCRIPTION: _("Overall physical and mental health status."),
        dailyreport.SECTION_KEY_ICON: "heart",
        dailyreport.SECTION_KEY_COLOR: "F47174",
        dailyreport.SECTION_KEY_TREND_IDS: [
            "trend.sleep_score", 
            "trend.bedtime_score", 
            "trend.wakeup_score", 
            "trend.restlessness_score", 
            "trend.wellness_score", 
            "trend.mobility_score",
            "trend.stability_score",
            "trend.hygiene_score", 
            "trend.bathroom_score",
            "trend.social_score", 
            "trend.care_score",
            "trend.illbeing_score",
            "trend.positivity_score",
            "trend.sleep_diary",
            "trend.percieved_stress_scale",
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
            "care.inactivity.bedtime_awake_too_late", 
            "sleep.low_sleep_quality.warning", 
            "sleep.too_many_bathrooms.warning", 
            "care.inactivity.time_to_stretch", 
            "care.inactivity.warning", 
            "care.inactivity.good_morning_sleeping_in", 
            "care.inactivity.good_morning_problem_critical", 
            "care.inactivity.good_morning_problem", 
            "care.inactivity.not_back_home.warning", 
            "request_assistance", 
            "care.sms_sos", 
            "health_high_heart_rate_warning", 
            "health_movement_confirmed_alert", 
            "vayyar.fall_confirmed_alert", 
            "vayyar.stability_event_confirmed_alert",
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
            "sleep.duration_ms", 
            "sleep.bedtime_ms", 
            "sleep.wakeup_ms", 
            "sleep.sleep_score", 
            "sleep.underslept", 
            "sleep.overslept", 
            "sleep.bedtime_score", 
            "sleep.wakeup_ms", 
            "sleep.restlessness_score", 
            "sleep.sleep_prediction_ms", 
            "sleep.wake_prediction_ms",
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
            "trend.mobility_rooms", 
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
            "trend.bathroom_duration", 
            "trend.shower_visits", 
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
            "trend.together", 
            "occupancy.return_ms"
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
        dailyreport.SECTION_KEY_INSIGHT_IDS: [
            "security_mode", 
            "occupancy.status"
        ],
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
SERVICES_COLLECTION_NAME    = _("Daily Report Settings")
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

    States are managed in the `dailyreport` state variable.
    {   
        "version": Str, # Version of the daily report microservice
        "dailyreport.is_enabled": Bool, # Is the daily report service enabled
    }
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
            self.version = VERSION
        return

    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        if self.version != VERSION:
            self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, {'version': VERSION})
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

        if week_key not in self.weekly_reports:
            self.weekly_reports[week_key] = {}
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
        
        if f"insight-{insight_id}" not in self.weekly_reports[week_key]:
            self.weekly_reports[week_key][f"insight-{insight_id}"] = {
                "title": insight_json.get('title', "Insight"),
                "values": {},
            }

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

        if day_of_week not in self.weekly_reports[week_key][f"insight-{insight_id}"]["values"]:
            self.weekly_reports[week_key][f"insight-{insight_id}"]["values"][day_of_week] = []
        self.weekly_reports[week_key][f"insight-{insight_id}"]["values"][day_of_week].append(value)
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
            comment = display
            if metadata.get("title", None) is not None:
                comment = "{}: {}".format(metadata.get("title", None), comment)
            self._add_entry(botengine, section_id, comment=comment, identifier=f"trend-{trend_id}")
        
        # Track this trend for weekly and monthly reports
        timestamp = trend_info.get('updated_ms', botengine.get_timestamp())
        daily_key = self._report_key(botengine, report_address=DAILY_REPORT_ADDRESS, date=self.parent.get_local_datetime_from_timestamp(botengine, timestamp))
        weekly_key = self._report_key(botengine, report_address=WEEKLY_REPORT_ADDRESS, date=self.parent.get_local_datetime_from_timestamp(botengine, timestamp))
        monthly_key = self._report_key(botengine, report_address=MONTHLY_REPORT_ADDRESS, date=self.parent.get_local_datetime_from_timestamp(botengine, timestamp))

        if weekly_key not in self.weekly_reports:
            self.weekly_reports[weekly_key] = {}
        if f"trend-{trend_id}" not in self.weekly_reports[weekly_key]:
            self.weekly_reports[weekly_key][f"trend-{trend_id}"] = {}

        if monthly_key not in self.monthly_reports:
            self.monthly_reports[monthly_key] = {}
        if f"trend-{trend_id}" not in self.monthly_reports[monthly_key]:
            self.monthly_reports[monthly_key][f"trend-{trend_id}"] = {}
        updated_ms = trend_info.get('updated_ms', None)
        if updated_ms is None:
            updated_ms = botengine.get_timestamp()
        
        # Store daily trends for weekly report metrics
        self.weekly_reports[weekly_key][f"trend-{trend_id}"][daily_key] = trend_info

        # Store weekly trends for monthly report metrics
        self.monthly_reports[monthly_key][f"trend-{trend_id}"][weekly_key] = trend_info
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<trend_processed()")

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

                            # TODO: Add a comment for these insights
                            """
                            "security_mode", 
                            "occupancy.status"
                            """
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
                            comment = "You selpt the best on {}".format(WEEK_DAYS[max_index])
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
                            comment = "You selpt the best on {}".format(utilities.strftime(max_dt, "%A, %B %-d"))
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
            if section_id not in DEFAULT_SECTION_PROPERTIES:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<_add_entry() Unknown section '{}'".format(section_id))
                return
            section_properties = DEFAULT_SECTION_PROPERTIES[section_id]
            focused_section = {
                dailyreport.SECTION_KEY_ID: section_id,
                dailyreport.SECTION_KEY_WEIGHT: section_properties[dailyreport.SECTION_KEY_WEIGHT],
                dailyreport.SECTION_KEY_TITLE: section_properties[dailyreport.SECTION_KEY_TITLE],
                dailyreport.SECTION_KEY_ICON: section_properties[dailyreport.SECTION_KEY_ICON],
                dailyreport.SECTION_KEY_COLOR: section_properties[dailyreport.SECTION_KEY_COLOR],
                dailyreport.SECTION_KEY_ITEMS: []
            }

            if section_id == dailyreport.SECTION_ID_WELLNESS:
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

            elif section_id == dailyreport.SECTION_ID_MEDICATION:
                if len(focused_section['items']) == 0:
                    focused_section['subtitle'] = _("No medication accessed today.")

                elif len(focused_section['items']) == 1:
                    focused_section['subtitle'] = _("Accessed medicine once today.")

                elif len(focused_section['items']) > 1:
                    focused_section['subtitle'] = _("Accessed medicine {} times today.").format(len(focused_section['items']))

            elif section_id == dailyreport.SECTION_ID_BATHROOM:
                if len(focused_section['items']) == 0:
                    focused_section['subtitle'] = _("No bathroom visits observed today.")

                elif len(focused_section['items']) == 1:
                    focused_section['subtitle'] = _("Visited the bathroom once today.")

                elif len(focused_section['items']) > 1:
                    focused_section['subtitle'] = _("Visited the bathroom {} times today.").format(len(focused_section['items']))
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_add_daily_entry() Setting daily report to {}".format(json.dumps(report, indent=2, sort_keys=True)))
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
            if section_id not in DEFAULT_SECTION_PROPERTIES:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<_add_weekly_entry() Unknown section '{}'".format(section_id))
                return
            section_properties = DEFAULT_SECTION_PROPERTIES[section_id]
            focused_section = {
                dailyreport.SECTION_KEY_ID: section_id,
                dailyreport.SECTION_KEY_WEIGHT: section_properties[dailyreport.SECTION_KEY_WEIGHT],
                dailyreport.SECTION_KEY_TITLE: section_properties[dailyreport.SECTION_KEY_TITLE],
                dailyreport.SECTION_KEY_ICON: section_properties[dailyreport.SECTION_KEY_ICON],
                dailyreport.SECTION_KEY_COLOR: section_properties[dailyreport.SECTION_KEY_COLOR],
                dailyreport.SECTION_KEY_ITEMS: []
            }

            if section_id == dailyreport.SECTION_ID_WELLNESS:
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
            if section_id not in DEFAULT_SECTION_PROPERTIES:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<_add_monthly_entry() Unknown section '{}'".format(section_id))
                return
            section_properties = DEFAULT_SECTION_PROPERTIES[section_id]
            focused_section = {
                dailyreport.SECTION_KEY_ID: section_id,
                dailyreport.SECTION_KEY_WEIGHT: section_properties[dailyreport.SECTION_KEY_WEIGHT],
                dailyreport.SECTION_KEY_TITLE: section_properties[dailyreport.SECTION_KEY_TITLE],
                dailyreport.SECTION_KEY_ICON: section_properties[dailyreport.SECTION_KEY_ICON],
                dailyreport.SECTION_KEY_COLOR: section_properties[dailyreport.SECTION_KEY_COLOR],
                dailyreport.SECTION_KEY_ITEMS: []
            }

            if section_id == dailyreport.SECTION_ID_WELLNESS:
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
        for section_id in DEFAULT_SECTION_PROPERTIES.keys():
            if any(trend_id in id for trend_id in DEFAULT_SECTION_PROPERTIES[section_id][dailyreport.SECTION_KEY_INSIGHT_IDS]):
                return section_id
        return None


    def _section_id_for_trend(self, botengine, id):
        """
        Section ID for a trend
        :param botengine: BotEngine environment
        :param id: Trend ID
        :return: Section ID if we should process this event, or None if we shouldn't
        """
        for section_id in DEFAULT_SECTION_PROPERTIES.keys():
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
        self.version = VERSION

        botengine.set_collection(name=SERVICES_COLLECTION_NAME,
                                 icon="file-alt",
                                 description=_("Daily Report Settings"),
                                 weight=SERVICES_COLLECTION_WEIGHT)

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