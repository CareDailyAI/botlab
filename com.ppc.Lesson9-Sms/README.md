# Lesson 9 : SMS Conversational Agents

In this lesson, you will learn:

* How Group Text SMS messaging works
* How to send a Group Text SMS message
* How to receive an SMS message

SMS messaging is very exciting because the communications channel is very underutilized, and nearly everyone has it. SMS also enables a bi-directional conversation with users in a style that you can talk *with* them, rather than *at* them (as is the case with push notifications).

## Group Text SMS Messages

![sms_architecture](https://user-images.githubusercontent.com/1031168/42357671-eaeed058-808d-11e8-8670-59033dbe5a50.png)

SMS messages are delivered to *groups of people* in a way that allows your bot to participate in the conversation.

You must have a subscription service that includes the SMS subscription to enable SMS messaging in any user account.

There are several categories of groups defined, including:

* **Category 0** : People who live here
* **Category 1** : Friends
* **Category 2** : Family / Caregivers

The user declares who these people are through their mobile app. When a new person is added, they receive a text message like this:

    The Moss Family has added you to MyPlace Security to get SMS alerts from their home. 
    Your carrier may charge you for SMS msgs. 
    Reply STOP to opt-out.
    
## SMS Rules

There are a few rules the bot server abides by which you should be aware of:
* The bot server maintains user privacy and will not allow your bots to receive phone numbers of any individual.
* All SMS chats are initiated by the bot
* Your bot may receive replies to messages that were actually destined for another bot service in the user's account.
* If nobody replies for 1 hour, the chat is closed down and messages can no longer be received. This enables the phone numbers to be used for some other situation.
* SMS messages cost money. Please use them wisely.

## Sending SMS messages

To see who is in each group, use:
 
    botengine.get_sms_subscribers(self, to_me=True, to_my_friends=False, to_my_family=False)

To send an SMS message to one or more groups, call this `botengine` method:

    botengine.notify(sms_content="SMS Message content", to_me=True, to_my_friends=False, to_my_family=False)
    
Messages over 140 characters long will be automatically delivered as multiple SMS messages and order is not guaranteed.

## Receiving SMS messages

To receive an SMS message, edit your `runtime.json` file to turn on your `data stream` trigger and listen to the external data stream address `SMS`.

    # DATA STREAMS
    # This dataStreams block defines a list of data stream addresses that are allowed to trigger this bot.
    # Data stream messages can be passed around internally between microservices within the bot without
    # including their addresses on this list, but your bot cannot receive any data stream messages from
    # other authorized bots, apps, or clouds without opening a port for each address we want to listen to here.
    "dataStreams": [
      {
        # The 'SMS' data stream address is reserved for delivering SMS messages from the user to the bot
        "address": "SMS"
      }
    ]
    
## Explore more

You may connect your bots with a 3rd party Natural Language Processing (NLP) service to give it a boost. There are also Python NLP libraries available to help produce your own sophisticated SMS conversational agents.

 