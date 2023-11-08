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


        # I'm listing ALL device types on one of our servers here, so you can see each device type and how to add device microservices to each one.
        # For example, the first one for Smart Plugs says "For every device that shows up in this user's account that is
        # device type 10035 (which is a smart plug device), then create a new instance of the DeviceRealTimeDataMicroservice object
        # and attach it to this device."

        # Entry Sensors
        10014: [
            {"module": "intelligence.lesson1.device_entrysensor_microservice", "class": "DeviceEntrySensorMicroservice"}
            ],
        9114: [
            {"module": "intelligence.lesson1.device_entrysensor_microservice", "class": "DeviceEntrySensorMicroservice"}
            ],

        # Motion Sensor
        10038: [
            {"module": "intelligence.lesson1.device_motionsensor_microservice", "class": "DeviceMotionSensorMicroservice"}
            ],
        9138: [
            {"module": "intelligence.lesson1.device_motionsensor_microservice", "class": "DeviceMotionSensorMicroservice"}
            ],

        # Smart Plugs
        10035: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # iOS Cameras
        24: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Android Cameras
        23: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # ZigBee Thermostats
        10037: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Sensibo Sky A/C Infrared controller
        4220: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Honeywell Thermostats
        4230: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Ecobee Thermostats
        4240: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Touchpad
        25: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Netatmo Healthy Home Coach
        4200: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Netatmo Weather Station
        4201: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # GE In-Wall Switch
        9001: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Smart Bulb
        10036: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # TED Measuring Transmitting Unit - Load
        1000: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # TED Measuring Transmitting Unit - Solar
        1001: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # TED Measuring Transmitting Unit - Net
        1002: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # TED Measuring Transmitting Unit - Standalone
        1003: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # TED Gateway
        1004: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # M-Series Gateway
        31: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Squidlink Gateway
        36: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],
        37: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],
        38: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # ZigBee Gateway
        10031: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Smartenit Siren
        9002: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # People Power Siren
        9009: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Humidity, Temperature, and Light Sensor
        9004: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Water Sensors
        10017: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Touch Sensors
        10019: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Temperature Sensor
        10033: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Temperature & Humidity Sensor
        10034: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Virtual Light Bulb (for these lessons in case you don't have devices)
        10071: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],

        # Virtual Light Switch (for these lessons in case you don't have any devices)
        10072: [
            {"module": "intelligence.lesson1.device_realtimedata_microservice", "class": "DeviceRealTimeDataMicroservice"}
            ],
    },

    # Map locations to their microservices
    "LOCATION_MICROSERVICES": [
        # A location is like your home. This is a list of microservices to add to your location, which listen to
        # and coordinate devices across your entire location. Location microservices trigger off of all data inputs
        # from all devices.

        # The next line is an example of how to add a location-based microservice
        {"module": "intelligence.lesson1.location_realtimedata_microservice", "class": "LocationRealTimeDataMicroservice"}
        ]
}
