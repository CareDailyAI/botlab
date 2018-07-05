'''
Created on December 25, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import bot
from locations.location import Location

class Intelligence:
    """
    Base Intelligence Module Class / Interface
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        import uuid
        self.intelligence_id = str(uuid.uuid4())
        self.parent = parent
        
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
        
    def get_html_summary(self, botengine, oldest_timestamp_ms, newest_timestamp_ms, test_mode=False):
        """
        Return a human-friendly HTML summary of insights or status of this intelligence module to report in weekly and test mode emails
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: Oldest timestamp in milliseconds to summarize
        :param newest_timestamp_ms: Newest timestamp in milliseconds to summarize
        :param test_mode: True to add or modify details for test mode, instead of a general weekly summary
        """
        return ""
        
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

    #===============================================================================
    # Built-in Timer and Alarm methods.
    #===============================================================================
    def start_timer_ms(self, botengine, milliseconds, argument=None, reference=""):
        """
        Start a relative timer in milliseconds
        :param botengine: BotEngine environment
        :param seconds: Time in milliseconds for the timer to fire
        :param argument: Optional argument to provide when the timer fires.
        :param reference: Optional reference to use to manage this timer.
        """
        # We seed the reference with this intelligence ID to make it unique against all other intelligence modules.
        if isinstance(self.parent, Location):
            # Location intelligence
            bot.start_location_intelligence_timer_ms(botengine, milliseconds, self.intelligence_id, argument, self.intelligence_id + str(reference))

        else:
            # Device intelligence
            bot.start_device_intelligence_timer_ms(botengine, milliseconds, self.intelligence_id, argument, self.intelligence_id + str(reference))

    def start_timer_s(self, botengine, seconds, argument=None, reference=""):
        """
        Helper function with an explicit "_s" at the end, to start a timer in seconds
        :param botengine: BotEngine environment
        :param seconds: Time in seconds for the timer to fire
        :param argument: Optional argument to provide when the timer fires.
        :param reference: Optional reference to use to manage this timer.
        """
        self.start_timer(botengine, seconds, argument, str(reference))

    def start_timer(self, botengine, seconds, argument=None, reference=""):
        """
        Start a relative timer in seconds
        :param botengine: BotEngine environment
        :param seconds: Time in seconds for the timer to fire
        :param argument: Optional argument to provide when the timer fires.
        :param reference: Optional reference to use to manage this timer.
        """
        # We seed the reference with this intelligence ID to make it unique against all other intelligence modules.
        if isinstance(self.parent, Location):
            # Location intelligence
            bot.start_location_intelligence_timer(botengine, seconds, self.intelligence_id, argument, self.intelligence_id + str(reference))

        else:
            # Device intelligence
            bot.start_device_intelligence_timer(botengine, seconds, self.intelligence_id, argument, self.intelligence_id + str(reference))

    def is_timer_running(self, botengine, reference=""):
        """
        Check if a timer or alarm with the given reference is running
        :param botengine: BotEngine environment
        :param reference: Reference
        :return: True if timers or alarms with the given reference are running.
        """
        return botengine.is_timer_running(self.intelligence_id + str(reference))

    def cancel_timers(self, botengine, reference=""):
        """
        Cancel timers with the given reference
        :param botengine: BotEngine environment
        :param reference: Cancel all timers with the given reference
        """
        botengine.cancel_timers(self.intelligence_id + str(reference))
    
    def set_alarm(self, botengine, timestamp_ms, argument=None, reference=""):
        """
        Set an absolute alarm
        :param botengine: BotEngine environment
        :param timestamp_ms: Absolute time in milliseconds for the timer to fire
        :param argument: Optional argument to provide when the timer fires.
        :param reference: Optional reference to use to manage this timer.
        """
        # We seed the reference with this intelligence ID to make it unique against all other intelligence modules.
        if isinstance(self.parent, Location):
            # Location intelligence
            bot.set_location_intelligence_alarm(botengine, timestamp_ms, self.intelligence_id, argument, self.intelligence_id + str(reference))

        else:
            # Device intelligence
            bot.set_device_intelligence_alarm(botengine, timestamp_ms, self.intelligence_id, argument, self.intelligence_id + str(reference))

    def is_alarm_running(self, botengine, reference=""):
        """
        Check if a timer or alarm with the given reference is running
        :param botengine: BotEngine environment
        :param reference: Reference
        :return: True if timers or alarms with the given reference are running.
        """
        return botengine.is_timer_running(self.intelligence_id + str(reference))

    def cancel_alarms(self, botengine, reference=""):
        """
        Cancel alarms with the given reference
        :param botengine: BotEngine environment
        :param reference: Cancel all alarms with the given reference
        """
        # It's not a mistake that this is forwarding to `cancel_timers`.
        # They're all the same thing underneath, and this is a convenience method help to avoid confusion and questions.
        botengine.cancel_timers(self.intelligence_id + str(reference))
