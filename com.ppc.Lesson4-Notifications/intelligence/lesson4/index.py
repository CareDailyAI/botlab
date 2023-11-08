# This is an extremely important file for creating your own bot microservices.
#
# It dynamically connects microservices (your new application-layer features and services) with the representative
# models (locations and devices) provided by com.ppc.Bot.
#
# Your microservices extend and implement the event-driven interfaces provided in the intelligence.py file,
# and can either add features to devices or services to locations.
#
# A "device microservice" adds a new feature to a single type of device. Each instance of that device will have
# its own set of device microservices that extend the behavior of the base device. To add a device microservice,
# follow the example below by simply specifying the device type, and what modules/classes it should include,
# inside the DEVICE_MICROSERVICES dictionary. Device microservices only pay attention to a single device, and
# will not trigger off of device events from other devices.  The device microservice's 'parent' is a Device object which
# will extend device.py.
#
# A "location microservice" adds new services across a location (your home). A location can contain multiple devices, so
# these types of microservices can effectively coordinate the activities between multiple devices. Again, to add
# a location microservice, follow the example below by adding a new module/class to the
# LOCATION_MICROSERVICES list. Location microservices trigger off of everything. The location microservice's 'parent' is
# a Location object from location.py.
#
# Note the recommended naming conventions.
#
# You can also place your microservices into their own package for easy deployment into other bots. Include
# an index.py file for each package of microservices, and upon generating the bot, the botengine will merge
# all index.py files and therefore automatically aggregate all available microservices into your final service.
#
#
# Deleting a microservice file from an actively deployed bot can cause existing bot instances to be unable to unpickle their memory,
# which means they lose all memory and start over again as if brand new. There is a process for properly removing a
# microservice without causing a bot to lose its memory:
#
#   1. Remove references to the microservice from memory. In the case of the microservices below, you could simply
#      delete the reference to the module from this file. DO NOT DELETE the original microservice file.
#      Commit, Publish. The microservice will be removed from memory on the next executions of active bots.
#
#   2. After every active bot has executed at least once, you can now safely delete the entire .py microservice module.
#      Again, commit and publish. The next time an active bot executes, because it has no memory of the module,
#      it will be able to unpickle its memory correctly. And now your project is free of that old microservice.
#
# Since this file is loaded as a JSON structure during the generation of the bot, remember to remove all
# dangling commas at the end of your JSON objects.

MICROSERVICES = {
    # Map specific device types to a list of microservices
    "DEVICE_MICROSERVICES": {
        # This is a dictionary structure, where the keys are device types, and the value is a
        # list of all the microservices to add to that device type.
        # Use "botengine --device_types" to see the available device types for your brand / server.

        # Entry Sensors
        10014: [
            {"module": "intelligence.lesson4.device_entrynotification_microservice", "class": "DeviceEntryNotificationMicroservice"}
            ],
        9114: [
            {"module": "intelligence.lesson1.device_entrynotification_microservice", "class": "DeviceEntryNotificationMicroservice"}
            ],

    },

    # Map locations to their microservices
    "LOCATION_MICROSERVICES": [
        # A location is like your home. This is a list of microservices to add to your location, which listen to
        # and coordinate devices across your entire location. Location microservices trigger off of all data inputs
        # from all devices.

        {"module": "intelligence.lesson4.location_notification_microservice", "class": "LocationNotificationMicroserivce"}
        ]
}
