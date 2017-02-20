# -*- coding: utf-8 -*-
'''
Created on September 19, 2016

@author: David Moss

Email support@peoplepowerco.com if you have questions!
'''

# LESSON 11 - QUESTIONS
# BotEngine can ask users questions:
#    * To gain context in the data
#    * To configure an bot
#    * To inform behavior
#
# This is very bot-like behavior
#
# Questions can be open-ended text, yes/no, radio buttons, checkbox, date, time, etc.
# Questions can automatically tag users to segment the user base.
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
#    This will also purchase the bot for you.
#
#    botengine --commit com.yourname.YourBot
#
#
# 3. Run the bot locally.
#
#    botengine --run com.yourname.YourBot
#
#    This will automatically look up your bot instance ID and run the bot, using the real-time streaming data from the server
#    and the code that is on your local computer.
#

import json

# ACCESS CATEGORIES
ACCESS_CATEGORY_MODE = 1


def run(botengine):
    '''
    This is the execution starting point of your bot
    @param botengine: Instance of the BotEngine object, which provides built-in functions for you to privately interact with this user's data
    '''

    # Initialize the bot by grabbing access to all the important information
    logger = botengine.get_logger()                  # Debug logger, this will capture logged output to an external 'bot.log' file
    inputs = botengine.get_inputs()                  # Information input into the bot
    triggerType = botengine.get_trigger_type()       # What type of trigger caused the bot to execute this time
    trigger = botengine.get_trigger_info()           # Get the information about the trigger
    measures = botengine.get_measures_block()        # Capture new measurements, if any
    access = botengine.get_access_block()            # Capture info about all things this bot has permission to access

# INPUTS:
#{
#  "access": [
#    {
#      "category": 1,
#      "control": false,
#      "location": {
#        "event": "HOME",
#        "locationId": 205,
#        "name": "People Power Company",
#        "timezone": {
#          "dst": false,
#          "id": "US/Arizona",
#          "name": "Mountain Standard Time",
#          "offset": -420
#        }
#      },
#      "read": true,
#      "trigger": false
#    }
#  ],
#  "questions": [
#    {
#      "answer": "1",
#      "answerTime": 1474428712000,
#      "id": 89,
#      "key": "com.ppc.Lesson11-home"
#    }
#  ],
#  "time": 1474428712796,
#  "trigger": 16
#}

    if triggerType == botengine.TRIGGER_MODE:
        for item in access:
            if item['category'] == botengine.ACCESS_CATEGORY_MODE:
                mode = item['location']['event']

        # We start by generating a question. This produces a Question object.
        # The signature looks like this:
        # generate_question(key_identifier, response_type, editable=False, default_answer=None, correct_answer=None, answer_format=None, urgent=False, front_page=False, send_push=False, send_sms=False, send_email=False):

        if mode == "HOME":
            print("Asking the user a question about their trip")
            question = botengine.retrieve_question("Left your pets?")
            if question is not None:
                print("> Deleting the AWAY mode question")
                botengine.delete_question(question)

            question = botengine.generate_question("com.ppc.Lesson11-home", botengine.QUESTION_RESPONSE_TYPE_YESNO, editable=True, urgent=False, front_page=True, send_push=True)
            question.frame_question("Did you have a nice trip?", "en")
            question.frame_question("¿Tuviste un buen viaje?", "sp")
            botengine.ask_question(question)

        if mode == "AWAY":
            print("Asking the user a question about going away")

            question = botengine.retrieve_question("com.ppc.Lesson11-home")
            if question is not None:
                print("> Deleting the HOME mode question")
                botengine.delete_question(question)

            question = botengine.generate_question("Left your pets?", botengine.QUESTION_RESPONSE_TYPE_YESNO, urgent=True, front_page=True, send_push=True)
            question.frame_question("Did you leave the pets at home?", "en")
            question.frame_question("¿Dejaste a sus mascotas en casa?", "sp")
            botengine.ask_question(question)

    elif triggerType == botengine.TRIGGER_QUESTION_ANSWER:
        print("Triggered from a question being answered!")
        question = botengine.get_answered_question()
        print("The answer to '" + question.question["en"] + "' was " + str(question.answer))
