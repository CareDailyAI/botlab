'''
Created on July 13, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Andre Huang
'''

from intelligence.intelligence import Intelligence
from google.cloud import videointelligence
from google.cloud import storage
import os, uuid, sys

# User authentication/authorization is done through Google Cloud

# Copy/paste your Google Cloud Blob Storage bucket name here to store videos
BUCKET_NAME = 'test-bucket3578'

# Copy/paste your Video URL
VIDEO_URL = 'gs://test-bucket3578/video.mp4'


class LocationVideoMicroservice(Intelligence):
    """
    Video AI microservice for Google Video Analytics.

    This microservice will capture newly uploaded motion detection videos and deliver them to Google Video Intelligence for analysis.

    The intended audience is developers who are interested in making use of Google Video Analytics services to make smart homes smarter.
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
        When a device disconnects, it will send an alert like this:  [{u'alertType': u'status', u'params': [{u'name': u'deviceStatus', u'value': u'2'}], u'deviceId': u'eb10e80a006f0d00'}]
        When a device reconnects, it will send an alert like this:  [{u'alertType': u'on', u'deviceId': u'eb10e80a006f0d00'}]
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
        :param alert_params: Dictionary of alert parameters
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
        # We are demonstrating video processing here, so avoid video processing on files that are not videos.
        if "video" not in content_type:
            botengine.get_logger().info("The uploaded file is not a video, skipping processing ...")
            return

        # Create full file path 
        FILE_NAME = "video." + file_extension
        FULL_FILE_PATH = os.path.join(os.getcwd(), FILE_NAME)
        
        # Download file to local device
        botengine.download_file(file_id, FILE_NAME)

        # Create/Get Google Cloud Blob Storage
        client = storage.Client()
        bucket = client.get_bucket(BUCKET_NAME)

        # Convert the file to a Blob
        blob = bucket.blob(FILE_NAME)
        # Upload the Blob to the Cloud Storage
        blob.upload_from_filename(FULL_FILE_PATH)


        # Detects labels given a GCS path.
        video_client = videointelligence.VideoIntelligenceServiceClient()
        features = [videointelligence.enums.Feature.LABEL_DETECTION]
        operation = video_client.annotate_video(VIDEO_URL, features=features)
        botengine.get_logger().info('Processing video for label annotations:')

        # While loop that continues until the file is done processing

        # This synchronous call/timed loop is not best practice in our context of our framework
        # We require our bots to execute and exit as fast as possible due to unecessary billing 
        # from Amazon AWS Lambda: (Time spent executing) * (Max memory allocated) = $$$
        result = operation.result(timeout=90)

        # Video processing is completed, get Labels and print accordingly
        botengine.get_logger().info('LABELS: ')
        segment_labels = result.annotation_results[0].segment_label_annotations

        for i, segment_label in enumerate(segment_labels):
            print('Video label description: {}'.format(
                segment_label.entity.description))
            for category_entity in segment_label.category_entities:
                print('\tLabel category description: {}'.format(
                    category_entity.description))

            for i, segment in enumerate(segment_label.segments):
                start_time = (segment.segment.start_time_offset.seconds +
                                segment.segment.start_time_offset.nanos / 1e9)
                end_time = (segment.segment.end_time_offset.seconds +
                            segment.segment.end_time_offset.nanos / 1e9)
                positions = '{}s to {}s'.format(start_time, end_time)
                confidence = segment.confidence
                print('\tSegment {}: {}'.format(i, positions))
                print('\tConfidence: {}'.format(confidence))
            print('\n')
        return

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
