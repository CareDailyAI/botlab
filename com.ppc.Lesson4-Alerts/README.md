#Lesson 4 - Device Alerts

This is an example of an app that listens to alerts from devices. Alerts are different than measurements, in that they occur one time and without state, simply indicating something happened.

##Dependencies

To run this app install the "Presence" app on an iOS device and turn it into a camera. Enable motion recording. Run this app, and give the app permission to access your camera. When motion is recording, you'll see this app react.

##Running This App

 First, register your developer account at http://presto.peoplepowerco.com.
 
 You'll need to add a Presence Camera to your account to run this app. Download the Presence app for free in the app store, on iOS and Android. Sign into the app and turn your mobile device into a security camera.

 We've automated this for you with a script, 'runlesson.sh'. Run it from your terminal window:
 
   `$ ./runlesson.sh`
 
 This script will automatically do the following for you. 
 From a terminal window *above* this app's current directory:
 
 1. Create a new directory for your app with your given bundle ID, and copy all the files from this lesson into that new directory.

 2. Create a new app in your user account with the given bundle ID.
    
    `composer --new com.yourname.YourApp`
 
 3. Commit your app to the server. This will push all the code, version information, marketing information, and icon to the server. The app will become privately available.

    `composer --commit com.yourname.YourApp`
 
 4. Purchase the app as if you're an end-user. Note that because your app is privately available, other end users will not be able to see or access it.

    `composer --purchase com.yourname.YourApp`
 
    This will return a unique instance ID for your purchased app, which you may reference to reconfigure the app instance later.
    
 5. Run the app locally.
    
    `composer --run com.yourname.YourApp`
    
    This will automatically look up your app instance ID and run the app, using the real-time streaming data from the server and the code that is on your local computer.
