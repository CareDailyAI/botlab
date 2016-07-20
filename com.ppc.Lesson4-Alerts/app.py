'''
Created on 

@author: Destry Teeter and David Moss

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 4 - DEVICE ALERTS
# This lesson will demonstrate how to listen for alerts from devices.
# Alerts are different than measurements, in that they occur one time and without state, 
# simply indicating something happened.  Alerts are used in Presence Cameras to 
# declare that videos have been recorded, triggering the server to send out
# push notifications and emails to the user.
#
# To make this lesson work, install the "Presence" app on an iOS device and 
# turn it into a camera. Enable motion recording. Run this app, and give the
# app permission to access your camera. When motion is recording,
# you'll see this app react.
# 


# RUNNING THIS APP
# First, register your developer account at http://presto.peoplepowerco.com.
# 
# You'll need to add a Presence Camera to your account to run this app.
# Download the Presence app for free in the app store, on iOS and Android.
# Sign into the app and turn your mobile device into a security camera.
# 
#
# We've automated this for you with a script, 'runlesson.sh'. Run it from your terminal window:
# 
#    $ ./runlesson.sh
#
# 
# This script will automatically do the following for you. 
# From a terminal window *above* this app's current directory:
# 
# 1. Create a new directory for your app with your given bundle ID, and copy all the files from this
#    lesson into that new directory.
#
# 
# 2. Create a new app in your user account with the given bundle ID.
#    
#    composer --new com.yourname.YourApp
#    
# 
# 3. Commit your app to the server. 
#    This will push all the code, version information, marketing information, and icon to the server. 
#    The app will become privately available.
#
#    composer --commit com.yourname.YourApp
#
# 
# 4. Purchase the app as if you're an end-user. Note that because your app is privately available, other end users
#    will not be able to see or access it.
#
#    composer --purchase com.yourname.YourApp
# 
#    This will return a unique instance ID for your purchased app, which you may reference to reconfigure the app instance later.
#    
#    
# 5. Run the app locally.
#    
#    composer --run com.yourname.YourApp
#    
#    This will automatically look up your app instance ID and run the app, using the real-time streaming data from the server
#    and the code that is on your local computer.
# 
    
def run(composer, initialize=False):

    # Initialize
    logger = composer.get_logger()                  # Debug logger
    inputs = composer.get_inputs()                  # Information input into the app
    triggerType = composer.get_trigger_type()       # What type of trigger caused the app to execute this time
    trigger = composer.get_trigger_info()           # Get the information about the trigger
    measures = composer.get_measures_block()        # Capture new measurements, if any
    access = composer.get_access_block()            # Capture info about all things this app has permission to access
    alerts = composer.get_alerts_block()            # Capture new alerts, if any
    
    
# This is what inputs we see when I run this app against one of my Presence Cameras:
#
#{
#  "access": [
#    {
#      "category": 4,
#      "control": false,
#      "device": {
#        "deviceId": "8E340EFB-793E-4A62-89D6-509F95B7B99A::142",
#        "deviceType": 24,
#        "locationId": 205,
#        "measureDate": 1467597485000,
#        "startDate": 1467324073000,
#        "updateDate": 1467597488000,
#        "description": "Presence Camera"
#      },
#      "read": true,
#      "trigger": true
#    }
#  ],
#  "alerts": [
#    {
#      "alertType": "motion",
#      "deviceId": "8E340EFB-793E-4A62-89D6-509F95B7B99A::142",
#      "params": [
#        {
#          "name": "mediaType",
#          "value": "1"
#        },
#        {
#          "name": "deviceModel",
#          "value": "iPhone"
#        },
#        {
#          "name": "videoCount",
#          "value": "4"
#        },
#        {
#          "name": "fileRef",
#          "value": "166950"
#        }
#      ]
#    }
#  ],
#  "time": 1467597488090,
#  "trigger": 4
#}


    if triggerType == 4:
        # This app is triggered off an alert.
        # Notice that a single trigger can contain alerts from multiple devices, so we'll iterate through them.
        for focused_alert in alerts:
            alertType = focused_alert['alertType']
            deviceName = trigger['device']['description']
            
            print("\n\nGot a '" + alertType + "' alert from your '" + deviceName +"'!")
            
            for parameter in focused_alert['params']:
                print("\t" + parameter['name'] + " = " + parameter['value'])
            



    
    

