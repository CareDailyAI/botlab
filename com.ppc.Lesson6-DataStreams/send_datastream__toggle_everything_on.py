#!/usr/bin/env python
# encoding: utf-8
'''
Created on June 19, 2016

@author: David Moss
'''

# input function behaves differently in Python 2.x and 3.x. And there is no raw_input in 3.x.
if hasattr(__builtins__, 'raw_input'):
    input = raw_input

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
    parser.add_argument("-b", "--brand", dest="brand", help="Brand name partner to interact with the correct servers: 'myplace', 'origin', 'presence', etc.")
    parser.add_argument("-s", "--server", dest="server", help="Base server URL (app.presencepro.com)")
    parser.add_argument("--httpdebug", dest="httpdebug", action="store_true", help="HTTP debug logger output");

    # Process arguments
    args = parser.parse_args()

    # Extract the arguments
    username = args.username
    password = args.password
    server = args.server
    httpdebug = args.httpdebug
    brand = args.brand

    if brand is not None:
        brand = brand.lower()
        if brand == 'presence':
            print(Color.BOLD + "\nPresence by People Power" + Color.END)
            server = "app.presencepro.com"

        elif brand == 'myplace':
            print(Color.BOLD + "\nMyPlace - Smart. Simple. Secure." + Color.END)
            server = "iot.peoplepowerco.com"

        elif brand == 'origin':
            print(Color.BOLD + "\nOrigin Home HQ" + Color.END)
            server = "app.originhomehq.com.au"

        elif brand == 'innogy':
            print(Color.BOLD + "\ninnogy SmartHome" + Color.END)
            server = "innogy.presencepro.com"

        else:
            sys.stderr.write("This brand does not exist: " + str(brand) + "\n\n")
            return 1

    # Define the bot server
    if not server:
        server = "https://app.presencepro.com"

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
    app_key, user_info = _login(server, username, password)


    #===============================================================================
    # This is where we actually form and send the data stream message
    #===============================================================================
    content = {
        "on": True
    }

    send_datastream_message(server, app_key, "toggle_everything", content)
    print("Done!")



def send_datastream_message(server, app_key, address, content):
    """
    Send a datastream message
    :param server: Server to deliver the message to
    :param app_key: User's API key
    :param address: Data stream address
    :param content: Data stream content dictionary
    :return:
    """
    http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}

    params = {
        "address": address,
        "organizational": 1
    }

    body = {
        "feed": content
    }

    r = requests.post(server + "/cloud/appstore/stream/", params=params, data=json.dumps(body), headers=http_headers)
    j = json.loads(r.text)
    _check_for_errors(j)


def _login(server, username, password):
    """
    Login to the user's account to retrieve an API key.
    :param server: Server to log into
    :param username: Username
    :param password: Password
    :return: API key, JSON content
    """

    if not username:
        username = input('Email address: ')

    if not password:
        import getpass
        password = getpass.getpass('Password: ')

    try:
        import requests

        # login by username and password
        http_headers = {"PASSWORD": password, "Content-Type": "application/json"}
        r = requests.get(server + "/cloud/json/login", params={"username": username}, headers=http_headers)
        j = json.loads(r.text)
        _check_for_errors(j)
        app_key = j['key']

        # get user info
        http_headers = {"PRESENCE_API_KEY": app_key, "Content-Type": "application/json"}
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
    """
    Check for errors in the JSON response from API calls to the server.
    This will raise an exception if something goes wrong.
    :param json_response: JSON content
    """
    if not json_response:
        raise BotError("No response from the server!", -1)

    if json_response['resultCode'] > 0:
        msg = "Unknown error!"
        if 'resultCodeMessage' in json_response.keys():
            msg = json_response['resultCodeMessage']
        elif 'resultCodeDesc' in json_response.keys():
            msg = json_response['resultCodeDesc']
        raise BotError(msg, json_response['resultCode'])

    del (json_response['resultCode'])


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


if __name__ == "__main__":
    sys.exit(main())









