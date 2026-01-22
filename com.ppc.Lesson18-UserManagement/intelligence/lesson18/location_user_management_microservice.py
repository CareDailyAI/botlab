"""
Lesson 18 - User Management

Demonstrates how to retrieve and summarize users associated with a location.
"""

from intelligence.intelligence import Intelligence  # type: ignore


STATE_ADDRESS = "lesson18/users"


class LocationUserManagementMicroservice(Intelligence):
    def __init__(self, botengine, parent):
        super().__init__(botengine, parent)

    def initialize(self, botengine):
        # Publish user snapshot on initialize for demo purposes.
        self.publish_user_snapshot(botengine, reason="initialize")

    def schedule_fired(self, botengine, schedule_id):
        self.publish_user_snapshot(botengine, reason=f"schedule:{schedule_id}")

    def publish_user_snapshot(self, botengine, reason):
        users = []
        if hasattr(botengine, "get_location_users"):
            try:
                users = botengine.get_location_users() or []
            except Exception:
                users = []

        summary = [
            {
                "id": u.get("id"),
                "firstName": u.get("firstName"),
                "lastName": u.get("lastName"),
                "email": (u.get("email") or {}).get("email"),
                "role": u.get("role"),
                "category": u.get("category"),
                "temporary": u.get("temporary"),
                "language": u.get("language"),
            }
            for u in users
        ]

        botengine.set_state(
            STATE_ADDRESS,
            {"reason": reason, "count": len(summary), "users": summary},
            overwrite=True,
        )

