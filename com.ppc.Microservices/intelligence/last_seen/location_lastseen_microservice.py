"""
Created on October 5, 2018
Restructed on November 20, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

import properties  # type: ignore
import signals.dashboard as dashboard  # type: ignore
import signals.insights as insights  # type: ignore
import utilities.utilities as utilities  # type: ignore
from devices.entry.entry import EntryDevice  # type: ignore
from devices.motion.motion import MotionDevice  # type: ignore
from devices.radar.radar import RadarDevice  # type: ignore
from intelligence.intelligence import Intelligence  # type: ignore

# Time between narrations
TIME_BETWEEN_NARRATIONS_MS = utilities.ONE_MINUTE_MS

# Minimum time between updates if the person is still in the same room
MINIMUM_UPDATE_TIMESTAMP_MS = utilities.ONE_MINUTE_MS * 5


class LocationLastSeenMicroservice(Intelligence):
    """
    Continually describe where the person was last seen in the house.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # Last motion object observed to detect motion
        self.last_observed_motion_object = None

        # Last update timestamp
        self.last_timestamp_ms = 0

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        # Added November 24, 2020
        if not hasattr(self, "last_timestamp_ms"):
            self.last_timestamp_ms = 0

        return

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        if isinstance(device_object, MotionDevice):
            if device_object == self.last_observed_motion_object:
                # Already got it
                if (
                    self.last_timestamp_ms
                    > botengine.get_timestamp() - MINIMUM_UPDATE_TIMESTAMP_MS
                ):
                    botengine.get_logger().info("=> Already got it")
                    return

            if device_object.did_start_detecting_motion(botengine):
                self.last_observed_motion_object = device_object
                self.last_timestamp_ms = botengine.get_timestamp()

                botengine.get_logger().info(
                    "Last Seen : Motion detected in '{}'".format(
                        device_object.description
                    )
                )

                if self.parent.is_sleeping(
                    botengine
                ) and not device_object.is_in_bedroom(botengine):
                    comment = _(  # noqa: F821 # type: ignore
                        "Occupants should be asleep, but someone was last detected near the '{}'"
                    ).format(device_object.description)
                    dashboard.update_dashboard_header(
                        botengine,
                        location_object=self.parent,
                        name="lastseen",
                        priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                        percent_good=70,
                        title=_("Last Detected"),  # noqa: F821 # type: ignore
                        comment=comment,
                        icon=device_object.get_icon(),
                        icon_font=device_object.get_icon_font(),
                        resolution_object=None,
                        conversation_object=None,
                        future_timestamp_ms=None,
                        ttl_ms=utilities.ONE_DAY_MS,
                    )

                else:
                    comment = _("Someone was last detected near the '{}'").format(  # noqa: F821 # type: ignore
                        device_object.description
                    )
                    dashboard.update_dashboard_header(
                        botengine,
                        location_object=self.parent,
                        name="lastseen",
                        priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                        percent_good=100,
                        title=self.generate_all_good_title(botengine),
                        comment=comment,
                        icon=device_object.get_icon(),
                        icon_font=device_object.get_icon_font(),
                        resolution_object=None,
                        conversation_object=None,
                        future_timestamp_ms=None,
                        ttl_ms=utilities.ONE_DAY_MS,
                    )

                insights.capture_insight(
                    botengine,
                    location_object=self.parent,
                    insight_id="occupancy.last_seen",
                    value=1,
                    title=_("Last Detected"),  # noqa: F821 # type: ignore
                    description=_("Last detected near the '{}'.").format(  # noqa: F821 # type: ignore
                        device_object.description
                    ),
                    device_object=device_object,
                )

        elif isinstance(device_object, EntryDevice):
            if device_object.did_open(botengine):
                botengine.get_logger().info(
                    "Last Seen : '{}' door opened".format(device_object.description)
                )

                comment = _("Someone was last detected opening the '{}'").format(  # noqa: F821 # type: ignore
                    device_object.description
                )
                dashboard.update_dashboard_header(
                    botengine,
                    location_object=self.parent,
                    name="lastseen",
                    priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                    percent_good=100,
                    title=self.generate_all_good_title(botengine),
                    comment=_("Someone was last detected opening the '{}'").format(  # noqa: F821 # type: ignore
                        device_object.description
                    ),
                    icon=device_object.get_icon(),
                    icon_font=device_object.get_icon_font(),
                    resolution_object=None,
                    conversation_object=None,
                    future_timestamp_ms=None,
                    ttl_ms=utilities.ONE_DAY_MS,
                )

                insights.capture_insight(
                    botengine,
                    location_object=self.parent,
                    insight_id="occupancy.last_seen",
                    value=1,
                    title=_("Last Detected"),  # noqa: F821 # type: ignore
                    description=_("Last detected opening the '{}'.").format(  # noqa: F821 # type: ignore
                        device_object.description
                    ),
                    device_object=device_object,
                )

                self.last_observed_motion_object = None

            elif device_object.did_close(botengine):
                botengine.get_logger().info(
                    "Last Seen : '{}' door closed".format(device_object.description)
                )

                comment = _("Someone was last detected closing the '{}'").format(  # noqa: F821 # type: ignore
                    device_object.description
                )
                dashboard.update_dashboard_header(
                    botengine,
                    location_object=self.parent,
                    name="lastseen",
                    priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                    percent_good=100,
                    title=self.generate_all_good_title(botengine),
                    comment=comment,
                    icon=device_object.get_icon(),
                    icon_font=device_object.get_icon_font(),
                    resolution_object=None,
                    conversation_object=None,
                    future_timestamp_ms=None,
                    ttl_ms=utilities.ONE_DAY_MS,
                )

                insights.capture_insight(
                    botengine,
                    location_object=self.parent,
                    insight_id="occupancy.last_seen",
                    value=0,
                    title=_("Last Detected"),  # noqa: F821 # type: ignore
                    description=_("Last detected closing the '{}'.").format(  # noqa: F821 # type: ignore
                        device_object.description
                    ),
                    device_object=device_object,
                )

                self.last_observed_motion_object = None

            else:
                # Nothing to do
                return

    # ===========================================================================
    # Radar events
    # ===========================================================================
    def knowledge_did_update_radar_occupants(
        self, botengine, device_object, total_occupants
    ):
        """
        Updated radar occupants for the given device
        Declare what room the occupants are in
        :param botengine:
        :param device_object:
        :param total_occupants:
        :return:
        """
        max_occupants = 0
        max_device = None
        for device in list(self.parent.devices.values()):
            if isinstance(device, RadarDevice):
                if device.knowledge_total_occupants > max_occupants:
                    max_occupants = device.knowledge_total_occupants
                    max_device = device

        if max_device is None:
            # Left all rooms
            dashboard.update_dashboard_header(
                botengine,
                location_object=self.parent,
                name="lastseen",
                priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                percent_good=100,
                title=_("Last Detected"),  # noqa: F821 # type: ignore
                comment=_("Last detected leaving the '{}'").format(  # noqa: F821 # type: ignore
                    device_object.description
                ),
                icon=device_object.get_icon(),
                icon_font=device_object.get_icon_font(),
                ttl_ms=utilities.ONE_DAY_MS,
            )

            insights.capture_insight(
                botengine,
                location_object=self.parent,
                insight_id="occupancy.last_seen",
                value=1,
                title=_("Last Detected"),  # noqa: F821 # type: ignore
                description=_("Last detected leaving the '{}'").format(  # noqa: F821 # type: ignore
                    device_object.description
                ),
                device_object=device_object,
                icon=device_object.get_icon(),
                icon_font=device_object.get_icon_font(),
            )

        else:
            # Inside at least 1 room
            if self.parent.is_sleeping(botengine) and not device_object.is_in_bedroom(
                botengine
            ):
                dashboard.update_dashboard_header(
                    botengine,
                    location_object=self.parent,
                    name="lastseen",
                    priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                    percent_good=100,
                    title=_("Last Detected"),  # noqa: F821 # type: ignore
                    comment=_(  # noqa: F821 # type: ignore
                        "Occupants should be asleep, but someone was last detected near the '{}'"
                    ).format(device_object.description),
                    icon=device_object.get_icon(),
                    icon_font=device_object.get_icon_font(),
                    ttl_ms=utilities.ONE_DAY_MS,
                )

            else:
                dashboard.update_dashboard_header(
                    botengine,
                    location_object=self.parent,
                    name="lastseen",
                    priority=dashboard.DASHBOARD_PRIORITY_OKAY,
                    percent_good=100,
                    title=_("Last Detected"),  # noqa: F821 # type: ignore
                    comment=_("Someone was last detected near the '{}'").format(  # noqa: F821 # type: ignore
                        device_object.description
                    ),
                    icon=device_object.get_icon(),
                    icon_font=device_object.get_icon_font(),
                    ttl_ms=utilities.ONE_DAY_MS,
                )

            insights.capture_insight(
                botengine,
                location_object=self.parent,
                insight_id="occupancy.last_seen",
                value=1,
                title=_("Last Detected"),  # noqa: F821 # type: ignore
                description=_("Last detected in the '{}'").format(  # noqa: F821 # type: ignore
                    device_object.description
                ),
                device_object=device_object,
                icon=device_object.get_icon(),
                icon_font=device_object.get_icon_font(),
            )

    # We leave this information-level to allow it to refresh periodically throughout the night.
    def information_did_arrive_bed(
        self, botengine, device_object, unique_id, context_id, name
    ):
        botengine.get_logger().info(
            utilities.Color.RED
            + "location_lastseen_microservice: information_did_arrive_bed()"
            + utilities.Color.END
        )
        dashboard.update_dashboard_header(
            botengine,
            location_object=self.parent,
            name="lastseen",
            priority=dashboard.DASHBOARD_PRIORITY_OKAY,
            percent_good=100,
            title=_("Last Detected"),  # noqa: F821 # type: ignore
            comment=_("'{}' - Last detected in bed.").format(device_object.description),  # noqa: F821 # type: ignore
            icon="bed",
            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
            ttl_ms=utilities.ONE_DAY_MS,
        )

        insights.capture_insight(
            botengine,
            location_object=self.parent,
            insight_id="occupancy.last_seen",
            value=1,
            title=_("Last Detected"),  # noqa: F821 # type: ignore
            description=_("Last detected in bed."),  # noqa: F821 # type: ignore
            device_object=device_object,
            icon="bed",
            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
        )

    # We leave this information-level to allow it to refresh periodically throughout the night.
    def information_did_leave_bed(
        self, botengine, device_object, unique_id, context_id, name
    ):
        botengine.get_logger().info(
            utilities.Color.RED
            + "location_lastseen_microservice: information_did_leave_bed()"
            + utilities.Color.END
        )
        self.knowledge_did_update_radar_occupants(
            botengine, device_object, device_object.knowledge_total_occupants
        )

    def knowledge_did_arrive_shower(
        self, botengine, device_object, unique_id, context_id, name
    ):
        botengine.get_logger().info(
            utilities.Color.RED
            + "location_lastseen_microservice: information_did_arrive_shower()"
            + utilities.Color.END
        )
        dashboard.update_dashboard_header(
            botengine,
            location_object=self.parent,
            name="lastseen",
            priority=dashboard.DASHBOARD_PRIORITY_OKAY,
            percent_good=100,
            title=_("Taking a shower"),  # noqa: F821 # type: ignore
            comment=_("'{}' - Last detected in the shower.").format(  # noqa: F821 # type: ignore
                device_object.description
            ),
            icon="shower",
            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
            ttl_ms=utilities.ONE_DAY_MS,
        )

        insights.capture_insight(
            botengine,
            location_object=self.parent,
            insight_id="occupancy.last_seen",
            value=1,
            title=_("Taking a shower"),  # noqa: F821 # type: ignore
            description=_("Last detected in the shower."),  # noqa: F821 # type: ignore
            device_object=device_object,
            icon="shower",
            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
        )

    def knowledge_did_leave_shower(
        self, botengine, device_object, unique_id, context_id, name
    ):
        botengine.get_logger().info(
            utilities.Color.RED
            + "location_lastseen_microservice: information_did_leave_shower()"
            + utilities.Color.END
        )
        self.knowledge_did_update_radar_occupants(
            botengine, device_object, device_object.knowledge_total_occupants
        )

    # We keep this 'information'-based because it's higher frequency and makes for a better live demo of the technology
    def information_did_arrive_chair(
        self, botengine, device_object, unique_id, context_id, name
    ):
        botengine.get_logger().info(
            utilities.Color.RED
            + "location_lastseen_microservice: information_did_arrive_chair()"
            + utilities.Color.END
        )
        dashboard.update_dashboard_header(
            botengine,
            location_object=self.parent,
            name="lastseen",
            priority=dashboard.DASHBOARD_PRIORITY_OKAY,
            percent_good=100,
            title=_("Sitting"),  # noqa: F821 # type: ignore
            comment=_("'{}' - Last detected in the {}.").format(  # noqa: F821 # type: ignore
                device_object.description, name
            ),
            icon="chair",
            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
            ttl_ms=utilities.ONE_DAY_MS,
        )

        insights.capture_insight(
            botengine,
            location_object=self.parent,
            insight_id="occupancy.last_seen",
            value=1,
            title=_("Sitting"),  # noqa: F821 # type: ignore
            description=_("Sitting in the '{}'.").format(name),  # noqa: F821 # type: ignore
            device_object=device_object,
            icon="chair",
            icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
        )

    # We keep this 'information'-based because it's higher frequency and makes for a better live demo of the technology
    def information_did_leave_chair(
        self, botengine, device_object, unique_id, context_id, name
    ):
        botengine.get_logger().info(
            utilities.Color.RED
            + "location_lastseen_microservice: information_did_leave_chair()"
            + utilities.Color.END
        )
        self.knowledge_did_update_radar_occupants(
            botengine, device_object, device_object.knowledge_total_occupants
        )

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        return

    def generate_all_good_title(self, botengine):
        """
        When everything is good, produce a random title that describes we're all good.
        :param botengine:
        :return:
        """

        titles = properties.get_property(
            botengine, "LAST_SEEN_DASHBOARD", complain_if_missing=False
        )

        if titles is not None:
            if len(titles) == 0:
                titles = None

        if titles is None:
            titles = [
                _("Last Detected"),  # noqa: F821 # type: ignore
                _("Looking Good"),  # noqa: F821 # type: ignore
                _("Everything Looks Fine"),  # noqa: F821 # type: ignore
                _("All Right"),  # noqa: F821 # type: ignore
                _("Going Well"),  # noqa: F821 # type: ignore
                _("All Good Here"),  # noqa: F821 # type: ignore
                _("All Good"),  # noqa: F821 # type: ignore
                _("Okay"),  # noqa: F821 # type: ignore
                _("No Problems Found"),  # noqa: F821 # type: ignore
                _("Things are Good"),  # noqa: F821 # type: ignore
                _("Good"),  # noqa: F821 # type: ignore
            ]

        # Every 100 seconds the title will increment.
        return titles[int(str(botengine.get_timestamp())[6:-5]) % len(titles)]
