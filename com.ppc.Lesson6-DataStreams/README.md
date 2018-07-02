# Lesson 6 : Data Streams

By the end of this lesson you will understand:

* What are data stream messages
* 3 ways data stream messages are communicated and how to distribute them.
* What to modify in your `runtime.json` to allow your bot to listen to data stream messages from the outside world
* Best practices for reacting to data stream messages
* How to inject data into your bot from an web or mobile UI, or command line script

## Data Stream Messages

A data stream message contains an **address**, and a **dictionary of content** containing key-value pairs.

Data stream messages communicate information between individual microservices, between individual bots, and from UIs to bots.

To send a data stream message, invoke the following method from your `Location` object:

    def distribute_datastream_message(self, botengine, address, content, internal=True, external=True):
        """
        Distribute a data stream message both internally to any intelligence module within this bot,
        and externally to any other bots that might be listening.
        :param botengine: BotEngine environment
        :param address: Data stream address
        :param content: Message content
        :param internal: True to deliver this message internally to any intelligence module that's listening (default)
        :param external: True to deliver this message externally to any other bot that's listening (default)
        """

The `datastream_updated(self, botengine, address, content)` event method will be triggered for any and every microservice that receives the data stream message.

### Microservice-to-Microservice Communications

There are several ways to make microservices communicate with each other, but the preferred method is by using data stream messages.

For example, one microservice might identify when users come home and communicate a data stream message to other nearby microservices which may react and control their individual devices.

To communicate between microservices in your current bot, set `internal=True` and `external=False` to keep it internal. The data stream message will then only be communicated and shared amongst the microservices that are immediately part of your bot.

### Bot-to-Bot Communications

Data stream messages can be communicated between bots in two scenarios:

1. Bots within a single user's account can communicate data stream messages to each other, but not outside that user's account to other users.
2. We haven't touched on it yet, but it is possible to run bots at an enterprise / admin level. Enterprise Bots running at an admin level can communicate bi-directionally with bots that remain private to each individual user's account.

To send a data stream message from one bot to other bots inside the user's account who are listening, set `external=True` in your call to the `distribute_datastream_message(...)`. This is the default option.

To allow a bot to listen for and receive a data stream message from the outside world and other bots, you must check 2 things in your `runtime.json` file:

* First, make sure your `runtime.json` file includes trigger 256 in its `trigger` definition to activate the ability to receive data stream messages.
* Second, specify which data stream addresses your bot is interested in receiving:


    "dataStreams": [
      {
        "address": "datastream_demo_address"
      }
    ]
    
### UI-to-Bot Communications

In the same way that a bot can communicate data stream messages to other bots, it is possible to allow a user interface to communicate data stream messages directly into one or more bots.

See the following API to send a message from a script or UI. Again, the message will contain an `address` and a dictionary of key-value `content`.

https://iotapps.docs.apiary.io/#reference/data-stream/data-stream/send-message

Your bot must explicitly include trigger 256 in the `runtime.json` file to enable data stream messages, and specify which data stream addresses you'd like to listen for in the `dataStreams` list.

Lesson 6 here contains a Python script to inject a data stream message into your account, triggering the bot to react. After running the bot, execute these scripts:

    python send_datastream__push_notification.py -b <brand>
    
    python send_datastream__toggle_everything_on.py -b <brand>
    
    python send_datastream__toggle_everything_off.py -b <brand>
    
The `runtime.json` file opens up listeners for external data stream messages sent to the `send_push_notification` address and the `toggle_everything` address. If you are just communicating data stream messages internally, you do not need to open up ports in your `runtime.json` file.

## Best practices for reacting to data stream messages

One of the easiest ways to implement support for receiving specific data stream messages inside a microservice is to transform the data stream address directly into a method call. Here's how to do it.

First, implement these two lines of code inside your `datastream_updated(...)` event method:

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        if hasattr(self, address):
            getattr(self, address)(botengine, content)

This says, "If this class contains a method with the name of the data stream address we just received, execute the method and pass in the data stream content."

Next, implement a method with the name of the data stream address you want to react to and allow it to access the `botengine` and `content` arguments. If the `content` isn't going to be used, you can make it an optional argument of course.

    def datastream_demo_address(self, botengine, content=None):
        # React to the `datastream_demo_address` data stream message.
        

## Explore More

The `intelligence/lesson6/location_datastream_microservice.py` module will do two things:

* It will send out an internal data stream message telling everything to turn OFF when you go away, and turn ON when you come back home.
* It will react to the `send_push_notification` data stream message from an external script.

The `intelligence/lesson6/device_datastream_microservice.py` module attaches to lights and smart plugs. It will listen for the `toggle_everything` data stream address, and turn its parent device on or off when the message is received.

Run it in the cloud: 
    
    cp -r com.ppc.Lesson6-DataStreams com.yourname.Lesson6
    botengine --commit com.yourname.Lesson6 -b <brand> -u <user@email.com> -p <password>
    botengine --purchase com.yourname.Lesson6 -b <brand> -u <user@email.com> -p <password>
    
Watch it run locally:

    botengine --run com.yourname.Lesson6 -b <brand> -u <user@email.com> -p <password>
    
In a different Terminal window, run the `send_datastream__push_notification.py`, `send_datastream__toggle_everything_on.py`, and `send_datastream__toggle_everything_off.py` scripts to inject data stream messages into your account from a script. This script could just as well be a web UI, mobile app, or another cloud service that has your API key.

    python send_datastream__push_notification.py -u <user> -p <password> -b <brand>
    
Pause it when you're ready to move on:

    botengine --pause com.yourname.Lesson6 -b <brand> -u <user@email.com> -p <password>

