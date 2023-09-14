#!/usr/bin/env python
# encoding: utf-8
'''
Created on September 24, 2019

@author: David Moss
'''

import time

# Time conversions to ms
ONE_SECOND_MS = 1000
ONE_MINUTE_MS = 60 * ONE_SECOND_MS
ONE_HOUR_MS = ONE_MINUTE_MS * 60
ONE_DAY_MS = ONE_HOUR_MS * 24
ONE_WEEK_MS = ONE_DAY_MS * 7
ONE_MONTH_MS = ONE_DAY_MS * 30
ONE_YEAR_MS = ONE_DAY_MS * 365

# Timestamped commands
COMMAND_DELETE = -2
COMMAND_SET_STATUS_HIDDEN = -1
COMMAND_SET_STATUS_GOOD = 0
COMMAND_SET_STATUS_WARNING = 1
COMMAND_SET_STATUS_CRITICAL = 2

# Data Stream Address
DATASTREAM_ADDRESS = "update_dashboard_content"


# # Data Stream Content
# DATASTREAM_CONTENT = {
#     "type": 0,
#     "title": "NOW",
#     "weight": 0,
#     "content": {
#         "status": 0,
#         "comment": "Left the house once today.",
#         "weight": 25,
#         "id": "leave",
#         "icon": "house-leave",
#         "icon_font": "far",
#         "alarms": {
#             int(time.time() * 1000) + (ONE_SECOND_MS * 600): COMMAND_DELETE,
#         }
#     }
# }


# # Data Stream Content
# DATASTREAM_CONTENT = {
#     "type": 0,
#     "title": "NOW",
#     "weight": 0,
#     "content": {
#         "status": 0,
#         "comment": "81% sleep score.",
#         "weight": 20,
#         "id": "sleep",
#         "icon": "snooze",
#         "icon_font": "far",
#         "alarms": {
#             int(time.time() * 1000) + (ONE_SECOND_MS * 600): COMMAND_DELETE,
#         }
#     }
# }

# Data Stream Content
# DATASTREAM_CONTENT = {
#     "type": 0,
#     "title": "NOW",
#     "weight": 0,
#     "content": {
#         "status": 0,
#         "comment": "Judy Bessee reached out today.",
#         "weight": 30,
#         "id": "temporary",
#         "icon": "comment-smile",
#         "icon_font": "far",
#         "alarms": {
#             int(time.time() * 1000) + (ONE_SECOND_MS * 600): COMMAND_DELETE,
#         }
#     }
# }

DATASTREAM_CONTENT = {
    "type": 0,
    "title": "NOW",
    "weight": 0,
    "content": {
        "status": 0,
        "comment": "Accessed morning medication",
        "weight": 40,
        "id": "pills",
        "icon": "pills",
        "icon_font": "far",
        "alarms": {
            int(time.time() * 1000) + (ONE_SECOND_MS * 600): COMMAND_DELETE,
        }
    }
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
    
    r = requests.post(server + "/cloud/appstore/stream/", params=params, data=json.dumps(body), headers=http_headers)
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




