#!/usr/bin/env python
# encoding: utf-8
'''
Created on Febuary 21, 2024

@author: Destry Teeter
'''

# Data Stream Address
DATASTREAM_ADDRESS = "update_daily_report_gpt_report_types"

# Default report types
DEFAULT_REPORT_TYPES = [
    {
        "id": 0,
        "role_type": 2,
        "assistant_example": "Digs had a low-average trips, little bit of wiggle room, but nothing major. Mostly chillin' recently.",
        "rules": [
            "Provide a concise summary in less than 30 words.",
            "Use slang.",
        ],
        "supported_section_ids": [
            "wellness",
            # "alerts",
            # "notes",
            # "tasks",
            # "sleep",
            # "activities",
            # "meals",
            # "medication",
            # "bathroom",
            # "social",
            # "memories",
            # "system",
        ],
        "supported_trend_ids": [
            # "trend.sleep_score", 
            # "trend.bedtime_score", 
            # "trend.wakeup_score", 
            # "trend.restlessness_score", 
            "trend.wellness_score", 
            # "trend.mobility_score",
            # "trend.stability_score",
            # "trend.hygiene_score", 
            # "trend.bathroom_score",
            # "trend.social_score", 
            # "trend.care_score",
            # "trend.illbeing_score",
            # "trend.positivity_score",
            # "trend.sleep_diary",
            # "trend.percieved_stress_scale",
            # "trend.total_falls", 
            # "trend.fall_duration",
            # "trend.bedtime", 
            # "trend.sleep_bathroom_visits", 
            # "trend.sleep_duration", 
            # "trend.wakeup", 
            # "trend.sleep_movement", 
            # "trend.nap_duration",
            # "trend.mobility_duration", 
            # "trend.mobility_rooms", 
            # "sitting",
            # "trend.bathroom_visits", 
            # "trend.bathroom_duration", 
            # "trend.shower_visits", 
            # "trend.absent", 
            # "trend.checkedin", 
            # "trend.visitor", 
            # "trend.together", 
            # "occupancy.return_ms"
        ],
        "supported_insight_ids": [
            # "care.inactivity.bedtime_awake_too_late", 
            # "sleep.low_sleep_quality.warning", 
            # "sleep.too_many_bathrooms.warning", 
            # "care.inactivity.time_to_stretch", 
            # "care.inactivity.warning", 
            # "care.inactivity.good_morning_sleeping_in", 
            # "care.inactivity.good_morning_problem_critical", 
            # "care.inactivity.good_morning_problem", 
            # "care.inactivity.not_back_home.warning", 
            # "request_assistance", 
            # "care.sms_sos", 
            # "health_high_heart_rate_warning", 
            # "health_movement_confirmed_alert", 
            # "vayyar.fall_confirmed_alert", 
            # "vayyar.stability_event_confirmed_alert",
            # "sleep.duration_ms", 
            # "sleep.bedtime_ms", 
            # "sleep.wakeup_ms", 
            # "sleep.sleep_score", 
            # "sleep.underslept", 
            # "sleep.overslept", 
            # "sleep.bedtime_score", 
            # "sleep.wakeup_ms", 
            # "sleep.restlessness_score", 
            # "sleep.sleep_prediction_ms", 
            # "sleep.wake_prediction_ms",
            # "security_mode", 
            # "occupancy.status"
        ]
    },
    {
        "id": 1,
        "role_type": 4,
        "assistant_example": "In a 30-day period, this residence recorded an average of 0.2 potential falls, with a high variability as indicated by a standard deviation of 1.4. The standard score of 0.67 suggests the data is slightly above the mean. The information suggests fluctuating fall risks within this setting.",
        "rules": [
            "Provide a concise summary in less than 100 words.",
            "Use medical terminology.",
        ],
        "supported_section_ids": [
            "wellness",
            # "alerts",
            # "notes",
            # "tasks",
            # "sleep",
            # "activities",
            # "meals",
            # "medication",
            # "bathroom",
            # "social",
            # "memories",
            # "system",
        ],
        "supported_trend_ids": [
            "trend.sleep_score", 
            "trend.bedtime_score", 
            "trend.wakeup_score", 
            "trend.restlessness_score", 
            "trend.wellness_score", 
            "trend.mobility_score",
            "trend.stability_score",
            "trend.hygiene_score", 
            "trend.bathroom_score",
            "trend.social_score", 
            "trend.care_score",
            # "trend.illbeing_score",
            # "trend.positivity_score",
            # "trend.sleep_diary",
            # "trend.percieved_stress_scale",
            # "trend.total_falls", 
            # "trend.fall_duration",
            # "trend.bedtime", 
            # "trend.sleep_bathroom_visits", 
            # "trend.sleep_duration", 
            # "trend.wakeup", 
            # "trend.sleep_movement", 
            # "trend.nap_duration",
            # "trend.mobility_duration", 
            # "trend.mobility_rooms", 
            # "sitting",
            # "trend.bathroom_visits", 
            # "trend.bathroom_duration", 
            # "trend.shower_visits", 
            # "trend.absent", 
            # "trend.checkedin", 
            # "trend.visitor", 
            # "trend.together", 
            # "occupancy.return_ms"
        ],
        "supported_insight_ids": [
            # "care.inactivity.bedtime_awake_too_late", 
            # "sleep.low_sleep_quality.warning", 
            # "sleep.too_many_bathrooms.warning", 
            # "care.inactivity.time_to_stretch", 
            # "care.inactivity.warning", 
            # "care.inactivity.good_morning_sleeping_in", 
            # "care.inactivity.good_morning_problem_critical", 
            # "care.inactivity.good_morning_problem", 
            # "care.inactivity.not_back_home.warning", 
            # "request_assistance", 
            # "care.sms_sos", 
            # "health_high_heart_rate_warning", 
            # "health_movement_confirmed_alert", 
            # "vayyar.fall_confirmed_alert", 
            # "vayyar.stability_event_confirmed_alert",
            # "sleep.duration_ms", 
            # "sleep.bedtime_ms", 
            # "sleep.wakeup_ms", 
            # "sleep.sleep_score", 
            # "sleep.underslept", 
            # "sleep.overslept", 
            # "sleep.bedtime_score", 
            # "sleep.wakeup_ms", 
            # "sleep.restlessness_score", 
            # "sleep.sleep_prediction_ms", 
            # "sleep.wake_prediction_ms",
            # "security_mode", 
            # "occupancy.status"
        ]
    },
]

# Default system rules
DEFAULT_SYSTEM_RULES = [
    "You will be provided with statistical data for a single residence.",
]

# Data Stream Content
DATASTREAM_CONTENT = {
    "report_types": DEFAULT_REPORT_TYPES,
    "system_rules": DEFAULT_SYSTEM_RULES,
}


# input function behaves differently in Python 2.x and 3.x. And there is no raw_input in 3.x.
if hasattr(__builtins__, 'raw_input'):
    input=raw_input

import requests
import sys
import json
import logging

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

def main(argv=None):

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
        
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    
    parser.add_argument("-u", "--username", dest="username", help="Username")
    parser.add_argument("-p", "--password", dest="password", help="Password")
    parser.add_argument("-s", "--server", dest="server", help="Base server URL (app.peoplepowerco.com)")
    parser.add_argument("-l", "--location", dest="location_id", help="Location ID")
    parser.add_argument("-a", "--api_key", dest="apikey", help="User's API key instead of a username/password")
    parser.add_argument("--httpdebug", dest="httpdebug", action="store_true", help="HTTP debug logger output");
    
    # Process arguments
    args, unknown = parser.parse_known_args()
    
    # Extract the arguments
    username = args.username
    password = args.password
    server = args.server
    httpdebug = args.httpdebug
    app_key = args.apikey
    location_id = args.location_id

    if location_id is not None:
        location_id = int(location_id)
        print(Color.BOLD + "Location ID: {}".format(location_id) + Color.END)

    # Define the bot server
    if not server:
        server = "https://app.peoplepowerco.com"
    
    if "http" not in server:
        server = "https://" + server

    # HTTP Debugging
    if httpdebug:
        try:
            import http.client as http_client
                
        except ImportError:
            # Python 2
            import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1
                    
        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        
    # Login to your user account
    if app_key is None:
        app_key, user_info = _login(server, username, password)

    send_datastream_message(server, app_key, location_id, DATASTREAM_ADDRESS, DATASTREAM_CONTENT)
    print("Done!")
    
    
def send_datastream_message(server, app_key, location_id, address, content):
    http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}
    
    params = {
              "address": address,
              "scope": 1,
              "locationId": location_id
              }
    
    body = {
        "feed": content
        }
    
    print("Body: " + json.dumps(body, indent=2, sort_keys=True))
    print("Server: " + server)
    
    r = requests.post(server + "/cloud/appstore/stream", params=params, data=json.dumps(body), headers=http_headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    print(str(r.text))
    
    
def _login(server, username, password):
    """Get an Bot API key and User Info by login with a username and password"""

    if not username:
        username = raw_input('Email address: ')
        
    if not password:
        import getpass
        password = getpass.getpass('Password: ')
    
    try:
        import requests

        # login by username and password
        http_headers = {"PASSWORD": password, "Content-Type": "application/json"}
        r = requests.get(server + "/cloud/json/login", params={"username":username}, headers=http_headers)
        j = json.loads(r.text)
        _check_for_errors(j)
        app_key = j['key']

        # get user info
        http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}
        r = requests.get(server + "/cloud/json/user", headers=http_headers)
        j = json.loads(r.text)
        _check_for_errors(j)
        return app_key, j

    except BotError as e:
        sys.stderr.write("Error: " + e.msg)
        sys.stderr.write("\nCreate an account on " + server + " and use it to sign in")
        sys.stderr.write("\n\n")
        raise e
    
    

def _check_for_errors(json_response):
    """Check some JSON response for BotEngine errors"""
    if not json_response:
        raise BotError("No response from the server!", -1)
    
    if json_response['resultCode'] > 0:
        msg = "Unknown error!"
        if 'resultCodeMessage' in json_response.keys():
            msg = json_response['resultCodeMessage']
        elif 'resultCodeDesc' in json_response.keys():
            msg = json_response['resultCodeDesc']
        raise BotError(msg, json_response['resultCode'])

    del(json_response['resultCode'])
    
    
    
class BotError(Exception):
    """BotEngine exception to raise and log errors."""
    def __init__(self, msg, code):
        super(BotError).__init__(type(self))
        self.msg = msg
        self.code = code
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg


#===============================================================================
# Color Class for CLI
#===============================================================================
class Color:
    """Color your command line output text with Color.WHATEVER and Color.END"""
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

if __name__ == "__main__":
    sys.exit(main())




