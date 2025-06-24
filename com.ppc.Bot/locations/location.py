"""
Created on June 28, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

import datetime
import importlib

import index
import properties
import pytz
import utilities.utilities as utilities
from users.user import User
from utilities.narrative import (
    Narrative,
    NARRATIVE_TYPE_OBSERVATION,
)


class Location:
    """
    Provide tools and information to manage the Location.
    """

    # Security States
    SECURITY_STATE_DISARMED = 0
    SECURITY_STATE_EXIT_DELAY_FULL = 1
    SECURITY_STATE_EXIT_DELAY_PERIMETER = 2
    SECURITY_STATE_ARMED_FULLY = 3
    SECURITY_STATE_ARMED_PERIMETER = 4
    SECURITY_STATE_ENTRY_DELAY = 5
    SECURITY_STATE_ALARMING_RECENT_CLOSING = 6
    SECURITY_STATE_ALARMING = 7
    SECURITY_STATE_TEST_MODE = 8

    def __init__(self, botengine, location_id):
        """
        Constructor
        :param botengine: BotEngine environment
        :param location_id: Location ID
        """
        self.location_id = int(location_id)

        # Born on date
        self.born_on = botengine.get_timestamp()

        # Data filtration modules to optionally correct data before entering into the upper layers of our stack
        self.filters = {}

        # Representative model of all device objects. { 'device_id': <device_object> }
        self.devices = {}

        # All Location Intelligence modules
        self.intelligence_modules = {}

        # Mode of this location (i.e. "HOME", "AWAY", etc.). This is the mode of the security system.
        self.mode = botengine.get_mode(self.location_id)

        # Try to update our current mode
        self.update_mode(botengine)

        # Conversational UI
        self.conversational_ui = None

        # Security state
        self.security_state = Location.SECURITY_STATE_DISARMED

        # Occupancy status as determined by AI occupancy detection algorithms.
        self.occupancy_status = ""

        # Reason for the current occupancy status. For example: "ML.MOTION" or "USER".
        self.occupancy_reason = ""

        # Last time our location properties were sync'd
        self.properties_timestamp_ms = 0

        # Latest copy of our location properties
        self.location_properties = {}

        # Narratives we're tracking from various microservices for your location.  { "unique_id" : narrative_object }.
        self.location_narratives = {}

        # Narratives we're tracking from various microservices for your organization. { "unique_id" : narrative_object }.
        self.org_narratives = {}

        # Latitude
        self.latitude = None

        # Longitude
        self.longitude = None

        # Daylight setting, populated by the 'daylight' microservice package
        self.is_daylight = None

        # Language
        self.language = botengine.get_language()

        # Users in location, {"userid": user_object, ...}
        self.users = {}
        self.synchronize_users(botengine)

        # Activate trends for locations without devices
        # TODO: Deprecate.  Individual services should use the trends signal as needed,
        # and should have service specific logic to prevent capturing trends.
        self.deviceless_trends = False

        # TODO: Discuss removing this.  It's a temporary fix and will be resolved with the inclusion of EngageKit.
        self.skip_handled_message = False

    def new_version(self, botengine):
        """
        New bot version - runs one time when we are executing a new bot version

        The new_version() event is distributed throughout our environment in the following order:
            * Device objects
            * Filter objects
            * Microservices

        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">new_version() New bot version detected"
        )

        # Added October 21, 2021
        if not hasattr(self, "filters"):
            self.filters = {}

        # Added July 2, 2021
        if not hasattr(self, "users"):
            self.users = {}
            self.synchronize_users(botengine)

        # Added February 2, 2022
        if not hasattr(self, "language"):
            self.language = botengine.get_language()

        # Added January 13th, 2023
        if not hasattr(self, "deviceless_trends"):
            self.deviceless_trends = False

        if not hasattr(self, "skip_handled_message"):
            self.skip_handled_message = False

        # Synchronize all microservices
        self._sync_modules(
            botengine,
            self.intelligence_modules,
            index.MICROSERVICES.get("LOCATION_MICROSERVICES", []),
        )

        # Synchronize all data filters
        self._sync_modules(
            botengine,
            self.filters,
            index.MICROSERVICES.get("DATA_FILTER_MICROSERVICES", []),
        )

        # Tell all device objects and their device microservices we're running a new version
        for device_object in self.devices.values():
            try:
                device_object.new_version(botengine)
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|new_version() - Error delivering new_version to device object (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

        # Tell all filters we're running a new version
        for filter_object in self.sorted_filters(botengine).values():
            try:
                filter_object.new_version(botengine)
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|new_version() - Error delivering new_version to data filter (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

        # Tell all microservices we're running a new version
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.new_version(botengine)
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|new_version() - Error delivering new_version to device microservice (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<new_version()")

    def initialize(self, botengine):
        """
        Initialize - runs on every execution of the bot
        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">initialize()")

        # Synchronize all microservices
        self._sync_modules(
            botengine,
            self.intelligence_modules,
            index.MICROSERVICES.get("LOCATION_MICROSERVICES", []),
        )

        # Synchronize all data filters
        self._sync_modules(
            botengine,
            self.filters,
            index.MICROSERVICES.get("DATA_FILTER_MICROSERVICES", []),
        )

        for filter_object in self.sorted_filters(botengine).values():
            try:
                filter_object.initialize(botengine)
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "location.py - Error initializing data filter (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

        for device_object in self.devices.values():
            try:
                device_object.initialize(botengine)
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|new_version() - Error initializing device microservice (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

        for user_object in self.users.values():
            try:
                user_object.initialize(botengine)
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|new_version() - Error initializing user (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                # Reset location microservice statistics
                microservice_object.reset_statistics(botengine)

                import time

                t = time.time()
                microservice_object.initialize(botengine)
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )

            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|new_version() - Error initializing microservice (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

        # Check if our language has changed
        if self.language != botengine.get_language():
            self.language = botengine.get_language()
            self.language_updated(botengine, self.language)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<initialize()")

    def add_device(self, botengine, device_object):
        """
        Start tracking a new device here.
        Perform any bounds checking, for example with multiple gateways at one location.
        :param device_object: Device object to track
        """
        self.devices[device_object.device_id] = device_object

        if hasattr(device_object, "intelligence_modules"):
            for intelligence_id in device_object.intelligence_modules:
                try:
                    device_object.intelligence_modules[intelligence_id].device_added(
                        botengine, device_object
                    )
                except Exception as e:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                        "|add_device() - Error delivering add_device to device microservice (continuing execution): "
                        + str(e)
                    )
                    import traceback

                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                        traceback.format_exc()
                    )

        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.device_added(botengine, device_object)
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|add_device() - Error delivering add_device to location microservice (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )

        for filter_object in self.sorted_filters(botengine).values():
            try:
                filter_object.device_added(botengine, device_object)
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|add_device() - Error delivering add_device to filter (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<add_device()")

    def delete_device(self, botengine, device_id):
        """
        Delete the given device ID
        :param device_id: Device ID to delete
        """
        if device_id in self.devices:
            device_object = self.devices[device_id]

            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    try:
                        device_object.intelligence_modules[intelligence_id].destroy(
                            botengine
                        )
                    except Exception as e:
                        botengine.get_logger(
                            f"{__name__}.{__class__.__name__}"
                        ).warning(
                            "|delete_device() Exception destroying device intelligence module. device_id={} device_type={} description={} intelligence_id={} exception={}".format(
                                device_object.device_id,
                                device_object.device_type,
                                device_object.description,
                                intelligence_id,
                                e,
                            )
                        )

            try:
                device_object.destroy(botengine)
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|delete_device() Exception destroying device. exception={}".format(
                        e
                    )
                )

            del self.devices[device_id]

            for microservice_object in self.sorted_intelligence_modules(
                botengine
            ).values():
                try:
                    import time

                    t = time.time()
                    microservice_object.device_deleted(botengine, device_object)
                    microservice_object.track_statistics(
                        botengine, (time.time() - t) * 1000
                    )
                except Exception as e:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                        "|delete_device() - Error delivering delete_device to location microservice (continuing execution): "
                        + str(e)
                    )
                    import traceback

                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                        traceback.format_exc()
                    )

            for filter_object in self.sorted_filters(botengine).values():
                try:
                    filter_object.device_deleted(botengine, device_object)
                except Exception as e:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                        "|delete_device() - Error delivering delete_device to filter (continuing execution): "
                        + str(e)
                    )
                    import traceback

                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                        traceback.format_exc()
                    )

    def mode_updated(self, botengine, mode):
        """
        Update this location's mode
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">mode_updated() mode={}".format(mode)
        )
        self.mode = mode.upper()

        # Location microservices
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.mode_updated(botengine, mode)
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|mode_updated() - Error delivering mode_updated to location microservice (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

        # Device microservices
        for device_object in self.devices.values():
            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    try:
                        device_object.intelligence_modules[
                            intelligence_id
                        ].mode_updated(botengine, mode)
                    except Exception as e:
                        import traceback

                        botengine.get_logger(
                            f"{__name__}.{__class__.__name__}"
                        ).warning(
                            "|mode_updated() - Error delivering mode_updated to device microservice (continuing execution). exception={} trace={}".format(
                                e, traceback.format_exc()
                            )
                        )
                        if botengine.playback:
                            # Give us a chance to see the error as we playback data in fast-forward mode
                            import time

                            time.sleep(2)

        # Filters
        for filter_object in self.sorted_filters(botengine).values():
            try:
                filter_object.mode_updated(botengine, mode)
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|mode_updated() - Error delivering mode_updated to filter (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

    def filter_measurements(self, botengine, device_object, measurements):
        """
        Optionally filter device measurement data before it reaches the upper layers of the stack.
        :param botengine: BotEngine environment
        :param device_object: Device object pending update
        :param measurements: Measurements dictionary we're about to trigger off of, which is modified in place.
        :return: Nothing, because the measurements dictionary should be directly modified to correct the data.
        """
        for filter_object in self.sorted_filters(botengine).values():
            try:
                filter_object.filter_measurements(
                    botengine, device_object, measurements
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|filter_measurements() - Error delivering filter_measurements to filter (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

    def device_measurements_updated(self, botengine, device_object):
        """
        Evaluate a device that was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.device_measurements_updated(
                    botengine, device_object
                )
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|device_measurements_updated() - Error delivering device_measurements_updated to location microservice (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.device_metadata_updated(botengine, device_object)
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|device_metadata_updated() - Error delivering device_metadata_updated to location microservice (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

    def device_alert(self, botengine, device_object, alert_type, alert_params):
        """
        Device sent an alert
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alerts_list: List of alerts
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">device_alert() device_id={} alert_type={}".format(
                device_object.device_id, alert_type
            )
        )
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.device_alert(
                    botengine, device_object, alert_type, alert_params
                )
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|device_alert() - Error delivering device_alert to location microservice (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

    def question_answered(self, botengine, question):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question: Question object
        """
        # Microservices
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.question_answered(botengine, question)
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|question_answered() - Error delivering question_answered to location microservice (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )

        # Device microservices
        for device_object in self.devices.values():
            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    try:
                        device_object.intelligence_modules[
                            intelligence_id
                        ].question_answered(botengine, question)
                    except Exception as e:
                        import traceback

                        botengine.get_logger(
                            f"{__name__}.{__class__.__name__}"
                        ).warning(
                            "|question_answered() - Error delivering question_answered to device microservice (continuing execution). exception={} trace={}".format(
                                e, traceback.format_exc()
                            )
                        )

        # Filters
        for filter_object in self.sorted_filters(botengine).values():
            try:
                filter_object.question_answered(botengine, question)
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "location.py - Error delivering question_answered to filter (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )

    def messages_updated(self, botengine, messages):
        """
        List of Messages were updated
        :param botengine: BotEngine environment
        :param messages: Message objects
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">messages_updated()"
        )
        # Microservices
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|messages_updated() - Delivering messages_updated to location microservice: {}".format(
                    microservice_object
                )
            )
            if not hasattr(microservice_object, "messages_updated"):
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    "|messages_updated() - No messages_updated() method in location microservice: {}".format(
                        microservice_object
                    )
                )
                continue
            try:
                import time

                t = time.time()
                microservice_object.messages_updated(botengine, messages)
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                import traceback

                botengine.get_logger().warning(
                    "|messages_updated() - Error delivering messages_updated to location microservice (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )

        # Device microservices
        for device_object in self.devices.values():
            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    microservice_object = device_object.intelligence_modules[
                        intelligence_id
                    ]
                    if not hasattr(microservice_object, "messages_updated"):
                        continue
                    try:
                        microservice_object.messages_updated(botengine, messages)
                    except Exception as e:
                        import traceback

                        botengine.get_logger().warning(
                            "|messages_updated() - Error delivering messages_updated to device microservice (continuing execution). exception={} trace={}".format(
                                e, traceback.format_exc()
                            )
                        )

        # Filters
        for filter_object in self.filters.values():
            if not hasattr(filter_object, "messages_updated"):
                continue
            try:
                filter_object.messages_updated(botengine, messages)
            except Exception as e:
                import traceback

                botengine.get_logger().warning(
                    "|messages_updated() - Error delivering messages_updated to filter (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">messages_updated()"
        )

    def datastream_updated(self, botengine, address, content, raise_exceptions=False):
        """
        Data Stream Updated
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Data Stream content
        """
        # Top priority - Location microservices
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">datastream_updated()"
        )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "|datastream_updated() raise_exceptions={}".format(raise_exceptions)
        )
        # Raise exceptions if requested
        exceptions = []  # (Exception, traceback) tuples
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            if not hasattr(microservice_object, "datastream_updated"):
                continue
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|datastream_updated() - Delivering datastream message '{}' to location microservice: {}".format(
                    address, microservice_object
                )
            )
            try:
                import time

                t = time.time()
                microservice_object.datastream_updated(
                    botengine,
                    address,
                    content.copy() if isinstance(content, dict) else content,
                )
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|datastream_updated() - Error delivering datastream message '{}' to location microservice (continuing execution). exception={} trace={}".format(
                        address, e, traceback.format_exc()
                    )
                )
                exceptions.append((e, traceback.format_exc()))
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

        # Second priority - Device microservices
        for device_object in self.devices.values():
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|datastream_updated() - Delivering datastream message '{}' to device microservice: {}".format(
                    address, device_object
                )
            )
            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                        "|datastream_updated() - Delivering datastream message '{}' to device microservice: {}".format(
                            address, device_object.intelligence_modules[intelligence_id]
                        )
                    )
                    try:
                        device_object.intelligence_modules[
                            intelligence_id
                        ].datastream_updated(
                            botengine,
                            address,
                            content.copy() if isinstance(content, dict) else content,
                        )
                    except Exception as e:
                        import traceback

                        botengine.get_logger(
                            f"{__name__}.{__class__.__name__}"
                        ).warning(
                            "|datastream_updated() - Error delivering datastream message '{}' to device microservice (continuing execution). exception={} trace={}".format(
                                address, e, traceback.format_exc()
                            )
                        )
                        exceptions.append((e, traceback.format_exc()))
                        if botengine.playback:
                            # Give us a chance to see the error as we playback data in fast-forward mode
                            import time

                            time.sleep(2)

        # Lowest priority - filters
        for filter_object in self.sorted_filters(botengine).values():
            try:
                filter_object.datastream_updated(
                    botengine,
                    address,
                    content.copy() if isinstance(content, dict) else content,
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|datastream_updated() - Error delivering datastream message '{}' to filter (continuing execution). exception={} trace={}".format(
                        address, e, traceback.format_exc()
                    )
                )
                exceptions.append((e, traceback.format_exc()))
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)
        if raise_exceptions and len(exceptions) > 0:
            raise Exception(
                "Error delivering datastream message to microservices", exceptions
            )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<datastream_updated()"
        )

    def schedule_fired(self, botengine, schedule_id):
        """
        Schedule Fired.
        It is this location's responsibility to notify all sub-intelligence modules, including both device and location intelligence modules
        :param botengine: BotEngine environment
        """
        if schedule_id == "MIDNIGHT":
            self.synchronize_users(botengine)

        # Filters
        for filter_object in self.sorted_filters(botengine).values():
            try:
                filter_object.schedule_fired(botengine, schedule_id)
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|schedule_fired() - Error delivering schedule_fired to filter (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

        # Location intelligence modules
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.schedule_fired(botengine, schedule_id)
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|schedule_fired() - Error delivering schedule_fired to location microservice (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )
                if botengine.playback:
                    # Give us a chance to see the error as we playback data in fast-forward mode
                    import time

                    time.sleep(2)

        # Device intelligence modules
        for device_object in self.devices.values():
            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    try:
                        device_object.intelligence_modules[
                            intelligence_id
                        ].schedule_fired(botengine, schedule_id)
                    except Exception as e:
                        import traceback

                        botengine.get_logger(
                            f"{__name__}.{__class__.__name__}"
                        ).warning(
                            "|schedule_fired() - Error delivering schedule_fired to device microservice (continuing execution). exception={} trace={}".format(
                                e, traceback.format_exc()
                            )
                        )
                        if botengine.playback:
                            # Give us a chance to see the error as we playback data in fast-forward mode
                            import time

                            time.sleep(2)

    def timer_fired(self, botengine, microservice_id, argument):
        """
        Timer fired
        :param botengine: BotEngine environment
        :param microservice_id: Microservice to trigger
        :param argument: Optional argument
        """
        # Search for and trigger location intelligence instances
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            if microservice_id == microservice_object.intelligence_id:
                try:
                    import time

                    t = time.time()
                    microservice_object.timer_fired(botengine, argument)
                    microservice_object.track_statistics(
                        botengine, (time.time() - t) * 1000
                    )
                except Exception as e:
                    import traceback

                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                        "|timer_fired() - Error triggering timer_fired in location microservice (continuing execution). exception={} trace={}".format(
                            e, traceback.format_exc()
                        )
                    )
                    if botengine.playback:
                        # Give us a chance to see the error as we playback data in fast-forward mode
                        import time

                        time.sleep(2)
                return

        # Search for and trigger filters
        for filter_object in self.sorted_filters(botengine).values():
            if microservice_id == filter_object.filter_id:
                try:
                    filter_object.timer_fired(botengine, argument)
                except Exception as e:
                    import traceback

                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                        "|timer_fired() - Error triggering timer_fired in filter (continuing execution). exception={} trace={}".format(
                            e, traceback.format_exc()
                        )
                    )
                    if botengine.playback:
                        # Give us a chance to see the error as we playback data in fast-forward mode
                        import time

                        time.sleep(2)
                return

    def file_uploaded(
        self,
        botengine,
        device_object,
        file_id,
        filesize_bytes,
        content_type,
        file_extension,
    ):
        """
        A device file has been uploaded
        :param botengine: BotEngine environment
        :param device_object: Device object that uploaded the file
        :param file_id: File ID to reference this file at the server
        :param filesize_bytes: The file size in bytes
        :param content_type: The content type, for example 'video/mp4'
        :param file_extension: The file extension, for example 'mp4'
        """
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.file_uploaded(
                    botengine,
                    device_object,
                    file_id,
                    filesize_bytes,
                    content_type,
                    file_extension,
                )
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|file_uploaded() - Error delivering file_uploaded to location microservice (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )

    def user_role_updated(
        self,
        botengine,
        user_id,
        role,
        category,
        location_access,
        previous_category,
        previous_location_access,
    ):
        """
        A user changed roles
        :param botengine: BotEngine environment
        :param location_id: Location ID
        :param user_id: User ID that changed roles
        :param role: Application-layer agreed upon role integer which may auto-configure location_access and alert category
        :param category: User's current alert/communications category (1=resident; 2=supporter)
        :param location_access: User's access to the location and devices. (0=None; 10=read location/device data; 20=control devices and modes; 30=update location info and manage devices)
        :param previous_category: User's previous category, if any
        :param previous_location_access: User's previous access to the location, if any
        """
        self.synchronize_users(botengine)

        # User objects
        if user_id in self.users:
            try:
                self.users[user_id].user_role_updated(
                    botengine,
                    user_id,
                    role,
                    category,
                    location_access,
                    previous_category,
                    previous_location_access,
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|user_role_updated() - Error delivering user_role_updated to user object (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )

        # Location intelligence modules
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.user_role_updated(
                    botengine,
                    user_id,
                    role,
                    category,
                    location_access,
                    previous_category,
                    previous_location_access,
                )
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "location.py - Error delivering user_role_updated to location microservice (continuing execution): "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )

        # Device intelligence modules
        for device_object in self.devices.values():
            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    try:
                        device_object.intelligence_modules[
                            intelligence_id
                        ].user_role_updated(
                            botengine,
                            user_id,
                            role,
                            category,
                            location_access,
                            previous_category,
                            previous_location_access,
                        )
                    except Exception as e:
                        import traceback

                        botengine.get_logger(
                            f"{__name__}.{__class__.__name__}"
                        ).warning(
                            "|user_role_updated() - Error delivering user_role_updated to device microservice (continuing execution). exception={} trace={}".format(
                                e, traceback.format_exc()
                            )
                        )

    def call_center_updated(self, botengine, user_id, status):
        """
        Emergency call center status has changed
        :param botengine: BotEngine environment
        :param user_id: User ID that made the change
        :param status: Current call center status
        """
        # Location intelligence modules
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.call_center_updated(botengine, user_id, status)
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|call_center_updated() - Error delivering call_center_updated to location microservice (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )

        # Device intelligence modules
        for device_object in self.devices.values():
            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    try:
                        device_object.intelligence_modules[
                            intelligence_id
                        ].call_center_updated(botengine, user_id, status)
                    except Exception as e:
                        import traceback

                        botengine.get_logger(
                            f"{__name__}.{__class__.__name__}"
                        ).warning(
                            "|call_center_updated() - Error delivering call_center_updated to device microservice (continuing execution). exception={} trace={}".format(
                                e, traceback.format_exc()
                            )
                        )

    def data_request_ready(self, botengine, reference, device_csv_dict):
        """
        A botengine.request_data() asynchronous request for CSV data is ready.
        :param botengine: BotEngine environment
        :param reference: Optional reference passed into botengine.request_data(..)
        :param device_csv_dict: { 'device_id': 'csv data string' }
        """
        # Filters to correct data before passing to other microservices
        # Edit the device_csv_dict in place inside the filter
        for filter_object in self.sorted_filters(botengine).values():
            try:
                filter_object.data_request_ready(botengine, reference, device_csv_dict)
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|data_request_ready() - Error delivering data_request_ready to filter (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )

        # Location microservices
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.data_request_ready(
                    botengine, reference, device_csv_dict
                )
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|data_request_ready() - Error delivering data_request_ready to location microservice (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )

        # Device microservices
        for device_object in self.devices.values():
            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    try:
                        device_object.intelligence_modules[
                            intelligence_id
                        ].data_request_ready(botengine, reference, device_csv_dict)
                    except Exception as e:
                        botengine.get_logger(
                            f"{__name__}.{__class__.__name__}"
                        ).warning(
                            "location.py - Error delivering data_request_ready to device microservice : "
                            + str(e)
                        )
                        import traceback

                        botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                            traceback.format_exc()
                        )

    def update_coordinates(self, botengine, latitude, longitude):
        """
        Attempt to update coordinates
        :param botengine: BotEngine environment
        :param latitude: Current latitude
        :param longitude: Current longitude
        """
        # Added June 26, 2019
        if not hasattr(self, "latitude"):
            self.latitude = None
            self.longitude = None

        if self.latitude != latitude or self.longitude != longitude:
            self.latitude = latitude
            self.longitude = longitude

            for microservice_object in self.sorted_intelligence_modules(
                botengine
            ).values():
                try:
                    import time

                    t = time.time()
                    microservice_object.coordinates_updated(
                        botengine, self.latitude, self.longitude
                    )
                    microservice_object.track_statistics(
                        botengine, (time.time() - t) * 1000
                    )
                except Exception as e:
                    import traceback

                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                        "|update_coordinates() - Error delivering coordinates_updated to location microservice (continuing execution). exception={} trace={}".format(
                            e, traceback.format_exc()
                        )
                    )

    def language_updated(self, botengine, language):
        """
        Location's preferred language has been updated
        :param botengine: BotEngine environment
        :param language: New language identifier, i.e. 'en'
        """
        for filter_object in self.sorted_filters(botengine).values():
            try:
                filter_object.language_updated(botengine, language)
            except Exception as e:
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "|language_updated() - Error delivering language_updated to filter (continuing execution). exception={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )

        # Location microservices
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            try:
                import time

                t = time.time()
                microservice_object.language_updated(botengine, language)
                microservice_object.track_statistics(
                    botengine, (time.time() - t) * 1000
                )
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    "location.py - Error delivering language_updated to location microservice : "
                    + str(e)
                )
                import traceback

                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                    traceback.format_exc()
                )

        # Device microservices
        for device_object in self.devices.values():
            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    try:
                        device_object.intelligence_modules[
                            intelligence_id
                        ].language_updated(botengine, language)
                    except Exception as e:
                        import traceback

                        botengine.get_logger(
                            f"{__name__}.{__class__.__name__}"
                        ).warning(
                            "|language_updated() - Error delivering language_updated to device microservice (continuing execution). exception={} trace={}".format(
                                e, traceback.format_exc()
                            )
                        )

    def get_microservice_by_id(self, botengine, microservice_id):
        """
        Get a microservice ("intelligence module") by its id ("intelligence_id").
        Sorry we named them 'intelligence modules' at first when they were really microservices.

        :param microservice_id: Microservice ID
        :return: Microservice object, or None if it doesn't exist.
        """
        for microservice_object in self.sorted_intelligence_modules(botengine).values():
            if microservice_object.intelligence_id == microservice_id:
                return microservice_object

        for device_object in self.devices.values():
            for microservice in device_object.intelligence_modules:
                if (
                    device_object.intelligence_modules[microservice].intelligence_id
                    == microservice_id
                ):
                    return device_object.intelligence_modules[microservice]

        return None

    # ===========================================================================
    # Location User
    # ===========================================================================
    def synchronize_users(self, botengine):
        """
        Synchronize our set of users
        :param botengine: Botengine environment
        """
        users = botengine.get_location_users()
        user_id_list = []
        for user_json in users:
            user_id = user_json["id"]
            user_id_list.append(user_id)
            first_name = ""
            last_name = ""
            location_access = None
            alert_category = None
            role = None
            language = "en"

            if "firstName" in user_json:
                first_name = user_json["firstName"]

            if "lastName" in user_json:
                last_name = user_json["lastName"]

            if "locationAccess" in user_json:
                location_access = user_json["locationAccess"]

            if "category" in user_json:
                alert_category = user_json["category"]

            if "role" in user_json:
                role = user_json["role"]

            if user_id not in self.users:
                self.users[user_id] = User(botengine, user_json["id"])

            # Synchronize
            self.users[user_id].first_name = first_name
            self.users[user_id].last_name = last_name
            self.users[user_id].location_access = location_access
            self.users[user_id].alert_category = alert_category
            self.users[user_id].role = role
            self.users[user_id].language = language
            self.users[user_id].location_object = self

        # Delete users that no longer exist
        for user_id in list(self.users.keys()):
            if user_id not in user_id_list:
                self.users[user_id].destroy(botengine)
                del self.users[user_id]

    def get_user(self, botengine, user_id):
        """
        Get user object by ID
        :param botengine: BotEngine environment
        :param user_id: User ID
        :return: User object, or None if it doesn't exist
        """
        if user_id in self.users:
            return self.users[user_id]

        # Resynchronize and try one more time...
        self.synchronize_users(botengine)

        if user_id in self.users:
            return self.users[user_id]

        return None

    def get_users(
        self,
        botengine,
        device_object=None,
        location_access=None,
        alert_category=None,
        role=None,
    ):
        """
        Get all users in this location that match the criteria.
        Prioritize return elements by (1) device user (2) role, (3) alert_category, (4) location_access.
        :param botengine: BotEngine environment
        :param location_access: Optional location access level
        :param alert_category: Optional alert category
        :param role: Optional role
        :return: List of User objects
        """
        self.synchronize_users(botengine)
        users = []
        # Device
        if device_object is not None:
            for user_id in self.users:
                if device_object.user_id == user_id:
                    users.append(self.users[user_id])
        # Role
        for user_id in self.users:
            if role is not None and self.users[user_id].role == role:
                users.append(self.users[user_id])
        # Alert category
        for user_id in self.users:
            if (
                alert_category is not None
                and self.users[user_id].alert_category == alert_category
            ):
                if self.users[user_id] not in users:
                    users.append(self.users[user_id])
        # Location access
        for user_id in self.users:
            if (
                location_access is not None
                and self.users[user_id].location_access == location_access
            ):
                if self.users[user_id] not in users:
                    users.append(self.users[user_id])
        # No criteria
        if role is None and alert_category is None and location_access is None:
            users = list(self.users.values())

        return users

    def get_personal_callback_number(self, botengine, user_id):
        """
        Get the personal callback number for a user by extracting a
        phone number from existing devices that this user is assigned to.

        :param botengine: BotEngine environment
        :param user_id: User ID
        :return: Personal callback number
        """
        self.synchronize_users(botengine)
        if user_id in self.users:
            for device_object in self.devices.values():
                if device_object.user_id == user_id:
                    if hasattr(device_object, "get_phone"):
                        return device_object.get_phone(botengine)
        return None

    # ===========================================================================
    # General location information
    # ===========================================================================
    def get_location_name(self, botengine):
        """
        Get the nickname of this location
        :param botengine: BotEngine environment
        :return: Nickname
        """
        return botengine.get_location_name()

    # ===========================================================================
    # Mode
    # ===========================================================================
    def set_mode(self, botengine, mode, comment=None):
        """
        Set the mode for this location
        :param botengine: BotEngine environment
        :param comment: Optional comment about why the mode was set
        """
        botengine.set_mode(self.location_id, mode, comment)
        # Allow the bot to trigger again and set the mode from a single unified action.

    def get_user_facing_mode(self, botengine, mode):
        """
        The modes recognized by most services include "HOME", "AWAY", "STAY", "TEST".

        The user-facing representation of these modes may be different. For example,
        some brands prefer the user to see "OFF" instead of "HOME".

        This method will transform a mode name into the user-facing representation
        for interaction with the user. Use the domain.py file at the root of your bot
        to specify this mapping.

        :param botengine: BotEngine environment
        :param mode: Internal mode name, including "HOME", "AWAY", "STAY", "TEST".
        :return: User-facing text representation of that mode
        """
        try:
            return properties.get_property(botengine, "USER_FACING_MODES", False)[mode]
        except Exception:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "|get_user_facing_mode() Mode '{}' not found in domain.USER_FACING_MODES".format(
                    mode
                )
            )

        return mode

    # ===========================================================================
    # Location Properties
    # ===========================================================================
    def set_location_property(
        self, botengine, property_name, property_value, track=True
    ):
        """
        Set a location property
        :param botengine: BotEngine environment
        :param property_name: Property name
        :param property_value: Property value
        :param track: True to automatically copy these properties to the 3rd party analytics (default is True
        """
        self._sync_location_properties(botengine)
        self.location_properties[property_name] = property_value
        botengine.set_state("location_properties", self.location_properties)

        if track:
            import signals.analytics as analytics

            analytics.people_set(botengine, self, {property_name: property_value})

    def update_location_properties(self, botengine, properties_dict, track=True):
        """
        Update multiple location properties simultaneously from a dictionary.
        If the properties don't exist yet, they will be added.

        :param botengine: BotEngine environment
        :param properties_dict: Properties dictionary with key/values to update
        :param track: True to automatically copy these properties to the 3rd party analytics (default is True)
        """
        self._sync_location_properties(botengine)
        self.location_properties.update(properties_dict)
        botengine.set_state("location_properties", self.location_properties)

        if track:
            import signals.analytics as analytics

            analytics.people_set(botengine, self, properties_dict)

    def increment_location_property(
        self, botengine, property_name, increment_amount=1, track=True
    ):
        """
        Increment a location property integer by the amount given.

        If the property doesn't exist, it will be initialized to 0 and then incremented by the amount given.
        An existing property must be numeric to increment.

        :param botengine: BotEngine environment
        :param property_name: Property name to increment
        :param increment_amount: Incremental amount to add (default is 1)
        :param track: True to automatically copy these properties to the 3rd party analytics (default is True)
        """
        self._sync_location_properties(botengine)
        if property_name not in self.location_properties:
            self.location_properties[property_name] = 0

        self.location_properties[property_name] += increment_amount
        botengine.set_state("location_properties", self.location_properties)

        import signals.analytics as analytics

        analytics.people_increment(botengine, self, {property_name: increment_amount})

    def get_location_property(self, botengine, property_name):
        """
        Retrieve a location property
        :param botengine: BotEngine environment
        :param property_name: Property name to retrieve
        :return: The property value, or None if it doesn't exist
        """
        self._sync_location_properties(botengine)
        if property_name in self.location_properties:
            return self.location_properties[property_name]
        return None

    def get_location_properties(self, botengine):
        """
        Get all location properties
        :param botengine: BotEngine environment
        :return: Dictionary of all location properties
        """
        self._sync_location_properties(botengine)
        return self.location_properties

    def delete_location_property(self, botengine, property_name):
        """
        Delete a location property
        :param botengine: BotEngine environment
        :param property_name: Property name to delete
        """
        self._sync_location_properties(botengine)
        if property_name in self.location_properties:
            del self.location_properties[property_name]
            botengine.set_state("location_properties", self.location_properties)

    def delete_location_property_separately(
        self,
        botengine,
        additional_property_name,
        timeseries_property=False,
        overwrite=True,
    ):
        """
        Deletes a large location property. The name is referenced by our 'location_properties' but stored separately
        and referenced in the location_properties as 'additional_properties' or 'timerseries_properties' .

        This method will remove all remnants of the state from the reference in location_properties
        and from the address where it gets stored separately. You must specify if it is a timeseries property or not.

        :param botengine: BotEngine environment
        :param additional_property_name: Property name to delete separately and dereference from location_properties and delete from address where it is stored
        :param overwrite: True to overwrite all existing content (default), False to update existing server content only with the top-level dictionary keys that are presented leaving others untouched
        :param timeseries_property: True if this is a timeseries_property, Default is False and will remove property from the reference 'additional_properties' in location_properties
        """
        if not timeseries_property:
            additional_properties = self.get_location_property(
                botengine, "additional_properties"
            )

            if (
                additional_properties is not None
                and additional_property_name in additional_properties
            ):
                additional_properties.remove(additional_property_name)
                self.set_location_property(
                    botengine, "additional_properties", additional_properties
                )

        else:
            timeseries_properties = self.get_location_property(
                botengine, "timeseries_properties"
            )

            if (
                timeseries_properties is not None
                and additional_property_name in timeseries_properties
            ):
                del timeseries_properties[additional_property_name]
                self.set_location_property(
                    botengine, "timeseries_properties", timeseries_properties
                )

        botengine.delete_state(
            additional_property_name,
            timeseries_property=timeseries_property,
            overwrite=overwrite,
        )

    def set_location_property_separately(
        self,
        botengine,
        additional_property_name,
        additional_property_json,
        overwrite=False,
        timestamp_ms=None,
        fields_updated=[],
        fields_deleted=[],
        track=True,
    ):
        """
        Set a large location property. The name is referenced by our 'location_properties' but stored separately
        and referenced in the location_properties as 'additional_properties'.

        You must use botengine.get_state(..) when retrieving the content of this additional property,
        since it is referenced by the 'location_property' but stored separately.

        :param botengine: BotEngine environment
        :param additional_property_name: Property name to store separately and reference in our location_properties
        :param additional_property_json: Property JSON value
        :param overwrite: True to overwrite all existing content, False to update existing server content only with the top-level dictionary keys that are presented leaving others untouched (default)
        :param timestamp_ms: Timestamp for time-series
        :param fields_updated: Optional. To optimize integrations with 3rd party clouds, this is a list of the fields that were added/updated. Always used in conjunction with overwrite=True and non-time-series states.
        :param fields_deleted: Optional. List of fields that were removed. Always used in conjunction with overwrite=True and non-time-series states.
        :param track: True to automatically copy these properties to the 3rd party analytics (default is True)
        """
        if timestamp_ms is None:
            additional_properties = self.get_location_property(
                botengine, "additional_properties"
            )
            if additional_properties is None:
                additional_properties = []

            if additional_property_name not in additional_properties:
                additional_properties.append(additional_property_name)
                self.set_location_property(
                    botengine, "additional_properties", additional_properties, track=track
                )

        else:
            timeseries_properties = self.get_location_property(
                botengine, "timeseries_properties"
            )
            if timeseries_properties is None:
                timeseries_properties = {}

            try:
                if timeseries_properties[additional_property_name] != timestamp_ms:
                    raise ValueError
            except Exception:
                timeseries_properties[additional_property_name] = timestamp_ms
                self.set_location_property(
                    botengine, "timeseries_properties", timeseries_properties, track=track
                )

        botengine.set_state(
            additional_property_name,
            additional_property_json,
            overwrite=overwrite,
            timestamp_ms=timestamp_ms,
            fields_updated=fields_updated,
            fields_deleted=fields_deleted,
        )

    def _sync_location_properties(self, botengine):
        """
        Internal method to synchornize our local copy of location properties with the server
        :param botengine: BotEngine environment
        """
        if self.properties_timestamp_ms != botengine.get_timestamp():
            location_properties = botengine.get_state("location_properties")
            if location_properties is not None:
                self.location_properties = location_properties

            else:
                self.location_properties = {}

            self.properties_timestamp_ms = botengine.get_timestamp()

    # ===========================================================================
    # Data Stream Message delivery
    # ===========================================================================
    def distribute_datastream_message(
        self,
        botengine,
        address,
        content=None,
        internal=True,
        external=True,
        raise_exceptions=False,
    ):
        """
        Distribute a data stream message both internally to any intelligence module within this bot,
        and externally to any other bots that might be listening.
        :param botengine: BotEngine environment
        :param address: Data stream address
        :param content: Message content
        :param internal: True to deliver this message internally to any intelligence module that's listening (default)
        :param external: True to deliver this message externally to any other bot that's listening (default)
        :param raise_exceptions: True to raise an exception if an error occurs when distributing internally, False to log the error and continue
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">distribute_datastream_message()"
        )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "|distribute_datastream_message() - address={} content={} internal={} external={} raise_exceptions={}".format(
                address, content, internal, external, raise_exceptions
            )
        )
        if internal:
            self.datastream_updated(
                botengine, address, content, raise_exceptions=raise_exceptions
            )

        if external:
            botengine.send_datastream_message(address, content)

    # ===========================================================================
    # Narration
    # ===========================================================================
    def narrate(
        self,
        botengine,
        title=None,
        description=None,
        priority=None,
        icon=None,
        icon_font=None,
        timestamp_ms=None,
        narrative_type=NARRATIVE_TYPE_OBSERVATION,
        file_ids=None,
        extra_json_dict=None,
        event_type=None,
        update_narrative_id=None,
        update_narrative_timestamp=None,
        user_id=None,
        users=None,
        device_object=None,
        device_id=None,
        devices=None,
        goal_id=None,
        question_key=None,
        comment=None,
        status=None,
        microservice_identifier=None,
        to_user=True,
        to_admin=False,
        publish_to_partner=None,
    ):
        """
        Narrate some activity
        :param botengine: BotEngine environment
        :param title: Title of the event
        :param description: Description of the event
        :param priority: 0=debug; 1=info; 2=warning; 3=critical
        :param icon: Icon name, like 'motion' or 'phone-alert'. See http://peoplepowerco.com/icons and http://fontawesome.com
        :param icon_font: Icon font package. Please see the ICON_FONT_* descriptions in utilities/utilities.py.
        :param timestamp_ms: Optional timestamp for this event. Can be in the future. If not set, the current timestamp is used.
        :param narrative_type: Narrative type. See NARRATIVE_TYPE_* constants in utilities/narrative.py.
        :param file_ids: List of file ID's (media) to reference and show as part of the record in the UI
        :param extra_json_dict: Any extra JSON dictionary content we want to communicate with the UI
        :param event_type: Unique identifier for partner clouds to understand this narrative.
        :param update_narrative_id: Specify a narrative ID to update an existing record.
        :param update_narrative_timestamp: Specify a narrative timestamp to update an existing record. This is a double-check to make sure we're not overwriting the wrong record.
        :param to_admin: True to deliver to an administrator History
        :param to_user: True to deliver to end user History
        :param device_object: Device object to reference
        :param publish_to_partner: Set to False to avoid streaming this narrative to partner clouds (default is always True)
        :return:  { "user": narrative_object, "admin": narrative_object }. The narrative_object may be None. See com.ppc.Bot/narrative.py
        """
        # Do not narrate if UI override has been set in place to put location in ABSENT/VACATION MODE
        occupancy = botengine.get_state("occupancy")
        if occupancy is not None:
            if "override" in occupancy:
                if occupancy["override"] == "True":
                    return {"user": None, "admin": None}

        payload = {}

        if user_id is not None:
            payload["user_id"] = user_id

        if users is not None:
            payload["users"] = users

        if device_id is not None:
            payload["device_id"] = device_id

        if devices is not None:
            payload["devices"] = devices

        if goal_id is not None:
            payload["goal_id"] = goal_id

        if question_key is not None:
            payload["question_key"] = question_key

        if comment is not None:
            payload["comment"] = comment

        if device_object is not None:
            payload["device_id"] = device_object.device_id
            payload["device_type"] = device_object.device_type
            payload["device_desc"] = device_object.description

        if extra_json_dict is None:
            extra_json_dict = payload

        else:
            extra_json_dict.update(payload)

        response_dict = {"user": None, "admin": None}

        narrate_body = {}
        if title is not None:
            narrate_body["title"] = title
        if description is not None:
            narrate_body["description"] = description

        if narrate_body:
            narrate_body["priority"] = priority
            self.distribute_datastream_message(
                botengine,
                "capture_narrate",
                content=narrate_body,
                internal=True,
                external=False,
            )

        if to_admin:
            response = botengine.narrate(
                title,
                description,
                priority,
                icon,
                icon_font=icon_font,
                status=status,
                timestamp_ms=timestamp_ms,
                narrative_type=narrative_type,
                file_ids=file_ids,
                extra_json_dict=extra_json_dict,
                event_type=event_type,
                update_narrative_id=update_narrative_id,
                update_narrative_timestamp=update_narrative_timestamp,
                admin=True,
                publish_to_partner=publish_to_partner,
            )

            if response is not None:
                response_dict["admin"] = Narrative(
                    response["narrativeId"], response["narrativeTime"], admin=True
                )
                if microservice_identifier is not None:
                    self.org_narratives[microservice_identifier] = response_dict[
                        "admin"
                    ]

        else:
            if microservice_identifier is not None:
                if microservice_identifier in self.org_narratives:
                    del self.org_narratives[microservice_identifier]

        if to_user:
            response = botengine.narrate(
                title,
                description,
                priority,
                icon,
                icon_font=icon_font,
                status=status,
                timestamp_ms=timestamp_ms,
                narrative_type=narrative_type,
                file_ids=file_ids,
                extra_json_dict=extra_json_dict,
                event_type=event_type,
                update_narrative_id=update_narrative_id,
                update_narrative_timestamp=update_narrative_timestamp,
                admin=False,
                publish_to_partner=publish_to_partner,
            )

            if response is not None:
                response_dict["user"] = Narrative(
                    response["narrativeId"], response["narrativeTime"], admin=False
                )
                if microservice_identifier is not None:
                    self.location_narratives[microservice_identifier] = response_dict[
                        "user"
                    ]

        else:
            if microservice_identifier is not None:
                if microservice_identifier in self.location_narratives:
                    del self.location_narratives[microservice_identifier]

        return response_dict

    def resolve_narrative(self, botengine, microservice_identifier):
        """
        Resolve a narrative entry
        :param botengine: BotEngine environment
        :param microservice_identifier: The same microservice identifier used to create the narrative
        :param admin: True to update the admin status on this narrative
        :return:  { "narrativeId": id, "narrativeTime": timestamp_ms } if successful, otherwise None.
        """
        if microservice_identifier in self.org_narratives:
            if self.org_narratives[microservice_identifier] is not None:
                if isinstance(self.org_narratives[microservice_identifier], Narrative):
                    self.org_narratives[microservice_identifier].resolve(botengine)

                del self.org_narratives[microservice_identifier]

        if microservice_identifier in self.location_narratives:
            if self.location_narratives[microservice_identifier] is not None:
                if isinstance(
                    self.location_narratives[microservice_identifier], Narrative
                ):
                    self.location_narratives[microservice_identifier].resolve(botengine)

                del self.location_narratives[microservice_identifier]

    def delete_narration(self, botengine, narrative_id, narrative_timestamp):
        """
        Delete a narrative record
        :param botengine: BotEngine environment
        :param narrative_id: ID of the record to delete
        :param narrative_timestamp: Timestamp of the record to delete
        """
        botengine.delete_narration(narrative_id, narrative_timestamp)

    # ===========================================================================
    # Mode helper methods
    # ===========================================================================

    def is_on_vacation(self, botengine):
        """
        :return: True if the location is on vacation mode
        """
        return "VACATION" in self.mode

    def is_present(self, botengine=None):
        """
        Is the person likely physically present in the home?
        :return: True if the person is in HOME, STAY, SLEEP, or TEST mode. False for all others.
        """
        return (
            "ABSENT" not in self.occupancy_status
            and "A2H" not in self.occupancy_status
            and "H2A" not in self.occupancy_status
            and "AWAY" not in self.occupancy_status
            and "VACATION" not in self.occupancy_status
        )

    def is_definitely_absent(self, botengine=None):
        """
        :param botengine:
        :return: True if the occupants are definitely away
        """
        return (
            "ABSENT" in self.occupancy_status
            or "A2H" in self.occupancy_status
            or "AWAY" in self.occupancy_status
            or "VACATION" in self.occupancy_status
        )

    def is_present_and_protected(self, botengine=None):
        """
        Is the person at home and wants to be alerted if the perimeter is breached?
        :return: True if the person is in STAY or SLEEP mode
        """
        return (
            utilities.MODE_STAY in self.mode
            or "SLEEP" in self.occupancy_status
            or "H2S" in self.occupancy_status
            or "S2H" in self.occupancy_status
        )

    def is_sleeping(self, botengine=None):
        """
        :return: True if the person is sleeping or about to wake up.
        """
        return "SLEEP" in self.occupancy_status or "S2H" in self.occupancy_status

    def update_mode(self, botengine):
        """
        Extract this location's current mode from our botengine environment
        :param botengine: BotEngine environment
        """
        location_block = botengine.get_location_info()
        if location_block is not None:
            if "event" in location_block.get("location", {}):
                self.mode = str(location_block["location"]["event"])

    # ===========================================================================
    # Time
    # ===========================================================================
    def get_local_datetime(self, botengine):
        """
        Get the datetime in the user's local timezone.
        :param botengine: BotEngine environment
        :param timestamp: Unix timestamp in milliseconds
        :returns: datetime
        """
        return self.get_datetime_from_timestamp(
            botengine,
            botengine.get_timestamp(),
            self.get_local_timezone_string(botengine),
        )

    def get_local_format_date(self, botengine):
        """
        Get formatted date in the user's local timezone
        :returns: eg:30/01/2021
        """
        timestamp_ms = botengine.get_timestamp()
        timezone = self.get_local_timezone_string(botengine)
        return datetime.datetime.fromtimestamp(
            timestamp_ms / 1000.0, pytz.timezone(timezone)
        ).strftime("%d/%m/%y")

    def get_local_datetime_from_timestamp(self, botengine, timestamp_ms):
        """
        Get a datetime in the user's local timezone, based on an input timestamp_ms
        :param botengine: BotEngine environment
        :param timestamp_ms: Timestamp in milliseconds to transform into a timezone-aware datetime object
        """
        return self.get_datetime_from_timestamp(
            botengine, timestamp_ms, self.get_local_timezone_string(botengine)
        )

    def get_datetime_from_timestamp(self, botengine, timestamp_ms=None, timezone=None):
        """
        Get a datetime in the user's local timezone, based on an input timestamp_ms
        :param botengine: BotEngine environment
        :param timestamp_ms: Timestamp in milliseconds to transform into a timezone-aware datetime object
        :param timezone: Optional timezone
        """
        if timestamp_ms is None:
            timestamp_ms = botengine.get_timestamp()

        if timezone is None:
            timezone = self.get_local_timezone_string(botengine)
        return datetime.datetime.fromtimestamp(
            timestamp_ms / 1000.0, pytz.timezone(timezone)
        )

    def get_local_timezone_string(self, botengine):
        """
        Get the local timezone string
        :param botengine: BotEngine environment
        :return: timezone string
        """
        location_block = botengine.get_location_info()

        # Default Timezone
        timezone = (
            properties.get_property(botengine, "DEFAULT_TIMEZONE", False)
            or "US/Pacific"
        )
        # Try to get the user's location's timezone string
        if "location" in location_block:
            if "timezone" in location_block["location"]:
                timezone = location_block["location"]["timezone"]["id"]

        return timezone

    def get_relative_time_of_day(self, botengine, timestamp_ms=None, timezone=None):
        """
        Transform our local datetime into a float hour and minutes
        :param botengine: BotEngine environment
        :param timestamp_ms: Transform this timestamp if given, otherwise transform the current time from botengine.
        :param timezone: Optional timezone
        :return: Relative time of day - hours.minutes where minutes is divided by 60. 10:15 AM = 10.25
        """
        dt = self.get_datetime_from_timestamp(botengine, timestamp_ms, timezone)
        return dt.hour + (dt.minute / 60.0)

    def get_midnight_last_night(self, botengine):
        """
        Get a datetime of midnight last night in local time
        :param botengine: BotEngine environment
        :return: Datetime object of midnight last night in the local timezone
        """
        return self.get_local_datetime(botengine).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    def get_midnight_tonight(self, botengine):
        """
        Get a datetime of midnight tonight in local time
        :param botengine: BotEngine environment
        :return: Datetime object of midnight tonight in the local timezone
        """
        return self.get_local_datetime(botengine).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

    def local_timestamp_ms_from_relative_hours(
        self, botengine, weekday, hours, future=True
    ):
        """
        Calculate an absolute timestamp from relative day-of-week and hour
        :param botengine: BotEngine environment
        :param dow: day-of-week (Monday is 0)
        :param hours: Relative hours into the day (i.e. 23.5 = 11:30 PM local time)
        :param future: True to return a timestamp that is always in the future
        :return: Unix epoch timestamp in milliseconds
        """
        from datetime import timedelta

        hours = float(hours)
        weekday = int(weekday)

        reference = self.get_local_datetime(botengine)
        hour, minute = divmod(hours, 1)
        minute = round(minute * 60)
        if minute >= 60:
            minute -= 60
        days = reference.weekday() - weekday
        target_dt = (reference - timedelta(days=days)).replace(
            hour=int(hour), minute=int(minute), second=0, microsecond=0
        )
        timestamp_ms = self.timezone_aware_datetime_to_unix_timestamp(
            botengine, target_dt
        )

        if future:
            if timestamp_ms <= botengine.get_timestamp():
                timestamp_ms += utilities.ONE_WEEK_MS

        return timestamp_ms

    def timezone_aware_datetime_to_unix_timestamp(self, botengine, dt):
        """
        Convert a local datetime / timezone-aware datetime to a unix timestamp
        :param botengine: BotEngine environment
        :param dt: Datetime to convert to unix timestamp
        :return: timestamp in milliseconds
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">timezone_aware_datetime_to_unix_timestamp() dt={}".format(dt)
        )
        tz = pytz.timezone(self.get_local_timezone_string(botengine))
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "|timezone_aware_datetime_to_unix_timestamp() tz={}".format(tz)
        )
        local_dt = dt.astimezone(tz)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "|timezone_aware_datetime_to_unix_timestamp() local_dt={}".format(local_dt)
        )
        timestamp = int((local_dt).timestamp()) * 1000
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<timezone_aware_datetime_to_unix_timestamp() timestamp={}".format(
                timestamp
            )
        )
        return timestamp

    def get_local_hour_of_day(self, botengine):
        """
        Get the local hour of the day (float), used in machine learning algorithms.

        Examples:
        * Midnight last night = 0.0
        * Noon = 12.0
        * 9:15 PM = 21.25

        :param botengine: BotEngine environment
        :return: hour of the day (float)
        """
        return (
            (
                botengine.get_timestamp()
                - self.timezone_aware_datetime_to_unix_timestamp(
                    botengine, self.get_midnight_last_night(botengine)
                )
            )
            / 1000
            / 60.0
            / 60.0
        )

    def get_local_day_of_week(self, botengine):
        """
        Get the local day of the week (0-6)

        :param botengine: BotEngine environment
        :return: local day of the week (0 - 6)
        """
        return self.get_local_datetime(botengine).weekday()

    def day_of_week_to_local_midnight_datetime(self, botengine, dow):
        """
        Get the datetime at midnight of the next relative day of the week.
            0 = Monday
            1 = Tuesday
            2 = Wednesday
            3 = Thursday
            4 = Friday
            5 = Saturday
            6 = Sunday

        :param dow: Python day-of-week (0 = Monday)
        :return: Datetime of midnight on this next day-of-week
        """
        from datetime import timedelta

        midnight_dt = self.get_midnight_last_night(botengine)
        offset = dow - midnight_dt.weekday()
        if offset < 0:
            offset += 7

        return midnight_dt + timedelta(days=offset)

    def is_last_day_of_month(self, botengine):
        import calendar
        import datetime

        date = self.get_local_datetime(botengine)
        last_day_of_month = calendar.monthrange(date.year, date.month)[1]
        return datetime.date(date.year, date.month, date.day) == datetime.date(
            date.year, date.month, last_day_of_month
        )

    # ===========================================================================
    # Weather
    # ===========================================================================
    def get_weather_forecast(self, botengine, units=None, hours=12):
        """
        Get the weather forecast for this location
        :param units: Default is Metric. 'e'=English; 'm'=Metric; 'h'=Hybrid (UK); 's'=Metric SI units (not available for all APIs)
        :param hours: Forecast depth in hours, default is 12. Available hours are 6, 12.
        :return: Weather JSON data
        """
        return botengine.get_weather_forecast_by_location(
            self.location_id, units, hours
        )

    def get_current_weather(self, botengine, units=None):
        """
        Get the current weather by Location ID
        :param units: Default is Metric. 'e'=English; 'm'=Metric; 'h'=Hybrid (UK); 's'=Metric SI units (not available for all APIs)
        :return: Weather JSON data
        """
        return botengine.get_current_weather_by_location(self.location_id, units)

    # ===========================================================================
    # Synchronize local modules
    # ===========================================================================
    def _sync_modules(self, botengine, modules, desired_modules_dict):
        """
        Synchronize the modules declared in our index.py file with this local class
        :param botengine: BotEngine environment
        :param modules: Dictionary of local modules { 'module_id': module_object }
        :param desired_modules_dict: Dictionary of desired modules, typically loaded from an index.py file
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">_sync_modules()"
        )
        module_names = [x["module"] for x in desired_modules_dict]

        changed = False
        for m in module_names:
            changed |= m not in modules

        for m in list(modules.keys()):
            changed |= m not in module_names

        if changed:
            # Remove modules that no longer exist
            for module_name in dict(modules).keys():
                found = False
                for intelligence_info in desired_modules_dict:
                    if intelligence_info["module"] == module_name:
                        found = True
                        break

                if not found:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                        "|_sync_modules() Deleting module {}".format(module_name)
                    )
                    modules[module_name].destroy(botengine)
                    del modules[module_name]

            # Add more modules
            for intelligence_info in desired_modules_dict:
                if intelligence_info["module"] not in modules:
                    try:
                        intelligence_module = importlib.import_module(
                            intelligence_info["module"]
                        )
                        class_ = getattr(
                            intelligence_module, intelligence_info["class"]
                        )
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                            "|_sync_modules() Adding module {}".format(
                                str(intelligence_info["module"])
                            )
                        )
                        intelligence_object = class_(botengine, self)
                        modules[intelligence_info["module"]] = intelligence_object

                    except Exception as e:
                        import traceback

                        botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                            "|_sync_modules() Could not add module {}. exception={} trace={}".format(
                                str(intelligence_info), str(e), traceback.format_exc()
                            )
                        )
                        if botengine.playback:
                            import time

                            time.sleep(5)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<_sync_modules()"
        )

    # ===========================================================================
    # CSV methods for machine learning algorithm integrations
    # ===========================================================================
    def get_csv(self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None):
        """
        Get a .csv string of all the data
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: oldest timestamp in milliseconds
        :param newest_timestamp_ms: newest timestamp in milliseconds
        :return: .csv string, largely matching the .csv data you would receive from the "botengine --download_device [device_id]" command line interface. Or None if this device doesn't have data.
        """
        output = "location_id,timestamp_ms,timestamp_iso,event,source_type\n"

        # This number happens to be the oldest timestamp
        if oldest_timestamp_ms < 1262304000000:
            oldest_timestamp_ms = 1262304000000

        try:
            modes = botengine.get_mode_history(
                self.location_id,
                oldest_timestamp_ms=oldest_timestamp_ms,
                newest_timestamp_ms=newest_timestamp_ms,
            )
        except Exception as e:
            # This can happen because this bot may not have read permissions for this device.

            botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                "|get_csv() Could not download modes history for location {}: {}".format(
                    self.location_id,
                    str(e),
                )
            )
            return None

        if "events" not in modes:
            return None

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "|get_csv() {} mode changes captured".format(len(modes["events"]))
        )

        for event in modes["events"]:
            timestamp_ms = event["eventDateMs"]
            dt = self.get_local_datetime_from_timestamp(botengine, timestamp_ms)

            event_name = event["event"].replace(",", ".")

            output += "{},{},{},{},{}".format(
                self.location_id,
                timestamp_ms,
                utilities.iso_format(dt),
                event_name,
                event["sourceType"],
            )
            output += "\n"

        return output

    def sorted_intelligence_modules(self, botengine):
        """
        Order intelligence modules alphabetically then by execution priority
        :param botengine: BotEngine environment
        :return: List of intelligence modules sorted by execution priority
        """
        # Order intelligence modules alphabetically then by execution priority
        modules = dict(
            sorted(self.intelligence_modules.items(), key=lambda module: module[0])
        )
        execution_priorities = {}
        for intelligence_info in index.MICROSERVICES.get("LOCATION_MICROSERVICES", []):
            execution_priorities[intelligence_info["module"]] = intelligence_info.get(
                "execution_priority", 0
            )

        return dict(
            sorted(
                modules.items(),
                key=lambda module: execution_priorities.get(module[0], 0),
                reverse=True,
            )
        )

    def sorted_filters(self, botengine):
        """
        Order filters modules alphabetically then by execution priority
        :param botengine: BotEngine environment
        :return: List of filters modules sorted by execution priority
        """
        # Order intelligence modules alphabetically then by execution priority
        if not hasattr(self, "filters"):
            return {}
        modules = dict(sorted(self.filters.items(), key=lambda module: module[0]))
        execution_priorities = {}
        for intelligence_info in index.MICROSERVICES.get(
            "DATA_FILTER_MICROSERVICES", []
        ):
            execution_priorities[intelligence_info["module"]] = intelligence_info.get(
                "execution_priority", 0
            )

        return dict(
            sorted(
                modules.items(),
                key=lambda module: execution_priorities.get(module[0], 0),
                reverse=True,
            )
        )
