#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Administrative API

RULES OF THE API IMPLEMENTATIONS IN THIS FILE:
* No user input allowed in this file - API implementations and data transformations only.
* No requesting time-series data parameters, narratives, modes, or lists of locations using standard
  Application APIs. You must use data requests for anything that can be accessed with a data request.
* Always reference a link to the API documentation in the header of your functions

@author:     David Moss

@copyright:  2012 - 2022 People Power Company. All rights reserved.

@contact:    dmoss@peoplepowerco.com
"""

import requests
import json
import os
import sys
import shutil
import datetime
import pytz
import zipfile
import copy
import pandas as pd
import openpyxl

_https_proxy = None

# Requests session
session = None

# Narrative priority levels
NARRATIVE_PRIORITY_ANALYTIC = -1
NARRATIVE_PRIORITY_DEBUG = 0
NARRATIVE_PRIORITY_DETAIL = 0
NARRATIVE_PRIORITY_INFO = 1
NARRATIVE_PRIORITY_WARNING = 2
NARRATIVE_PRIORITY_CRITICAL = 3

# Data Request types
DATA_REQUEST_TYPE_DEVICE_PARAMETERS = 1
DATA_REQUEST_TYPE_DEVICE_ACTIVITIES = 2
DATA_REQUEST_TYPE_ORGANIZATION_LOCATIONS = 3
DATA_REQUEST_TYPE_LOCATION_MODES = 4
DATA_REQUEST_TYPE_LOCATION_NARRATIVES = 5
DATA_REQUEST_TYPE_ORGANIZATION_DEVICES = 6
DATA_REQUEST_TYPE_DATA_STREAMS = 7
DATA_REQUEST_TYPE_DEVICE_ALERTS = 9

# Service plan types
SERVICE_PLAN_STATUS_ACTIVE = 0
SERVICE_PLAN_STATUS_CANCELLED = 1
SERVICE_PLAN_STATUS_INITIAL = -1

# Time conversions to ms
ONE_SECOND_MS = 1000
ONE_MINUTE_MS = 60 * ONE_SECOND_MS
ONE_HOUR_MS = ONE_MINUTE_MS * 60
ONE_DAY_MS = ONE_HOUR_MS * 24

# Default start_time_ms calculator
DEFAULT_TOTAL_DAYS_TO_DOWNLOAD = 30

# This is how many days of data to download in each chunk
DEFAULT_DAYS_TO_DOWNLOAD_IN_EACH_REQUEST = 14

# Sleep time between data request polling attempts to appease the server gods
SLEEP_TIME_BETWEEN_DATA_REQUESTS_SECONDS = 5

# When downloading data that may contain commas, this character will replace those commas
COMMA_DELIMITER_REPLACEMENT_CHARACTER = '&&'

# When downloading data that may contain quotes like '[""This""]' to enclose fields, this character will replace those quotes with '[\"This\"]'
# See https://stackoverflow.com/a/76784255
QUOTE_DELIMITER_REPLACEMENT_CHARACTER = '""'

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


def login(server, username, password, admin=False, cache_api_key=True):
    """
    Login and obtain an API key
    https://iotapps.docs.apiary.io/#reference/login-and-logout/login/login-by-username

    :param server: Server address
    :param username: Username
    :param password: Password
    :param admin: True if we're logging in as an administrator
    :param cache_api_key: True if we'll store the API key to non-volatile memory. Only use this if we're on a trusted machine.
    :return: API Key
    """
    import pickle

    if not username:
        username = input('Email address: ')

    if not password:
        import getpass
        password = getpass.getpass()

    try:
        type = "user"
        if admin:
            type = "admin"

        fixed_server = _get_subdomain_from_url(server)

        filename = "{}.{}.{}".format(username, fixed_server, type)

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
            pref_delivery_type = input('To use SMS to get your passcode type "y"?: ')
            pref_delivery_type = 3 if len(pref_delivery_type) == 0 or pref_delivery_type[0].lower() == 'y' else 2
            params['keyType'] = 11
            params['prefDeliveryType'] = pref_delivery_type

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
                key = j['key']

                if cache_api_key:
                    with open(filename, 'wb') as f:
                        pickle.dump(key, f)

        _check_for_errors(j)

        return j['key']

    except ApiError as e:
        sys.stderr.write("Application API Error: " + e.msg)
        sys.stderr.write("\nCreate an account on " + server + " and use it to sign in")
        sys.stderr.write("\n\n")
        raise e


def get_organizations(cloud_url, admin_key, organization_id=None, domain_name=None, name=None):
    """
    Retrieve organization information by administrator
    https://iotadmins.docs.apiary.io/reference/organizations/manage-an-organization/get-organizations

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param organization_id: Search field. Optional specific organization ID to retrieve information about
    :param domain_name: Search field. Extract information about an organization with the given domain name
    :param name: Search field. First characters of an organization name.
    :return: JSON content list of organizations
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {}
    if organization_id is not None:
        params['organizationId'] = organization_id

    if domain_name is not None:
        params['domainName'] = domain_name

    if name is not None:
        params['name'] = name

    r = _session().get(cloud_url + "/admin/json/organizations", params=params, headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)

    if 'organizations' in j:
        return j['organizations']
    return []


def get_files(cloud_url, admin_key, location_id=None, device_id=None):
    """
    https://iotapps.docs.apiary.io/reference/application-files/files-management/get-files

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API Key
    :param location_id: Optional Location ID
    :param device_id: Optional Device ID
    :return: JSON content list of files
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {}
    if location_id is not None:
        params['locationId'] = location_id

    if device_id is not None:
        params['deviceId'] = device_id

    r = _session().get(cloud_url + "/cloud/json/appfiles", params=params, headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    if 'files' in j:
        return j['files']
    return []


def get_file_download_url(cloud_url, admin_key, location_id, file_id):
    """
    https://iotapps.docs.apiary.io/#reference/application-files/single-file-management/get-download-url

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API Key
    :param location_id: Location ID
    :param file_id: File ID
    :return: Download URL
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {
        "locationId": location_id
    }

    r = _session().get(cloud_url + "/cloud/json/appfiles/{}/url".format(file_id), params=params, headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    if 'contentUrl' in j:
        return j['contentUrl']
    return None


def get_organization_id_from_signup_code(cloud_url, admin_key, signup_code):
    """
    Get the Organization ID from a signup code.
    https://iotadmins.docs.apiary.io/#reference/organizations/manage-an-organization/get-organizations

    :param server: Cloud URL
    :param admin_key: Admin Key
    :param signup_code: Also known as the 'domain name' or the 'short name' - but we've converged toward 'signup code' to make it more user friendly lately.
    :return: Organization ID or None if we can't retrieve it
    """
    organization_info = get_organizations(cloud_url, admin_key, domain_name=signup_code)
    if len(organization_info) > 0:
        return organization_info[0]['id']
    return None


def get_sub_organizations(cloud_url, admin_key, organization_id):
    """
    Retrieve the parent and sub-organizations
    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param organization_id: Parent organization ID
    :return: JSON content list of organizations
    """
    orgs = get_organizations(cloud_url, admin_key)
    all_orgs = []
    for o in orgs:
        if int(o['id']) == int(organization_id):
            all_orgs.append(o)

        elif 'parentId' in o:
            if int(o['parentId']) == int(organization_id):
                all_orgs.append(o)

    return all_orgs


def get_organization_statistics(cloud_url, admin_key, organization_id):
    """
    Get organization statistics and totals
    https://iotadmins.docs.apiary.io/#reference/organizations/organization-totals/get-organization-totals

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param organization_id: Organization ID
    :param locations: True to get total locations
    :param user_devices: True to get total devices
    :return: total_locations, active_devices, inactive_devices
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {
        'locations': True,
        'userDevices': True
    }

    r = _session().get(cloud_url + "/admin/json/organizations/{}/totals".format(organization_id), params=params,
                       headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    j = j['totals']

    total_locations = 0
    active_devices = 0
    inactive_devices = 0

    if 'locationsCount' in j:
        total_locations = j['locationsCount']

    if 'organizationDevices' in j:
        active_devices = j['organizationDevices']['active']
        inactive_devices = j['organizationDevices']['inactive']

    return total_locations, active_devices, inactive_devices


def get_organization_properties(cloud_url, admin_key, organization_id):
    """
    Get a list of objects and properties
    https://iotadmins.docs.apiary.io/#reference/organizations/organization-objects-and-properties/list-objects-and-properties

    :param cloud_url: Cloud URL
    :param admin_key: Admin Key
    :param organization_id: Organization ID
    :return: JSON
    """
    headers = {
        'API_KEY': admin_key
    }

    r = _session().get(cloud_url + "/admin/json/organizations/{}/objects".format(organization_id), headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    if 'organizationObjects' in j:
        if len(j['organizationObjects']) > 0:
            return j['organizationObjects']

    return None


def set_organization_properties(cloud_url, admin_key, organization_id, properties, private=False):
    """
    Set organization properties
    https://iotadmins.docs.apiary.io/#reference/organizations/organization-objects-and-properties/set-properties

    :param cloud_url: Cloud URL
    :param admin_key: Admin Key
    :param organization_id: Organization ID
    :param properties: Dictionary of key:value pairs of properties
    :param private: True to make this a private record that is only available to administrators
    """
    headers = {
        'API_KEY': admin_key
    }

    organization_objects = []

    for key in properties:
        organization_objects.append({
            "name": key,
            "value": properties[key],
            "privateContent": private
        })

    body = {
        "organizationObjects": organization_objects
    }

    r = _session().post(cloud_url + "/admin/json/organizations/{}/objects".format(organization_id), headers=headers,
                        data=json.dumps(body))
    j = json.loads(r.text)
    _check_for_errors(j)

    return None


def get_location(cloud_url, admin_key, location_id):
    """
    Get information about a specific location
    https://iotadmins.docs.apiary.io/reference/users-and-locations/locations-in-an-organization/get-locations

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param location_id: Location ID
    :return: JSON content information about the location, None if we can't get it
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {
        'locationId': location_id
    }

    r = _session().get(cloud_url + "/admin/json/locations", params=params, headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    if 'locations' in j:
        if len(j['locations']) > 0:
            return j['locations'][0]

    return None


def get_devices(cloud_url, admin_key, location_id):
    """
    Get the devices from a location
    https://iotadmins.docs.apiary.io/#reference/devices/devices/get-devices

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param location_id: Location ID
    :return: JSON content list of devices
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {
        'locationId': location_id
    }

    r = _session().get(cloud_url + "/cloud/json/devices", params=params, headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    if 'devices' in j:
        return j['devices']

    return None


def get_device_properties(cloud_url, admin_key, location_id, device_id, property_name=None, index=None):
    """
    https://iotapps.docs.apiary.io/#reference/devices/device-properties/get-device-properties
    Retrieve device properties for the given device ID
    :param cloud_url: Cloud URL
    :param admin_key: Admin Key
    :param location_id: Location ID
    :param device_id: Device ID
    :param property_name: Optional name of a property to retrieve
    :param index: Optional index number of the property to retrieve
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {
        'locationId': location_id
    }

    if property_name is not None:
        params['name'] = property_name

    if index is not None:
        params['index'] = index

    r = _session().get(cloud_url + "/cloud/json/devices/{}/properties".format(device_id), params=params, headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    if 'properties' in j:
        return j['properties']
    return None


def get_organization_narratives(cloud_url, admin_key, organization_id, row_count=100, newest_first=True, page_marker=None, minimum_priority=None, maximum_priority=None):
    """
    https://iotadmins.docs.apiary.io/#reference/users-and-locations/narratives/get-organization-narratives

    Do not use this API to extract all narratives.
    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param organization_id: Organization ID
    :param row_count: Number of rows to return, default is 100. Don't abuse this.
    :param minimum_priority: Return narratives that are equal to or greater than this priority. See api.NARRATIVE_PRIORITY_*
    :param maximum_priority: Return narratives that are less than or equal to this priority. See api.NARRATIVE_PRIORITY_*
    :return: Tuple: (narratives_json_list, next_marker)
    """
    headers = {
        'API_KEY': admin_key
    }

    if newest_first:
        sort_order = 'desc'
    else:
        sort_order = 'asc'

    params = {
        'rowCount': row_count,
        'sortOrder': sort_order
    }

    if page_marker is not None:
        params['pageMarker'] = page_marker

    if minimum_priority is not None:
        params['priority'] = minimum_priority

    if maximum_priority is not None:
        params['toPriority'] = maximum_priority

    r = _session().get(cloud_url + "/admin/json/organizations/{}/narratives".format(organization_id), params=params,
                       headers=headers)
    j = json.loads(r.text)
    try:
        _check_for_errors(j)
    except ApiError as e:
        # If no location (err code 6) then exit out gracefully
        if e.code == 6:
            return ([], None)

    narratives = []
    next_marker = None

    if 'narratives' in j:
        narratives = j['narratives']

    if 'nextMarker' in j:
        next_marker = j['nextMarker']

    return (narratives, next_marker)


def get_subscriptions(cloud_url, admin_key, location_id, status=SERVICE_PLAN_STATUS_ACTIVE):
    """
    Get subscriptions / service plans from the given location ID
    https://iotapps.docs.apiary.io/#reference/paid-services/location-service-plans/get-location-service-plans

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param location_id: Location ID
    :param status: Service plan status to extract. SERVICE_PLAN_STATUS_ACTIVE is default
    :return: JSON content list of subscriptions, or None if this location does not exist
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {
        'locationId': location_id
    }

    if status is not None:
        params['status'] = status

    url = cloud_url + "/cloud/json/userServicePlans"
    r = _session().get(url, params=params, headers=headers)
    j = json.loads(r.text)
    try:
        _check_for_errors(j)
    except ApiError as e:
        if e.code == 7:
            return None

    if 'subscriptions' in j:
        return j['subscriptions']

    return []


def get_location_ids(cloud_url, admin_key, organization_id, has_gateway=True, device_types=[]):
    """
    Get all locations by performing a data request, blocking until the request is ready, and then obtaining results
    :param cloud_url:
    :param admin_key:
    :param organization_id:
    :param has_gateway:
    :param device_types:
    :return:
    """
    if len(device_types) == 0 and has_gateway:
        # Add gateway device types
        device_types.append(31)
        device_types.append(32)
        device_types.append(34)
        device_types.append(36)
        device_types.append(37)
        device_types.append(2000)
        device_types.append(4130)
        device_types.append(10031)
        device_types.append(40)

    download_path = data_request(cloud_url, admin_key, DATA_REQUEST_TYPE_ORGANIZATION_LOCATIONS, organization_id=organization_id,
                                 device_types=device_types)
    narratives_path = os.path.join(os.getcwd(), 'downloads', 'locations')

    locations = []
    with zipfile.ZipFile(download_path, "r") as z:
        for extracted_filename in z.namelist():
            z.extract(extracted_filename, narratives_path)
            extracted_path = os.path.join(narratives_path, extracted_filename)
            print("Extracted: {}".format(extracted_path))

            with open(extracted_path, 'r') as in_file:
                l = 0
                for line in in_file.readlines():
                    if l > 0:
                        locations.append(int(line.split(",")[0]))
                    l += 1

            os.remove(extracted_path)

    return locations


def generate_bill(cloud_url, admin_key, organization_id, date=None):
    """
    Practice generating a bill.

    The API (re)generates a bill for one billing period (month). The generated bill is saved in the database and displayed in the response body.
    The response body also displays the input data used to calculate the bill.

    By default, the target billing period is the previous month. You can specify any other target period using the parameter 'date'.

    The API is mainly intended for testing purposes. There is a recurring background process that generates bills for all organizations on a monthly basis.

    https://iotadmins.docs.apiary.io/#reference/billing/billing/generate-bill
    :param cloud_url: Cloud URL
    :param admin_key: Admin API Key
    :param organization_id: Organization ID
    :param date: The date following the end of the target billing period. By default, the current date is used.
    :return:
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {}

    if date is not None:
        params['date'] = date
    r = _session().put(cloud_url + "/admin/json/organizations/{}/billing".format(organization_id), params=params,
                       headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    return j


def data_request(cloud_url, admin_key, type, location_id=None, organization_id=None, start_time_ms=None, end_time_ms=None, device_types=None, ordered=1, compression=1, no_download=False):
    """
    Submit a data request. Blocks until the data request is ready, downloads it, extracts it, and returns the file reference.
    https://iotapps.docs.apiary.io/#reference/device-measurements/data-requests/submit-data-request
    https://iotapps.docs.apiary.io/#reference/device-measurements/data-requests/get-data

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param location_id: Optional Location ID to extract data from
    :param organization_id: Optional Organization ID to extract data from
    :param type: See DATA_REQUEST_TYPE_*, default is Narratives
    :param request_key: Unique request key for later reference
    :param start_time_ms: Optional start time in milliseconds
    :param end_time_ms: Optional end time in milliseconds
    :param device_types: Device types to filter by for DATA_REQUEST_TYPE_LOCATIONS
    :param ordered: 1=ASC (default); -1=DESC
    :param compression: 0=LZ4; 1=ZIP (default); 2=None
    :param no_download: True to only make the data request and then not actually do the download. This is useful for prepping a ton of downloads in the background before performing the downloads one-by-one. Default is False.
    :return: Unique request key to be used in the retrieve_data_request() method to request this data.
    """
    import uuid
    import time

    # Each request key we need to download
    request_keys = []

    # Data requests to make in the HTTP body
    data_requests = []

    # Association between a request key and a device for which to download parameters
    # { device : [request_key, request_key, request_key] }
    parameter_requestkeys_by_device = {}

    # Assocation between a request key and a device for while to download online/offline activities
    # { device : [request_key, request_key, request_key] }
    activity_requestkeys_by_device = {}

    # Assocation between a request key and a device for while to download alerts
    # { device : [request_key, request_key, request_key] }
    alert_requestkeys_by_device = {}

    # Assocation between a device and a request key
    # { request_key : device }
    device_by_requestkey = {}

    # Association between a device object and its ID
    # { device_id : device_object }
    device_by_id = {}

    # Assocation between a request key and download modes. Designed this way to support chunked modes downloads in the future if we need it.
    modes_keys = []

    # Assocation between a request key and download datastreams. Designed this way to support chunked datastream downloads in the future if we need it.
    datastreams_keys = []

    # Location object placeholder
    location_object = None

    # Force a start time
    if start_time_ms is None:
        start_time_ms = int(time.time() * 1000) - (DEFAULT_TOTAL_DAYS_TO_DOWNLOAD * ONE_DAY_MS)
    else:
        start_time_ms = int(start_time_ms)

    # Force an end time
    if end_time_ms is None:
        end_time_ms = int(time.time() * 1000)
    else:
        end_time_ms = int(end_time_ms)

    # STEP 1: Request the data
    # HTTP params
    params = {}

    # HTTP headers
    headers = {
        'API_KEY': admin_key
    }

    if location_id is not None:
        params.update({
            "locationId": location_id
        })
        location_object = get_location(cloud_url, admin_key, location_id)

    if organization_id is not None:
        params.update({
            "organizationId": organization_id
        })

    if type == DATA_REQUEST_TYPE_DEVICE_PARAMETERS:
        # This is a device data request
        devices = get_devices(cloud_url, admin_key, location_id)
        if devices is None:
            print("=> No devices at location {}".format(location_id))
            return

        # print("Devices: {}".format(json.dumps(devices, indent=2, sort_keys=True)))

        this_download_end_time_ms = int(end_time_ms)

        # We deliberately set the focused start time to the end time, because the next step is to
        # execute a while-loop which works backwards from the end time to the start time.
        # As long as our focused start time is greater than the actual beginning of time we're trying to download,
        # the while-loop will keep generating data requests.
        this_download_start_time_ms = int(end_time_ms)

        # Break this up into multiple data requests, each one being a length of time that is the DEFAULT_DAYS_TO_DOWNLOAD_IN_EACH_REQUEST
        while this_download_start_time_ms > start_time_ms:
            this_download_start_time_ms = this_download_end_time_ms - (DEFAULT_DAYS_TO_DOWNLOAD_IN_EACH_REQUEST * ONE_DAY_MS)

            # Guardrails on the minimum
            if this_download_start_time_ms < start_time_ms:
                this_download_start_time_ms = start_time_ms

            for device in devices:
                # DEVICE PARAMETER request
                # This resulting CSV will look like this
                #
                # measureTime,paramName,index,group,value
                # 1644369206930,occupancy,,,1
                # 1644369206930,occupancyTarget,,,"0:19,73,127"
                # 1644369212357,occupancyTarget,,,"0:18,63,127"

                # Filter specific device types
                if device_types is not None:
                    if int(device['type']) not in device_types:
                        continue

                # print("Device {} start date is {}. Current range is {} to {}".format(device["id"], device["startDateMs"], this_download_start_time_ms, this_download_end_time_ms))
                if this_download_end_time_ms < int(device["startDateMs"]):
                    # print("Device {} has a start date of {} which is after the end time of this download request. Skipping.".format(device["id"], device["startDateMs"]))
                    continue
                this_device_download_start_time_ms = this_download_start_time_ms
                if this_download_start_time_ms < int(device["startDateMs"]):
                    # print("Device {} has a start date of {} which is after the start time of this download request. Adjusting.".format(device["id"], device["startDateMs"]))
                    this_device_download_start_time_ms = int(device["startDateMs"])
                request_key = str(uuid.uuid4())
                device_by_requestkey[request_key] = device
                device_by_id[device["id"]] = device
                request_keys.append(request_key)

                if device["id"] not in parameter_requestkeys_by_device:
                    parameter_requestkeys_by_device[device["id"]] = []
                parameter_requestkeys_by_device[device["id"]].append(request_key)

                request = {
                    "type": DATA_REQUEST_TYPE_DEVICE_PARAMETERS,
                    "key": request_key,
                    "ordered": ordered,
                    "compression": compression,
                    'deviceId': device['id'],
                    'startTime': this_device_download_start_time_ms,
                    'endTime': this_download_end_time_ms
                }

                data_requests.append(request)

            # Step backwards in time and loop to download the next traunch.
            this_download_end_time_ms -= (DEFAULT_DAYS_TO_DOWNLOAD_IN_EACH_REQUEST * ONE_DAY_MS)

        print("From [ms]: {}".format(start_time_ms))
        print("To [ms]: {}".format(end_time_ms))

        # Grab device online/offline activities in one swoop.
        # There usually isn't a ton of data here so we don't need to break it up.
        #
        # The resulting CSV will look like this below, where startTime = online and endTime = went offline
        # When the endTime is that crazy huge value at the end, that means the device is still online
        #
        # startTime,endTime
        # 1642109099000,1642109454000
        # 1642109502000,1642110066000
        # 1642196084000,5000000000000
        for device in devices:
            # DEVICE ACTIVITY (i.e. online/offline alert) request
            
            # Filter specific devices by `type`
            if device_types is not None:
                if int(device['type']) not in device_types:
                    continue

            this_download_start_time_ms = start_time_ms
            if end_time_ms < int(device["startDateMs"]):
                # print("Device {} has a start date of {} which is after the end time of this download request. Skipping.".format(device["id"], device["startDateMs"]))
                continue
            if start_time_ms < int(device["startDateMs"]):
                # print("Device {} has a start date of {} which is after the start time of this download request. Adjusting.".format(device["id"], device["startDateMs"]))
                this_download_start_time_ms = int(device["startDateMs"])

            request_key = str(uuid.uuid4())
            device_by_requestkey[request_key] = device
            request_keys.append(request_key)

            if device["id"] not in activity_requestkeys_by_device:
                activity_requestkeys_by_device[device["id"]] = []
            activity_requestkeys_by_device[device["id"]].append(request_key)

            request = {
                "type": DATA_REQUEST_TYPE_DEVICE_ACTIVITIES,
                "key": request_key,
                "ordered": ordered,
                "compression": compression,
                'deviceId': device['id'],
                'startTime': this_download_start_time_ms,
                'endTime': end_time_ms
            }

            data_requests.append(request)
        
        # Grab device alerts in one swoop.
        # There usually isn't a ton of data here so we don't need to break it up.
        #
        # The resulting CSV will look like this below, where startTime = online and endTime = went offline
        # When the endTime is that crazy huge value at the end, that means the device is still online
        #
        # startTime,endTime
        # 1642109099000,1642109454000
        # 1642109502000,1642110066000
        # 1642196084000,5000000000000
        for device in devices:
            # DEVICE ALERT (i.e. ...) request
            # Filter specific device types
            if device_types is not None:
                if int(device['type']) not in device_types:
                    continue
            this_download_start_time_ms = start_time_ms
            if end_time_ms < int(device["startDateMs"]):
                # print("Device {} has a start date of {} which is after the end time of this download request. Skipping.".format(device["id"], device["startDateMs"]))
                continue
            if start_time_ms < int(device["startDateMs"]):
                # print("Device {} has a start date of {} which is after the start time of this download request. Adjusting.".format(device["id"], device["startDateMs"]))
                this_download_start_time_ms = int(device["startDateMs"])

            request_key = str(uuid.uuid4())
            device_by_requestkey[request_key] = device
            request_keys.append(request_key)

            if device["id"] not in alert_requestkeys_by_device:
                alert_requestkeys_by_device[device["id"]] = []
            alert_requestkeys_by_device[device["id"]].append(request_key)

            request = {
                "type": DATA_REQUEST_TYPE_DEVICE_ALERTS,
                "key": request_key,
                "ordered": ordered,
                "compression": compression,
                'deviceId': device['id'],
                'startTime': this_download_start_time_ms,
                'endTime': end_time_ms
            }

            data_requests.append(request)

        # LOCATION MODE data request
        request_key = str(uuid.uuid4())
        request_keys.append(request_key)
        modes_keys.append(request_key)
        request = {
            "type": DATA_REQUEST_TYPE_LOCATION_MODES,
            "key": request_key,
            "ordered": ordered,
            "compression": compression
        }

        if start_time_ms is not None:
            request['startTime'] = int(start_time_ms)

        if end_time_ms is not None:
            request['endTime'] = int(end_time_ms)

        data_requests.append(request)

        # DATA STREAM data request
        request_key = str(uuid.uuid4())
        request_keys.append(request_key)
        datastreams_keys.append(request_key)
        request = {
            "type": DATA_REQUEST_TYPE_DATA_STREAMS,
            "key": request_key,
            "ordered": ordered,
            "compression": compression
        }

        if start_time_ms is not None:
            request['startTime'] = int(start_time_ms)

        if end_time_ms is not None:
            request['endTime'] = int(end_time_ms)

        data_requests.append(request)

        if not no_download:
            print("{} data requests".format(len(data_requests)))

    else:
        # This is not a device data request and we only need to make one request
        request_key = str(uuid.uuid4())
        request_keys.append(request_key)
        request = {
            "type": type,
            "key": request_key,
            "ordered": ordered,
            "compression": compression
        }

        if organization_id is not None:
            request['organizationId'] = organization_id

        if device_types is not None:
            request["deviceTypes"] = device_types

        if start_time_ms is not None:
            request['startTime'] = int(start_time_ms)

        if end_time_ms is not None:
            request['endTime'] = int(end_time_ms)

        data_requests.append(request)

    print("Executing data requests")
    total_requests = 0
    for request in data_requests:
        sys.stdout.write('.')
        sys.stdout.flush()
        body = {
            "byEmail": False,
            "dataRequests": [request]
        }

        # print("Headers: {}".format(json.dumps(headers, indent=2, sort_keys=True)))
        # print("Params: {}".format(json.dumps(params, indent=2, sort_keys=True)))
        # print("Body: {}".format(json.dumps(body, indent=2, sort_keys=True)))

        downloaded = False
        while not downloaded:
            try:
                r = _session().post(cloud_url + "/cloud/json/dataRequests", params=params, headers=headers, data=json.dumps(body))
                j = json.loads(r.text)
                # print("DATA REQUEST RESPONSE: {}".format(json.dumps(j, indent=2, sort_keys=True)))
                _check_for_errors(j)
                downloaded = True

            except ApiError as e:
                if e.is_locked_out():
                    e.wait_for_lock_timeout()
                    print("Trying again...")

    if no_download:
        return

    print("Waiting data requests")
    # STEP 2: Wait for all data to become available
    results = {}
    attempts = 0
    while True:
        # print("REQUEST CHECK\nURL={}\nPARAMS={}\nHEADERS={}\n".format(cloud_url + "/cloud/json/dataRequests", params, headers))
        r = _session().get(cloud_url + "/cloud/json/dataRequests", params=params, headers=headers)
        j = json.loads(r.text)

        # print("REQUEST CHECK RESPONSE: {}".format(json.dumps(j, indent=2, sort_keys=True)))

        if 'results' in j:
            for result in j['results']:
                if result['key'] in request_keys and result['key'] not in results:
                    sys.stdout.write("!")
                    if 'url' in result:
                        results[result['key']] = result['url']

                    elif result['dataLength'] == 0:
                        # No data to download
                        results[result['key']] = None

            if len(results) == len(request_keys):
                break

        attempts += 1
        sys.stdout.write(".")
        sys.stdout.flush()

        # 2020.12.01 - There was a bug on the server where data requests that would result in no data would never return.
        # This was occurring often with 'modes' on many care users we were extracting.
        # So we're looking for cases where the number of results is only 1 less than the number of requests.
        stop = False
        if len(results) >= len(request_keys) - 1:
            for request_key in request_keys:
                if request_key not in results.keys():
                    if request_key in ["modes","datastreams"]:
                        print("\nMissing Key (skipping): {}".format(request_key))
                        stop = True

        if stop:
            break

        # Attempt the data request again
        if attempts % 50 == 0:
            print("Attempting the data request again...")
            r = _session().post(cloud_url + "/cloud/json/dataRequests", params=params, headers=headers,
                                data=json.dumps(body))
            j = json.loads(r.text)
            _check_for_errors(j)

        if attempts > 320:
            print("SKIPPING LOCATION {}; \n\nDATA REQUESTS {}; \n\nRESULTS {}".format(location_id,
                                                                                      data_requests,
                                                                                      results))
            for request_key in request_keys:
                if request_key not in results.keys():
                    print("\nMissing Key: {}".format(request_key))

            break

        time.sleep(SLEEP_TIME_BETWEEN_DATA_REQUESTS_SECONDS)

    print("\n")

    # STEP 3: Download all data
    download_paths = {}
    # print("RESULTS: {}".format(json.dumps(results, indent=2, sort_keys=True)))
    for result_key in list(results.keys()):
        if results[result_key] is None:
            del results[result_key]

    if len(results) == 0:
        print("No data request results were provided by the server.")
        raise ApiError("No data request results were provided by the server.", -1)

    for result_key in results:
        if results[result_key] is None:
            continue

        server_type = 'prod'
        if 'sbox' in cloud_url:
            server_type = 'sbox'

        narratives_path = os.path.join(os.getcwd(), 'downloads', 'narratives')
        locations_path = os.path.join(os.getcwd(), 'downloads', 'locations')
        data_path = os.path.join(os.getcwd(), 'downloads', 'data')

        final_path = os.path.join(os.getcwd(), 'downloads', "{}.zip".format(result_key))
        download_path = os.path.join(os.path.join(os.getcwd(), 'downloads'), "{}.zip".format(result_key))

        if not os.path.exists(os.path.join(os.getcwd(), 'downloads')):
            os.makedirs(os.path.join(os.getcwd(), 'downloads'))

        if not os.path.exists(narratives_path):
            os.makedirs(narratives_path)

        if not os.path.exists(locations_path):
            os.makedirs(locations_path)

        if not os.path.exists(data_path):
            os.makedirs(data_path)

        if type == DATA_REQUEST_TYPE_ORGANIZATION_LOCATIONS:
            filename_no_extension = "{}_{}_locations_from_org_{}".format(datetime.datetime.now().strftime("%Y.%m.%d"),
                                                                         server_type, organization_id)
            final_path = os.path.join(locations_path, "{}.zip".format(filename_no_extension))
            download_path = os.path.join(locations_path, "{}.zip".format(result_key))

        elif type == DATA_REQUEST_TYPE_LOCATION_NARRATIVES:
            filename_no_extension = "{}_{}_narratives_from_location_{}".format(
                datetime.datetime.now().strftime("%Y.%m.%d"), server_type, location_id)
            final_path = os.path.join(narratives_path, "{}.zip".format(filename_no_extension))
            download_path = os.path.join(narratives_path, "{}.zip".format(result_key))

        elif type == DATA_REQUEST_TYPE_DEVICE_PARAMETERS:
            days = int((end_time_ms - start_time_ms) / ONE_DAY_MS)
            filename_no_extension = "location_{}-{}_days_of_data".format(location_id, days)
            final_path = os.path.join(data_path, "{}.zip".format(filename_no_extension))
            download_path = os.path.join(data_path, "{}.zip".format(result_key))
            download_paths[result_key] = download_path

        if os.path.exists(final_path):
            os.remove(final_path)

        if os.path.exists(download_path):
            os.remove(download_path)

        download_file(results[result_key], download_path)
        print("Downloaded file: {}".format(download_path))

    # STEP 4 : Transform and finalize all previously downloaded data
    if type == DATA_REQUEST_TYPE_LOCATION_NARRATIVES:
        # We want to add the locationId column to the CSV to help with post-processing
        extracted_files = []

        with zipfile.ZipFile(download_path, "r") as z:
            for extracted_filename in z.namelist():
                z.extract(extracted_filename, narratives_path)
                extracted_path = os.path.join(narratives_path, extracted_filename)
                print("Extracted: {}".format(extracted_path))
                filename = transform_narrative_csv(extracted_path,
                                                   filename_no_extension + ".csv",
                                                   location_object)

                zip_out = zipfile.ZipFile(final_path, 'w', zipfile.ZIP_DEFLATED)
                zip_out.write(filename, arcname=os.path.basename(filename))
                zip_out.close()

                if os.path.exists(filename):
                    os.remove(filename)

                if os.path.exists(extracted_path):
                    os.remove(extracted_path)

        if os.path.exists(download_path):
            os.remove(download_path)

    elif type == DATA_REQUEST_TYPE_ORGANIZATION_LOCATIONS:
        os.rename(download_path, final_path)

    elif type == DATA_REQUEST_TYPE_DEVICE_PARAMETERS:
        transformed_files = []

        # Extract all files and form a list of extracted files, referenced by request_key
        # { request_key : [extracted_file, extracted_file, extracted_file] }
        extractedpath_by_requestkey = {}

        # Device parameter extracted files
        # { device : [extracted_file, extracted_file, extracted_file] }
        extracted_parameters_paths_by_device = {}

        # Device alert extracted files
        # { device : [extracted_file, extracted_file, extracted_file] }
        extracted_alerts_paths_by_device = {}

        # Extract all our files
        all_extracted_paths = []
        for request_key in download_paths:
            with zipfile.ZipFile(download_paths[request_key], "r") as z:
                for extracted_filename in z.namelist():
                    z.extract(extracted_filename, data_path)
                    # extracted_filename = extracted_filename.replace(":", "_" )
                    extracted_path = os.path.join(data_path, extracted_filename)
                    all_extracted_paths.append(extracted_path)
                    extractedpath_by_requestkey[request_key] = extracted_path

                    # Log which ones of these relate to a device's parameters, activities, and alerts
                    if request_key in device_by_requestkey:
                        device = device_by_requestkey[request_key]

                        if 'measures' in extracted_path:
                            if device["id"] not in extracted_parameters_paths_by_device:
                                extracted_parameters_paths_by_device[device["id"]] = []
                            extracted_parameters_paths_by_device[device["id"]].append(extracted_path)
                        elif 'alerts' in extracted_path:
                            if device["id"] not in extracted_alerts_paths_by_device:
                                extracted_alerts_paths_by_device[device["id"]] = []
                            extracted_alerts_paths_by_device[device["id"]].append(extracted_path)

                    elif request_key in modes_keys:
                        transformed_files.append(transform_modes_csv(extracted_path, location_object))
                        if os.path.exists(extracted_path):
                            os.remove(extracted_path)

                    elif request_key in datastreams_keys:
                        transformed_files.append(transform_datastreams_csv(extracted_path, location_object))
                        if os.path.exists(extracted_path):
                            os.remove(extracted_path)

                    print("Extracted: {}".format(extracted_path))

            # Delete the original downloaded .zip files
            if os.path.exists(download_paths[request_key]):
                os.remove(download_paths[request_key])

        print("Extracted paths by device: {}".format(json.dumps(extractedpath_by_requestkey, indent=2, sort_keys=True)))
        print("Extracted parameter paths by device: {}".format(json.dumps(extracted_parameters_paths_by_device, indent=2, sort_keys=True)))
        print("Extracted alerts paths by device: {}".format(json.dumps(extracted_alerts_paths_by_device, indent=2, sort_keys=True)))

        # Focus on the activities first.
        # Transform device activity files into something like looks more like a device measurement file so we can merge the two later.
        for device_id in activity_requestkeys_by_device:
            request_keys = activity_requestkeys_by_device[device_id]

            csv_activity_data = ""
            for r in request_keys:
                if r in extractedpath_by_requestkey:
                    with open(extractedpath_by_requestkey[r], "r") as f:
                        for line in f:
                            if line.strip() == "":
                                continue

                            if line.startswith("start"):
                                continue

                            # We're going to form this into the same style of CSV as our measurements
                            # timestamp_ms,param_name,index,group,value
                            timestamps = line.split(",")
                            online_ms = int(timestamps[0])
                            offline_ms = int(timestamps[1])

                            csv_activity_data += "{},{},{},{},{}\n".format(online_ms,
                                                                         "[online]",
                                                                         "",
                                                                         "",
                                                                         1)

                            # This giant number is the timestamp the server puts in when a device is still connected.
                            # Anything less than that means disconnected
                            if int(offline_ms) < 5000000000000:
                                csv_activity_data += "{},{},{},{},{}\n".format(offline_ms,
                                                                         "[online]",
                                                                         "",
                                                                         "",
                                                                         0)

                    if os.path.exists(extractedpath_by_requestkey[r]):
                        os.remove(extractedpath_by_requestkey[r])
                        del extractedpath_by_requestkey[r]

            # If we have something to write, then throw some CSV headers on top and write it out
            if len(csv_activity_data) > 0:
                csv_activity_data = "measureTime,paramName,index,group,value\n" + csv_activity_data
                activities_filename = os.path.join(data_path, slugify(device_id + "_activities") + ".csv")

                with open(activities_filename, "w") as f:
                    f.write(csv_activity_data)

                if device_id not in extracted_parameters_paths_by_device:
                    extracted_parameters_paths_by_device[device_id] = []
                extracted_parameters_paths_by_device[device_id].append(activities_filename)

        # We've just merged our activities together and made them look like device parameter files.
        # Now go through the full list of these device parameters and let's merge those, too.
        data_request_params_files = {}
        for device_id in extracted_parameters_paths_by_device:
            paths = extracted_parameters_paths_by_device[device_id]
            data = ""
            out_file = os.path.join(data_path, slugify("{}_parameters".format(device_id)) + ".csv")
            for p in paths:
                with open(p, "r") as f:
                    for line in f:
                        if line.startswith("measureTime"):
                            continue
                        data += line

                os.remove(p)

            data = sorted(data.split("\n"))

            if os.path.exists(out_file):
                os.remove(out_file)

            with open(out_file, "w") as f:
                f.write("measureTime,paramName,index,group,value")
                for d in data:
                    f.write(d + "\n")
            if device_id in device_by_id:
                transformed_files.append(transform_device_csv(out_file, device_by_id[device_id]))

            # Clean up the merged CSVs
            if os.path.exists(out_file):
                data_request_params_files[device_id] = out_file
                # os.remove(out_file)
        
        # Focus on the alerts next.
        data_request_alerts_files = {}

        for device_id in extracted_alerts_paths_by_device:
            paths = extracted_alerts_paths_by_device[device_id]
            data = ""
            out_file = os.path.join(data_path, slugify("{}_alerts".format(device_id)) + ".csv")
            for p in paths:
                with open(p, "r") as f:
                    for line in f:
                        if line.startswith("time"):
                            continue
                        data += line

                os.remove(p)

            data = sorted(data.split("\n"))

            if os.path.exists(out_file):
                os.remove(out_file)

            with open(out_file, "w") as f:
                f.write("time,type,params,content")
                for d in data:
                    f.write(d + "\n")

            if device_id in device_by_id:
                transformed_files.append(transform_device_csv(out_file, device_by_id[device_id], DATA_REQUEST_TYPE_DEVICE_ALERTS))

            # Clean up the merged CSVs
            if os.path.exists(out_file):
                data_request_alerts_files[device_id] = out_file
                # os.remove(out_file)

        print("Transformed files: {}".format(transformed_files))

        zip_all_these_file_paths = copy.copy(transformed_files)
        data_request_files = {}
        if data_request_params_files:
            for key, filename in data_request_params_files.items():
                zip_all_these_file_paths.append(filename)
                data_request_files["{}_param".format(key)] = filename
        if data_request_alerts_files:
            for key, filename in data_request_alerts_files.items():
                zip_all_these_file_paths.append(filename)
                data_request_files["{}_alert".format(key)] = filename

        zip_all_these_file_paths += _generate_recordings(cloud_url, admin_key, location_id, transformed_files, data_request_files, data_path, start_time_ms=start_time_ms, end_time_ms=end_time_ms)
        #zip_all_these_file_paths.append(_generate_ism(transformed_files, os.path.join(data_path, "ism_{}.pickle".format(location_id))))

        print("Final Path: {}".format(final_path))
        zip_out = zipfile.ZipFile(final_path, 'w', zipfile.ZIP_DEFLATED)
        for filename in zip_all_these_file_paths:
            zip_out.write(filename, arcname=os.path.basename(filename))
            if os.path.exists(filename):
                os.remove(filename)
        zip_out.close()

    return final_path


def get_service_plans(cloud_url, admin_key, location_id=None, organization_id=None):
    """
    Get service plans
    https://iotapps.docs.apiary.io/#reference/paid-services/service-plans/get-available-service-plans

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param location_id: Optional Location ID
    :param organization_id: Optional Organization ID
    :return: JSON content service plans
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {}
    if location_id is not None:
        params['locationId'] = location_id

    if organization_id is not None:
        params['organizationId'] = organization_id

    r = _session().get(cloud_url + "/cloud/json/servicePlans", params=params, headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)

    if 'servicePlans' in j:
        return j['servicePlans']
    return []


def get_location_subscriptions(cloud_url, admin_key, location_id):
    """
    Get a list of active subscriptions for the given location ID

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param location_id: Location ID
    :return: List of active subscriptions for this location
    """
    plans = get_service_plans(cloud_url, admin_key, location_id=location_id)
    subscriptions = []
    for p in plans:
        if 'subscribed' in p:
            if p['subscribed']:
                subscriptions.append(p)

    return subscriptions


def get_current_device_parameters(cloud_url, admin_key, location_id, device_id):
    """
    Get a list of parameter names from the current device

    https://iotapps.docs.apiary.io/#reference/device-measurements/parameters-for-a-specific-device/get-current-measurements
    :param cloud_url: Cloud URL
    :param admin_key: Admin key
    :param location_id: Location ID
    :param device_id: Device ID
    :return: JSON parameters content
    """
    headers = {
        'API_KEY': admin_key
    }

    params = {
        "locationId": location_id
    }

    url = cloud_url + "/cloud/json/devices/{}/parameters".format(device_id)
    r = _session().get(url, params=params, headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    try:
        return j['devices'][0]['parameters']
    except Exception:
        return []


def download_file(from_url, to_path):
    """
    Download a file from the given URL to a file in the local directory with the given filename
    :param from_url: URL to download from
    :param to_path: Full file path to download to
    :return: Full path to the local filename
    """
    with requests.get(from_url, stream=True) as r:
        with open(to_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def transform_narrative_csv(original_csv_file, recommended_csv_filename, location_object):
    """
    Transform a narrative CSV file in a way that injects more useful information and fixes carriage-returns
    :param original_csv_file: Original CSV file with all the data
    :param recommended_csv_filename: Recommendation for the transformed CSV filename
    :param location_object: JSON location object from get_location()
    :return: Full path to the transformed CSV file
    """
    narratives_path = os.path.dirname(original_csv_file)
    transform_path = os.path.join(narratives_path, recommended_csv_filename)
    location_id = location_object['id']

    timezone_string = "America/Los_Angeles"
    if 'timezone' in location_object:
        timezone_string = location_object['timezone']['id']

    print("Transforming: {}...".format(transform_path))

    TIMESTAMP_COLUMN = 1
    line_buffer = ""

    with open(original_csv_file, 'r') as in_file:
        with open(transform_path, 'w') as out_file:
            for index, line in enumerate(in_file.readlines()):
                if index == 0:
                    out_file.write("locationId,timestamp_iso,timestamp_excel," + line.strip())

                else:
                    line_list = line.split(",")

                    # ISO is UTC time while the Excel timestamp is in the user's local timezone
                    try:
                        timestamp_ms = int(line_list[TIMESTAMP_COLUMN])

                        # These narratives may contain arbitrary carriage-returns which may stretch a single narrative entry across multiple lines.
                        # If we can't extract a timestamp (as indicated by an integer in the second element of a comma-split list of words),
                        # then it's not a new narrative entry and we buffer it up and gather then next line
                        # If we found a solid new narrative entry, we make sure the last buffered line is written.
                        # And we always make sure the last line had a carriage-return.

                        # If we make it to this line and didn't get an exception, then we probably have a new narrative entry.
                        # So we either output the last buffered line, or if we don't have one then we at least make sure we have a carriage-return.
                        if line_buffer != "":
                            out_file.write(line_buffer.replace(",", " ") + "\n")
                            line_buffer = ""
                        else:
                            out_file.write("\n")

                    except:
                        line_buffer += line.strip()
                        continue

                    timestamp_iso = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000.0).isoformat() + "Z"
                    timestamp_excel = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, pytz.timezone(timezone_string)).strftime('%m/%d/%Y %H:%M:%S')
                    out_file.write("{},{},{},{}".format(location_id, timestamp_iso, timestamp_excel, line.strip()))

            if line_buffer != "":
                out_file.write(line_buffer.replace(",", " ") + "\n")
            else:
                out_file.write("\n")

            out_file.flush()

    return transform_path


def transform_device_csv(original_csv_file, device_object, type=DATA_REQUEST_TYPE_DEVICE_PARAMETERS):
    """
    Transform a device CSV file from the not-so-useful server format to a full time-series matrix of states
    :param file: Original CSV filename
    :param device_object: JSON data for this device extracted from the get_devices() function
    :param timezone_string: Timezone string like "America/Los_Angeles"
    :return: Newly created CSV filename
    """
    # Required fields
    device_type = device_object['type']
    location_id = device_object['locationId']
    device_id = device_object['id']
    
    # Optional fields
    import re
    device_model = re.sub('[^0-9a-zA-Z]+', '-', device_object.get('modelId', "NoModel").strip())
    device_description = re.sub('[^0-9a-zA-Z]+', '-', device_object.get('desc', "NoDescription").strip())
    behavior = device_object.get('goalId', -1)
    spaces = [f"{space['type']}" for space in device_object.get('spaces',[])]

    new_filename = "{}_{}_{}_{}_{}.csv".format(device_type, device_model, device_id, device_description, type)
    new_file_path = os.path.join(os.path.dirname(original_csv_file), new_filename)
    print("Transforming {} into {}...".format(original_csv_file, new_file_path))
    if type == DATA_REQUEST_TYPE_DEVICE_PARAMETERS:

        # STEP 1. Extract a list of all parameters and their initial (timestamp, value)
        print("Transforming parameters")
        # This is the type of data we're dealing with for devices
        # measureTime, paramName, index, group, value
        # 1589920192201, buttonStatus,,, 0
        # 1589920192201, alarmStatus, 2,, 0

        TIMESTAMP_COLUMN = 0
        PARAMETER_NAME_COLUMN = 1
        PARAMETER_INDEX_COLUMN = 2
        PARAMETER_GROUP_COLUMN = 3
        PARAMETER_VALUE_COLUMN = 4

        parameters = {}
        with open(original_csv_file, 'r') as f:
            for index, line in enumerate(f.readlines()):
                if index > 0:
                    value = ""
                    in_bracket = 0
                    in_quote = 0
                    line_list = []
                    for c in line:
                        if c == '[':
                            in_bracket += 1
                        elif c == ']':
                            in_bracket -= 1

                        if c == '\"' and in_quote > 0:
                            in_quote -= 1
                        elif c == '\"':
                            in_quote += 1

                        if in_bracket == 0 and in_quote == 0:
                            if c == ',':
                                line_list.append(value)
                                value = ""
                                continue

                        value += c

                    line_list.append(value)

                    param_name = line_list[PARAMETER_NAME_COLUMN].strip()
                    param_index = line_list[PARAMETER_INDEX_COLUMN].strip()

                    if len(param_index) > 0:
                        param_name = param_name + "." + param_index

                    if param_name not in parameters:
                        parameters[param_name] = line_list[PARAMETER_VALUE_COLUMN].strip()

        with open(new_file_path, 'w') as out:
            # STEP 2. Output CSV header
            out.write("trigger,location_id,device_type,device_id,description,timestamp_ms,timestamp_iso,timestamp_excel,behavior,spaces,updated_params")

            for p in sorted(list(parameters.keys())):
                out.write("," + p)
            out.write("\n")

            # STEP 3. Read from the original file and export all columns
            with open(original_csv_file, 'r') as f:
                line_buffer = ""
                last_timestamp_ms = 0
                updated_params = []

                for index, line in enumerate(f.readlines()):
                    if index > 0:
                        value = ""
                        in_bracket = 0
                        in_quote = 0
                        line_list = []
                        for c in line:
                            if c == '[':
                                in_bracket += 1
                            elif c == ']':
                                in_bracket -= 1

                            if c == '\"' and in_quote > 0:
                                in_quote -= 1
                            elif c == '\"':
                                in_quote += 1

                            if in_bracket == 0 and in_quote == 0:
                                if c == ',':
                                    line_list.append(value)
                                    value = ""
                                    continue

                            value += c

                        line_list.append(value)

                        param_name = line_list[PARAMETER_NAME_COLUMN].strip()
                        param_index = line_list[PARAMETER_INDEX_COLUMN].strip()
                        timestamp_ms = int(line_list[TIMESTAMP_COLUMN].strip())

                        if last_timestamp_ms != timestamp_ms:
                            if last_timestamp_ms > 0:
                                line_buffer += "\n"

                            out.write(line_buffer)
                            last_timestamp_ms = timestamp_ms
                            updated_params = []

                        if len(param_index) > 0:
                            param_name = param_name + "." + param_index

                        parameters[param_name] = line_list[PARAMETER_VALUE_COLUMN].strip()

                        trigger = 8
                        if param_name == "[online]":
                            trigger = 4
                        else:
                            updated_params.append(param_name)

                        # ISO is UTC time while the Excel timestamp is in the user's local timezone
                        timestamp_iso = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000.0).isoformat() + "Z"
                        timezone_string = "America/Los_Angeles"
                        if 'timezone' in device_object:
                            timezone_string = device_object['timezone']['id']
                        timestamp_excel = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, pytz.timezone(timezone_string)).strftime('%m/%d/%Y %H:%M:%S')

                        line_buffer = "{},{},{},{},{},{},{},{},{},{},{}".format(trigger, location_id, device_type, device_id,
                                                                        device_description, timestamp_ms, timestamp_iso,
                                                                        timestamp_excel, behavior,"&&".join(spaces),"&&".join(updated_params))

                        for p in sorted(list(parameters.keys())):
                            # Remove quotes on values - not sure where the quotes came from but it would be more ideal to remove them earlier.
                            if parameters[p].startswith("\"") and parameters[p].endswith("\""):
                                parameters[p] = parameters[p][1:-1]
                            line_buffer += ",{}".format(parameters[p].replace(",", COMMA_DELIMITER_REPLACEMENT_CHARACTER))

                line_buffer += "\n"
                out.write(line_buffer)

    elif type == DATA_REQUEST_TYPE_DEVICE_ALERTS:

        # STEP 1. Extract a list of all alerts and their initial (timestamp, value)
        # This is the type of data we're dealing with for devices
        # time,type,params,content
        # 1670107276000,on,,
        # 1670107276000,mqtt_disconnection,"{""disconnect_timestamp"":""1670107262070"",""disconnect_duration_s"":""13""}",

        TIMESTAMP_COLUMN = 0
        ALERT_NAME_COLUMN = 1
        ALERT_PARAM_GROUP_COLUMN = 2
        ALERT_CONTENT_COLUMN = 3

        alert_name = ""
        alert_params = {}
        if os.path.exists(original_csv_file):
            with open(original_csv_file, 'r') as f:
                for index, line in enumerate(f.readlines()):
                    if index > 0:
                        value = ""
                        in_bracket = 0
                        in_quote = 0
                        line_list = []
                        for c in line:
                            if c == '[':
                                in_bracket += 1
                            elif c == ']':
                                in_bracket -= 1

                            if c == '\"' and in_quote > 0:
                                in_quote -= 1
                            elif c == '\"':
                                in_quote += 1

                            if in_bracket == 0 and in_quote == 0:
                                if c == ',':
                                    line_list.append(value)
                                    value = ""
                                    continue

                            value += c

                        line_list.append(value)

                        alert_name = line_list[ALERT_NAME_COLUMN].strip()
                        params = line_list[ALERT_PARAM_GROUP_COLUMN].strip()
                        if len(params) > 0:
                            try:
                                params_json = json.loads(params.replace('"{','{').replace('}"','}').replace('""','"'))
                            except:
                                continue
                            for param_name in params_json.keys():
                                if param_name not in alert_params:
                                    alert_params[param_name] = params_json[param_name]

        with open(new_file_path, 'w') as out:
            # STEP 2. Output CSV header
            out.write("trigger,location_id,device_type,device_id,description,timestamp_ms,timestamp_iso,timestamp_excel,behavior,spaces")

            out.write("," + "alert_type")

            for p in sorted(list(alert_params.keys())):
                out.write("," + p)
            out.write("\n")

            # STEP 3. Read from the original file and export all columns
            if os.path.exists(original_csv_file):
                with open(original_csv_file, 'r') as f:
                    line_buffer = ""
                    last_timestamp_ms = 0

                    for index, line in enumerate(f.readlines()):
                        if index > 0:
                            value = ""
                            in_bracket = 0
                            in_quote = 0
                            line_list = []
                            for c in line:
                                if c == '[':
                                    in_bracket += 1
                                elif c == ']':
                                    in_bracket -= 1

                                if c == '\"' and in_quote > 0:
                                    in_quote -= 1
                                elif c == '\"':
                                    in_quote += 1

                                if in_bracket == 0 and in_quote == 0:
                                    if c == ',':
                                        line_list.append(value)
                                        value = ""
                                        continue

                                value += c

                            line_list.append(value)


                            timestamp_ms = int(line_list[TIMESTAMP_COLUMN].strip())

                            if last_timestamp_ms != timestamp_ms:
                                if last_timestamp_ms > 0:
                                    line_buffer += "\n"

                                out.write(line_buffer)
                                last_timestamp_ms = timestamp_ms

                            alert_name = line_list[ALERT_NAME_COLUMN].strip()
                            params = line_list[ALERT_PARAM_GROUP_COLUMN].strip()
                            cur_alert_params = {}
                            if len(params) > 0:
                                try:
                                    params_json = json.loads(params.replace('"{','{').replace('}"','}').replace('""','"'))
                                except:
                                    continue
                                for param_name in params_json.keys():
                                    if param_name not in cur_alert_params:
                                        cur_alert_params[param_name] = params_json[param_name]
                            print(alert_params)
                            print(cur_alert_params)
                            # asfd
                            trigger = 4

                            # ISO is UTC time while the Excel timestamp is in the user's local timezone
                            timestamp_iso = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000.0).isoformat() + "Z"
                            timezone_string = "America/Los_Angeles"
                            if 'timezone' in device_object:
                                timezone_string = device_object['timezone']['id']
                            timestamp_excel = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, pytz.timezone(timezone_string)).strftime('%m/%d/%Y %H:%M:%S')

                            line_buffer = "{},{},{},{},{},{},{},{},{},{},{}".format(trigger, location_id, device_type, device_id,
                                                                            device_description, timestamp_ms, timestamp_iso,
                                                                            timestamp_excel, behavior, "&&".join(spaces), alert_name)

                            for p in sorted(list(alert_params.keys())):
                                if p not in cur_alert_params:
                                    line_buffer += ","
                                    continue        
                                # Remove quotes on values - not sure where the quotes came from but it would be more ideal to remove them earlier.
                                if cur_alert_params[p].startswith("\"") and cur_alert_params[p].endswith("\""):
                                    cur_alert_params[p] = cur_alert_params[p][1:-1]
                                line_buffer += ",{}".format(cur_alert_params[p].replace(",", COMMA_DELIMITER_REPLACEMENT_CHARACTER))

                    line_buffer += "\n"
                    out.write(line_buffer)

    return new_file_path


def transform_modes_csv(original_csv_file, location_object):
    """
    Transform a modes CSV file to a useful format
    :param original_csv_file: Original CSV file
    :param location_object: JSON location object from get_location()
    :return: Newly created CSV filename
    """
    # Here's the type of data we're dealing with
    # time, mode, sourceType
    # 1590170066000, STAY.1315941, 0
    # 1590170181000, HOME.1315941, 0
    # 1604092695000, TEST, 0
    # 1604092696000, HOME, 2

    # Here's what it should get transformed into
    # trigger, location_id, timestamp_ms, timestamp_ms, timestamp_ms, event, source_type
    # 2, 1306512, 1596740404000, 2022-12-06T05:34:02Z, 12/05/2022 21:34:02, HOME.1313473, 0
    # 2, 1306512, 1596735015000, 2022-12-06T05:34:02Z, 12/05/2022 21:34:02, AWAY.1313473.:.PRESENT.AI, 2

    location_id = location_object['id']

    TIMESTAMP_COLUMN = 0
    EVENT_COLUMN = 1
    SOURCE_TYPE_COLUMN = 2

    new_filename = "location_{}_modes_history.csv".format(location_object['id'])
    new_file_path = os.path.join(os.path.dirname(original_csv_file), new_filename)
    print("Transforming {}...".format(new_file_path))

    with open(new_file_path, 'w') as out:
        # STEP 1. Output CSV header
        out.write("trigger,location_id,timestamp_ms,timestamp_iso,timestamp_excel,event,source_type\n")

        # STEP 2. Read from the original file and export all columns
        with open(original_csv_file, 'r') as f:
            for index, line in enumerate(f.readlines()):
                if index > 0:
                    line_list = line.split(",")

                    # ISO is UTC time while the Excel timestamp is in the user's local timezone
                    timestamp_ms = int(line_list[TIMESTAMP_COLUMN])
                    timestamp_iso = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000.0).isoformat() + "Z"
                    timezone_string = "America/Los_Angeles"
                    if 'timezone' in location_object:
                        timezone_string = location_object['timezone']['id']
                    timestamp_excel = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0,
                                                                      pytz.timezone(timezone_string)).strftime('%m/%d/%Y %H:%M:%S')
                    event = line_list[EVENT_COLUMN].strip()
                    source_type = line_list[SOURCE_TYPE_COLUMN].strip()
                    if source_type == 2:
                        # Ignore bot-driven modes to allow for playback of user-driven modes only
                        continue

                    out.write("{},{},{},{},{},{},{}\n".format(2,
                                                              location_id,
                                                              timestamp_ms,
                                                              timestamp_iso,
                                                              timestamp_excel,
                                                              event,
                                                              source_type))

    return new_file_path

def transform_datastreams_csv(original_csv_file, location_object):
    """
    Transform a datastreams CSV file to a useful format
    :param original_csv_file: Original CSV file
    :param location_object: JSON location object from get_location()
    :return: Newly created CSV filename
    """
    # Here's the type of data we're dealing with
    # time,address,feed
    # 1670175747000,do_something,"{""thing"":{""type"":""0""},""other_thing"":123}"

    # Here's what it should get transformed into
    # trigger, location_id, timestamp_ms, timestamp_iso,timestamp_excel, address, feed
    # 256, 1306512, 1596740404000, 2022-12-06T05:34:02Z, 12/05/2022 21:34:02, do_something, '{""thing"":{""type"":""0""}&&""other_thing"":123}'

    location_id = location_object['id']

    TIMESTAMP_COLUMN = 0
    ADDRESS_COLUMN = 1
    FEED_COLUMN = 2

    new_filename = "location_{}_datastreams_history.csv".format(location_object['id'])
    new_file_path = os.path.join(os.path.dirname(original_csv_file), new_filename)
    print("Transforming {}...".format(new_file_path))

    with open(new_file_path, 'w') as out:
        # STEP 1. Output CSV header
        out.write("trigger,location_id,timestamp_ms,timestamp_iso,timestamp_excel,address,feed\n")

        # STEP 2. Read from the original file and export all columns
        with open(original_csv_file, 'r') as f:
            for index, line in enumerate(f.readlines()):
                if index > 0:
                    line_list = line.split(",")

                    # ISO is UTC time while the Excel timestamp is in the user's local timezone
                    timestamp_ms = int(line_list[TIMESTAMP_COLUMN])
                    timestamp_iso = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000.0).isoformat() + "Z"
                    timezone_string = "America/Los_Angeles"
                    if 'timezone' in location_object:
                        timezone_string = location_object['timezone']['id']
                    timestamp_excel = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0,
                                                                      pytz.timezone(timezone_string)).strftime('%m/%d/%Y %H:%M:%S')
                    feed_content = {}
                    idx = line.find(line_list[FEED_COLUMN])
                    feed_content = line[idx:].replace('"{','{').replace('}"','}').replace(',','&&')
                    out.write("{},{},{},{},{},{},{}\n".format(256,
                                                              location_id,
                                                              timestamp_ms,
                                                              timestamp_iso,
                                                              timestamp_excel,
                                                              line_list[ADDRESS_COLUMN].strip(),
                                                              feed_content.strip()))
    return new_file_path

def __zipdir(path, z):
    for root, dirs, files in os.walk(path):
        for file in files:
            z.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))


def _generate_recordings(cloud_url, admin_key, location_id, transformed_files, data_request_files, output_directory, start_time_ms=None, end_time_ms=None):
    """
    Generate recordings for --playback from our downloaded, transformed files
    :param transformed_files:
    :return: List of recordings
    """
    print("Generating recordings for --playback...")
    location_info = get_location(cloud_url, admin_key, location_id)
    devices = get_devices(cloud_url, admin_key, location_id)
    device_properties = {}
    device_parameters = {}
    for device in devices:
        device_properties[device['id']] = get_device_properties(cloud_url, admin_key, location_id, device['id'])
        device_parameters[device['id']] = get_current_device_parameters(cloud_url, admin_key, location_id, device['id'])

    all_data = []
    for f in transformed_files:
        all_data += _csv_file_to_python(f)

    # Massive amount of data to sort by timestamp - btw, hope your computer has a lot of memory.
    all_data = sorted(all_data, key=lambda d: d['timestamp_ms'])

    if start_time_ms is not None:
        oldest_timestamp_ms = start_time_ms
    else:
        oldest_timestamp_ms = all_data[0]['timestamp_ms']

    if end_time_ms is not None:
        newest_timestamp_ms = end_time_ms
    else:
        newest_timestamp_ms = all_data[-1]['timestamp_ms']

    subdomain = _get_subdomain_from_url(cloud_url)

    days = int((newest_timestamp_ms - oldest_timestamp_ms) / ONE_DAY_MS)
    filename_no_extension = "recording-location_{}-{}_days_of_data".format(location_id, days)

    output_filename = os.path.join(output_directory, filename_no_extension + ".json")
    saved_files = [output_filename]

    # Extract all data into a total combined recording
    print("\t=> Exporting {}...".format(output_filename))
    with open(output_filename, 'w') as out:
        # We do it this way so our file remains totally readable and editable later.
        out.write("{\n")
        if data_request_files:
            param_data_request_files = {}
            for key, filename in data_request_files.items():
                if "_param" in key:
                    param_data_request_files[key.replace("_param","")] = os.path.basename(filename)

            out.write("\"data_requests\":" + json.dumps(param_data_request_files) + ",\n")
            data_request_files.clear()

        out.write("\"location_info\":" + json.dumps(location_info) + ",\n")
        out.write("\"device_properties\":" + json.dumps(device_properties) + ",\n")
        out.write("\"device_parameters\":" + json.dumps(device_parameters) + ",\n")
        out.write("\"data\":[\n")
        for index, line in enumerate(all_data):
            out.write("{}".format(json.dumps(line)))

            if index < len(all_data) - 1:
                out.write(",\n")
            else:
                out.write("\n")

        out.write("\n]}\n")

    # Now extract out each device into its own recording
    for device in devices:
        device_id = device['id']
        output_filename = os.path.join(output_directory, slugify("recording__{}_{}_location-{}".format(device['id'], device['desc'], location_id)) + ".json")

        lines_for_this_device = []
        for line in all_data:
            if int(line['trigger']) in [4,8]:
                if line['device_id'] != device_id:
                    continue
                lines_for_this_device.append(line)

        if len(lines_for_this_device) > 0:
            print("\t=> Exporting {}...".format(output_filename))
            with open(output_filename, 'w') as out:
                # We do it this way so our file remains totally readable and editable later.
                lines = 0
                out.write("{\n")
                if data_request_files:
                    param_data_request_files = {}
                    for key, filename in data_request_files.items():
                        if "_param" in key and device_id in key:
                            param_data_request_files[key.replace("_param","")] = os.path.basename(filename)

                    out.write("\"data_requests\":" + json.dumps(param_data_request_files) + ",\n")
                    data_request_files.clear()
                out.write("\"location_info\":" + json.dumps(location_info) + ",\n")
                out.write("\"device_properties\":" + json.dumps(device_properties[device['id']]) + ",\n")
                out.write("\"device_parameters\":" + json.dumps(device_parameters[device['id']]) + ",\n")
                out.write("\"data\":[\n")
                for index, line in enumerate(lines_for_this_device):
                    out.write("{}".format(json.dumps(line)))

                    if index < len(lines_for_this_device) - 1:
                        out.write(",\n")
                    else:
                        out.write("\n")

                out.write("\n]}\n")

            saved_files.append(output_filename)

    return saved_files

def _csv_file_to_python(csv_file):
    """
    Transform a CSV file into a Python list of dictionary content
    :param csv_file: CSV file path
    :return: [ { bunch of transformed csv data here } ]
    """
    headers = []
    all_data = []
    trim_dangling_comma = False
    with open(csv_file, 'r') as f:
        for index, line in enumerate(f.readlines()):
            line = line.strip()
            if trim_dangling_comma:
                line = line[:-1]

            if index == 0:
                # Headers
                # Correct some dangling comma export issues
                if line.strip().endswith(","):
                    line = line[:-1]
                    trim_dangling_comma = True
                headers = line.split(",")

            else:
                # Data
                data = {}
                values = line.split(",")
                for i, h in enumerate(headers):
                    if len(values) <= i:
                        continue
                    if len(values[i]) == 0:
                        continue
                    data[h] = values[i] \
                    .replace(COMMA_DELIMITER_REPLACEMENT_CHARACTER, ",") \
                    .replace(QUOTE_DELIMITER_REPLACEMENT_CHARACTER, "\"")
                all_data.append(data)
    return all_data

def _generate_ism(transformed_files, ism_path):
    """
    Generate an integrated sensor matrix
    TODO add modes
    TODO integrate behaviors to add context to devices - for example, a Vayyar device near an exit acts like an entry sensor.
    :param transformed_files: List of transformed files from our data request download
    :param ism_path: File path to save the resulting ISM file
    :return: ism_path if successful
    """
    print("Generating ISM {}...".format(ism_path))
    modes_csv = None
    csv_strings = []
    csv_types = []
    csv_total_headers = []
    is_file_broken = False
    for transformed_filename in transformed_files:
        print("\t=> Processing {}".format(transformed_filename))
        device_type = int(os.path.basename(transformed_filename).split('_')[0])
        # device_id = transformed_device_ids[file_index]
        # Need improvement to make the device type be easier to fetch and more solid.
        is_vayyar = device_type in [2000]
        is_motion = device_type in [9138, 10038]
        is_entry = device_type in [9114, 10014, 10074]
        is_pressurepad = device_type in [9039]

        # Currently not supporting other devices besides Entry and Motion
        # Currently not supporting index numbers
        if is_motion or is_pressurepad or is_entry or is_vayyar:
            focused_csv = "device_type,device_id,description,behavior,timestamp_ms,timestamp_iso"
            with open(transformed_filename, 'r') as f:
                for index, line in enumerate(f.readlines()):
                    if index == 0:
                        original_headers = line.replace('\n', '').replace('\r', '').split(",")
                        # The current_parameter_state will maintain the current state of each parameter
                        # Because the server doesn't fill out the complete state for each parameter at every timestamp
                        current_parameter_state = {}

                        for i in range(0, 9):
                            # Only keep the device param
                            del (original_headers[0])

                        # Add a placeholder for PIR motion detection events with Vayyar Home
                        # Note that this now produces more CSV headers than we have columns for in our data
                        if is_vayyar:
                            original_headers.append("motionStatus")

                        if is_entry and 'doorStatus' not in original_headers:
                            is_file_broken = True
                            break

                        is_file_broken = False

                        # Add the header to our csv headers
                        for header in original_headers:
                            focused_csv += ",{}".format(header)
                            current_parameter_state[header] = None

                        csv_total_headers.append(len(focused_csv.split(',')))

                        # Line break
                        focused_csv += "\r\n"
                    else:
                        line = line.replace('\n', '').replace('\r', '')
                        value = ""
                        in_bracket = 0
                        in_quote = 0
                        line_list = []
                        for c in line:
                            if c == '[':
                                in_bracket += 1
                            elif c == ']':
                                in_bracket -= 1

                            if c == '\"' and in_quote > 0:
                                in_quote -= 1
                            elif c == '\"':
                                in_quote += 1

                            if in_bracket == 0 and in_quote == 0:
                                if c == ',':
                                    line_list.append(value)
                                    value = ""
                                    continue

                            value += c

                        line_list.append(value)

                        for i in range(9, len(line_list)):
                            index = i - 9
                            try:
                                value = normalize_measurement(line_list[i])
                            except:
                                # Probably a Vayyar Home device where the 'motionStatus' header we added isn't in the real original headers of this device.
                                continue

                            if value != '':
                                current_parameter_state[original_headers[index]] = value

                                if is_vayyar:
                                    # Special handling for Vayyar Home to transform it into a PIR motion detector.
                                    if original_headers[index] == "occupancy":
                                        try:
                                            current_parameter_state["motionStatus"] = value > 0
                                        except Exception as e:
                                            print("Exception")

                                    elif original_headers[index] == "occupancyTarget":
                                        current_parameter_state[original_headers[index]] = str(value).replace("-", ";")
                                        current_parameter_state["motionStatus"] = value != ""

                        focused_csv += "{},{},{},{},{},{}".format(line_list[2], line_list[3],
                                                                  line_list[4], line_list[8],
                                                                  line_list[5], line_list[6])

                        for header in original_headers:
                            focused_csv += ",{}".format(current_parameter_state[header])

                        focused_csv += "\r\n"

            if is_file_broken:
                continue

            # CONCLUDE
            csv_strings.append(focused_csv)

            if is_motion or is_vayyar:
                csv_types.append("motion")

            elif is_entry:
                csv_types.append("entry")

            elif is_pressurepad:
                csv_types.append("pressure")

    # TODO properly extract the modes CSV for the ISM
    if modes_csv is not None:
        csv_strings.append(modes_csv)
        csv_types.append("modes")
        csv_total_headers.append(5)

    print("\t=> Generating ISM")
    import ism
    integrated_sensor_matrix = ism.create_integrated_sensor_matrix_str(csv_strings, csv_types, csv_total_headers, get_csv())

    import pickle
    if os.path.exists(ism_path):
        os.remove(ism_path)

    with open(ism_path, 'wb') as f:
        pickle.dump(integrated_sensor_matrix, f)
        print("Exported Integrated Sensor Matrix: {}".format(ism_path))

    return ism_path


def get_user_info(server, user_key, user_id=None):
    """
    Get the user info

    https://iotapps.docs.apiary.io/#reference/user-accounts/manage-a-user/get-user-information
    :param server: Server address
    :param user_key: User API key
    :param user_id: User ID for administrator access
    """
    import requests
    global _https_proxy

    try:
        # get user info
        http_headers = {"API_KEY": user_key, "Content-Type": "application/json"}
        params = {}

        if user_id is not None:
            params['userId'] = user_id

        r = requests.get(server + "/cloud/json/user", params=params, headers=http_headers, proxies=_https_proxy)
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    except ApiError as e:
        sys.stderr.write("Maestro Cli Get User Info Error: " + e.msg)
        sys.stderr.write("\n\n")
        raise e


def get_devices_from_location(server, user_key, location_id):
    """
    Get all the devices from your location
    https://iotapps.docs.apiary.io/reference/devices/manage-devices/get-a-list-of-devices

    :param server: Server
    :param user_key: API Key
    :param location_id: Location ID
    """
    http_headers = {"API_KEY": user_key, "Content-Type": "application/json"}
    import requests
    global _https_proxy

    params = {
        'locationId': location_id
    }

    r = requests.get(server + "/cloud/json/devices", headers=http_headers, params=params, proxies=_https_proxy)
    j = json.loads(r.text)

    _check_for_errors(j)
    return j.get('devices', [])


def normalize_measurement(measure):
    """
    Transform a measurement's value, which could be a string, into a real value - like a boolean or int or float
    :param measure: a raw measurement's value
    :return: a value that has been corrected into the right type
    """
    try:
        return eval(measure, {}, {})

    except:
        if measure in ['true', 'True']:
            return True

        elif measure in ['false', 'False']:
            return False

        else:
            return measure


def request_data(server, location_id, user_key, initialization_days=1, type=1, device_id=None, oldest_timestamp_ms=None, newest_timestamp_ms=None, param_name_list=None, reference=None, index=None, ordered=1):
    """
    Selecting a large amount of data from the database can take a significant amount of time and impact server
    performance. To avoid this long waiting period while executing bots, a bot can submit a request for all the
    data it wants from this location asynchronously. The server gathers all the data on its own time, and then
    triggers the bot with trigger 2048. Your bot must include trigger 2048 to receive the trigger.

    Selected data becomes available as a file in CSV format, compressed by LZ4, and stored for one day.
    The bot receives direct access to this file.

    You can call this multiple times to extract data out of multiple devices. The request will be queued up and
    the complete set of requests will be flushed at the end of this bot execution.

    :param type: DATA_REQUEST_TYPE_*, default (1) is key/value device parameters
    :param device_id: Device ID to download historical data from
    :param oldest_timestamp_ms: Oldest timestamp in milliseconds
    :param newest_timestamp_ms: Newest timestamp in milliseconds
    :param param_name_list: List of parameter names to download
    :param reference: Reference so when this returns we know who it's for
    :param index: Index to download when parameters are available with multiple indices
    :param ordered: 1=Ascending (default); -1=Descending.
    """

    import time
    data_requests = []
    request = {
        "type": type
    }

    if device_id is not None:
        request["deviceId"] = device_id

    if oldest_timestamp_ms is not None:
        request['startTime'] = oldest_timestamp_ms
    else:
        request['startTime'] = int(time.time()) - initialization_days * 24 * 60 * 60 * 1000

    if newest_timestamp_ms is not None:
        request['endTime'] = newest_timestamp_ms
    else:
        request['endTime'] = int(time.time())

    if param_name_list is not None:
        request['paramNames'] = param_name_list

    if reference is not None:
        request['key'] = reference

    if index is not None:
        request["index"] = index

    if ordered is not None:
        request["ordered"] = ordered

    data_requests.append(request)

    j = json.dumps({
        "dataRequests": data_requests
    })

    headers = {"API_KEY": user_key, "Content-Type": "application/json"}
    url = "{}/cloud/json/dataRequests?locationId={}".format(server, location_id)
    print(url)
    print(j)
    r = _session().post(url, headers=headers, data=j)
    j = json.loads(r.text)
    try:
        _check_for_errors(j)

    except ApiError as e:
        print(str(e.msg))

    r = _session().get(url, headers=headers)
    j = json.loads(r.text)
    _check_for_errors(j)

    return j


def _get_subdomain_from_url(cloud_url):
    """
    Return the subdomain from the given cloud URL, for example https://sboxall.peoplepowerco.com becomes 'sboxall'
    :param cloud_url: Full cloud URL to shorten into a subdomain
    :return: Subdomain
    """
    return cloud_url.replace("http://", "").replace("https://", "").split(".")[0]

def get_csv():
    output = "location_id,timestamp_ms,timestamp_iso,type,"
    output += "0,0,0,0,"
    return output


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    import unicodedata
    import re
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

# ===============================================================================
# ApiError Exception Class
# ===============================================================================
def _check_for_errors(json_response):
    """
    Check for JSON errors.
    The optional url, params, and headers will print out when an error is found.
    :param json_response: JSON response from the People Power cloud
    :return:
    """
    RESULT_CODE_LOCKOUT = 44

    if not json_response:
        raise ApiError("No response from the server!", -1)

    if json_response['resultCode'] > 0:
        msg = "Unknown error!"
        if 'resultCodeMessage' in json_response.keys():
            msg = json_response['resultCodeMessage']

        elif 'resultCodeDesc' in json_response.keys():
            msg = json_response['resultCodeDesc']

        result_code = int(json_response['resultCode'])
        exception = ApiError(msg, result_code)

        if result_code == RESULT_CODE_LOCKOUT:
            exception.lock_timeout = json_response['lockTimeout']
        else:
            print("API Error: \n{}".format(json.dumps(json_response, indent=2, sort_keys=True)))

        raise exception

    del (json_response['resultCode'])


class ApiError(Exception):
    """
    API Error from the AI+IoT Platform
    """

    def __init__(self, msg, code):
        super(ApiError).__init__(type(self))

        # Message from the server about this error
        self.msg = msg

        # Result Code
        self.code = code

        # Lockout time
        self.lock_timeout = None

    def is_locked_out(self):
        """
        :return: True if we're locked out
        """
        return self.lock_timeout is not None

    def wait_for_lock_timeout(self):
        """
        Sleep this whole system while we wait for the server to let us start talking again
        :return:
        """
        if self.lock_timeout is not None:
            print("\n\n⏰ The AI+IoT Platform told us to calm down on the API calls for {} seconds...".format(round(int(self.lock_timeout) / 1000)))
            import time
            time.sleep(int(self.lock_timeout) / 1000)

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg
