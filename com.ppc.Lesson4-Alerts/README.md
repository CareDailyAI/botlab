# Lesson 4 - Device Alerts

This is an example of an bot that listens to alerts from devices. Alerts are different than measurements, in that they occur one time and without state, simply indicating something happened. See bot.py for more information.

## Dependencies

To run this bot install the "Presence" bot on an iOS device and turn it into a camera. Enable motion recording. Run this bot, and give the bot permission to access your camera. When motion is recording, you'll see this bot react.

## Running This Bot

 First, register your developer account at http://presto.peoplepowerco.com.

 You'll need to add a Presence Camera to your account to run this bot. Download the Presence bot for free in the bot store, on iOS and Android. Sign into the bot and turn your mobile device into a security camera.

 There are several steps needed to run this bot:
    1. Create a new directory for your bot, with your own unique bundle ID. Copy all the files into it.
       Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourBot) and cannot be deleted or edited once created.
    2. Commit your bot to the server with botengine
    3. Purchase your bot with botengine
    4. Run your bot locally

 We've automated this for you with a script, 'runlesson.sh'. Run it from your terminal window:

  `$ ./runlesson.sh`


 This script will automatically do the following for you.  From a terminal window *above* this bot's current directory:

 1. Create a new directory for your bot with your given bundle ID, and copy all the files from this lesson into that new directory.

 2. Commit your bot to the server.
      This will push all the code, version information, marketing information, and icon to the server. The bot will become privately available.

      `botengine --commit com.yourname.YourBot`


 3. Purchase the bot as if you're an end-user. Note that because your bot is privately available, other end users will not be able to see or access it.

    `botengine --purchase com.yourname.YourBot`

    This will return a unique instance ID for your purchased bot, which you may reference to reconfigure the bot instance later.

 4. Run the bot locally.

      `botengine --run com.yourname.YourBot`

    This will automatically look up your bot instance ID and run the bot, using the real-time streaming data from the server and the code that is on your local computer.
