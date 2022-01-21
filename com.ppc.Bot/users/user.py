"""
Created on July 2, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Edward Liu
"""

import index
import importlib

class User:
    """
    The User class tracks information about an individual user associated with this location.
    """

    # Location Access Levels
    LOCATION_ACCESS_NONE = 0
    LOCATION_ACCESS_READ = 10
    LOCATION_ACCESS_CONTROL = 20
    LOCATION_ACCESS_ADMIN = 30

    # Alert Texting Categories
    ALERT_CATEGORY_NOALERTS = 0
    ALERT_CATEGORY_RESIDENT = 1
    ALERT_CATEGORY_SUPPORTER = 2
    ALERT_CATEGORY_SOCIALONLY = 3


    def __init__(self, botengine, user_id):
        """
        User constructor. Not all user fields are available to bots - especially contact information.
        https://iotapps.docs.apiary.io/reference/locations/location-users

        It is expected that a controlling object (location.py) will initialize the information for this user.

        :param botengine: BotEngine environment
        :param user_id: User ID
        """
        # User id
        self.user_id = user_id

        # First name
        self.first_name = ""

        # Last name
        self.last_name = ""

        # Location Access
        self.location_access = None

        # Alert Category
        self.alert_category = None

        # Preferred language
        self.language = None

        # This is set with the location
        self.location_object = None

    def initialize(self, botengine):
        """
        Initialize this object

        NOTE: YOU CANNOT CHANGE THE CLASS NAME OF A MICROSERVICE AT THIS TIME.
        Microservice changes will be identified through different 'module' names only. If you change the class name, it is currently ignored.
        This can be revisited in future architecture changes, noted below.

        The correct behavior is to create the object, then initialize() it every time you want to use it in a new bot execution environment
        """

    def new_version(self, botengine):
        """
        New version deployed
        :param botengine:
        :return:
        """
        return

    def initialize(self, botengine):
        """
        Initialize this object
        :param botengine:
        :return:
        """
        return

    def destroy(self, botengine):
        """
        This user object is getting destroyed
        :param botengine:
        :return:
        """
        return

    def user_role_updated(self, botengine, user_id, role, alert_category, location_access, previous_alert_category, previous_location_access):
        """
        A user changed roles
        :param botengine: BotEngine environment
        :param user_id: User ID that changed roles
        :param alert_category: User's current alert/communications category (1=resident; 2=supporter)
        :param location_access: User's access to the location and devices. (0=None; 10=read location/device data; 20=control devices and modes; 30=update location info and manage devices)
        :param previous_alert_category: User's previous category, if any
        :param previous_location_access: User's previous access to the location, if any
        """
        return
