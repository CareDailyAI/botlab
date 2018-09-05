# Google Video Analytics

This bot utilizes a Google Video Intelligence microservice to demonstrate the power of connecting bots with 3rd party clouds by adding AI video reconigtion to our Presence cameras. Upon motion detected via Presence cameras, a file will be downloaded into our local device. This file will then be uploaded for Amazon Rekonigition to apply it's AI video analytics and return powerful results for us to make smart homes smarter.

Google Video Intelligence uses Label Detection services to allow the developers to apply Video Analytics to their video files for a additional AI layer.

Step-by-step Instructions:

### 1. Create a virtual environment to avoid downloading unnecessary SDK into computer (Assuming you have pip)
    pip install virtualenv
    virtualenv {name_of_environment}
    source {name_of_environment}/bin/activate

### 2. Create a Google API account

### 3. Create a GCP project

### 4. Enable the Cloud Video Intelligence API

### 5. Set up authentication:
    Create service account key
    Create a new service account => Use this JSON file to set the environment variable GOOGLE_APPLICATION_CREDENTIALS to file path of JSON file that contains your service account key
    (EXPORT GOOGLE_APPLICATION_CREDENTIALS="{filepath}")

### 6. Install and intialize the Cloud SDK:
    $ pip install --upgrade google-cloud-videointelligence

### 7. Set up a Google Cloud Blob Storage account and retrieve the following:
    Bucket name

### 8. Fill in the requested global variables at top of file com.ppc.Microservices/intelligence/videoai/googlevideo/location_video_microservice.py

### 9. Upload/Purchase/Run this Bot instance:

You should give your bot a unique name before committing to the cloud.

    botengine --commit com.yourname.VideoRecognitionGoogle
    botengine --run com.yourname.VideoRecognitionGoogle
