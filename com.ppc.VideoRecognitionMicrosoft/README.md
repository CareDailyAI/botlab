# Microsoft Cognitive Services Bot
This bot utilizes a Microsoft Video Indexer microservice to demonstrate the power of connecting bots with 3rd party clouds by adding AI video reconigtion to our Presence cameras. Upon motion detected via Presence cameras, a file will be downloaded into our local device. This file will then be uploaded for Amazon Rekonigition to apply it's AI video analytics and return powerful results for us to make smart homes smarter.

Microsoft Video Indexer uses various services such as: Label Detection and Voice Recognition to allow the developers to apply Video Analytics to their video files for a additional AI layer.

Step-by-step Instructions:

### 1. Create a virtual environment to avoid downloading unnecessary SDK into computer (Assuming you have pip)
    pip install virtualenv
    virtualenv {name_of_environment}
    source {name_of_environment}/bin/activate
    
### 2. Download necessary packages:
    pip install azure

### 3. Set up a Microsoft Blob Storage account and retrieve the following:
    Account name
    Account key
    Container name

### 4. Set up a Microsoft Azure account and retrieve the following:
    Account ID
    Ocp-Apim-Subscription-Key

### 5. Fill in the requested global variables at top of file
    com.ppc.Microservices/intelligence/videoai/microsoftideo/location_video_microservice.py

### 6. Upload/Purchase/Run this Bot instance:

Give your bot a unique name before committing it to the cloud.
    
    botengine --commit com.yourname.VideoRecognitionMicrosoft
    botengine --run com.yourname.VideoRecognitionMicrosoft
