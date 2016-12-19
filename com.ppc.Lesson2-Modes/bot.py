'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 2 - MODES
# Each user account has at least 1 Location. Each Location has a Mode. Our standard modes include
# "HOME", "AWAY", "SLEEP", "VACATION", but it is technically possible for the mode to be called anything.
#
# Modes drive rules and botengine bots. This bot will explore how to trigger off of modes.
#
#
# VERSION.JSON
# Open your version.json file. You'll notice the trigger specifies we're looking for changes
# to the user's location's mode:
#
#     "trigger": 2,
#
# You'll see another line that specifies which modes we're triggering off of:
#
#     "event": "HOME,AWAY,VACATION",
#
#
# BOT.PY
# Just like triggering off of device measurement data, the bot will run exactly 1 time
# when your location's mode changes. When the bot finishes, it is gone forever, including
# any local variables you created.
#

# RUNNING THIS BOT
# First, register your developer account at http://presto.peoplepowerco.com.
#
# There are several steps needed to run this bot:
#    1. Create a new directory for your bot, with your own unique bundle ID. Copy all the files into it.
#       Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourBot) and cannot
#       be deleted or edited once created.
#    2. Create a new --bot on the server with botengine
#    3. Commit your bot to the server with botengine
#    4. Purchase your bot with botengine
#    5. Run your bot locally
#
#
# We've automated this for you with a script, 'runlesson.sh'. Run it from your terminal window:
#
#    $ ./runlesson.sh
#
#
# This script will automatically do the following for you.
# From a terminal window *above* this bot's current directory:
#
# 1. Create a new directory for your bot with your given bundle ID, and copy all the files from this
#    lesson into that new directory.
#
#
# 2. Commit your bot to the server.
#    This will push all the code, version information, marketing information, and icon to the server.
#    The bot will become privately available.
#
#    botengine --commit com.yourname.YourBot
#
#
# 3. Purchase the bot as if you're an end-user. Note that because your bot is privately available, other end users
#    will not be able to see or access it.
#
#    botengine --purchase com.yourname.YourBot
#
#    This will return a unique instance ID for your purchased bot, which you may reference to reconfigure the bot instance later.
#
#
# 4. Run the bot locally.
#
#    botengine --run com.yourname.YourBot
#
#    This will automatically look up your bot instance ID and run the bot, using the real-time streaming data from the server
#    and the code that is on your local computer.
#


def run(botengine):
    logger = botengine.get_logger()                  # Debug logger, this will capture logged output to an external 'bot.log' file
    inputs = botengine.get_inputs()                  # Information input into the bot
    access = botengine.get_access_block()            # Capture info about all things this bot has permission to access



# This is what I get back from our inputs. Notice it doesn't include any measurements, because
# we triggered off of a Location mode changing event
#
# {
#   'trigger':2,
#   'access':[
#      {
#         'category':1,
#         'control':True,
#         'trigger':True,
#         'location':{
#            'locationId':62,
#            'prevEvent':'HOME',
#            'event':'AWAY'
#         },
#         'read':True
#      }
#   ],
#   'time':1465681083053
# }

    mode = access[0]['location']['event']

    logger.debug("You are now in " + mode + " mode.")
    print("You are now in " + mode + " mode.")          # For your convenience, in case you didn't want to add --console to the command line
