"""
Lesson 15 - Analytics

Demonstrates analytics instrumentation using the `signals.analytics` helpers and
location properties that can fan out into 3rd party analytics integrations.
"""

from intelligence.intelligence import Intelligence  # type: ignore

import signals.analytics as analytics  # type: ignore


STATE_ADDRESS = "lesson15/analytics"
LOCATION_PROPERTY_KEY = "lesson15_analytics_initialized"


class LocationAnalyticsMicroservice(Intelligence):
    def __init__(self, botengine, parent):
        super().__init__(botengine, parent)
        self.last_analytics_track = None
        self.last_analytics_people_set = None

    def initialize(self, botengine):
        if self.parent.get_location_property(botengine, LOCATION_PROPERTY_KEY):
            return

        # Track an event. (In tests, BotEnginePyTest can record the outgoing datastream message.)
        analytics.track(
            botengine,
            self.parent,
            "lesson15.analytics_demo",
            properties={"source": "lesson15"},
            event_description="Lesson 15 analytics demo event",
        )

        # Setting a location property can optionally propagate people properties (track=True).
        self.parent.set_location_property(
            botengine,
            "lesson15_demo_property",
            "enabled",
            track=True,
        )

        self.parent.set_location_property(
            botengine, LOCATION_PROPERTY_KEY, True, track=False
        )

        botengine.set_state(
            STATE_ADDRESS,
            {
                "event": "lesson15.analytics_demo",
                "locationProperty": "lesson15_demo_property",
                "value": "enabled",
                "lastAnalyticsTrack": self.last_analytics_track,
                "lastAnalyticsPeopleSet": self.last_analytics_people_set,
            },
            overwrite=True,
        )

    # -------------------------------------------------------------------------
    # Internal analytics signal handlers (Data Stream / signals pattern)
    # -------------------------------------------------------------------------
    def analytics_track(self, botengine, content):
        """
        Handle internal `signals.analytics.track()` messages.
        """
        self.last_analytics_track = content

    def analytics_people_set(self, botengine, content):
        """
        Handle internal `signals.analytics.people_set()` messages.
        """
        self.last_analytics_people_set = content

