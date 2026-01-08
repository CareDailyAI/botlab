'''
Created on July 5, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# All microservices must extend the Intelligence class
from intelligence.intelligence import Intelligence

# Import an EntryDevice
from devices.entry.entry import EntryDevice

class LocationSmsMicroservice(Intelligence):
    """
    When a door opens while you're away, SMS the people who live in the house and ask if they want us to sound the sirens.
    A '1' anywhere in the reply will sound sirens.
    A '2' anywhere in the reply will make sure sirens are turned off.

    You'll need a siren in your account to run this.
    Your smart home app has a free built-in siren, when you transform your phone into a security camera.
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        # Always initialize your parent Intelligence class at the beginning
        Intelligence.__init__(self, botengine, parent)

        # True if there is at least one alarm/siren on
        self.alarm_on = False


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
        if "HOME" in current_mode:
            for device_id in self.parent.devices:
                # Duck-type our way through de-activating sirens
                try:
                    self.parent.devices[device_id].alarm(botengine, False)

                except:
                    pass

            self.alarm_on = False


    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        if isinstance(device_object, EntryDevice):
            if device_object.did_change_state(botengine) and device_object.is_open(botengine) and not self.parent.is_present(botengine) and not self.alarm_on:
                # The door just opened, and our Location object says the user shouldn't be home right now, and we don't have any sirens activated at the moment.
                content = "Hi, this is your Bot. The {} family '{}' opened while the house was in {} mode. Sound the sirens? Reply: [1] for 'Yes', [2] for 'No'".format(botengine.get_user_last_name(), device_object.description, self.parent.mode)
                botengine.notify(sms_content=content, to_me=True)

    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        # Device metadata can get updated multiple times in one execution. Uncomment this line if you'd like to see it.
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


    # This is a data stream message receiver
    def SMS(self, botengine, content):
        """
        This is a datastream message to receive SMS content in response to a group text message.
        :param botengine:
        :param content:
        :return:
        """
        if 'text' not in content:
            botengine.get_logger().warn("location_sms_microservice: Malformed SMS data stream message received: {}".format(content))
            return

        text = content['text'].lower()

        if '1' in text:
            # Turn on all alarms
            self.alarm_on = False
            for device_id in self.parent.devices:
                # Duck-type our way through activating sirens
                try:
                    self.parent.devices[device_id].alarm(botengine, True)
                    self.alarm_on = True
                except:
                    pass

            if self.alarm_on:
                content = "You got it, I am alarming sirens now. Reply [2] or flip to HOME mode to turn them off. -Bot"
                botengine.notify(sms_content=content, to_me=True)

            else:
                content = "Hmm, you don't have any connected sirens. Next time, you can turn your smart home app into a security camera and it will act like a siren. -Bot"
                botengine.notify(sms_content=content, to_me=True)


        elif '2' in text:
            # Make sure all alarms are off.
            content = "Okay. -Bot"
            botengine.notify(sms_content=content, to_me=True)

            for device_id in self.parent.devices:
                # Duck-type our way through de-activating sirens
                try:
                    self.parent.devices[device_id].alarm(botengine, False)

                except:
                    pass

            self.alarm_on = False


        else:
            # Do nothing. Remember that group text messages can include people talking amongst themselves and not to the bot.
            pass



