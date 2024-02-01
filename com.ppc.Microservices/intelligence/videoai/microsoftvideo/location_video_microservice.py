'''
Created on July 11, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Andre Huang
'''

from intelligence.intelligence import Intelligence
import os, uuid, sys
import urllib, base64
try:
    import http.client as http_client

except ImportError:
    # Python 2
    import httplib as http_client
import json
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import time

# Copy/paste Microsoft Blob Storage Account Name
ACCOUNT_NAME = 'andresdemo'

# Copy/paste Microsoft Blob Storage Account Key
ACCOUNT_KEY = '6kG0iguGEK9h41shJasZOW4v/uPKr1Guu8RFWfLhWf7MnDcJaaw5eFhhYGSqaFk2qpqX8JIpJobe0bY8MmYa+g=='

# Copy/paste Microsoft Blob Storage Container Name
CONTAINER_NAME = 'testcontainer'

# Copy/paste Microsoft Video Indexer Ocp-Apim-Subscription-Key
API_KEY = '81a077573ec04752badb072f3c1dd3cb'

# Copy/paste Microsoft Video Indexer Account ID
ACCOUNT_ID = 'd3156601-09f5-46aa-9160-dc3b1827c397'

# Copy/paste Microsoft Video Indexer Account Location
ACCOUNT_LOCATION = 'trial'

class LocationVideoMicroservice(Intelligence):
    """
    Video AI microservice for Microsoft Cognitive Services.

    This microservice will capture newly uploaded motion detection videos and deliver them to Microsoft Video Indexer for analysis.

    The intended audience is developers who are interested in making use of Microsoft Video Indexer services to make smart homes smarter.
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
        job_id = argument[0]
        token = argument[1]
        params = urllib.urlencode({
            'accessToken': token,
            'language': 'English',
        })
        conn = http_client.HTTPSConnection('api.videoindexer.ai')
        conn.request("GET", "/" + ACCOUNT_LOCATION + "/Accounts/" + ACCOUNT_ID + "/Videos/" + str(job_id) + "/Index?%s" % params)
        response = conn.getresponse()
        data = response.read()
        result = json.loads(data)

        # Check if the results are finished processing. Else restart a timer
        if result["state"] == 'Processed':
            botengine.get_logger().info(json.dumps(result, sort_keys=True))
            conn.close()
        else:
            self.start_timer_s(botengine, 5, [job_id, token])
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
        FILE_PATH= os.path.dirname(os.path.abspath(__file__))
        FULL_FILE_PATH =os.path.join(FILE_PATH, FILE_NAME)

        # Download file to local device
        botengine.download_file(file_id, FILE_NAME)

        # Create Blob service and upload file to Microsoft Blob Storage
        block_blob_service = BlockBlobService(account_name='andresdemo', account_key='6kG0iguGEK9h41shJasZOW4v/uPKr1Guu8RFWfLhWf7MnDcJaaw5eFhhYGSqaFk2qpqX8JIpJobe0bY8MmYa+g==')
        block_blob_service.create_container(CONTAINER_NAME)

        # Set Public Access to container
        # A try and except block is used due to a occassional logger exception (Doesn't imapact function)
        try:
            block_blob_service.set_container_acl(CONTAINER_NAME, public_access=PublicAccess.Container)
        except:
            pass
        
        # Convert the file into a blob and store it in Microsoft Azure Blob Storage
        # A try and except block is used due to a occassional logger exception (Doesn't imapact function)
        try:
            block_blob_service.create_blob_from_path(CONTAINER_NAME, FILE_NAME, FULL_FILE_PATH)
        except:
            pass
        
        # Get Video URL
        url = "https://" + ACCOUNT_NAME + ".blob.core.windows.net/" + CONTAINER_NAME + "/" + FILE_NAME

        # Get Access Token
        token = "";
        headers = {
            'Ocp-Apim-Subscription-Key': API_KEY,
        }
        params = urllib.urlencode({
            'allowEdit': 'True',
        })

        # HTTP GET request to Video Indexer API to acquire access token
        try:
            conn = http_client.HTTPSConnection('api.videoindexer.ai')
            conn.request("GET", "/auth/" + ACCOUNT_LOCATION + "/Accounts/" + ACCOUNT_ID + "/AccessToken?%s" % params, headers=headers)
            response = conn.getresponse()
            token = response.read()
            token = token[1:len(token)-1]
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
        
        # Use Access Token to upload Video file 
        headers = {
            'Content-Type': 'multipart/form-data',
        }
        params = urllib.urlencode({
            'Content-Type': 'multipart/form-data',
            'videoUrl': url,
            'streamingPreset': 'Default',
            'privacy': "Public"
        })
        try:
            conn = http_client.HTTPSConnection('api.videoindexer.ai')
            conn.request("POST", "/" + ACCOUNT_LOCATION + "/Accounts/" + ACCOUNT_ID + "/Videos?accessToken=" +token + "&name=Sample&%s" % params, headers=headers)
            response = conn.getresponse()
            data = response.read()
            d = json.loads(data)
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

        botengine.get_logger().info('Video Processing..')

        # Get Video Index
        params = urllib.urlencode({
            'accessToken': token,
            'language': 'English',
        })
        conn = http_client.HTTPSConnection('api.videoindexer.ai')
        conn.request("GET", "/" + ACCOUNT_LOCATION + "/Accounts/" + ACCOUNT_ID + "/Videos/"+d["id"]+"/Index?%s" % params)
        response = conn.getresponse()
        data = response.read()
        result = json.loads(data)
        # Set a timer to queue for results
        # Passing in Video ID and Access Token
        self.start_timer_s(botengine, 5, [d["id"], token])
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
