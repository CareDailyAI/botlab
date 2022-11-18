#!/usr/bin/env python
# encoding: utf-8
'''
Created on February 7th, 2022

@author: Parth Agrawal
'''

# This module will emulate a light switch device.

import requests
import sys
import json
import threading
import time
import logging
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

_https_proxy = None

# input function behaves differently in Python 2.x and 3.x. And there is no raw_input in 3.x.
if hasattr(__builtins__, 'raw_input'):
    input=raw_input

def main(argv=None):

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("-d", "--deviceId", dest="deviceId", help="Globally unique device ID")
    parser.add_argument("-u", "--username", dest="username", help="Username")
    parser.add_argument("-p", "--password", dest="password", help="Password")
    parser.add_argument("-s", "--server", dest="server", help="Base server URL (app.peoplepowerco.com)")
    parser.add_argument("-b", "--brand", dest="brand", help="Brand name partner to interact with the correct servers: 'myplace', 'origin', 'presence', etc.")
    parser.add_argument("-l", "--location", dest="location_id", help="Location ID")
    parser.add_argument("--httpdebug", dest="httpdebug", action="store_true", help="HTTP debug logger output")
    parser.add_argument("--https_proxy", dest="https_proxy", help="If your corporate network requires a proxy, type in the full HTTPS proxy address here (i.e. http://10.10.1.10:1080)")

    # Process arguments
    args = parser.parse_args()

    # Extract the arguments
    deviceId = args.deviceId
    username = args.username
    password = args.password
    server = args.server
    httpdebug = args.httpdebug
    locationId = args.location_id



    if not deviceId:
        deviceId = input('Specify a globally unique device ID for this virtual device: ')

    global _https_proxy
    _https_proxy = None
    if args.https_proxy is not None:
        _https_proxy = {
            'https': args.https_proxy
        }

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

    # Grab the device server
    device_server = _get_ensemble_server_url(server, deviceId)

    # Login to your user account
    app_key = _login(server, username, password)


    # This is the device type of this virtual device
    deviceType = 2000

    # Grab the user's primary location ID

    # Register the virtual device to your user's account
    _register_device(server, app_key, locationId, deviceId, deviceType, "Virtual Vayyar")

    # Persistent connection to listen for commands
    # This light switch device does not receive commands, keeping this code here for templating purposes.
    # t = threading.Thread(target=_listen, args=(device_server, deviceId))
    # t.start()


    # Menu to send data
    t = threading.Thread(target=_menu, args=(device_server, deviceId))
    t.start()

def _menu(device_server, device_id):
    """Print the menu of commands and let the user select a command"""
    print("test in")
    while True:
        print("\n\n")
        print("[" + device_id + "]: Virtual Vayyar")
        print("0 - Fall Calling")
        print("1 - Fall Finished")
        print("2 - Occupied")
        print("3 - Unoccupied")

        try:
            value = int(input('> '))

            if value == 0:
                _do_command(device_server, device_id, [{"name": "fallStatus", "value": "calling"}])
            if value == 1:
                _do_command(device_server, device_id, [{"name": "fallStatus", "value": "fall_exit"}])
            if value == 2:
                _do_command(device_server, device_id, [{"name": "occupancyTarget", "value": "0:100,100,100"}, {"name": "occupied", "value": "1"}])
                _do_command(device_server, device_id, [{"name": "occupancyTarget", "value": "0:100,100,101"}, {"name": "occupied", "value": "1"}])
            if value == 3:
                _do_command(device_server, device_id, [{"name": "occupied", "value": "0"}])


        except ValueError:
            print("???")

def _do_command(device_server, device_id, params):
    '''Send a command to the server
    :params device_server: Server to use
    :params device_id: Device ID to command
    :params value: Value to send
    '''
    global _https_proxy
    measurementPayload = {
        "version": 2,
        "sequenceNumber": 1,
        "proxyId": device_id,
        "measures": [
            {
                "deviceId": device_id,
                "params": params
            }
        ]
    }

    http_headers = {"Content-Type": "application/json"}
    print("Sending measurement: " + str(measurementPayload))
    r = requests.post(device_server + "/deviceio/mljson", headers=http_headers,
                      data=json.dumps(measurementPayload), proxies=_https_proxy)
    print("Sent: " + str(r.text))

def _listen(device_server, deviceId):
    """Listen for commands"""
    global _https_proxy
    while True:
        try:
            print("\n[" + deviceId + "]: Listening for commands")
            http_headers = {"Content-Type": "application/json"}
            r = requests.get(device_server + "/deviceio/mljson", params={"id": deviceId, "timeout": 60},
                             headers=http_headers, timeout=60, proxies=_https_proxy)
            command = json.loads(r.text)
            print("[" + deviceId + "]: Command received: " + str(command))

            # Ack the command
            commandId = command['commands'][0]['commandId']
            ackPayload = {"version": 2, "proxyId": deviceId, "sequenceNumber": 1,
                          "responses": [{"commandId": commandId, "result": 1}]}
            result = requests.post(device_server + "/deviceio/mljson", headers=http_headers,
                                   data=json.dumps(ackPayload), proxies=_https_proxy)

        except Exception as e:
            print("Exception: " + str(e))
            time.sleep(1)

def _login(server, username, password, admin=False):
    """
    Login and obtain an API key
    :param server: Server address
    :param username: Username
    :param password: Password
    :return: API Key
    """

    global _https_proxy
    import pickle

    if not username:
        username = input('Email address: ')

    if not password:
        import getpass
        password = getpass.getpass()

    try:
        import requests

        type = "user"
        if admin:
            type = "admin"

        fixed_server = server.replace("http://", "").replace("https://", "").split(".")[0]

        filename = "{}.{}.{}".format(username, fixed_server, type)

        if os.path.isfile(filename):
            try:
                with open(filename, 'rb') as f:
                    key = pickle.load(f)

                params = {
                    "keyType": 0
                }

                if admin:
                    params['keyType'] = 11
                    params['expiry'] = 2

                http_headers = {"API_KEY": key, "Content-Type": "application/json"}
                r = requests.get(server + "/cloud/json/loginByKey", params=params, headers=http_headers,
                                 proxies=_https_proxy)
                j = json.loads(r.text)

                if j['resultCode'] == 0:
                    key = j['key']

                    with open(filename, 'wb') as f:
                        pickle.dump(key, f)

                    return key

            except ValueError:
                # Can't unpickle the local file.
                # This happens as we switch back to Python 2.7 from Python 3.7.
                pass

        params = {
            "username": username
        }

        if admin:
            params['keyType'] = 11

        http_headers = {"PASSWORD": password, "Content-Type": "application/json"}
        r = requests.get(server + "/cloud/json/login", params=params, headers=http_headers, proxies=_https_proxy)
        j = json.loads(r.text)

        if j['resultCode'] == 17:
            passcode = input('Type in the passcode you received on your phone: ')

            passcode = passcode.upper()

            params['expiry'] = 2
            http_headers['passcode'] = passcode
            del http_headers['PASSWORD']
            r = requests.get(server + "/cloud/json/login", params=params, headers=http_headers,
                             proxies=_https_proxy)
            j = json.loads(r.text)

            if j['resultCode'] == 0:
                key = j['key']

                with open(filename, 'wb') as f:
                    pickle.dump(key, f)

        _check_for_errors(j)

        return j['key']

    except BotError as e:
        sys.stderr.write("BotEngine Error: " + e.msg)
        sys.stderr.write("\nCreate an account on " + server + " and use it to sign in")
        sys.stderr.write("\n\n")
        raise e

    # except Exception:
    #    sys.stderr.write(Color.RED + "Error trying to contact the server.\n\n" + Color.END)
    #    exit(1)

def _register_device(server, appKey, locationId, deviceId, deviceType, description):
    """
    Register a device to the user's account
    """
    global _https_proxy
    http_headers = {"API_KEY": appKey, "Content-Type": "application/json"}
    r = requests.post(server + "/cloud/json/devices",
                      params={"locationId": locationId, "deviceId": deviceId, "deviceType": deviceType,
                              "desc": description}, headers=http_headers, proxies=_https_proxy)
    j = json.loads(r.text)
    _check_for_errors(j)
    return j

def _get_ensemble_server_url(server, device_id=None):
    """
    Get server URL
    """
    global _https_proxy
    import requests
    http_headers = {"Content-Type": "application/json"}
    params = {"type": "deviceio", "ssl": True}
    if not device_id:
        # to be removed
        params['deviceId'] = "nodeviceid"
    else:
        params['deviceId'] = device_id
    r = requests.get(server + "/cloud/json/settingsServer", params=params, headers=http_headers,
                     proxies=_https_proxy)
    return r.text

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

    del (json_response['resultCode'])

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

 # ===============================================================================
# Color Class for CLI
# ===============================================================================
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
