"""
Created on June 28, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

# Narrative priority levels
NARRATIVE_PRIORITY_ANALYTIC = -1
NARRATIVE_PRIORITY_DEBUG = 0
NARRATIVE_PRIORITY_DETAIL = 0
NARRATIVE_PRIORITY_INFO = 1
NARRATIVE_PRIORITY_WARNING = 2
NARRATIVE_PRIORITY_CRITICAL = 3

# Narrative types
# High-frequency 'observation' entries for explainable AI and accountability
NARRATIVE_TYPE_OBSERVATION = 0

# Low-frequency 'journal' entries for SUMMARIZED exec-level communications to humans
NARRATIVE_TYPE_JOURNAL = 4

# High-frequency 'insight' entries for real-time CRITICAL exec-level communications to humans
NARRATIVE_TYPE_INSIGHT = 5


class Narrative:
    """
    This class is instantiated as a narrative object that can be updated later.
    """

    def __init__(self, narrative_id, narrative_time, admin):
        """
        Constructor
        :param narrative_id: Narrative ID
        :param narrative_time: Narrative timestamp
        :param to_admin: True if this is to the admin, False if it's to a user
        """
        # Narrative ID
        self.narrative_id = narrative_id

        # Narrative Timestamp
        self.narrative_time = narrative_time

        # To admin
        self.admin = admin

    def resolve(self, botengine):
        """
        Resolve this narrative
        :param botengine: BotEngine environment
        """
        response = botengine.narrate(
            update_narrative_id=self.narrative_id,
            update_narrative_timestamp=self.narrative_time,
            admin=self.admin,
            status=2,
        )

        if response is not None:
            self.narrative_id = response["narrativeId"]
            self.narrative_time = response["narrativeTime"]

    def add_comment(self, botengine, comment):
        """
        Add a comment to this narrative
        :param botengine: BotEngine environment
        :param comment: Comment to add
        :return:
        """
        narrative_content = botengine.get_narration(self.narrative_id, self.admin)

        if narrative_content is None:
            return

        else:
            if "target" not in narrative_content:
                narrative_content["target"] = {}

            if "comment" not in narrative_content["target"]:
                narrative_content["target"]["comment"] = ""

            narrative_content["target"]["comment"] += comment + "\n"

            response = botengine.narrate(
                update_narrative_id=self.narrative_id,
                update_narrative_timestamp=self.narrative_time,
                admin=self.admin,
                extra_json_dict=narrative_content["target"],
            )

            if response is not None:
                self.narrative_id = response["narrativeId"]
                self.narrative_time = response["narrativeTime"]

    def update_description(self, botengine, description):
        """
        Update the description of an existing narrative
        :param botengine: BotEngine environment
        :param description: New description
        """
        response = botengine.narrate(
            update_narrative_id=self.narrative_id,
            update_narrative_timestamp=self.narrative_time,
            admin=self.admin,
            description=description,
        )

        if response is not None:
            self.narrative_id = response["narrativeId"]
            self.narrative_time = response["narrativeTime"]

    def delete(self, botengine):
        """
        Delete this narrative
        :param botengine: BotEngine environment
        """
        botengine.delete_narration(self.narrative_id, self.narrative_time)
