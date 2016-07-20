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
# of this app.py. Then we modify the email template to inject a phrase based on your new mode.
# We also load an external .png image from outside this app.py file, and include it as an email
# attachment. 
# 
# Look in the email_template.vm file for the <img src="cid:inlineImageId" width="100%" alt=""> tag.
# This 'inlineImageId' identifier refers to the identifier of the inline image we attached to the
# email.
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


def run(composer, initialize=False):
    '''This is the execution starting point of your app
    
    @param composer: Instance of the Composer object, which provides built-in functions for you to privately interact with this user's data
    @param initialize: True if we should initialize this app for the given deviceId, and perhaps clear variables
    '''
    
    inputs = composer.get_inputs()              # Get the inputs to this app from Composer
    trigger = composer.get_trigger_info()        # Get the list of things we have permission to access.
    
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
    
    # First we need to identify this app's directory so we can extract the files that we included.
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
    composer.add_email_attachment(attachments, "inline_image.png", utf8_decoded_image, "image/png", "inlineImageId")
    
    # Send the messages. Messages are implied to the user only, unless otherwise specified
    composer.notify(
                    push_content = "Composer says you are now in " + mode + " mode.",
                    push_sound = None,
                    email_subject = "Composer email notification",
                    email_content = template,
                    email_html = True,
                    email_attachments = attachments
                    )
                    
    print("\t=> Notifications sent")
    

