# Amazon Rekognition

This bot utilizes a Amazon Rekognition microservice to demonstrate the power of connecting bots with 3rd party clouds by adding AI video reconigtion to our Presence cameras. Upon motion detected via Presence cameras, a file will be downloaded into our local device. This file will then be uploaded for Amazon Rekonigition to apply it's AI video analytics and return powerful results for us to make smart homes smarter.

Amazon Rekognition uses various services such as: Label Detection and Face Recognition to allow the developers to apply Video Analytics to their video files for a additional AI layer.

Step-by-step Instructions:

### 1. Create a virtual environment to avoid downloading unnecessary SDK into computer (Assuming you have pip)
    pip install virtualenv
    virtualenv {name_of_environment}
    source {name_of_environment}/bin/activate
    
### 2. Install Python SDK (boto3)
    pip install boto3
    
### 3. Create a IAM Account/Role and retrieve the following information: 
    IAM Access ID
    IAM Secret Key

### 4. Create an Amazon S3 Storage and retrieve the following information:
    Bucket name

### 5. Fill in the requested global variables at top of file 
    com.ppc.Microservices/intelligence/videoai/amazonvideo/location_video_microservice.py

### 6. Upload/Purchase/Run this Bot instance:
   
You should give your bot a unique name before committing to the cloud.

    botengine --commit com.yourname.VideoRecognitionAmazon
    botengine --run com.amazon.VideoRecognitionAmazon

