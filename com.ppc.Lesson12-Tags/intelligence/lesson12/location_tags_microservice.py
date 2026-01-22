"""
Lesson 12 - Tags

Demonstrates tagging (and deleting tags) for:
- People (users)
- Places (locations)
- Things (devices/files)
"""

from intelligence.intelligence import Intelligence  # type: ignore


TAG_USER = "lesson12.user"
TAG_LOCATION = "lesson12.location"
TAG_DEVICE = "lesson12.device"

STATE_ADDRESS = "lesson12/tags"
LOCATION_PROPERTY_KEY = "lesson12_tags_initialized"
LOCATION_PROPERTY_DEVICE_ID = "lesson12_tagged_device_id"


class LocationTagsMicroservice(Intelligence):
    def __init__(self, botengine, parent):
        super().__init__(botengine, parent)

    def initialize(self, botengine):
        """
        Tag a few entities once, then publish a summary to a UI-facing state variable.
        """
        if self.parent.get_location_property(botengine, LOCATION_PROPERTY_KEY):
            return

        # Tag a user (the current user account context)
        botengine.tag_user(TAG_USER)

        # Tag the current location
        botengine.tag_location(TAG_LOCATION, category="lesson", priority=0)

        # Optionally tag a device if one is present
        tagged_device_id = None
        if getattr(self.parent, "devices", None):
            try:
                tagged_device_id = next(iter(self.parent.devices.keys()))
            except Exception:
                tagged_device_id = None

        if tagged_device_id is not None:
            botengine.tag_device(TAG_DEVICE, tagged_device_id)
            self.parent.set_location_property(
                botengine, LOCATION_PROPERTY_DEVICE_ID, tagged_device_id, track=False
            )

        # Mark initialized so we don't spam tags on every trigger.
        self.parent.set_location_property(
            botengine, LOCATION_PROPERTY_KEY, True, track=False
        )

        self._publish_state(botengine, deleted=False)

    def delete_demo_tags(self, botengine):
        """
        Delete the demo tags used by this lesson.
        """
        botengine.delete_user_tag(TAG_USER)
        botengine.delete_location_tag(TAG_LOCATION)

        device_id = self.parent.get_location_property(botengine, LOCATION_PROPERTY_DEVICE_ID)
        if device_id is not None:
            botengine.delete_device_tag(TAG_DEVICE, device_id)

        self._publish_state(botengine, deleted=True)

    def _publish_state(self, botengine, deleted: bool):
        botengine.set_state(
            address=STATE_ADDRESS,
            json_content={
                "userTag": TAG_USER,
                "locationTag": TAG_LOCATION,
                "deviceTag": TAG_DEVICE,
                "deleted": deleted,
            },
            overwrite=True,
        )

