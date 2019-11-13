'''
Created on February 25, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence

class LocationMidnightMicroservice(Intelligence):
    """
    Announce midnight throughout the microservices framework
    """
    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """

        if schedule_id == "MIDNIGHT":
            self.parent.track(botengine, "midnight")
            self.parent.distribute_datastream_message(botengine, "midnight_fired", None, internal=True, external=False)
