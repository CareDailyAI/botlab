'''
Created on June 9, 2016

@author: David Moss and Destry Teeter

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 6 - NOTIFICATIONS
# In this lesson, we demonstrate notifications to the user, sent whenever the user changes modes.
# When you change your mode, we send a push notification and an HTML email.
# 
# The email is actually quite interesting. We load an HTML email template from a file outside
# of this bot.py. Then we modify the email template to inject a phrase based on your new mode.
# We also load an external .png image from outside this bot.py file, and include it as an email
# attachment. 
# 
# Look in the email_template.vm file for the <img src="cid:inlineImageId" width="100%" alt=""> tag.
# This 'inlineImageId' identifier refers to the identifier of the inline image we attached to the
# email.
# 


# RUNNING THIS BOT
# First, register your developer account at http://presto.peoplepowerco.com.
# 
# There are several steps needed to run this bot:
#    1. Create a new directory for your bot, with your own unique bundle ID. Copy all the files into it.
#       Note that bundle ID's are always reverse-domain notation (i.e. com.yourname.YourApp) and cannot
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
# 2. Create a new bot in your user account with the given bundle ID.
#    
#    botengine --new com.yourname.YourApp
#    
# 
# 3. Commit your bot to the server. 
#    This will push all the code, version information, marketing information, and icon to the server. 
#    The bot will become privately available.
#
#    botengine --commit com.yourname.YourApp
#
# 
# 4. Purchase the bot as if you're an end-user. Note that because your bot is privately available, other end users
#    will not be able to see or access it.
#
#    botengine --purchase com.yourname.YourApp
# 
#    This will return a unique instance ID for your purchased bot, which you may reference to reconfigure the bot instance later.
#    
#    
# 5. Run the bot locally.
#    
#    botengine --run com.yourname.YourApp
#    
#    This will automatically look up your bot instance ID and run the bot, using the real-time streaming data from the server
#    and the code that is on your local computer.
# 


def run(botengine):
    '''This is the execution starting point of your bot
    
    @param botengine: Instance of the BotEngine object, which provides built-in functions for you to privately interact with this user's data
    @param initialize: True if we should initialize this bot for the given deviceId, and perhaps clear variables
    '''
    
    inputs = botengine.get_inputs()              # Get the inputs to this bot from BotEngine
    trigger = botengine.get_trigger_info()        # Get the list of things we have permission to access.
    
# This is what I get back from our inputs. 
#{
#  "access": [
#    {
#      "category": 1,
#      "control": false,
#      "location": {
#        "event": "HOME",
#        "locationId": 205,
#        "prevEvent": "AWAY",
#        "timezone": {
#          "dst": false,
#          "id": "US/Arizona",
#          "name": "Mountain Standard Time",
#          "offset": -420
#        }
#      },
#      "read": true,
#      "trigger": true
#    }
#  ],
#  "time": 1467483289562,
#  "trigger": 2
#}

    # So you can see how long this takes.
    print("Sending ...")
    
    # First we need to identify this bot's directory so we can extract the files that we included.
    import os 
    my_app_directory = os.path.dirname(os.path.realpath(__file__))
    
    # Open the local email template
    with open(my_app_directory + '/email_template.vm', 'r') as email_template:
        template = email_template.read()
    
    # Modify the email template
    mode = trigger['location']['event']
    
    if mode == "HOME":
        template = template.replace("$message", "Welcome Home.")
    elif mode == "AWAY":
        template = template.replace("$message", "Goodbye.")
    elif mode == "VACATION":
        template = template.replace("$message", "Have a nice vacation.")
    elif mode == "SLEEP":
        template = template.replace("$message", "Goodnight.")
        
    # Load a picture and base64-encode it
    import base64
    with open(my_app_directory + "/inline_image.png", "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())
        utf8_decoded_image = encoded_image.decode('utf-8')
        
    # Form a list of attachments, and then add the image's base64-encoded utf-8 string as an attachment.
    attachments = []
    botengine.add_email_attachment(attachments, "inline_image.png", utf8_decoded_image, "image/png", "inlineImageId")
    
    # Send the messages. Messages are implied to the user only, unless otherwise specified
    botengine.notify(
                    push_content = "BotEngine says you are now in " + mode + " mode.",
                    push_sound = None,
                    email_subject = "BotEngine email notification",
                    email_content = template,
                    email_html = True,
                    email_attachments = attachments
                    )
                    
    print("\t=> Notifications sent")
    

