#!/usr/bin/env python
# encoding: utf-8
"""
Virtual Motion Sensor Device Emulator
"""

# This module will emulate a motion sensor device.

import getpass
import json
import logging
import os
import pickle
import sys
import threading
import time
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import Dict, Optional, Any

import requests

_https_proxy: Optional[Dict[str, str]] = None

def main(argv: Optional[list] = None) -> None:
    """
    Main entry point for the virtual motion sensor device.
    
    :param argv: Command line arguments (defaults to sys.argv if None)
    """
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("-d", "--deviceId", dest="deviceId", help="Globally unique device ID")
    parser.add_argument("-u", "--username", dest="username", help="Username")
    parser.add_argument("-p", "--password", dest="password", help="Password")
    parser.add_argument("-s", "--server", dest="server", help="Base server URL (app.peoplepowerco.com)")
    parser.add_argument("-b", "--brand", dest="brand", help="Brand name partner to interact with the correct servers: 'presencefamily', etc.")
    parser.add_argument("-l", "--location", dest="location_id", help="Location ID")
    parser.add_argument("--httpdebug", dest="httpdebug", action="store_true", help="HTTP debug logger output")
    parser.add_argument("--https_proxy", dest="https_proxy", help="If your corporate network requires a proxy, type in the full HTTPS proxy address here (i.e. http://10.10.1.10:1080)")

    # Process arguments
    args = parser.parse_args()

    # Extract the arguments
    device_id = args.deviceId
    username = args.username
    password = args.password
    server = args.server
    httpdebug = args.httpdebug
    location_id = args.location_id

    if not device_id:
        device_id = input('Specify a globally unique device ID for this virtual device: ')

    global _https_proxy
    _https_proxy = None
    if args.https_proxy is not None:
        _https_proxy = {'https': args.https_proxy}

    # Define the bot server
    if not server:
        server = "https://app.peoplepowerco.com"

    if "http" not in server:
        server = f"https://{server}"

    # HTTP Debugging
    if httpdebug:
        import http.client as http_client
        http_client.HTTPConnection.debuglevel = 1

        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    # Grab the Care Daily device server
    device_server = _get_care_daily_server_url(server, device_id)

    # Login to your user account
    app_key = _login(server, username, password)

    # This is the device type of this motion sensor device
    device_type = 10038

    # Register the virtual device to your user's account
    _register_device(server, app_key, location_id, device_id, device_type, "Virtual Motion Sensor")

    # Persistent connection to listen for commands
    # This motion sensor device does not receive commands, keeping this code here for templating purposes.
    # t = threading.Thread(target=_listen, args=(device_server, device_id))
    # t.start()

    # Menu to send data
    t = threading.Thread(target=_menu, args=(device_server, device_id))
    t.start()

def _menu(device_server: str, device_id: str) -> None:
    """
    Print the menu of commands and let the user select a command.
    
    :param device_server: Server URL to send commands to
    :param device_id: Device ID for this virtual device
    """
    while True:
        print("\n\n")
        print(f"[{device_id}]: Virtual Motion Sensor")
        print("0 - No Motion Detected")
        print("1 - Motion Detected")
        print("2 - Fast toggle: No Motion / Motion / No Motion")
        print("3 - Fast toggle: No Motion / Motion / No Motion / Motion / No Motion")
        print("4 - Simulate activity: Motion detected for 5 seconds")

        try:
            value = int(input('> '))

            if value == 0 or value == 1:
                _do_command(device_server, device_id, value)
            elif value == 2:
                _do_command(device_server, device_id, 0)
                time.sleep(0.5)
                _do_command(device_server, device_id, 1)
                time.sleep(0.5)
                _do_command(device_server, device_id, 0)
            elif value == 3:
                _do_command(device_server, device_id, 0)
                time.sleep(0.5)
                _do_command(device_server, device_id, 1)
                time.sleep(0.5)
                _do_command(device_server, device_id, 0)
                time.sleep(0.5)
                _do_command(device_server, device_id, 1)
                time.sleep(0.5)
                _do_command(device_server, device_id, 0)
            elif value == 4:
                print("Simulating motion detected for 5 seconds...")
                _do_command(device_server, device_id, 1)
                time.sleep(5)
                _do_command(device_server, device_id, 0)
                print("Motion simulation complete.")

        except ValueError:
            print("???")

def _do_command(device_server: str, device_id: str, value: int) -> None:
    """
    Send a command to the server.
    
    :param device_server: Server to use
    :param device_id: Device ID to command
    :param value: Value to send (0 for no motion, 1 for motion detected)
    """
    global _https_proxy
    measurement_payload = {
        "version": 2,
        "sequenceNumber": 1,
        "proxyId": device_id,
        "measures": [
            {
                "deviceId": device_id,
                "params": [
                    {
                        "name": "motionStatus",
                        "value": value
                    }
                ]
            }
        ]
    }

    http_headers = {"Content-Type": "application/json"}
    print(f"Sending measurement: {measurement_payload}")
    r = requests.post(f"{device_server}/deviceio/mljson", headers=http_headers,
                      data=json.dumps(measurement_payload), proxies=_https_proxy)
    print(f"Sent: {r.text}")

def _listen(device_server: str, device_id: str) -> None:
    """
    Listen for commands from the server.
    
    :param device_server: Server URL to listen to
    :param device_id: Device ID for this virtual device
    """
    global _https_proxy
    while True:
        try:
            print(f"\n[{device_id}]: Listening for commands")
            http_headers = {"Content-Type": "application/json"}
            r = requests.get(f"{device_server}/deviceio/mljson", params={"id": device_id, "timeout": 60},
                             headers=http_headers, timeout=60, proxies=_https_proxy)
            command = json.loads(r.text)
            print(f"[{device_id}]: Command received: {command}")

            # Ack the command
            command_id = command['commands'][0]['commandId']
            ack_payload = {"version": 2, "proxyId": device_id, "sequenceNumber": 1,
                          "responses": [{"commandId": command_id, "result": 1}]}
            result = requests.post(f"{device_server}/deviceio/mljson", headers=http_headers,
                                   data=json.dumps(ack_payload), proxies=_https_proxy)

        except Exception as e:
            print(f"Exception: {e}")
            time.sleep(1)

def _login(server: str, username: Optional[str], password: Optional[str], admin: bool = False) -> str:
    """
    Login and obtain an API key.
    
    :param server: Server address
    :param username: Username
    :param password: Password
    :param admin: Whether to login as admin
    :return: API Key
    """
    global _https_proxy

    if not username:
        username = input('Email address: ')

    if not password:
        password = getpass.getpass()

    try:
        key_type = "admin" if admin else "user"

        fixed_server = server.replace("http://", "").replace("https://", "").split(".")[0]

        filename = f"{username}.{fixed_server}.{key_type}"

        if os.path.isfile(filename):
            try:
                with open(filename, 'rb') as f:
                    key = pickle.load(f)

                params = {"keyType": 0}

                if admin:
                    params['keyType'] = 11
                    params['expiry'] = 2

                http_headers = {"API_KEY": key, "Content-Type": "application/json"}
                r = requests.get(f"{server}/cloud/json/loginByKey", params=params, headers=http_headers,
                                 proxies=_https_proxy)
                j = json.loads(r.text)

                if j['resultCode'] == 0:
                    key = j['key']

                    with open(filename, 'wb') as f:
                        pickle.dump(key, f)

                    return key

            except (ValueError, EOFError):
                # Can't unpickle the local file.
                pass

        params = {"username": username}

        if admin:
            params['keyType'] = 11

        http_headers = {"PASSWORD": password, "Content-Type": "application/json"}
        r = requests.get(f"{server}/cloud/json/login", params=params, headers=http_headers, proxies=_https_proxy)
        j = json.loads(r.text)

        if j['resultCode'] == 17:
            passcode = input('Type in the passcode you received on your phone: ')

            passcode = passcode.upper()

            params['expiry'] = 2
            http_headers['passcode'] = passcode
            del http_headers['PASSWORD']
            r = requests.get(f"{server}/cloud/json/login", params=params, headers=http_headers,
                             proxies=_https_proxy)
            j = json.loads(r.text)

            if j['resultCode'] == 0:
                key = j['key']

                with open(filename, 'wb') as f:
                    pickle.dump(key, f)

        _check_for_errors(j)

        return j['key']

    except BotError as e:
        sys.stderr.write(f"BotEngine Error: {e.msg}")
        sys.stderr.write(f"\nCreate an account on {server} and use it to sign in")
        sys.stderr.write("\n\n")
        raise e

def _register_device(server: str, app_key: str, location_id: str, device_id: str, 
                     device_type: int, description: str) -> Dict[str, Any]:
    """
    Register a device to the user's account.
    
    :param server: Server address
    :param app_key: API key for authentication
    :param location_id: Location ID to register device to
    :param device_id: Unique device ID
    :param device_type: Device type code
    :param description: Human-readable device description
    :return: JSON response from server
    """
    global _https_proxy
    http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}
    r = requests.post(f"{server}/cloud/json/devices",
                      params={"locationId": location_id, "deviceId": device_id, "deviceType": device_type,
                              "desc": description}, headers=http_headers, proxies=_https_proxy)
    j = json.loads(r.text)
    _check_for_errors(j)
    return j

def _get_care_daily_server_url(server: str, device_id: Optional[str] = None) -> str:
    """
    Get Care Daily server URL.
    
    :param server: Server address
    :param device_id: Device ID (optional)
    :return: Care Daily server URL
    """
    global _https_proxy
    http_headers = {"Content-Type": "application/json"}
    params = {"type": "deviceio", "ssl": True}
    if not device_id:
        params['deviceId'] = "nodeviceid"
    else:
        params['deviceId'] = device_id
    r = requests.get(f"{server}/cloud/json/settingsServer", params=params, headers=http_headers,
                     proxies=_https_proxy)
    return r.text

def _check_for_errors(json_response: Optional[Dict[str, Any]]) -> None:
    """
    Check some JSON response for BotEngine errors.
    
    :param json_response: JSON response from server
    :raises BotError: If response contains an error
    """
    if not json_response:
        raise BotError("No response from the server!", -1)

    if json_response['resultCode'] > 0:
        msg = "Unknown error!"
        if 'resultCodeMessage' in json_response:
            msg = json_response['resultCodeMessage']
        elif 'resultCodeDesc' in json_response:
            msg = json_response['resultCodeDesc']
        raise BotError(msg, json_response['resultCode'])

    del json_response['resultCode']


class BotError(Exception):
    """BotEngine exception to raise and log errors."""

    def __init__(self, msg: str, code: int):
        super().__init__(msg)
        self.msg = msg
        self.code = code

    def __str__(self) -> str:
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

