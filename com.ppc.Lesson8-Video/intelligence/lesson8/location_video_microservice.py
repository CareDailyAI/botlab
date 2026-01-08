'''
Created on May 30, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence

# Filename for the email template
EMAIL_TEMPLATE_FILENAME = "bots/motion_detected.vm"

class LocationVideoMicroservice(Intelligence):
    """
    Video alert microservice
    * Send out email and push notification alerts for mobile app cameras that record a motion detection video if the camera did not previously send its own alert, in all modes.
    * Demonstrate how to download the video, so you can connect with 3rd party AI video analytics platforms to understand the contents of the image or video
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
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
        :param alert_params: Dictionary of alert parameters
        """
        # Mobile app based cameras may send an alert to the server that a motion detection video was recorded.
        # The alert induces the server itself to send out push notifications and emails
        # Not shown here, you can catch this alert (before and just after a file is uploaded) and prevent
        # your bot from sending a duplicate alert if the server already delivered an alert
        botengine.get_logger().info("Device '{}' sent alert '{}': {}".format(device_object.description, alert_type, alert_params))
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
        # Here's how to download the file so you can process it through 3rd party AI video analytics platforms
        # including AWS Rekognition, Microsoft Cognitive Services, Google Video Analytics, or even your own OpenCV implementation.
        # This will download the video and store it in the bot's current working directory with the filename "media.mp4" for example.
        botengine.download_file(file_id, "media." + file_extension, thumbnail=False)

        # Here's an example of how to send out a video alert
        self._send_video_alert(botengine, device_object, botengine.get_timestamp(), file_id, content_type, file_extension)

    def sunrise_fired(self, botengine, proxy_object):
        """
        It is now sunrise.
        Must have previously called your location's "enable_sunrise_sunset_events(botengine)" method to make this trigger.
        :param botengine: BotEngine environment
        :param proxy_object: Proxy/gateway object where the sun is setting
        """
        return

    def sunset_fired(self, botengine, proxy_object):
        """
        It is now sunset.
        Must have previously called your location's "enable_sunrise_sunset_events(botengine)" method to make this trigger.
        :param botengine: BotEngine environment
        :param proxy_object: Proxy/gateway object where the sun is setting
        """
        return

    def coordinates_updated(self, botengine, latitude, longitude):
        """
        Approximate coordinates of the parent proxy device object have been updated
        :param latitude: Latitude
        :param longitude: Longitude
        """
        return


    def _send_video_alert(self, botengine, device_object, timestamp_ms, file_id, content_type, extension, send_push=True, send_email=True):
        """
        Send a video alert
        :param botengine: BotEngine environment
        :param device_object: Device object that captured the image or video
        :param timestamp_ms: Timestamp the media was captured
        :param file_id: File ID for the video / image
        :param content_type: Content type (i.e. "video/mp4")
        :param extension: File extension (i.e. "mp4")
        :param send_push: True to send a push notification
        :param send_email: True to send an email notification
        """
        import json
        botengine.get_logger().info("location_video_microservice: _send_video_alert({}, {}, {}, {})".format(device_object.description, timestamp_ms, file_id, content_type))

        # Local datetime the file was uploaded
        local_dt = self.parent.get_local_datetime_from_timestamp(botengine, timestamp_ms)
        local_dt_string = local_dt.strftime('%-I:%M %p on %B %d, %Y')

        # Capture the mediaType
        if "video" in content_type:
            subject = "Video captured on {} at {}".format(device_object.description, local_dt_string)
            media_type = 1

        elif "image" in content_type:
            subject = "Image captured on {} at {}".format(device_object.description)
            media_type = 2

        else:
            botengine.get_logger().warn("location_video_microservice: _send_video_alert() received content_type {} which is doesn't map to a 'video' or an 'image'".format(content_type))
            return

        if send_push:
            botengine.notify(subject)

        # This uses an email template on the server to send the video alert
        if send_email:
            # Produce a contentId for attachments
            content_id = "bot{}".format(file_id)

            # Get the user's brand name
            brand_name = botengine.get_user_brand()

            # Produce the model
            model = {
                    "debug": False,
                    "totalFiles": 1,
                    "files": [
                        {
                            "deviceFileId": file_id,
                            "time": local_dt_string,
                            "deviceDesc": "{}".format(device_object.description),
                            "mediaType": media_type,
                            "thumbnail": "cid:{}".format(content_id)
                        }
                    ],
                    "filesAction": None
            }

            # Reference attachments
            attachments = []
            botengine.add_email_attachment_from_camera(attachments, file_id, content_id)

            botengine.get_logger().info("Sending alert: " + json.dumps(model, indent=2, sort_keys=True))

            botengine.notify(email_subject=subject, email_template_filename=EMAIL_TEMPLATE_FILENAME, email_template_model=model, email_html=True, email_attachments=attachments, to_me=True, brand=brand_name)
