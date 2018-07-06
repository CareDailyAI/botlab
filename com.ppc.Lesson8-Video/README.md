# Lesson 8 : Video

In this lesson, you'll learn how to:

* Use the `file_uploaded()` event method to trigger the bot when a video is recorded into the user's account
* Send out video alerts using pre-formatted email templates
* Download the video for further processing with a 3rd party AI video analytics platform

## Reacting to videos

Open any app powered by People Power (for example 'Presence by People Power'), and you'll find a killer feature built right into the app: a free security camera.

Your app will transform a spare smartphone or tablet into a free internet security camera with the ability to view live, record motion detection videos, and even talk back to people and pets who are nearby your camera.

Now, when your camera records motion detection videos, your bots can react. This can allow you to send out intelligent alerts, or download the video into the bot's temporary file system for processing by a 3rd party AI video analytics service.

### Exploring the video microservice

* `index.py`: Specifies that we'll attach the `location_video_microservice.py` to the user's Location object
* `runtime.json`: Specifies we'll trigger off of new device files being uploaded from iOS and Android camera device types. We also want permission to access the user's files that are uploaded
* `location_video_microservice.py`: In the `file_uploaded(..)` event method, we show two ways to react to the newly recorded video or image file. First, we demonstrate how to use `def download_file(self, file_id, local_filename, thumbnail=False)` to download the media to the local file system for further processing. We also demonstrate how to send out push and email notifications using a pre-formatted email template at the server designed for delivering motion video alerts.

## Explore more

Try to connect your video microservice with a 3rd party AI video analytics platform such as AWS Rekognition, Microsoft Cognitive Services, or Google Video Analytics. Can you intelligently deliver alerts only when a person appears on video while the user's home is set to AWAY mode?
 
 

