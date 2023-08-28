'''
Created on June 21, 2022

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Edward Liu
'''

import utilities.utilities as utilities


class StartUpUtil:
    """
    This is the main class that will coordinate all our sensors and behavior
    """
    
    def __init__(self):
        """
        Constructor
        """
        # Event execute queue
        self.event_queue = []

        # Is bot launching
        self.is_preparing = False

        # Bot first trigger start time
        self.start_timestamps = 0

        self.data_request_data = None

    def initialize(self, botengine):
        """
        Initialize the controller.
        This is mandatory to call once for each new execution of the bot
        :param botengine: BotEngine environment
        """
        return

    def reset(self):
        """
        Reset bot preparing status, triggered event start times, events.(No need to reset data request event)
        """
        self.is_preparing = False
        self.start_timestamps = 0
        self.event_queue.clear()
        self.data_request_data = None

    def queue_triggers(self, triggers):
        """
        Queue the event triggers.
        :param triggers: event triggers
        """
        self.event_queue.append(triggers)

    def is_bot_preparing(self):
        """
        Bot is preparing or not.
        """
        return self.is_preparing

    def set_is_preparing(self, is_preparing):
        """
        Set Bot is preparing or not.
        """
        self.is_preparing = is_preparing

    def set_start_time(self, botengine):
        """
        Set bot start time.
        """
        if self.start_timestamps == 0:
            self.start_timestamps = botengine.get_timestamp()

    def has_pending_data_request(self):
        return self.data_request_data is not None

    def set_data_request_data(self, data_block):
        """
        Save data request data block
        """
        self.data_request_data = data_block

    def is_something_wrong(self, botengine):
        """
        Bot may crashed and the startup may be always in preparing status.
        :param botengine: BotEngine environment
        """
        return (botengine.get_timestamp() - self.start_timestamps) > utilities.ONE_MINUTE_MS * 3
