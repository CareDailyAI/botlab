'''
Created on June 28, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

class Narrative:
    """
    December 3, 2019 - Deprecated.

    SHOULD BE SAFE TO DELETE THIS FILE AFTER MARCH, 2020. TEST BY RUNNING YOUR BOT.

    This file remains active for now while its object is still being referenced by existing bots with dill/pickle.

    We've updated the location.py file to reference utilities.narrative for future narrative object creation,
    but expect it will take awhile for everyone's current bots to clear out those old references.
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
        response = botengine.narrate(update_narrative_id=self.narrative_id, update_narrative_timestamp=self.narrative_time, admin=self.admin, status=2)

        if response is not None:
            self.narrative_id = response['narrativeId']
            self.narrative_time = response['narrativeTime']

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
            if 'target' not in narrative_content:
                narrative_content['target'] = {}

            if 'comment' not in narrative_content['target']:
                narrative_content['target']['comment'] = ""

            narrative_content['target']['comment'] += comment + "\n"

            response = botengine.narrate(update_narrative_id=self.narrative_id, update_narrative_timestamp=self.narrative_time, admin=self.admin, extra_json_dict=narrative_content['target'])

            if response is not None:
                self.narrative_id = response['narrativeId']
                self.narrative_time = response['narrativeTime']

    def update_description(self, botengine, description):
        """
        Update the description of an existing narrative
        :param botengine: BotEngine environment
        :param description: New description
        """
        response = botengine.narrate(update_narrative_id=self.narrative_id, update_narrative_timestamp=self.narrative_time, admin=self.admin, description=description)

        if response is not None:
            self.narrative_id = response['narrativeId']
            self.narrative_time = response['narrativeTime']

    def delete(self, botengine):
        """
        Delete this narrative
        :param botengine: BotEngine environment
        """
        botengine.delete_narration(self.narrative_id, self.narrative_time)