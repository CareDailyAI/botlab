#!/usr/bin/env python
# encoding: utf-8
'''
Created on January 4, 2019

@author: David Moss
'''

# Data Stream Address
DATASTREAM_ADDRESS = "set_radar_room"

# Requests session
session = None

# Data Stream Content
DATASTREAM_CONTENT = {
    "device_id": "",
    "x_left_meters": -2.0,
    "x_right_meters": 0.9,
    "y_max_meters": 2.1
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
    parser.add_argument("--admin_username", dest="admin_username", help="Administrative username")
    parser.add_argument("--admin_password", dest="admin_password", help="Administrative password")
    parser.add_argument("-s", "--server", dest="server", help="Base server URL (app.peoplepowerco.com)")
    parser.add_argument("-l", "--location", dest="location_id", help="Location ID")
    parser.add_argument("-a", "--api_key", dest="apikey", help="User's API key instead of a username/password")
    parser.add_argument("-f", "--file_name", dest="file_name", help="Room file name with no extension")
    parser.add_argument("--httpdebug", dest="httpdebug", action="store_true", help="HTTP debug logger output");
    
    # Process arguments
    args, unknown = parser.parse_known_args()
    
    # Extract the arguments
    username = args.username
    password = args.password
    admin_username = args.admin_username
    admin_password = args.admin_password
    server = args.server
    httpdebug = args.httpdebug
    app_key = args.apikey
    location_id = args.location_id
    file_name = args.file_name

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
        if file_name:
            app_key, user_info = _login(server, admin_username, admin_password, True)
        else:
            app_key, user_info = _login(server, username, password, False)

    if file_name:
        import os
        csv_file = os.path.join(os.getcwd(), file_name)
        if not csv_file.endswith((".csv")):
            csv_file += ".csv"
        config_room_by_file(server, app_key, DATASTREAM_ADDRESS, csv_file)
        print("Done!")
        return

    send_datastream_message(server, app_key, location_id, DATASTREAM_ADDRESS, DATASTREAM_CONTENT)
    print("Done!")


def config_room_by_file(server, app_key, address, csv_file):
    """
    Configure the room by CSV file
    :param server:
    :param app_key:
    :param address:
    :param csv_file:
    :return:
    """
    PARAMETER_MAC_COLUMN = 0
    PARAMETER_DEVICE_ID_COLUMN = 1
    PARAMETER_LOCATION_ID_COLUMN = 2
    PARAMETER_X_LEFT_COLUMN = 3
    PARAMETER_X_RIGHT_COLUMN = 4
    PARAMETER_Y_MIN_COLUMN = 5
    PARAMETER_Y_MAX_COLUMN = 6
    PARAMETER_Z_MIN_COLUMN = 7
    PARAMETER_Z_MAX_COLUMN = 8
    PARAMETER_MOUNT_TYPE_COLUMN = 9
    PARAMETER_SENSOR_HEIGHT_COLUMN = 10

    import base64
    import time
    import os

    line_buffer = []
    with open(csv_file, 'r') as in_file:
        for index, line in enumerate(in_file.readlines()):
            if index == 0:
                line_buffer.append(line.replace('\n', ''))
            else:
                line_list = line.split(",")
                device_mac = line_list[PARAMETER_MAC_COLUMN].strip()
                device_id = line_list[PARAMETER_DEVICE_ID_COLUMN].strip()
                y_min = line_list[PARAMETER_Y_MIN_COLUMN].strip()
                z_min = line_list[PARAMETER_Z_MIN_COLUMN].strip()
                z_max = line_list[PARAMETER_Z_MAX_COLUMN].strip()
                mount_type = line_list[PARAMETER_MOUNT_TYPE_COLUMN].strip()
                sensor_height = line_list[PARAMETER_SENSOR_HEIGHT_COLUMN].strip()

                if device_id == '':
                    if device_mac != '':
                        device_id = 'id_' + base64.b64encode(device_mac.encode('ascii')).decode('ascii').replace('=', '')
                        line_list[PARAMETER_DEVICE_ID_COLUMN] = device_id

                elif device_mac == '':
                    formatted_base64 = (device_id.replace('id_', '') + '=').encode('ascii')
                    line_list[PARAMETER_MAC_COLUMN] = base64.b64decode(formatted_base64).decode('ascii')

                if device_id == '':
                    print("Line #{} missed the device id, please check the file.".format(index))
                    continue

                if y_min == '':
                    line_list[PARAMETER_Y_MIN_COLUMN] = '0.3'

                if z_min == '':
                    line_list[PARAMETER_Z_MIN_COLUMN] = '0'

                if z_max == '':
                    line_list[PARAMETER_Z_MAX_COLUMN] = '2.0'

                if mount_type == '':
                    line_list[PARAMETER_MOUNT_TYPE_COLUMN] = '0'

                if sensor_height == '':
                    line_list[PARAMETER_SENSOR_HEIGHT_COLUMN] = '1.5'

                location_id = _get_location_id(server, app_key, device_id)
                time.sleep(5)

                if location_id is None:
                    print("Could not find the location id for line #{}, please make sure you have the correct device id in file.".format(index))
                    continue

                line_list[PARAMETER_LOCATION_ID_COLUMN] = str(location_id)
                line_buffer.append(','.join(line_list))
                datastream_content = {'device_id': device_id,
                                      'x_left_meters': float(line_list[PARAMETER_X_LEFT_COLUMN].strip()),
                                      'x_right_meters': float(line_list[PARAMETER_X_RIGHT_COLUMN].strip()),
                                      'y_min_meters': float(line_list[PARAMETER_Y_MIN_COLUMN].strip()),
                                      'y_max_meters': float(line_list[PARAMETER_Y_MAX_COLUMN].strip()),
                                      'z_min_meters': float(line_list[PARAMETER_Z_MIN_COLUMN].strip()),
                                      'z_max_meters': float(line_list[PARAMETER_Z_MAX_COLUMN].strip()),
                                      'mounting_type': int(line_list[PARAMETER_MOUNT_TYPE_COLUMN].strip()),
                                      'sensor_height_m': float(line_list[PARAMETER_SENSOR_HEIGHT_COLUMN].strip())}

                send_datastream_message(server, app_key, location_id, address, datastream_content)

    temp_file = csv_file + '_temp'
    with open(temp_file, 'w') as out_file:
        for index, line in enumerate(line_buffer):
            out_file.write(line)
            if index == 0:
                out_file.write("\n")

    os.remove(csv_file)
    os.rename(temp_file, csv_file)


def _get_location_id(server, app_key, device_id):
    """Get location id by using device id"""
    http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}
    params = {
        "deviceId": device_id
    }
    r = requests.get(server + "/admin/json/devices", params=params, headers=http_headers)
    j = json.loads(r.text)
    if j['resultCode'] == 0:
        devices = j['devices']
        if devices:
            device = devices[0]
            location = device['location']
            if location:
                return location['id']
    _check_for_errors(j)
    print(str(r.text))
    return None


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


def _session():
    """
    Retrieve the current HTTP session
    :return: Requests session
    """
    global session
    if session is None:
        session = requests.Session()
        session.headers.update({
            'Content-Type': 'application/json'
        })

    return session


def _login(server, username, password, admin=False, cache_api_key=True):
    """Get an Bot API key and User Info by login with a username and password"""
    if not username:
        username_hint = 'Email address: '
        if admin:
            username_hint = 'Admin email address: '

        if hasattr(__builtins__, 'raw_input'):
            username = raw_input(username_hint)
        else:
            username = input(username_hint)

    if not password:
        import getpass
        password = getpass.getpass('Password: ')

    try:
        import pickle
        import requests
        import os

        type = "user"
        if admin:
            type = "admin"

        fixed_server = server.replace("http://", "").replace("https://", "").split(".")[0]

        filename = "{}.{}.{}".format(username, fixed_server, type)

        get_app_key = False
        if cache_api_key:
            if os.path.isfile(filename):
                try:
                    with open(filename, 'rb') as f:
                        key = pickle.load(f)

                    params = {
                        "keyType": 0
                    }

                    if admin:
                        params['keyType'] = 11
                        params['expiry'] = -1

                    http_headers = {"API_KEY": key, "Content-Type": "application/json"}
                    r = _session().get(server + "/cloud/json/loginByKey", params=params, headers=http_headers)
                    j = json.loads(r.text)

                    if j['resultCode'] == 0:
                        app_key = j['key']

                        with open(filename, 'wb') as f:
                            pickle.dump(app_key, f)

                        get_app_key = True
                except ValueError:
                    # Can't unpickle the local file.
                    # This happens as we switch back to Python 2.7 from Python 3.7.
                    pass

        if not get_app_key:
            params = {
                "username": username
            }
            if admin:
                params['keyType'] = 11

            # login by username and password
            http_headers = {"PASSWORD": password, "Content-Type": "application/json"}
            r = requests.get(server + "/cloud/json/login", params=params, headers=http_headers)
            j = json.loads(r.text)
            if j['resultCode'] == 17:
                passcode = input('Type in the passcode you received on your phone: ')
                passcode = passcode.upper()
                params['expiry'] = -1
                http_headers['passcode'] = passcode
                r = _session().get(server + "/cloud/json/login", params=params, headers=http_headers)
                j = json.loads(r.text)

                if j['resultCode'] == 0:
                    app_key = j['key']
                    if cache_api_key:
                        with open(filename, 'wb') as f:
                            pickle.dump(app_key, f)
            else:
                app_key = j['key']

            _check_for_errors(j)

        # get user info
        http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}
        r = requests.get(server + "/cloud/json/user", headers=http_headers)
        j = json.loads(r.text)
        try:
            _check_for_errors(j)
        except Exception as e:
            print("Couldn't download user info: {}".format(json.dumps(j, indent=2, sort_keys=True)))
            exit(-1)

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




