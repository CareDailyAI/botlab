#Lesson 5 - Combining Triggers

This is an example of an app that is triggered from multiple types of triggers. This app triggers off of 4 different trigger types: measurements, modes, alerts, and schedulues. See app.py for more information.

##Running This App

 First, register your developer account at http://presto.peoplepowerco.com.

 This app will require a device to be connected to your account:
 
   Option A:  Buy a Presence Security Pack (http://presencepro.com/store). This is recommended because it will give you a lot more tools to create cool apps with.

   Option B:  Create a virtual light switch locally. Open up another terminal window. In this lesson's directory, run

			`$ python lightSwitch.py`

   This will register a new 'Virtual Light Switch' into your account, which you can control manually from its command line. It uses the Device API, and from the point of view of the Ensemble software suite server, is a real device.
 
    You will need to have at least 1 entry sensor OR 1 virtual light switch in your account before you can purchase this app to run it (see below). Otherwise, this app will be incompatible with your account.
 
 
 There are several steps needed to run this app:
    1. Create a new directory for your app, with your own unique bundle ID. Copy all the files into it. Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourApp) and cannot be deleted or edited once created.
    2. Create a new --app on the server with composer
    3. Commit your app to the server with composer
    4. Purchase your app with composer
    5. Run your app locally

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
