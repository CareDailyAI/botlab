'''
Created on Febuary 20, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
'''

from intelligence.intelligence import Intelligence

import properties
import json
import utilities.utilities as utilities
import utilities.genai as genai

import signals.analytics as analytics
import signals.dailyreport as dailyreport
import signals.dashboard as dashboard

from users.user import User

from intelligence.dailyreport.location_dailyreport_microservice import *

# Daily Report Summary State Variable
DAILYREPORT_SUMMARY_STATE_VARIABLE_NAME = "dailyreport_summary"

# Organization Domain Service Key Active
DOMAIN_KEY_SUMMARY_ENABLED = "DAILYREPORT_SUMMARY_ENABLED"

# Summary not enabled by default
DEFAULT_SUMMARY_ENABLED = False

# Enable or disable summary services
SERVICE_SECTION_ID_SUMMARY         = 0
SERVICE_KEY_SUMMARY_ACTIVE         = "summary.is_enabled"
SERVICE_WEIGHT_SUMMARY_ACTIVE      = 200

#===============================================================================

class LocationDailyReportSummaryMicroservice(Intelligence):
    """
    Interpret daily reports and produce SMS and Email summary reports for location users.

    Additional states are managed in the `dailyreport` state variable.
    {   
    
        "has_summary": Bool, # Summary microservice included in bundle
        "summary.is_enabled": Bool, # Summary service enabled
    }

    Front end information is managed through the `dailyreport_summary` state variable.
    {
        TBD
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

        # Items to notify
        self.items_to_notify = None

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

        self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, {'has_summary': False})

        question_object = botengine.retrieve_question(SERVICE_KEY_SUMMARY_ACTIVE)
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
        When a device disconnects, it will send an alert like this:  [{u'alertType': u'status', u'params': [{u'name': u'deviceStatus', u'value': u'2'}], u'deviceId': u'eb10e80a006f0d00'}]
        When a device reconnects, it will send an alert like this:  [{u'alertType': u'on', u'deviceId': u'eb10e80a006f0d00'}]
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
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

        # SUMMARY ENABLED
        if question_object.key_identifier == SERVICE_KEY_SUMMARY_ACTIVE:
            
            # Services are turned on
            if utilities.get_answer(question_object):
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|question_answered() Summary enabled")
                analytics.track(botengine, self.parent, "service_dailyreport_summary_activated")
                self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, {SERVICE_KEY_SUMMARY_ACTIVE: True})
                # NOTE: Summary service turned on.
                self.parent.narrate(botengine,
                                    title=_("Daily Report Summary services activated."),
                                    description=_("Summary services have been turned on{}.").format(message),
                                    priority=botengine.NARRATIVE_PRIORITY_INFO,
                                    icon="file-alt",
                                    icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                                    question_key=SERVICE_KEY_SUMMARY_ACTIVE,
                                    event_type="dailyreport_summary.activated")
            else:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|question_answered() Summary disabled")
                analytics.track(botengine, self.parent, "service_dailyreport_summary_deactivated")
                self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, {SERVICE_KEY_SUMMARY_ACTIVE: False})
                # NOTE: Summary service turned off.
                self.parent.narrate(botengine,
                                    title=_("Daily Report Summary services deactivated."),
                                    description=_("Summary services have been turned off{}.").format(message),
                                    priority=botengine.NARRATIVE_PRIORITY_INFO,
                                    icon="file-alt",
                                    icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                                    question_key=SERVICE_KEY_SUMMARY_ACTIVE,
                                    event_type="dailyreport_summary.deactivated")
                
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
        # TODO: Add timer logic
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
            # SUMMARY is not active
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
            # TODO: Add logic to notify over SMS and Email based on user role
            if period == DAILY_REPORT_ADDRESS:
                self._complete_report(botengine, report, period, metadata)
            pass
        pass

    def _complete_report(self, botengine, report, period, metadata):
        """
        Completes the report by generating narratives and deliverying notificaiton.
        :param botengine: BotEngine environment
        :param report: dict Report object
        :param period: string Period of the report
        :param metadata: dict Metadata
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_complete_report() period={}".format(period))

        # Track Analytics
        analytics.track(botengine, self.parent, "dailyreport_summary_completed", {"period": period})

        # Randomly select up to 3 events without duplication from the content within each section
        section_ids = [section["id"] for section in report.get("sections", [])]
        weighted_sections = [DEFAULT_SECTION_PROPERTIES[section_id][dailyreport.SECTION_KEY_WEIGHT] for section_id in section_ids] # [-5, 0, 10]

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() section_ids={}".format(section_ids))
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() weighted_sections={}".format(weighted_sections))

        # Notify user's with role "4" (Professional Caregiver) over SMS
        location_users = botengine.get_location_users()
        user_ids = []
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() location_users={}".format(json.dumps(location_users)))
        for user in location_users:
            if user.get("role") == User.ROLE_TYPE_PROFESSIONAL_CAREGIVER:
                user_ids.append(user.get("id"))
        
        if len(user_ids) > 0:
            # Notify professional caregivers
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() Notify professional caregivers over SMS")

            sorted_sections = [(max(weighted_sections) + 10) - weight for weight in weighted_sections] # [15, 10, 5]
            import random
            random_sections = random.choices(section_ids, weights=set(sorted_sections), k=len(section_ids))
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() sorted_sections={}".format(sorted_sections))
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() random_sections={}".format(random_sections))
            
            random_items = []
            for section_id in random_sections:
                section = None
                for _section in report.get("sections", []):
                    if _section.get("id") == section_id:
                        section = _section
                        break
                if section is None:
                    continue
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() section={}".format(section))
                items = section.get("items", [])
                if len(items) == 0:
                    continue
                random_item = random.choice(items)
                if random_item.get('id', '') not in [item.get('id', '') for item in random_items]:
                    random_items.append(random_item)

            if len(random_items) > 0:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() random_items={}".format(random_items))
                
                # Store the items to notify over SMS to be delivered at sunrise
                self.items_to_notify = random_items[:3]
                analytics.track(botengine, self.parent, "dailyreport_summary_notify_professional_caregivers", {"period": period, "items_to_notify": self.items_to_notify, "user_ids": user_ids})
            else:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|_complete_report() No items to report over SMS to professional caregivers.")
                analytics.track(botengine, self.parent, "dailyreport_summary_notify_professional_caregivers", {"delivered": False, "period": period, "items_to_notify": 0, "user_ids": user_ids})
            
        else:
            analytics.track(botengine, self.parent, "dailyreport_summary_notify_professional_caregivers", {"delivered": False, "period": period, "items_to_notify": 0, "user_ids": []})
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() No professional caregivers to notify over SMS")

        # Notify user's with role "2", "3" or "4" (Primary Family Caregiver) over Email
        user_ids = []
        for user in location_users:
            if user.get("role") in [User.ROLE_TYPE_PRIMARY_FAMILY_CAREGIVER, User.ROLE_TYPE_SECONDARY_FAMILY_CAREGIVER, User.ROLE_TYPE_PROFESSIONAL_CAREGIVER]:
                user_ids.append(user.get("id"))
        
        if len(user_ids) > 0:
            # Notify professional caregivers
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() Notify family and professional caregivers over email")

            content_header = "The information below is the daily summary for this home."
            content_footer = "Location ID: {}".format(self.parent.location_id)
            content_array = []

            for section in report.get("sections", []):
                section_id = section.get("id")
                if section_id not in DEFAULT_SECTION_PROPERTIES:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|_complete_report() Missing section properties for section_id: {}".format(section_id))
                    continue
                
                content = {
                    "title": section[dailyreport.SECTION_KEY_TITLE],
                    "icon": section[dailyreport.SECTION_KEY_ICON],
                    "content": [],
                }
                if section.get("subtitle", None) is not None:
                    content["desc"] = section["subtitle"]
                for item in section.get("items", []):
                    content["content"].append(item["comment"])
                content_array.append(content)

            if len(content_array) > 0:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() notify family and professional caregivers over email")
                botengine.notify(
                    email_subject="{} Summary Report".format(self.parent.get_location_name(botengine)),
                    email_html=True,
                    email_template_filename="bots/daily_report.vm",
                    email_template_model={
                        "title": _("Daily Summary Report"),
                        "subtitle": utilities.strftime(self.parent.get_local_datetime(botengine), "%A, %B %-d, %Y at %-I:%M %p %Z"),
                        "icon": "file-alt",
                        "contentHeader": content_header,
                        "contentArray": content_array,
                        "contentFooter": content_footer
                    },
                    brand=properties.get_property(botengine, "ORGANIZATION_BRAND"),
                    user_id_list=user_ids
                )
            else:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|_complete_report() No content to report over email to family and professional caregivers.")
                analytics.track(botengine, self.parent, "dailyreport_summary_notify_all_caregivers", {"delivered": False, "period": period, "user_ids": user_ids})
        else:
            analytics.track(botengine, self.parent, "dailyreport_summary_notify_all_caregivers", {"delivered": False, "period": period, "user_ids": []})
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_complete_report() No family or professional caregivers to notify over email")

        # Publish as analytic narrative
        self.parent.narrate(botengine,
                            title=_("Daily Report Summary"),
                            description=_("Summary completed."),
                            priority=botengine.NARRATIVE_PRIORITY_ANALYTIC,
                            extra_json_dict={"period": period},
                            icon="file-alt",
                            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                            event_type="dailyreport_summary_completed.{}".format(period))
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_complete_report()")
        pass
    
    def sunrise_fired(self, botengine, content):
        """
        Sunrise fired
        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">sunrise_fired()")
        if self.items_to_notify is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_sunrise_fired() No items to notify")
            return

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_sunrise_fired() items_to_notify={}".format(json.dumps(self.items_to_notify)))
        content = "Daily Report Summary for '{}'\n".format(self.parent.get_location_name(botengine))
        content += " | ".join([item.get("comment") for item in self.items_to_notify])
        self.items_to_notify = None

        location_users = botengine.get_location_users()
        user_ids = []
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_complete_report() location_users={}".format(json.dumps(location_users)))
        for user in location_users:
            if user.get("role") == User.ROLE_TYPE_PROFESSIONAL_CAREGIVER:
                user_ids.append(user.get("id"))
        
        if len(user_ids) > 0:
            analytics.track(botengine, self.parent, "dailyreport_summary_notify_professional_caregivers_delivered", {"delivered": True, "items_to_notify": self.items_to_notify, "user_ids": user_ids})
            botengine.notify(sms_content=content, user_id_list=user_ids)
        else:
            analytics.track(botengine, self.parent, "dailyreport_summary_notify_professional_caregivers_delivered", {"delivered": False, "items_to_notify": self.items_to_notify})
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_sunrise_fired()")

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

        dailyreport_summary_state =  botengine.get_state(DAILYREPORT_SUMMARY_STATE_VARIABLE_NAME)
        if dailyreport_summary_state is None:
            dailyreport_summary_state = {}

        # SUMMARY ACTIVATION
        summary_is_enabled = dailyreport_state.get(SERVICE_KEY_SUMMARY_ACTIVE, None)
        if summary_is_enabled is None:
            import properties
            if properties.get_property(botengine, DOMAIN_KEY_SUMMARY_ENABLED, False) is not None:
                summary_is_enabled = properties.get_property(botengine, DOMAIN_KEY_SUMMARY_ENABLED, False)
            else:
                summary_is_enabled = DEFAULT_SUMMARY_ENABLED

        # Create a new question if needed
        summary_is_enabled_question_object = botengine.retrieve_question(SERVICE_KEY_SUMMARY_ACTIVE)

        if summary_is_enabled_question_object is None:
            summary_is_enabled_question_object = botengine.generate_question(SERVICE_KEY_SUMMARY_ACTIVE,
                                                                            botengine.QUESTION_RESPONSE_TYPE_BOOLEAN,
                                                                            collection=SERVICES_COLLECTION_NAME,
                                                                            icon="sms",
                                                                            display_type=botengine.QUESTION_DISPLAY_BOOLEAN_ONOFF,
                                                                            default_answer=summary_is_enabled,
                                                                            editable=True,
                                                                            section_id=SERVICE_SECTION_ID,
                                                                            question_weight=SERVICE_WEIGHT_SUMMARY_ACTIVE)
        
        # Reference the dailyreport service question which is required to enable this supplementary service
        summary_is_enabled_question_object.editable = dailyreport_state.get(SERVICE_KEY_ACTIVE, False)
        summary_is_enabled_question_object.answer = self.parent.get_location_property(botengine, SERVICE_KEY_SUMMARY_ACTIVE)
        summary_is_enabled_question_object.default_answer = summary_is_enabled
        botengine.ask_question(summary_is_enabled_question_object)
        
        framed_question = _("Daily Report SMS Summary")
        if 'en' not in summary_is_enabled_question_object.question:
            summary_is_enabled_question_object.frame_question(framed_question, 'en')
            botengine.ask_question(summary_is_enabled_question_object)

        if summary_is_enabled_question_object.question['en'] != framed_question:
            summary_is_enabled_question_object.frame_question(framed_question, "en")
            botengine.ask_question(summary_is_enabled_question_object)

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<ask_question() summary services enabled: {}".format(summary_is_enabled))

    def _is_active(self, botengine):
        """
        Checks if Trend Monitoring is active
        :param botengine:
        :return: True if this microservice is actively monitoring trends
        """
        if botengine.playback:
            return True

        # Reference the dailyreport service question which is required to enable this supplementary service
        is_enabled_question_object = botengine.retrieve_question(SERVICE_KEY_ACTIVE)
        if is_enabled_question_object is not None and not utilities.get_answer(is_enabled_question_object):
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|_is_active() Daily Report service is not enabled")
            return False
        active = DEFAULT_SUMMARY_ENABLED
        question = botengine.retrieve_question(SERVICE_KEY_SUMMARY_ACTIVE)
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
        dailyreport_state = {"has_summary": True}
        if botengine.get_state(self, DAILYREPORT_STATE_VARIABLE_NAME) is not None and SERVICE_KEY_SUMMARY_ACTIVE not in botengine.get_state(self, DAILYREPORT_STATE_VARIABLE_NAME).keys():
            dailyreport_state[SERVICE_KEY_SUMMARY_ACTIVE] = DEFAULT_SUMMARY_ENABLED
        self.parent.set_location_property_separately(botengine, DAILYREPORT_STATE_VARIABLE_NAME, dailyreport_state)

        # Initialize `dailyreport_summary` state variable
        dailyreport_summary_state = botengine.get_state(self, DAILYREPORT_SUMMARY_STATE_VARIABLE_NAME) or {}
        
        # TODO: Add state variable initialization    

        self.parent.set_location_property_separately(botengine, DAILYREPORT_SUMMARY_STATE_VARIABLE_NAME, dailyreport_summary_state)

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