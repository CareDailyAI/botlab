#Lesson 2 - Modes

This bot shows how to trigger off of modes. Each user account has at least 1 location, and each location has a mode. The standard modes are: "HOME", "AWAY", "SLEEP", "VACATION", but it is technically possible for the mode to be called anything. See bot.py for more information.

## Running This Bot

 First, register your developer account at http://app.presencepro.com.

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
