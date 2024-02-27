#!/usr/bin/env python
# encoding: utf-8
'''
Created on January 4, 2019

@author: David Moss
'''

# Data Stream Address
DATASTREAM_ADDRESS = "conversation_resolved"

# Data Stream Content
DATASTREAM_CONTENT = {
    "microservice_id": None,
    "conversation_id": None,
    "answer": 0
}


# input function behaves differently in Python 2.x and 3.x. And there is no raw_input in 3.x.
if hasattr(__builtins__, 'raw_input'):
    input=raw_input

import requests
import sys
import json
import logging
import time

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
        app_key = login(server, username, password)
    user_info = get_user_info(server, app_key)

    while True:
        dashboard_header = get_state(server, app_key, location_id, "dashboard_header")['value']

        # buttons[#] = {content}
        buttons = {}

        print("\n\nDASHBOARD (CMD+Z to quit)")
        print("=" * 50)
        print("\tIcon: {}".format(dashboard_header['icon']))
        print("\tTitle: {}".format(dashboard_header['title']))
        print("\tComment: {}".format(dashboard_header['comment']))
        if 'ecc' in dashboard_header:
            if dashboard_header['ecc'] and dashboard_header['call']:
                print("\t({}) Button: [Emergency Call Center]".format(len(buttons)))
                buttons[len(buttons)] = {
                    "address": "contact_ecc",
                    "content": {
                        "user_id": user_info['user']['id']
                    }
                }

        if 'resolution' in dashboard_header:
            resolution = dashboard_header['resolution']
            datastream_address = resolution['datastream_address']
            for r in resolution['response_options']:
                print("\t({}) Button: [{}]".format(len(buttons), r['text']))
                buttons[len(buttons)] = {
                    "address": datastream_address,
                    "content": {**resolution['content'], **r['content'], **{"user_id": user_info['user']['id']}}
                }

        minutes_ago = round((int(time.time() * 1000) - dashboard_header['updated_ms']) / 1000 / 60, 2)
        print("\nUpdated {} minutes ago.".format(minutes_ago))
        print("=" * 50)

        if len(buttons) > 0:
            answer = input("\nPress Button (R to refresh; Q to quit): ")
        else:
            answer = input("\nR to Refresh; Q to Quit: ")

        if 'q' == answer.lower():
            exit(0)

        if 'r' == answer.lower() or '' == answer.lower():
            continue

        answer = int(answer)
        if answer in buttons:
            print("Button {}".format(answer))
            print("\t=> Address: {}".format(buttons[answer]['address']))
            print("\t=> Content: {}".format(buttons[answer]['content']))
            send_datastream_message(server, app_key, location_id, buttons[answer]['address'], buttons[answer]['content'])

    print("Done!")
    

def send_datastream_message(server, app_key, location_id, address, content):
    """
    Send a data stream message
    :param server:
    :param app_key:
    :param location_id:
    :param address:
    :param content:
    :return:
    """
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
    
    
def login(server, username, password):
    """Get an Bot API key and User Info by login with a username and password"""
    if not username:
        username = input('Email address: ')
        
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

        return app_key

    except BotError as e:
        sys.stderr.write("Error: " + e.msg)
        sys.stderr.write("\nCreate an account on " + server + " and use it to sign in")
        sys.stderr.write("\n\n")
        raise e


def get_user_info(server, app_key):
    """
    Get user info
    :param server:
    :param app_key:
    :return:
    """
    # get user info
    http_headers = {
        "API_KEY": app_key,
        "Content-Type": "application/json"
    }

    r = requests.get(server + "/cloud/json/user", headers=http_headers)
    j = json.loads(r.text)
    try:
        _check_for_errors(j)
    except Exception as e:
        print("Couldn't download user info: {}".format(json.dumps(j, indent=2, sort_keys=True)))
        exit(-1)
    return j
    

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
    
def get_state(server, app_key, location_id, name):
    """
    Extract a state variable
    :param server:
    :param app_key:
    :param location_id:
    :param name:
    :return:
    """
    http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}

    params = {
        "name": name
    }

    r = requests.get(server + "/cloud/json/locations/{}/state".format(location_id), params=params, headers=http_headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    return j

    
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




