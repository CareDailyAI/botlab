#!/usr/bin/env python3
# encoding: utf-8
'''
Created on June 19, 2016

@author: David Moss
'''

# This module will emulate a light bulb device.

import requests
import sys
import json
import threading
import time
import logging

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter


def main(argv=None):

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("-d", "--deviceId", dest="deviceId", help="Globally unique device ID")
    parser.add_argument("-u", "--username", dest="username", help="Username")
    parser.add_argument("-p", "--password", dest="password", help="Password")
    parser.add_argument("-s", "--server", dest="server", help="Base server URL (app.presencepro.com)")
    parser.add_argument("--httpdebug", dest="httpdebug", action="store_true", help="HTTP debug logger output");

    # Process arguments
    args = parser.parse_args()

    # Extract the arguments
    deviceId = args.deviceId
    username = args.username
    password = args.password
    server = args.server
    httpdebug = args.httpdebug

    if not deviceId:
        sys.stderr.write("Specify a device ID for this virtual device with the -d option. Use --help for more info.")
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

    # Grab the device server
    device_server = _get_ensemble_server_url(server, deviceId)

    # Login to your user account
    app_key, user_info = _login(server, username, password)

    # This is the device type of this virtual device
    deviceType = 10071

    # Grab the user's primary location ID
    locationId = user_info['locations'][0]['id']

    # Register the virtual device to your user's account
    _register_device(server, app_key, locationId, deviceId, deviceType, "Virtual Light Bulb")

    # Persistent connection to listen for commands
    t = threading.Thread(target=_listen, args=(device_server, deviceId))
    t.start()





def _listen(device_server, deviceId):
    """Listen for commands"""
    while True:
        try:
            print("\n[" + deviceId + "]: Listening for commands")
            http_headers = {"Content-Type": "application/json"}
            r = requests.get(device_server + "/deviceio/mljson", params={"id":deviceId, "timeout":60}, headers=http_headers, timeout=60)
            command = json.loads(r.text)
            print("[" + deviceId + "]: Command received: " + str(command))

            # Ack the command
            commandId = command['commands'][0]['commandId']
            ackPayload = {"version":2, "proxyId": deviceId, "sequenceNumber": 1, "responses": [{"commandId":commandId, "result":1}]}
            result = requests.post(device_server + "/deviceio/mljson", headers=http_headers, data=json.dumps(ackPayload))

        except Exception as e:
            print("Exception: " + str(e))
            time.sleep(1)



def _login(server, username, password):
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

        # get user info
        http_headers = {"PRESENCE_API_KEY": app_key, "Content-Type": "application/json"}
        r = requests.get(server + "/cloud/json/user", headers=http_headers)
        j = json.loads(r.text)
        _check_for_errors(j)
        return app_key, j

    except ComposerError as e:
        sys.stderr.write("Error: " + e.msg)
        sys.stderr.write("\nCreate an account on " + server + " and use it to sign in")
        sys.stderr.write("\n\n")
        raise e


def _register_device(server, appKey, locationId, deviceId, deviceType, description):
    """Register a device to the user's account"""
    http_headers = {"API_KEY": appKey, "Content-Type": "application/json"}
    r = requests.post(server + "/cloud/json/devices", params={"locationId":locationId, "deviceId":deviceId, "deviceType":deviceType, "desc":description}, headers=http_headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    return j


def _get_ensemble_server_url(server, device_id=None):
    """Get Ensemble server URL"""
    import requests
    http_headers = {"Content-Type": "application/json"}
    params = {"type": "deviceio", "ssl": True}
    if not device_id:
        # to be removed
        params['deviceId'] = "nodeviceid"
    else:
        params['deviceId'] = device_id
    r = requests.get(server + "/cloud/json/settingsServer", params=params, headers=http_headers)
    return r.text


def _check_for_errors(json_response):
    """Check some JSON response for BotEngine errors"""
    if not json_response:
        raise ComposerError("No response from the server!", -1)

    if json_response['resultCode'] > 0:
        msg = "Unknown error!"
        if 'resultCodeMessage' in json_response.keys():
            msg = json_response['resultCodeMessage']
        elif 'resultCodeDesc' in json_response.keys():
            msg = json_response['resultCodeDesc']
        raise ComposerError(msg, json_response['resultCode'])

    del(json_response['resultCode'])



class ComposerError(Exception):
    """BotEngine exception to raise and log errors."""
    def __init__(self, msg, code):
        super(ComposerError).__init__(type(self))
        self.msg = msg
        self.code = code
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg


if __name__ == "__main__":
    sys.exit(main())
