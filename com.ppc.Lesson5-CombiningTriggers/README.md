#Lesson 5 - Combining Triggers

This is an example of an bot that is triggered from multiple types of triggers. This bot triggers off of 4 different trigger types: measurements, modes, alerts, and schedulues. See bot.py for more information.

##Running This Bot

 First, register your developer account at http://presto.peoplepowerco.com.

 This bot will require a device to be connected to your account:
 
   Option A:  Buy a Presence Security Pack (http://presencepro.com/store). This is recommended because it will give you a lot more tools to create cool apps with.

   Option B:  Create a virtual light switch locally. Open up another terminal window. In this lesson's directory, run

			`$ python lightSwitch.py`

   This will register a new 'Virtual Light Switch' into your account, which you can control manually from its command line. It uses the Device API, and from the point of view of the Ensemble software suite server, is a real device.
 
    You will need to have at least 1 entry sensor OR 1 virtual light switch in your account before you can purchase this bot to run it (see below). Otherwise, this bot will be incompatible with your account.
 
 
 There are several steps needed to run this bot:
    1. Create a new directory for your bot, with your own unique bundle ID. Copy all the files into it. Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourApp) and cannot be deleted or edited once created.
    2. Create a new --bot on the server with botengine
    3. Commit your bot to the server with botengine
    4. Purchase your bot with botengine
    5. Run your bot locally

 We've automated this for you with a script, 'runlesson.sh'. Run it from your terminal window:
 
    `$ ./runlesson.sh`
 
 This script will automatically do the following for you. 
 From a terminal window *above* this bot's current directory:
 
 1. Create a new directory for your bot with your given bundle ID, and copy all the files from this lesson into that new directory.
 
 2. Create a new bot in your user account with the given bundle ID.
    
    `botengine --new com.yourname.YourApp`
 
 3. Commit your bot to the server. This will push all the code, version information, marketing information, and icon to the server. The bot will become privately available.

    `botengine --commit com.yourname.YourApp`

 4. Purchase the bot as if you're an end-user. Note that because your bot is privately available, other end users will not be able to see or access it.

    `botengine --purchase com.yourname.YourApp`
 
    This will return a unique instance ID for your purchased bot, which you may reference to reconfigure the bot instance later.
    
 5. Run the bot locally.
    
    `botengine --run com.yourname.YourApp`
    
    This will automatically look up your bot instance ID and run the bot, using the real-time streaming data from the server and the code that is on your local computer.
