'''
Created on July 9, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Andre Huang
'''

from intelligence.intelligence import Intelligence
import boto3
import time
import json
from botocore.client import Config

# Copy/paste your Amazon AWS Access Key ID here
ACCESS_KEY_ID = ''

# Copy/paste your Amazon AWS Access Secret Key here
ACCESS_SECRET_KEY = ''

# Copy/paste your Amazon AWS S3 bucket name here to store videos
BUCKET_NAME = 'test-video-file-upload'

# Set to True to make AWS Rekognition extract the labels of the objects it sees in the video
EXTRACT_LABELS = True

# Set to True to make AWS Rekognition extract information about faces it sees in the video
EXTRACT_FACES = False


# State references for our timer to finish executing split-phase facial and label extractions from AWS
TIMER_REFERENCE__EXTRACT_LABELS = 0
TIMER_REFERENCE__EXTRACT_FACES = 1



class LocationVideoMicroservice(Intelligence):
    """
    Video AI microservice for Amazon AWS Rekognition.

    This microservice will capture newly uploaded motion detection videos and deliver them to AWS Rekognition for analysis.

    The intended audience is developers who are interested in making use of AWS Rekognition services to make smart homes smarter.
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
        state, job_id, file_id = argument

        client = boto3.client('rekognition')

        if state == TIMER_REFERENCE__EXTRACT_LABELS:
            labels = client.get_label_detection(
                JobId=job_id,
                MaxResults=1000,
                SortBy='NAME'
            )

            if labels["JobStatus"] == "SUCCEEDED":
                # Label detection completed
                botengine.get_logger().info("LABELS: ")
                botengine.get_logger().info(json.dumps(labels, sort_keys=True))

                names = []

                if 'Labels' in labels:
                    for label_object in labels['Labels']:
                        if 'Label' in label_object:
                            if 'Name' in label_object['Label']:
                                name = label_object['Label']['Name']
                                if name not in names:
                                    names.append(name)
                                    botengine.get_logger().info("Tagged: {}".format(name))
                                    botengine.tag_file(name, file_id)

            else:
                # Label detection is still processing ... wait a few more seconds
                self.start_timer_s(botengine, 5, (TIMER_REFERENCE__EXTRACT_LABELS, job_id, file_id))
                
        elif state == TIMER_REFERENCE__EXTRACT_FACES:
            faces = client.get_face_detection(
                JobId=job_id,
                MaxResults=50,
            )

            if faces['JobStatus'] == "SUCCEEDED":  
                # Facial recognition completed
                botengine.get_logger().info("FACES: ")
                botengine.get_logger().info(json.dumps(faces, sort_keys=True))
            else:
                # Facial recognition is still processing ... wait a few more seconds
                self.start_timer_s(botengine, 5, (TIMER_REFERENCE__EXTRACT_FACES, job_id, file_id))

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

        # Start by downloading the file from the user's account. This gets stored into your local
        # filesystem. If executing on the cloud, each bot gets a small temporary file system to play with.
        FILE_NAME = "video." + file_extension
        botengine.download_file(file_id, FILE_NAME)

        # Now the file exists locally, open and forward it to Amazon S3.
        data = open(FILE_NAME, 'rb')

        # Configure Amazon S3 parameters using boto3
        s3 = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )

        # Upload file into the Amazon S3 Bucket
        s3.Bucket(BUCKET_NAME).put_object(Key=FILE_NAME, Body=data, ACL='public-read')
        botengine.get_logger().info("File uploaded to S3.")

        client = boto3.client('rekognition')

        if EXTRACT_LABELS:
            # Initate Asynchronous Label Detection from given Bucket/File properties in Amazon S3
            botengine.get_logger().info("Now detecting labels...")
            response = client.start_label_detection(
                Video={
                    'S3Object': {
                        'Bucket': BUCKET_NAME,
                        'Name': FILE_NAME,
                    }
                },
                ClientRequestToken=str(botengine.get_timestamp()),
                MinConfidence = 50,
                JobTag='job-labels'
            )

            self.start_timer_s(botengine, 5, (TIMER_REFERENCE__EXTRACT_LABELS, response["JobId"], file_id))


            # We've gotten you this far.
            # Now it's your job - the developer - to do something useful with these labels from the video.


        if EXTRACT_FACES:
            # Initate Asynchronous Face Detection from given Bucket/File properties in Amazon S3
            botengine.get_logger().info("Now detecting faces...")
            response = client.start_face_detection(
                Video={
                    'S3Object': {
                        'Bucket': BUCKET_NAME,
                        'Name': FILE_NAME,
                    }
                },
                ClientRequestToken='request-faces',
                FaceAttributes='DEFAULT',
                JobTag='job-faces'
            )

            self.start_timer_s(botengine, 5, (TIMER_REFERENCE__EXTRACT_FACES, response["JobId"], file_id))

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