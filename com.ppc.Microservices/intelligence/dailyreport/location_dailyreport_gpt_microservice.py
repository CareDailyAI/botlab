'''
Created on September 15, 2023

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
TODO: Finish implementing logic to understand user context and deliver and track events
'''

from intelligence.intelligence import Intelligence

import properties
import json
import utilities.utilities as utilities
import utilities.genai as genai

import signals.analytics as analytics
import signals.dailyreport as dailyreport
import signals.dashboard as dashboard

from users.user import (
    User,
    ROLE_TYPE_PROFESSIONAL_CAREGIVER,
    ROLE_TYPE_PRIMARY_FAMILY_CAREGIVER,
)

from intelligence.dailyreport.location_dailyreport_microservice import *

# Daily Report GPT State Variable
DAILYREPORT_GPT_STATE_VARIABLE_NAME = "dailyreport_gpt"

# OpenAI response key identifer prefix
OPENAI_RESPONSE_KEY_PREFIX = "dailyreport_gpt"

# Timer to defer the report generation
# Period and report type ID are replaced at runtime
PUBLISH_REPORT_TIMER = "publish_report_timer_<period>_<report_type_id>"

# Default time to wait before submitting the report to OpenAI
DEFAULT_REPORT_DELAY_TIME_MS = utilities.ONE_MINUTE_MS * 30

# Default time to wait before between each OpenAI request
DEFAULT_REPORT_DEFER_TIME = utilities.ONE_MINUTE_MS * 10

# Minimum time between each OpenAI request
REPORT_DEFER_TIME_MINIMUM = utilities.ONE_MINUTE_MS * 5

# Organization Domain Service Key Supported
DOMAIN_KEY_GPT_SUPPORTED = "DAILYREPORT_GPT_SUPPORTED"

# Organization Domain Service Key Active
DOMAIN_KEY_GPT_ENABLED = "DAILYREPORT_GPT_ENABLED"

# GPT not enabled by default
DEFAULT_GPT_ENABLED = False

# Enable or disable gpt services
SERVICE_SECTION_ID_GPT         = 0
SERVICE_KEY_GPT_ACTIVE         = "gpt.is_enabled"
SERVICE_WEIGHT_GPT_ACTIVE      = 100

# Default report types
DEFAULT_REPORT_TYPES = [
    {
        "id": 0,
        "role_type": ROLE_TYPE_PRIMARY_FAMILY_CAREGIVER,
        "assistant_example": "Digs had a low-average trips, little bit of wiggle room, but nothing major. Mostly chillin' recently.",
        "rules": [
            "Provide a concise summary in less than 30 words.",
            "Use slang.",
        ],
        "supported_section_ids": [
            dailyreport.SECTION_ID_WELLNESS,
            # dailyreport.SECTION_ID_ALERTS,
            # dailyreport.SECTION_ID_NOTES,
            # dailyreport.SECTION_ID_TASKS,
            # dailyreport.SECTION_ID_SLEEP,
            # dailyreport.SECTION_ID_ACTIVITIES,
            # dailyreport.SECTION_ID_MEALS,
            # dailyreport.SECTION_ID_MEDICATION,
            # dailyreport.SECTION_ID_BATHROOM,
            # dailyreport.SECTION_ID_SOCIAL,
            # dailyreport.SECTION_ID_MEMORIES,
            # dailyreport.SECTION_ID_SYSTEM,
        ],
        "supported_trend_ids": [
            # "trend.sleep_score", 
            # "trend.bedtime_score", 
            # "trend.wakeup_score", 
            # "trend.restlessness_score", 
            "trend.wellness_score", 
            # "trend.mobility_score",
            # "trend.stability_score",
            # "trend.hygiene_score", 
            # "trend.bathroom_score",
            # "trend.social_score", 
            "trend.care_score",
            # "trend.illbeing_score",
            # "trend.positivity_score",
            # "trend.sleep_diary",
            # "trend.percieved_stress_scale",
            # "trend.total_falls", 
            # "trend.fall_duration",
            # "trend.bedtime", 
            # "trend.sleep_bathroom_visits", 
            # "trend.sleep_duration", 
            # "trend.wakeup", 
            # "trend.sleep_movement", 
            # "trend.nap_duration",
            # "trend.mobility_duration", 
            # "trend.mobility_rooms", 
            # "sitting",
            # "trend.bathroom_visits", 
            # "trend.bathroom_duration", 
            # "trend.shower_visits", 
            # "trend.absent", 
            # "trend.checkedin", 
            # "trend.visitor", 
            # "trend.together", 
            # "occupancy.return_ms"
        ],
        "supported_insight_ids": [
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
            # "security_mode", 
            # "occupancy.status"
        ]
    },
    {
        "id": 1,
        "role_type": ROLE_TYPE_PROFESSIONAL_CAREGIVER,
        "assistant_example": "In a 30-day period, this residence recorded an average of 0.2 potential falls, with a high variability as indicated by a standard deviation of 1.4. The standard score of 0.67 suggests the data is slightly above the mean. The information suggests fluctuating fall risks within this setting.",
        "rules": [
            "Provide a concise summary in less than 100 words.",
            "Use medical terminology.",
        ],
        "supported_section_ids": [
            dailyreport.SECTION_ID_WELLNESS,
            # dailyreport.SECTION_ID_ALERTS,
            # dailyreport.SECTION_ID_NOTES,
            # dailyreport.SECTION_ID_TASKS,
            # dailyreport.SECTION_ID_SLEEP,
            # dailyreport.SECTION_ID_ACTIVITIES,
            # dailyreport.SECTION_ID_MEALS,
            # dailyreport.SECTION_ID_MEDICATION,
            # dailyreport.SECTION_ID_BATHROOM,
            # dailyreport.SECTION_ID_SOCIAL,
            # dailyreport.SECTION_ID_MEMORIES,
            # dailyreport.SECTION_ID_SYSTEM,
        ],
        "supported_trend_ids": [
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
            # "trend.illbeing_score",
            # "trend.positivity_score",
            # "trend.sleep_diary",
            # "trend.percieved_stress_scale",
            # "trend.total_falls", 
            # "trend.fall_duration",
            # "trend.bedtime", 
            # "trend.sleep_bathroom_visits", 
            # "trend.sleep_duration", 
            # "trend.wakeup", 
            # "trend.sleep_movement", 
            # "trend.nap_duration",
            # "trend.mobility_duration", 
            # "trend.mobility_rooms", 
            # "sitting",
            # "trend.bathroom_visits", 
            # "trend.bathroom_duration", 
            # "trend.shower_visits", 
            # "trend.absent", 
            # "trend.checkedin", 
            # "trend.visitor", 
            # "trend.together", 
            # "occupancy.return_ms"
        ],
        "supported_insight_ids": [
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
            # "security_mode", 
            # "occupancy.status"
        ]
    },
]

# Default system rules
DEFAULT_SYSTEM_RULES = [
    "You will be provided with statistical data for a single residence.",
]

# Primary Caregiver GPT Reports default
PRIMARY_CAREGIVER_GPT_REPORT_ENABLED = False

# Maximum number of tokens
MAX_TOKENS = 1000

#===============================================================================

class LocationDailyReportGPTMicroservice(Intelligence):
    """
    Interpret daily reports and produce GPT reports.

    This microservce coordinates report generation based on Activities of Daily Living and other data.
    Accumulated daily, weekly, and monthly, the report content is distributed to LLM Services (i.e., OpenAI ChatGPT) for analysis and generation of 1 or more reports based on user roles at this location.
    Reports are distributed to the user's preferred communication channel at appropriate times, and can be available on command (TODO: Add hooks to "download" your report.).

    Additional states are managed in the `dailyreport` state variable.
    {   
    
        "has_gpt": Bool, # GPT microservice included in bundle
        "gpt.is_enabled": Bool, # GPT service enabled
    }

    Front end information is managed through the `dailyreport_gpt` state variable.
    {
        "report_types": [
            {
                "id": Int, # Unique Report Type ID
                "role_type": Int, # Role Type ID (users.user.ROLE_TYPE_*)
                "role": String, # Name of the role
                "rules": [String], # Rules for this role
                "supported_section_ids": [Int], # Supported section IDs (See dailyreport.SECTION_ID_*)
                "supported_trend_ids": [String], # Supported trend IDs
                "supported_insight_ids": [String], # Supported insight IDs

            }
        ],
        "system_rules": [String], # System rules
    }

    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # Version
        self.version = None

        # Active report content
        self.report_content = {}

        # Array of messages in the gpt chat
        self.messages = {}

        # Initialize the state variable
        self._initialize_state_variable(botengine)

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        pass

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """

        if self.version != VERSION:
            self._ask_questions(botengine)
        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">destroy()")

        self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, {'has_gpt': False})

        question_object = botengine.retrieve_question(SERVICE_KEY_GPT_ACTIVE)
        if question_object is not None:
            botengine.delete_question(question_object)
        pass

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        pass

    def occupancy_status_updated(self, botengine, status, reason, last_status, last_reason):
        """
        AI Occupancy Status updated
        :param botengine: BotEngine
        :param status: Current occupancy status
        :param reason: Current occupancy reason
        :param last_status: Last occupancy status
        :param last_reason: Last occupancy reason
        """
        pass

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        pass

    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        pass

    def device_alert(self, botengine, device_object, alert_type, alert_params):
        """
        Device sent an alert.
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
        :param alert_params: Alert parameters as key/value dictionary
        """
        pass

    def device_added(self, botengine, device_object):
        """
        A new Device was added to this Location
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting added
        """
        pass

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

        # GPT ENABLED
        if question_object.key_identifier == SERVICE_KEY_GPT_ACTIVE:
            
            # Services are turned on
            if utilities.get_answer(question_object):
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|question_answered() GPT enabled")
                analytics.track(botengine, self.parent, "service_dailyreport_gpt_activated")
                self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, {SERVICE_KEY_GPT_ACTIVE: True})
                # NOTE: GPT service turned on.
                self.parent.narrate(botengine,
                                    title=_("Daily Report Wellness Reports services activated."),
                                    description=_("Wellness Reports have been turned on{}.").format(message),
                                    priority=botengine.NARRATIVE_PRIORITY_INFO,
                                    icon="file-alt",
                                    icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                                    question_key=SERVICE_KEY_GPT_ACTIVE,
                                    event_type="dailyreport_gpt.activated")
            else:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|question_answered() GPT disabled")
                analytics.track(botengine, self.parent, "service_dailyreport_gpt_deactivated")
                self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, {SERVICE_KEY_GPT_ACTIVE: False})
                # NOTE: GPT service turned off.
                self.parent.narrate(botengine,
                                    title=_("Daily Report Wellness Report services deactivated."),
                                    description=_("Wellness Reports have been turned off{}.").format(message),
                                    priority=botengine.NARRATIVE_PRIORITY_INFO,
                                    icon="file-alt",
                                    icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                                    question_key=SERVICE_KEY_GPT_ACTIVE,
                                    event_type="dailyreport_gpt.deactivated")
                
        elif question_object.key_identifier == SERVICE_KEY_ACTIVE:
            pass
        else:
            # Not Supported
            return
        self._ask_questions(botengine)   
        pass

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
        pass

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">timer_fired() argument={}".format(json.dumps(argument)))
        if argument is None:
            return
        period = argument.get("period", None)
        report_type_id = argument.get("report_type_id", None)
        if period is None or report_type_id is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<timer_fired() Missing period or report_type_id")
            return
        if period not in self.report_content.keys():
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<timer_fired() Missing report content for period={}".format(period))
            return
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|timer_fired() period={} report_type_id={}".format(period, report_type_id))
        if self.messages[period].get(report_type_id, {}).get('messages'):
            messages = self.messages[period][report_type_id]['messages']
            responses = self.messages[period][report_type_id]['responses']
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|timer_fired() messages={}".format(json.dumps(messages, indent=2)))
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|timer_fired() responses={}".format(json.dumps(responses, indent=2)))
            if len(messages) - len(responses) > 0:
                _messages = messages[len(responses)]
                openai_params = genai.chat_completion_model(
                    botengine, 
                    messages=_messages,
                    max_tokens=MAX_TOKENS,
                    stop=[]
                    )
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|timer_fired() openai_params={}".format(json.dumps(openai_params)))
                import signals.openai as openai
                # Key the request by period, report type, and the number of responses we've already received
                key = self._created_openai_key(botengine, period, report_type_id, len(responses))
                openai.submit_chat_completion_request(botengine, self.parent, key, openai_params)
                
                # Process the next request in 10 minutes.  Pass through to completion if none are left.
                # May be overridden by bot domain property GPT_PROMPT_DEFERRAL.
                deferral_time_ms = DEFAULT_REPORT_DEFER_TIME
                if properties.get_property(botengine, "GPT_PROMPT_DEFERRAL", False) is not None:
                    gpt_prompt_deferral = properties.get_property(botengine, "GPT_PROMPT_DEFERRAL", False)
                    # Make sure the deferral time is at least 5 minutes
                    if gpt_prompt_deferral > REPORT_DEFER_TIME_MINIMUM:
                        deferral_time_ms = gpt_prompt_deferral
                self.start_timer_ms(botengine, deferral_time_ms, argument={"period": period, "report_type_id": report_type_id}, reference=PUBLISH_REPORT_TIMER.replace('<period>', period).replace('<report_type_id>', str(report_type_id)))
            else:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|timer_fired() No more messages to send")
                self._complete_report(botengine, period, report_type_id)
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<timer_fired()")
            return
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|timer_fired() Publish the report")
        report = self.report_content[period]["report"]
        metadata = self.report_content[period]["metadata"]
        self._publish_gpt_report(botengine, period, report_type_id, report, metadata)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<timer_fired()")
        pass

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
        pass

    def coordinates_updated(self, botengine, latitude, longitude):
        """
        Approximate coordinates of the parent proxy device object have been updated
        :param latitude: Latitude
        :param longitude: Longitude
        """
        pass

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
        pass

    def daily_report_status_updated(self, botengine, content):
        """
        Notify that a daily report status has changed
        :param botengine: BotEngine environment
        :param content: Daily Report json object
        
        content = {
            "report": report,
            "status": status,
            "metadata": metadata,
            "delay_ms": delay_ms,
        }

        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">daily_report_status_updated()")
        active = self._is_active(botengine)
        if not active:
            # GPT is not active
            return
        report = content.get("report", None)
        status = content.get("status", None)
        metadata = content.get("metadata", None)

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|daily_report_status_updated() status={} report={} metadata={}".format(status, json.dumps(report), json.dumps(metadata)))

        if report is None or status is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<daily_report_status_updated() Missing report or status")
            return

        if status == dailyreport.REPORT_STATUS_CREATED:
            # A new report was created
            # We don't need to do anything here, because we'll get the daily_report_entry messages next
            return
        if status == dailyreport.REPORT_STATUS_COMPLETED:
            # The report is complete
            period = report.get("period", DAILY_REPORT_ADDRESS)
            if period == DAILY_REPORT_ADDRESS:
                # We do not provide GPT reports for daily reports, only weekly and monthly
                return
            self.report_content[period] = {"report": report, "metadata": metadata}
            self.messages[report["period"]] = {}

            # Start a thread for each report type
            for report_type in self._get_report_types(botengine):
                if not self._should_publish_gpt_report(botengine, report, report_type.get("id")):
                    # We don't have any data to provide
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<daily_report_status_updated() Insufficient data")
                    return
                report_type_id = report_type["id"]
                delay_ms = content.get("delay_ms", DEFAULT_REPORT_DELAY_TIME_MS)
                self.start_timer_ms(botengine, delay_ms, argument={"period": period, "report_type_id": report_type_id}, reference=PUBLISH_REPORT_TIMER.replace('<period>', period).replace('<report_type_id>', str(report_type_id)))
            pass
        pass

    def update_daily_report_gpt_report_types(self, botengine, content):
        """
        Update the daily report GPT report types
        :param botengine: BotEngine environment
        :param content: Content of the message
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">update_daily_report_gpt_report_types() content={}".format(json.dumps(content)))
        
        report_types = content.get("report_types", DEFAULT_REPORT_TYPES)
        system_rules = content.get("system_rules", DEFAULT_SYSTEM_RULES)
        self.parent.set_location_property_separately(botengine, DAILYREPORT_GPT_STATE_VARIABLE_NAME, {"report_types": report_types, "system_rules": system_rules})
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<update_daily_report_gpt_report_types()")
        pass

    ####################################################################
    # Private methods
    ####################################################################

    def _publish_gpt_report(self, botengine, period, report_type_id, report, metadata):
        """
        Generate and publish a GPT report for this report.
        :param botengine: BotEngine environment
        :param report: Report object
        :param metadata: Report metadata
        """
        # Start a thread for each report type
        report_type = None
        for rt in self._get_report_types(botengine):
            if rt["id"] == report_type_id:
                report_type = rt
                break
        if report_type is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<_publish_gpt_report() Missing report type")
            return
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_publish_gpt_report() Submitting report to OpenAI for period={} report_type_id={}".format(period, report_type_id))
        
        # Submit chat completion requests to OpenAI
        # Each section item represents a unique request
        # An additional request is provided for each section with a summary of the items within it
        simplified_report = self._simplified_report_data(botengine, report, report_type.get("id"))
        
        # Store information about each request
        self.messages[period][report_type_id] = {"item_ids": [], "messages": [], "responses": []}
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_publish_gpt_report() simplified_report={}".format(json.dumps(simplified_report)))
        for section in simplified_report["sections"]:
            for item in section.get("items", []):
                if not item.get("id"):
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|_publish_gpt_report() Missing item ID: {}".format(json.dumps(item)))
                    continue
                if not item.get("comment"):
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|_publish_gpt_report() Missing item comment: {}".format(json.dumps(item)))
                    continue
                item_id = item["id"]
                trend_id = None
                for _trend_id in report_type.get("supported_trend_ids", []):
                    if _trend_id in item_id:
                        trend_id = item_id
                        break
                insight_id = None
                for _insight_id in report_type.get("supported_insight_ids", []):
                    if _insight_id in item_id:
                        insight_id = item_id
                        break
                if trend_id is None and insight_id is None:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|_publish_gpt_report() Missing trend or insight ID: {}".format(json.dumps(item)))
                    continue
                comment = item["comment"]

                # Generate messages for this completion
                # Include system rules and specific rules for this report type
                # Include an example data set and response from the assistant
                # System rules are consistent for each item
                system_rules = self._get_system_rules(botengine) + report_type.get("rules", [])
                
                # Add the example data and message
                if trend_id:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_publish_gpt_report() trend_id={}".format(trend_id))
                    example_data = {"Current Comment": "1 fall today", "Average": 0.2, "Standard Deviation": 1.4, "Standard Score": 0.67, "Title": "Potential Falls", "Description": "Total falls detected.", "Window": 30}
                else:
                    # TODO: Add insight example data
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_publish_gpt_report() insight_id={}".format(insight_id))
                    example_data = {"Current Comment": "No falls this week"}

                messages = [
                    {"role": "system", "content": "{}".format("\n".join(system_rules))},
                    {"role": "user", "content": "\n".join(["{}: {}".format(k, v) for k, v in list(example_data.items())])},
                    {"role": "assistant", "content": report_type["assistant_example"]}
                ]

                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_publish_gpt_report() initial messages = {}".format(messages))
                
                # Add the meta data if available
                completion_metadata = {"Comment": comment}
                
                if trend_id:
                    # If the daily report tracked metadata for this trend then include it
                    if metadata.get(trend_id):
                        item_metadata = list(metadata[trend_id].items())[-1][1]
                        if item_metadata.get("avg") is not None:
                            completion_metadata["Average"] = item_metadata["avg"]
                        if item_metadata.get("std") is not None:
                            completion_metadata["Standard Deviation"] = item_metadata["std"]
                        if item_metadata.get("zscore") is not None:
                            completion_metadata["Standard Score"] = item_metadata["zscore"]
                    else:
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|_publish_gpt_report() Missing metadata for trend_id={}".format(trend_id))

                    # Add trend metadata if provided
                    trend_metadata = self._get_trend_metadata_for_trend_id(botengine, trend_id)
                    if trend_metadata:
                        completion_metadata["Title"] = trend_metadata["title"]
                        completion_metadata["Description"] = trend_metadata["comment"]
                        completion_metadata["Window"] = trend_metadata["window"]
                    else:
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|_publish_gpt_report() Missing trend_metadata for trend_id={}".format(trend_id))
                
                else:
                    # TODO: Add insight metadata
                    # botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_publish_gpt_report() insight_id={}".format(insight_id))
                    pass
                # Add the final request to the messages
                messages.append({"role": "user", "content": "\n".join(["{}: {}".format(k, v) for k, v in list(completion_metadata.items())])})
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_publish_gpt_report() final message = {}".format(messages[-1]))

                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_publish_gpt_report() all messages = {}".format(messages))

                self.messages[period][report_type_id]["item_ids"].append(item_id)
                self.messages[period][report_type_id]["messages"].append(messages)

        # Generate an Info narrative
        self.parent.narrate(botengine,
                            title=_("Preparing Wellness Report"),
                            description=_("A new report is being processed. Stay tuned!"),
                            priority=botengine.NARRATIVE_PRIORITY_INFO,
                            extra_json_dict={"report_type": report_type, "period": period},
                            icon="file-alt",
                            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                            event_type="dailyreport_gpt.{}".format(period))

        # Submit the report to OpenAI 5 minutes later
        self.start_timer_ms(botengine, utilities.ONE_MINUTE_MS * 5, argument={"period": period, "report_type_id": report_type_id}, reference=PUBLISH_REPORT_TIMER.replace('<period>', period).replace('<report_type_id>', str(report_type_id)))

    def _should_publish_gpt_report(self, botengine, report, report_type_id):
        """
        Determine if we should publish a GPT report for this report.
        :param botengine: BotEngine environment
        :param report: Report object
        :param report_type_id: Report type ID
        :return: True if we should publish a GPT report for this report.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_should_publish_gpt_report() report_type_id={}".format(report_type_id))
        # Only provide a report if there is a valid item in a valid section
        supported_section_ids = self._get_section_ids_to_include(botengine, report_type_id)
        supported_trend_ids = self._get_trend_ids_to_include(botengine, report_type_id)
        supported_insight_ids = self._get_insight_ids_to_include(botengine, report_type_id)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_should_publish_gpt_report() supported_section_ids={} supported_trend_ids={} supported_insight_ids={}".format(supported_section_ids, supported_trend_ids, supported_insight_ids))
        for section in report["sections"]:
            if section.get("id", "") in supported_section_ids:
                for item in section.get("items", []):
                    if any(trend_id in item.get("id", "") for trend_id in supported_trend_ids) \
                        or any(insight_id in item.get("id", "") for insight_id in supported_insight_ids):
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_should_publish_gpt_report() True")
                        return True
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_should_publish_gpt_report() False")
        return False
    
    def _simplified_report_data(self, botengine, report, report_type_id):
        """
        Simplify the report data to reduce the number of tokens provided in the prompt.
        :param botengine: BotEngine environment
        :param report: Report object
        :param role_type: Role type
        :return: Simplified report data
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_simplified_report_data() report_type_id={}".format(report_type_id))
        # Copy the original report and remove unnecessary fields
        _report = json.loads(json.dumps(report))
        simplified_report = {
            "sections": []
        }

        # Only include the sections and items we care about
        supported_section_ids = self._get_section_ids_to_include(botengine, report_type_id)
        supported_trend_ids = self._get_trend_ids_to_include(botengine, report_type_id)
        supported_insight_ids = self._get_insight_ids_to_include(botengine, report_type_id)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_simplified_report_data() supported_section_ids={} supported_trend_ids={} supported_insight_ids={}".format(supported_section_ids, supported_trend_ids, supported_insight_ids))
        for report_key, report_value in _report.items():
            if report_key in ["title", "created_ms", "period"]:
                continue
            elif report_key != "sections":
                simplified_report[report_key] = report_value
                continue
            for section in report_value:
                if section.get("id", "") in supported_section_ids:
                    _section = {"items": []}
                    for section_key, section_value in section.items():
                        if section_key in ["title", "weight", "icon", "color"]:
                            continue
                        elif section_key != "items":
                            _section[section_key] = section_value
                            continue
                        for item in section_value:
                            if any(trend_id in item.get("id", "") for trend_id in supported_trend_ids) \
                                or any(insight_id in item.get("id", "") for insight_id in supported_insight_ids):
                                _item = {}
                                for item_key, item_value in item.items():
                                    if item_key in ["timestamp_ms", "comment_raw", "timestamp_str"]:
                                        continue
                                    _item[item_key] = item_value
                                _section["items"].append(_item)
                    
                    if len(_section["items"]) > 0:
                        simplified_report["sections"].append(_section)

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_simplified_report_data() simplified_report={}".format(json.dumps(simplified_report)))
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_simplified_report_data()")
        return simplified_report
    
    def _gpt_callback_response(self, botengine, completion, metadata, message_idx):
        """
        Callback response from GPT
        :param botengine: BotEngine environment
        :param completion: Completion object
        :param metadata: Metadata object
        :param message_idx: Message index
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_gpt_callback_response() response={} metadata={}".format(completion, json.dumps(metadata)))
        choices = completion.get("choices", None)
        if choices is None or len(choices) == 0:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<_gpt_callback_response() Completion object is missing choices")
            return
        
        finish_reason = choices[0]['finish_reason']

        if finish_reason == genai.FINISH_REASON_CONTENT_FILTER:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<_gpt_callback_response() Completion was rejected by the content filter: {}".format(completion))
            return
        
        if finish_reason == genai.FINISH_REASON_LENGTH:
            # TODO: How do we handle this?
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|_gpt_callback_response() Completion exceeded the maximum token length: {}".format(completion))
            pass
        
        if finish_reason == genai.FINISH_REASON_FUNCTION:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<_gpt_callback_response() Completion return a function call (not supported here): {}".format(completion))
            return
        
        if finish_reason != genai.FINISH_REASON_STOP:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<_gpt_callback_response() Unrecognized `finish_reason`: {}".format(completion))
            return
        
        # Get the response
        response = choices[0]['message']['content']

        # Get metadata keys
        if metadata.get("period") is None or metadata.get("report_type_id") is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<_gpt_callback_response() Missing period or report_type_id in metadata: {}".format(metadata))
            return
        period = metadata.get("period")
        report_type_id = metadata.get("report_type_id")
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_gpt_callback_response() period={} report_type_id={}".format(period, report_type_id))
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_gpt_callback_response() report={}".format(json.dumps(self.messages[period][report_type_id])))
        # Get the item ID
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_gpt_callback_response() item_ids={}".format(self.messages[period][report_type_id]["item_ids"]))
        item_id = self.messages[period][report_type_id]["item_ids"][message_idx]
        
        messages = self.messages[period][report_type_id]["messages"]
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_gpt_callback_response() messages={}".format(messages))

        # Update the report content
        responses = self.messages[period][report_type_id].get("responses", [])
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_gpt_callback_response() responses={}".format(responses))
        self.report_content[period]["responses"] = {report_type_id: responses}
        
        # Append the messages for reference later
        self.messages[period][report_type_id]["responses"].append(response)

        # Track responses
        report_type = self._get_report_types(botengine)[report_type_id]

        # Track Analytics
        analytics.track(botengine, self.parent, "dailyreport_gpt_generated", {"period": period, "report_type_id": report_type_id, "item_id": item_id, "usage": completion.get("usage", {})})

        role = report_type.get("role_type", ROLE_TYPE_PRIMARY_FAMILY_CAREGIVER)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_gpt_callback_response() role={}".format(role))

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_gpt_callback_response() len(messages)={} len(responses={}".format(len(messages), len(responses)))
        message_index = len(responses) - 1
        if len(messages) <= message_idx:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|_gpt_callback_response() Missing message index: {}".format(message_idx))
            message_index = -1

        # Publish as analytic narrative
        self.parent.narrate(botengine,
                            title=_("Daily Report Wellness Report"),
                            description=response,
                            priority=botengine.NARRATIVE_PRIORITY_ANALYTIC,
                            extra_json_dict={"report_type": report_type, "period": period, "trend_id": item_id, "messages": messages[message_index]},
                            icon="file-alt",
                            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                            event_type="dailyreport_gpt.{}".format(period))
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_gpt_callback_response()")

    def _complete_report(self, botengine, period, report_type_id):
        """
        Completes the report by generating narratives, updating the daily report, and notifying admins.
        :param botengine: BotEngine environment
        :param period: Period of the report
        :param report_type_id: Report type ID
        """

        # Notify and send the report
        report_type = self._get_report_types(botengine)[report_type_id]

        # Track Analytics
        analytics.track(botengine, self.parent, "dailyreport_gpt_completed", {"period": period, "report_type_id": report_type_id, "messages": len(self.messages[period][report_type_id]["messages"])})

        role = report_type.get("role_type", ROLE_TYPE_PRIMARY_FAMILY_CAREGIVER)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() role={}".format(role))
        # Publish as analytic narrative
        self.parent.narrate(botengine,
                            title=_("Daily Report Wellness Report"),
                            description=_("Report completed."),
                            priority=botengine.NARRATIVE_PRIORITY_ANALYTIC,
                            extra_json_dict={"report_type": report_type, "period": period, "messages": len(self.messages[period][report_type_id]["messages"])},
                            icon="file-alt",
                            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                            event_type="dailyreport_gpt_completed.{}".format(period))

        primary_caregiver_enabled = PRIMARY_CAREGIVER_GPT_REPORT_ENABLED
        if properties.get_property(botengine, "GPT_PRIMARY_CAREGIVER_REPORT_ENABLED", False) is not None:
            primary_caregiver_enabled = properties.get_property(botengine, "GPT_PRIMARY_CAREGIVER_REPORT_ENABLED", False)

        if role == ROLE_TYPE_PRIMARY_FAMILY_CAREGIVER and primary_caregiver_enabled:
            # Publish as info narrative
            self.parent.narrate(botengine,
                            title=_("Daily Report Wellness Report"),
                            description="\n".join(self.messages[period][report_type_id]["responses"]),
                            priority=botengine.NARRATIVE_PRIORITY_INFO,
                            extra_json_dict={"report_type": report_type, "period": period, "messages": len(self.messages[period][report_type_id]["messages"])},
                            icon="file-alt",
                            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                            event_type="dailyreport_gpt.{}".format(period))
            
            for idx in range(len(self.messages[period][report_type_id]["responses"])):
                
                response = self.messages[period][report_type_id]["responses"][idx]
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() response={}".format(response))
                if len(self.messages[period][report_type_id]["item_ids"]) <= idx:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|_complete_report() Missing item ID for message index: idx={} len(messages)={} len(responses)={} len(items)={}".format(idx, len(self.messages[period][report_type_id]["messages"]), len(self.messages[period][report_type_id]["responses"]), len(self.messages[period][report_type_id]["item_ids"])))
                    break
                item_id = self.messages[period][report_type_id]["item_ids"][idx]

                subtitle = None
                for trend_id in report_type.get("supported_trend_ids", []):
                    if trend_id in item_id:
                        trend_metadata = self._get_trend_metadata_for_trend_id(botengine, trend_id)
                        if trend_metadata:
                            subtitle = trend_metadata.get("title")
                        break
                # Publish as a daily report entry
                dailyreport.add_entry(
                    botengine,
                    self.parent,
                    section_id=dailyreport.SECTION_ID_WELLNESS,
                    comment=response,
                    subtitle=subtitle,
                    identifier="gpt_report_{}".format(period),
                )
        elif role == ROLE_TYPE_PROFESSIONAL_CAREGIVER:
            self.parent.narrate(botengine,
                            title=_("Daily Report Wellness Report"),
                            description=self.messages[period][report_type_id]["responses"][0],
                            priority=botengine.NARRATIVE_PRIORITY_INFO,
                            narrative_type=botengine.NARRATIVE_TYPE_JOURNAL,
                            extra_json_dict={"report_type": report_type, "period": period, "messages": len(self.messages[period][report_type_id]["messages"])},
                            icon="file-alt",
                            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                            event_type="dailyreport_gpt.{}".format(period))
            
            for idx in range(len(self.messages[period][report_type_id]["responses"])):
                
                response = self.messages[period][report_type_id]["responses"][idx]
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() response={}".format(response))
                if len(self.messages[period][report_type_id]["item_ids"]) <= idx:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|_complete_report() Missing item ID for message index: idx={} len(messages)={} len(responses)={} len(items)={}".format(idx, len(self.messages[period][report_type_id]["messages"]), len(self.messages[period][report_type_id]["responses"]), len(self.messages[period][report_type_id]["item_ids"])))
                    break
                item_id = self.messages[period][report_type_id]["item_ids"][idx]

                subtitle = None
                for trend_id in report_type.get("supported_trend_ids", []):
                    if trend_id in item_id:
                        trend_metadata = self._get_trend_metadata_for_trend_id(botengine, trend_id)
                        if trend_metadata:
                            subtitle = trend_metadata.get("title")
                        break
                # Publish as a daily report entry
                if period == WEEKLY_REPORT_ADDRESS:
                    dailyreport.add_weekly_entry(
                        botengine,
                        self.parent,
                        section_id=dailyreport.SECTION_ID_WELLNESS,
                        comment=response,
                        subtitle=subtitle,
                        identifier="gpt_report_{}".format(period),
                    )
                elif period == MONTHLY_REPORT_ADDRESS:
                    dailyreport.add_monthly_entry(
                        botengine,
                        self.parent,
                        section_id=dailyreport.SECTION_ID_WELLNESS,
                        comment=response,
                        subtitle=subtitle,
                        identifier="gpt_report_{}".format(period),
                    )
            
            # Notify user's by role
            location_users = botengine.get_location_users()
            user_ids = []
            for user in location_users:
                if user.get("role") == report_type.get("role_type"):
                    user_ids.append(user.get("id"))
            content_header = "The information below is a summary of the wellness report for this home."
            content_footer = "Location ID: {}".format(self.parent.location_id)
            content_array = []
            # Organize the content by {section:[items], using the dailyreport microservice as a reference
            sections = {}
            for idx in range(len(self.messages[period][report_type_id]["responses"])):
                response = self.messages[period][report_type_id]["responses"][idx]
                if len(self.messages[period][report_type_id]["item_ids"]) <= idx:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|_complete_report() Missing item ID for message index: idx={} len(messages)={} len(responses)={} len(items)={}".format(idx, len(self.messages[period][report_type_id]["messages"]), len(self.messages[period][report_type_id]["responses"]), len(self.messages[period][report_type_id]["item_ids"])))
                    break
                item_id = self.messages[period][report_type_id]["item_ids"][idx]

                section_id = self._get_section_id_for_item_id(botengine, item_id)
                if section_id is None:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|_complete_report() Missing section for item_id: {}".format(item_id))
                    continue
                
                
                if section_id not in sections:
                    section = json.loads(json.dumps(DEFAULT_SECTION_PROPERTIES[section_id]))
                    sections[section_id] = section
                else:
                    section = sections[section_id]
                
                if "responses" not in section:
                    section["responses"] = []

                section_response = {"response": response}
                context = None
            
                # Add trend metadata if available
                for trend_id in report_type.get("supported_trend_ids", []):
                    if trend_id in item_id:
                        trend_metadata = self._get_trend_metadata_for_trend_id(botengine, trend_id)
                        if trend_metadata:
                            context = trend_metadata["title"] + "\n: " + trend_metadata["comment"]
                        break 
                # Add insight metadata if available
                for insight_id in report_type.get("supported_insight_ids", []):
                    if insight_id in item_id:
                        pass

                if context is not None:
                    section_response["context"] = context

                # TODO: Add media (charts, etc.)
                section_response["media"] = None
                section["responses"].append(section_response)
            
            for section_id, section in sorted(sections.items(), key=lambda x: x[1][dailyreport.SECTION_KEY_WEIGHT]):
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() section_id={} section={}".format(section_id, section))
                content = {
                    "title": section[dailyreport.SECTION_KEY_TITLE],
                    "desc": section[dailyreport.SECTION_KEY_DESCRIPTION],
                    "icon": section[dailyreport.SECTION_KEY_ICON],
                    "content": [],
                }
                for response in section["responses"]:
                    if response.get("context") is not None:
                        content["content"].append(response["context"] + "\n\n" + response["response"])
                    else:
                        content["content"].append(response["response"])

                content_array.append(content)

            if len(user_ids) > 0:
                content_footer += "\n" + _("User IDs who received this Wellness Report: {}").format(", ".join([str(user_id) for user_id in user_ids]))
                botengine.notify(
                    email_subject="{} Wellness Report".format(self.parent.get_location_name(botengine)),
                    email_html=True,
                    email_template_filename="bots/daily_report.vm",
                    email_template_model={
                        "title": _("{} Wellness Report").format(_("Weekly") if period == WEEKLY_REPORT_ADDRESS else _("Monthly")),
                        "subtitle": utilities.strftime(self.parent.get_local_datetime(botengine), "%A, %B %-d, %Y at %-I:%M %p %Z"),
                        "icon": "file-alt",
                        "contentHeader": content_header,
                        "contentArray": content_array,
                        "contentFooter": content_footer
                    },
                    brand=properties.get_property(botengine, "ORGANIZATION_BRAND"),
                    user_id_list=user_ids
                )

            # Email administrators
            url = utilities.get_admin_url_for_location(botengine)
            if url:
                content_header += "\n\n<a href=\"{}\">".format(url) + _("VIEW THIS HOME") + "</a>"
            botengine.email_admins(
                email_subject="{} Wellness Report".format(self.parent.get_location_name(botengine)),
                email_html=True,
                email_template_filename="bots/daily_report.vm",
                email_template_model={
                    "title": _("{} Wellness Report").format(_("Weekly") if period == WEEKLY_REPORT_ADDRESS else _("Monthly")),
                    "subtitle": utilities.strftime(self.parent.get_local_datetime(botengine), "%A, %B %-d, %Y at %-I:%M %p %Z"),
                    "icon": "file-alt",
                    "contentHeader": content_header,
                    "contentArray": content_array,
                    "contentFooter": content_footer
                },
                brand=properties.get_property(botengine, "ORGANIZATION_BRAND"),
                categories=utilities.get_organization_user_notification_categories(botengine, self.parent))
        pass

    def _ask_questions(self, botengine):
        """
        Refresh questions
        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">ask_question()")
        self.version = VERSION

        dailyreport_state =  botengine.get_state(DAILYREPORT_STATE_VARIABLE_NAME)
        if dailyreport_state is None:
            dailyreport_state = {}

        dailyreport_gpt_state =  botengine.get_state(DAILYREPORT_GPT_STATE_VARIABLE_NAME)
        if dailyreport_gpt_state is None:
            dailyreport_gpt_state = {}

        # GPT ACTIVATION
        gpt_is_enabled = dailyreport_state.get(SERVICE_KEY_GPT_ACTIVE, None)
        if gpt_is_enabled is None:
            import properties
            if properties.get_property(botengine, DOMAIN_KEY_GPT_ENABLED, False) is not None:
                gpt_is_enabled = properties.get_property(botengine, DOMAIN_KEY_GPT_ENABLED, False)
            else:
                gpt_is_enabled = DEFAULT_GPT_ENABLED

        # Create a new question if needed
        gpt_is_enabled_question_object = botengine.retrieve_question(SERVICE_KEY_GPT_ACTIVE)

        if gpt_is_enabled_question_object is None:
            gpt_is_enabled_question_object = botengine.generate_question(SERVICE_KEY_GPT_ACTIVE,
                                                                            botengine.QUESTION_RESPONSE_TYPE_BOOLEAN,
                                                                            collection=SERVICES_COLLECTION_NAME,
                                                                            icon="brain",
                                                                            display_type=botengine.QUESTION_DISPLAY_BOOLEAN_ONOFF,
                                                                            default_answer=gpt_is_enabled,
                                                                            editable=True,
                                                                            section_id=SERVICE_SECTION_ID,
                                                                            question_weight=SERVICE_WEIGHT_GPT_ACTIVE)
        
        # Reference the dailyreport service question which is required to enable this supplementary service
        import properties
        supported = properties.get_property(botengine, DOMAIN_KEY_GPT_SUPPORTED, False) or False
        gpt_is_enabled_question_object.editable = dailyreport_state.get(SERVICE_KEY_ACTIVE, False) and supported
        gpt_is_enabled_question_object.answer = self.parent.get_location_property(botengine, SERVICE_KEY_GPT_ACTIVE)
        gpt_is_enabled_question_object.default_answer = gpt_is_enabled
        gpt_is_enabled_question_object.icon = "brain"
        botengine.ask_question(gpt_is_enabled_question_object)
        
        framed_question = _("Weekly and Monthly Wellness Reports")
        if 'en' not in gpt_is_enabled_question_object.question:
            gpt_is_enabled_question_object.frame_question(framed_question, 'en')
            botengine.ask_question(gpt_is_enabled_question_object)

        if gpt_is_enabled_question_object.question['en'] != framed_question:
            gpt_is_enabled_question_object.frame_question(framed_question, "en")
            botengine.ask_question(gpt_is_enabled_question_object)

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<ask_question() gpt services enabled: {}".format(gpt_is_enabled))

        # Clear old service
        dashboard.delete_service(botengine, self.parent, unique_identifier=SERVICE_KEY_GPT_ACTIVE)

    def _is_active(self, botengine):
        """
        Checks if Trend Monitoring is active
        :param botengine:
        :return: True if this microservice is actively monitoring trends
        """
        # Check that the service is supported at the domain level
        if not properties.get_property(botengine, DOMAIN_KEY_GPT_SUPPORTED, False) or False:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_is_active() GPT is not supported at the domain level")
            return False
        if botengine.playback:
            return True
        # Reference the dailyreport service question which is required to enable this supplementary service
        is_enabled_question_object = botengine.retrieve_question(SERVICE_KEY_ACTIVE)
        if is_enabled_question_object is not None and not utilities.get_answer(is_enabled_question_object):
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_is_active() Daily Report service is not enabled")
            return False
        active = DEFAULT_GPT_ENABLED
        question = botengine.retrieve_question(SERVICE_KEY_GPT_ACTIVE)
        if question is not None:
            if question.answer is not None:
                active = utilities.normalize_measurement(question.answer)
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_is_active() question.answer is not None: {}; Result={}".format(question.answer, active))

            else:
                active = utilities.normalize_measurement(question.default_answer)
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_is_active() question.answer is None: default_answer={}; Result={}".format(question.default_answer, active))
    
        return active
    
    def _initialize_state_variable(self, botengine):
        """
        Initialize the state variables
        :param botengine: BotEngine environment
        """
        # Update `dailyreport` state variable
        import properties
        dailyreport_state = {"has_gpt": properties.get_property(botengine, DOMAIN_KEY_GPT_SUPPORTED, False) or False}
        if botengine.get_state(self, DAILYREPORT_STATE_VARIABLE_NAME) is not None and SERVICE_KEY_GPT_ACTIVE not in botengine.get_state(self, DAILYREPORT_STATE_VARIABLE_NAME).keys():
            dailyreport_state[SERVICE_KEY_GPT_ACTIVE] = DEFAULT_GPT_ENABLED
        self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, dailyreport_state)

        # Initialize `dailyreport_gpt` state variable
        dailyreport_gpt_state = botengine.get_state(self, DAILYREPORT_GPT_STATE_VARIABLE_NAME) or {}
        
        if dailyreport_gpt_state.get("report_types") is None:
            dailyreport_gpt_state["report_types"] = DEFAULT_REPORT_TYPES
        if dailyreport_gpt_state.get("system_rules") is None:
            dailyreport_gpt_state["system_rules"] = DEFAULT_SYSTEM_RULES        

        self.parent.set_location_property_separately(botengine, DAILYREPORT_GPT_STATE_VARIABLE_NAME, dailyreport_gpt_state)

    def _get_trend_metadata_for_trend_id(self, botengine, trend_id) -> dict:
        """
        Get the metadata for this trend ID
        :param botengine: BotEngine environment
        :param trend_id: Trend ID
        :param metadata: Metadata
        :return: Metadata for this trend ID
        """
        trends_metadata = botengine.get_state(TRENDS_METADATA_NAME)
        if trends_metadata is None:
            return None
        
        return trends_metadata.get(trend_id)

    def _get_trend_category_for_primary_trend_id(self, botengine, primary_trend_id) -> dict:
        """
        Get the metadata for this trend ID
        :param botengine: BotEngine environment
        :param trend_id: Trend ID
        :param metadata: Metadata
        :return: Metadata for this trend ID
        """
        trend_metadata = self._get_trend_metadata_for_trend_id(botengine, primary_trend_id)
        if trend_metadata is None:
            return None
        trends_category = botengine.get_state("trends_category")
        if trends_category is None:
            return None
        if trend_metadata.get("category") and trends_category.get(trend_metadata.get("category")):
            if trends_category[trend_metadata["category"]]["primary_trend"] in primary_trend_id:
                return trends_category[trend_metadata["category"]]
        return None
    
    def _created_openai_key(self, botengine, period, report_type_id, message_idx) -> str:
        """
        Create a unique key for this report
        :param botengine: BotEngine environment
        :param period: Period of the report
        :param report_type_id: Report type ID
        :param message_idx: Message index
        :return: Unique key for this report
        """
        return "{}.{}.{}.{}".format(OPENAI_RESPONSE_KEY_PREFIX, period, report_type_id, message_idx)
    
    def _get_openai_key(self, botengine, content):
        """
        Return the report key identifiers from the openai response.
        :param botengine: BotEngine environment
        :param content: Content of the message
        :return: Report key identifiers (period, report_type_id, message_idx)
        """
        if not content.get("key") or not OPENAI_RESPONSE_KEY_PREFIX in content["key"]:
            return None
        key = content["key"]
        if len(key.split(".")) < 3:
            return None
        period = key.split(".")[1]
        report_type_id = key.split(".")[2]
        message_idx = key.split(".")[3]
        return (period, report_type_id, int(message_idx))
    
    def _get_report_types(self, botengine):
        """
        Get the report types
        :param botengine: BotEngine environment
        :return: Report types
        """
        return (self.parent.get_location_property(botengine, DAILYREPORT_GPT_STATE_VARIABLE_NAME) or {}).get("report_types", DEFAULT_REPORT_TYPES)
    
    def _get_system_rules(self, botengine):
        """
        Get the system rules
        :param botengine: BotEngine environment
        :return: System rules
        """
        return (self.parent.get_location_property(botengine, DAILYREPORT_GPT_STATE_VARIABLE_NAME) or {}).get("system_rules", DEFAULT_SYSTEM_RULES)

    def _get_section_ids_to_include(self, botengine, report_type_id):
        """
        Get the section IDs to include
        :param botengine: BotEngine environment
        :param report_type_id: Report type ID
        :return: Section IDs to include
        """
        for report_type in self._get_report_types(botengine):
            if report_type["id"] == report_type_id:
                return report_type.get("supported_section_ids", [])
        return []
    
    def _get_trend_ids_to_include(self, botengine, report_type_id):
        """
        Get the trend IDs to include
        :param botengine: BotEngine environment
        :param report_type_id: Report type ID
        :return: Trend IDs to include
        """
        for report_type in self._get_report_types(botengine):
            if report_type["id"] == report_type_id:
                return report_type.get("supported_trend_ids", [])
        return []
    
    def _get_insight_ids_to_include(self, botengine, report_type_id):
        """
        Get the insight IDs to include
        :param botengine: BotEngine environment
        :param report_type_id: Report type ID
        :return: Insight IDs to include
        """
        for report_type in self._get_report_types(botengine):
            if report_type["id"] == report_type_id:
                return report_type.get("supported_insight_ids", [])
        return []
    
    def _get_section_id_for_item_id(self, botengine, item_id):
        """
        Get the section ID for this item ID
        :param botengine: BotEngine environment
        :param item_id: Item ID
        :return: Section ID for this item ID
        """
        for section_id in list(DEFAULT_SECTION_PROPERTIES.keys()):
            for trend_id in DEFAULT_SECTION_PROPERTIES[section_id].get("trend_ids", []):
                if trend_id in item_id:
                    return section_id
            for insight_id in DEFAULT_SECTION_PROPERTIES[section_id].get("insight_ids", []):
                if insight_id in item_id:
                    return section_id
        return None
    
    #===========================================================================
    # DATA STREAMS
    #===========================================================================

    def openai(self, botengine, content):
        """
        Bots can interact asynchronously with Open AI ChatGPT using this API. The response from CharGPT is delivered to the bot in a data stream message to the 'openai' address.

        Data stream message content example:
        ```
        {
            "key": "MyRequest",
            "id" : "chatcmpl-86GKbsl3bP5YmmxutIY8aS5c5o5gK",
            "object" : "chat.completion",
            "created" : 1696503437,
            "model" : "gpt-3.5-turbo-0613",
            "choices" : [ {
                "index" : 0,
                "message" : {
                    "role" : "assistant",
                    "content" : "This is a test!"
                },
                "finish_reason" : "stop"
            } ],
            "usage" : {
                "prompt_tokens" : 13,
                "completion_tokens" : 5,
                "total_tokens" : 18
            }
        }
        ```

        :param botengine: BotEngine environment
        :param content: Content of the message
        """
        if not self._get_openai_key(botengine, content):
            return
        period, report_type_id, message_idx = self._get_openai_key(botengine, content)
        metadata = self.report_content[period]["metadata"]
        metadata["period"] = period
        metadata["report_type_id"] = int(report_type_id)
        self._gpt_callback_response(botengine, content, metadata, message_idx)
        return
        