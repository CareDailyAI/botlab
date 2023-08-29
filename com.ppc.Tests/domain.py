'''
Created on May 25, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import utilities.utilities as utilities


############### BRANDING AND ORGANIZATION ###############
# Organization short name, which allows us to send emails to this organization's administrators
ORGANIZATION_SHORT_NAME = "acme"

# NOTE: Name of the service
SERVICE_NAME = "ACME Service"

# Notification case-sensitive brand, which can be different from the organization short name. Use this to force a specific branded template.
ORGANIZATION_BRAND = "acme"

# Default language for this brand
DEFAULT_LANGUAGE = 'en'

# Default timezone for this brand
DEFAULT_TIMEZONE = 'US/Pacific'

# Dashboard title comments for the 'last seen' service which runs all the time
LAST_SEEN_DASHBOARD = [
            "Looking Good",
            "Everything Looks Fine",
            "All Right",
            "Going Well",
            "All Good Here",
            "All Good",
            "Okay",
            "No Problems Found",
            "Things are Good",
            "Good"
        ]

# Name of the chat bot assistant
CHAT_ASSISTANT_NAME = "Arti"

############### ORGANIZATION ADMIN MONITORING ###############
# True to allow for monitoring by organizational administrators via email alerts
ALLOW_ADMINISTRATIVE_MONITORING = True

# Don't contact admins before this hour of the day
DO_NOT_CONTACT_ADMINS_BEFORE_RELATIVE_HOUR = 0.0

# Don't contact admins after this hour of the day
DO_NOT_CONTACT_ADMINS_AFTER_RELATIVE_HOUR = 24.0

# Timezone admins are in
ADMIN_DEFAULT_TIMEZONE = "US/Pacific"

# Command Center URLs
COMMAND_CENTER_URLS = {
    "app.peoplepowerco.com": "https://app.caredaily.ai",
    "sboxall.peoplepowerco.com": "https://app-sbox.caredaily.ai"
}


############### CONFIGURATION ###############

# Available services to tailor messaging to the users
CARE_SERVICES = True

# User facing modes. { "MODE": "User Facing Name" }
USER_FACING_MODES = {
    "HOME": "OFF",
    "AWAY": "AWAY",
    "STAY": "STAY",
    "TEST": "TEST"
}

############### ANALYTICS ###############
# MixPanel token
MIXPANEL_TOKEN = None

# Amplitude tokens
AMPLITUDE_TOKENS = {
    "app.peoplepowerco.com": "",
    "sboxall.peoplepowerco.com": ""
}


############### APP DOWNLOAD ###############
# iOS download URL
APP_IOS_URL = "https://apple.co/3PEaSnK"

# Android download URL
APP_ANDROID_URL = "https://play.google.com/store/apps/details?id=com.peoplepowerco.family"

############### CUSTOMER SUPPORT ###############
# Customer support calendar scheduling and assisted connect URL
CS_SCHEDULE_URL = "https://calendly.com/d/gsc-qhr-nhd/assisted-connection-session"

# Customer support email
CS_EMAIL_ADDRESS = "support@peoplepowerco.com"

# Customer support phone number
CS_PHONE_NUMBER = None

# After creating a new location and firing up the bot for the first time, how long do we wait before suggesting a virtual install session?
CS_VIRTUAL_CONNECT_SMS_DELAY_MS = utilities.ONE_HOUR_MS * 4
