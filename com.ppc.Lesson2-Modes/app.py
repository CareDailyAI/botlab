'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 2 - MODES
# Each user account has at least 1 Location. Each Location has a Mode. Our standard modes include 
# "HOME", "AWAY", "SLEEP", "VACATION", but it is technically possible for the mode to be called anything.
# 
# Modes drive rules and composer apps. This app will explore how to trigger off of modes.
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
# APP.PY
# Just like triggering off of device measurement data, the app will run exactly 1 time
# when your location's mode changes. When the app finishes, it is gone forever, including
# any local variables you created.
# 

# RUNNING THIS APP
# First, register your developer account at http://presto.peoplepowerco.com.
# 
# There are several steps needed to run this app:
#    1. Create a new directory for your app, with your own unique bundle ID. Copy all the files into it.
#       Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourApp) and cannot
#       be deleted or edited once created.
#    2. Create a new --app on the server with composer
#    3. Commit your app to the server with composer
#    4. Purchase your app with composer
#    5. Run your app locally
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


def run(composer):
    logger = composer.get_logger()                  # Debug logger, this will capture logged output to an external 'app.log' file
    inputs = composer.get_inputs()                  # Information input into the app
    access = composer.get_access_block()            # Capture info about all things this app has permission to access
    
    
    
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
    

