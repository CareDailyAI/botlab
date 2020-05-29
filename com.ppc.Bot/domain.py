'''
Created on May 25, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# Organization short name, which allows us to send emails to this organization's administrators
ORGANIZATION_SHORT_NAME = "family"

# NOTE: Name of the service
SERVICE_NAME = "People Power Family"

# Name of the pack of products people can purchase
PACK_NAME = "Family Pack"

# URL to purchase the pack of products
PACK_PURCHASE_URL = ""

# Professional Monitoring Subscription Name
PROFESSIONAL_MONITORING_SUBSCRIPTION_NAME = "Avantguard"

# Professional Monitoring Callback Number
PROFESSIONAL_MONITORING_CALLBACK_NUMBER = "1-844-950-0582"

# Notification case-sensitive brand, which can be different from the organization short name. Use this to force a specific branded template.
# See https://presence.atlassian.net/wiki/spaces/CLOUD/pages/23385710/Branding+Configuration
ORGANIZATION_BRAND = ""

# Default language for this brand
DEFAULT_LANGUAGE = 'en'

# Default timezone for this brand
DEFAULT_TIMEZONE = 'US/Pacific'

# MixPanel token
MIXPANEL_TOKEN = None

# Amplitude tokens
AMPLITUDE_TOKENS = {
    "app.presencepro.com": "",
    "sboxall.presencepro.com": ""
}

# iOS download URL
APP_IOS_URL = ""

# Android download URL
APP_ANDROID_URL = ""

# Customer support scheduling URL
CUSTOMER_SUPPORT_URL = ""

# True to declare that the people who run this service are part of a "drug trial" and in the control group
DRUG_TESTING_CONTROL_GROUP = False

# True to allow security events to escalate to professional monitoring. False to keep it trusted circle monitored.
ALLOW_PROFESSIONAL_MONITORING_SECURITY = False

# True to allow the emergency call center to be contacted twice if the action plan calls for it, usually to dispatch.
ALLOW_SECONDARY_PROFESSIONAL_MONITORING = True

# Available services to tailor messaging to the users
CARE_SERVICES = True
ENERGY_SERVICES = True
SECURITY_SERVICES = True

# True if this brand can support a siren.
HAS_SIREN = True

# Automatic tagging for people who run this service.
ADD_TAGS = []
REMOVE_TAGS = []

# User facing modes. { "MODE": "User Facing Name" }
USER_FACING_MODES = {
    "HOME": "OFF",
    "AWAY": "AWAY",
    "STAY": "STAY",
    "TEST": "TEST"
}
