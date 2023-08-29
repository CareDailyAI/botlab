#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maestro CLI for developers

To get started you will need an Organization.  Visit https://app.caredaily.ai/signup to create one now!

To see a list of organizations, use an Organization Admin or Super Admin account.
    --print

Then, to use the rest of the tool, you need to create a new user account and assign it the Data Access role
and associated that user account with the organization as an administrator. Then type:
    --help

@author:     David Moss, Destry Teeter

@copyright:  2012 - 2023 People Power Company. All rights reserved.

@contact:    dmoss@caredaily.ai, destry@caredaily.ai
"""

import sys
import json

try:
    import maestro_cli.api as api
except:
    import api
import time

# Our default server address
DEFAULT_BASE_SERVER_URL = "app.peoplepowerco.com"

def main():
    """
    Main Function
    :return:
    """
    import colorama
    colorama.init(autoreset=True)

    # Setup argument parser
    from argparse import ArgumentParser
    from argparse import RawDescriptionHelpFormatter
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = """%s

      Created by David Moss

      Copyright 2023 People Power Company. All rights reserved.

      Distributed on an "AS IS" basis without warranties
      or conditions of any kind, either express or implied.
    """ % (program_shortdesc)
    parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter, add_help=False)
    primary_group = parser.add_argument_group(Color.BOLD + "Primary Arguments" + Color.END)
    primary_group.add_argument("--admin_username", dest="admin_username", help="Administrative username")
    primary_group.add_argument("--admin_password", dest="admin_password", help="Administrative password")
    primary_group.add_argument("-a", "--apikey", dest="admin_key", help="Admin API key, instead of a admin_username / admin_password")
    primary_group.add_argument("-s", "--server", dest="cloud_url", help="Base cloud server URL (default is " + DEFAULT_BASE_SERVER_URL + ")")
    primary_group.add_argument("-o", "--organization_id", dest="organization_id", help="The organization ID to extract data from")
    primary_group.add_argument("-l", "--location_id", dest="location_id", help="The location ID to extract data from")
    primary_group.add_argument("-h", "--help", dest="help", action="store_true", help="Show this help message and exit")
    primary_group.add_argument("-d", "--device_id", dest="device_id", help="The device ID to extract device params lz4 file address")
    primary_group.add_argument("-i", "--import_path", dest="import_path", help="Import additional python modules from a folder path.")

    functional_group = parser.add_argument_group(Color.BOLD + "Functions" + Color.END)
    functional_group.add_argument("--print", dest="print_organizations", action="store_true", help="Print a list of all organizations you have access to.")
    functional_group.add_argument("--narratives", dest="narratives", action="store_true", help="Gracefully download all narratives.")
    functional_group.add_argument("--data", dest="data", action="store_true", help="Gracefully download all device data.")
    functional_group.add_argument("--media", dest="media", action="store_true", help="Download all media from the given organization or location")
    functional_group.add_argument("--subscriptions", dest="subscriptions", action="store_true", help="Capture a list of active subscriptions.")
    functional_group.add_argument("--installations", dest="installations", action="store_true", help="Capture the installation date of the earliest smart home center.")
    functional_group.add_argument("--get_properties", dest="get_properties", action="store_true", help="Download a list of properties from this organization.")
    functional_group.add_argument("--set_properties", dest="set_properties", help="Properties in JSON format such '{\"name1\": \"value1\", \"name2\": \"value2\"} or '{\"bot.LIST\": \"[1, 2, 3]\"}' or '{\"bot.DICT\": \"{\\\"Hello\\\": \\\"World\\\"}\"}'. All parameters beginning with 'bot.' will be sent to bots and can overrride default bot properties.")
    functional_group.add_argument("--properties", dest="properties", help="Specify a properties module (i.e. 'properties/something.py') to apply/update directly from a file.")
    functional_group.add_argument("--ism", dest="generate_ism", action="store_true", help="Generate an integrated sensor matrix from all device data from this location, useful for building machine learning models.")
    functional_group.add_argument("--lz4_request", dest="lz4_request", help="Generate a download link for the resulting .lz4 data request.")
    functional_group.add_argument("--start_time_ms", dest="start_time_ms", help="For data downloads, this is an optional absolute Unix epoch start time in milliseconds")
    functional_group.add_argument("--days_ago", dest="days_ago", help="Number of days ago to start a data request. Instead of looking up a start_time_ms, this will figure it out for you.")
    functional_group.add_argument("--end_time_ms", dest="end_time_ms", help="For data downloads, this is an optional absolute Unix epoch end time in milliseconds")

    # Process arguments
    args, unknown = parser.parse_known_args()

    if args.help:
        parser.print_help()
        return 0

    if not args.cloud_url:
        args.cloud_url = DEFAULT_BASE_SERVER_URL

    if "http" not in args.cloud_url:
        args.cloud_url = "https://" + args.cloud_url

    print("Cloud URL: {}".format(args.cloud_url))

    if args.days_ago is not None:
        now = int(time.time() * 1000)
        args.start_time_ms = now - (int(args.days_ago) * api.ONE_DAY_MS)

    if args.start_time_ms is not None:
        start_time_ms = args.start_time_ms
        print("Applying start_time_ms {}".format(start_time_ms))
    else:
        start_time_ms = 1546300800000

    if args.end_time_ms is not None:
        print("Applying end_time_ms {}".format(args.end_time_ms))

    if args.admin_key is None:
        if args.admin_username is None:
            args.admin_username = input('Admin email address: ')

        if args.admin_password is None:
            import getpass
            args.admin_password = getpass.getpass()

        args.admin_key = api.login(args.cloud_url, args.admin_username, args.admin_password, admin=True)

    if args.import_path:
        import sys
        sys.path.insert(0, args.import_path)

    if args.print_organizations:
        print_organizations(args.cloud_url, args.admin_key, args.organization_id)
        return

    if args.narratives:
        if args.organization_id is None and args.location_id is None:
            print(Color.RED + "Please provide an organization or location ID.\n" + Color.END)
            return

        print(Color.BOLD + "\nDOWNLOADING NARRATIVES" + Color.END)
        if args.location_id is None and args.location_id is None:
            locations = api.get_location_ids(args.cloud_url, args.admin_key, args.organization_id)
            print("Locations: {}".format(locations))
        else:
            locations = [args.location_id]

        index = 0
        for location_id in locations:
            index += 1
            print("({} of {}) Narrative request for this location ID: {}".format(index, len(locations), location_id))
            api.data_request(args.cloud_url, args.admin_key, api.DATA_REQUEST_TYPE_LOCATION_NARRATIVES, location_id=location_id, start_time_ms=start_time_ms, end_time_ms=args.end_time_ms)

    if args.data:
        if args.organization_id is None and args.location_id is None:
            print(Color.RED + "Please provide an organization or location ID.\n" + Color.END)
            return

        if args.organization_id is not None:
            locations = api.get_location_ids(args.cloud_url, args.admin_key, args.organization_id)
            print("Locations: {}".format(locations))
        else:
            locations = [args.location_id]

        # This doesn't work right now because the data requests in api.py are now chunked and don't cache the previous request keys for each chunk.
        # print(Color.BOLD + "\nPRE-REQUESTING DEVICE DATA" + Color.END)
        # index = 0
        # for location_id in locations:
        #     index += 1
        #     print("({} of {}) Data pre-request for location ID: {}".format(index, len(locations), location_id))
        #     api.data_request(args.cloud_url, args.admin_key, api.DATA_REQUEST_TYPE_DEVICE_PARAMETERS, location_id=location_id, no_download=True, start_time_ms=start_time_ms, end_time_ms=args.end_time_ms)
        #     time.sleep(5)

        print(Color.BOLD + "\nDOWNLOADING DEVICE DATA" + Color.END)
        index = 0
        for location_id in locations:
            index += 1
            print("({} of {}) Data download request for this location ID: {}".format(index, len(locations), location_id))
            api.data_request(args.cloud_url, args.admin_key, api.DATA_REQUEST_TYPE_DEVICE_PARAMETERS, location_id=location_id, no_download=False, start_time_ms=start_time_ms, end_time_ms=args.end_time_ms)

    if args.lz4_request is not None:
        if args.location_id is None:
            print(Color.RED + "Please provide an organization or location ID.\n" + Color.END)
            return

        if args.device_id is None:
            print(Color.RED + "Please provide a device ID.\n" + Color.END)
            return

        import uuid
        reference = str(uuid.uuid4())
        print("Making data request with reference {}".format(reference))
        response = api.request_data(args.cloud_url,
                                    args.location_id,
                                    args.admin_key,
                                    device_id=args.device_id,
                                    oldest_timestamp_ms=args.start_time_ms,
                                    param_name_list=None,
                                    reference=reference)

        if 'results' in response:
            print("{}".format(response['results']))
        else:
            print("No result.")

    if args.subscriptions:
        if args.organization_id is None and args.location_id is None:
            print(Color.RED + "Please provide an organization or location ID.\n" + Color.END)
            return

        if args.organization_id is not None:
            locations = api.get_location_ids(args.cloud_url, args.admin_key, args.organization_id)
            print("Locations: {}".format(locations))
        else:
            locations = [args.location_id]

        print(Color.BOLD + "\nDOWNLOADING SUBSCRIPTIONS" + Color.END)

        empty = 0

        print("LOCATION ID, STATUS, SUBSCRIPTION, START DATE, START DATE MS, END DATE, END DATE MS")
        for location_id in locations:
            print()
            time.sleep(5)

            # Get active subscriptions
            subscriptions = api.get_subscriptions(args.cloud_url, args.admin_key, location_id)
            if subscriptions is None:
                # Location does not exist
                print("{}, DNE, , , ".format(location_id))
                continue

            if len(subscriptions) > 0:
                for sub in subscriptions:
                    print("{}, ACTIVE, {}, {}, {}, {}, {}".format(location_id, sub['plan']['name'], sub['issueDate'], sub['issueDateMs'], sub['endDate'], sub['endDateMs']))
            else:
                empty += 1
                print("{}, ACTIVE, NONE, NONE, NONE".format(location_id))

            # Get old subscriptions
            subscriptions = api.get_subscriptions(args.cloud_url, args.admin_key, location_id, status=api.SERVICE_PLAN_STATUS_CANCELLED)
            if len(subscriptions) > 0:
                for sub in subscriptions:
                    print("{}, INACTIVE, {}, {}, {}, {}, {}".format(location_id, sub['plan']['name'], sub['issueDate'], sub['issueDateMs'], sub['endDate'], sub['endDateMs']))

        print("Total locations: {}; Total locations without an active subscription: {}".format(len(locations), empty))

        # get_subscription_totals(args.cloud_url, args.admin_key, args.organization_id)

    if args.media:
        # Download files and media
        if args.organization_id is None and args.location_id is None:
            print(Color.RED + "Please provide an organization or location ID.\n" + Color.END)
            return

        if args.organization_id is not None:
            locations = api.get_location_ids(args.cloud_url, args.admin_key, args.organization_id)
            print("Locations: {}".format(locations))
        else:
            locations = [args.location_id]

        print(Color.BOLD + "\nDOWNLOADING MEDIA" + Color.END)

        import urllib.request
        from pathlib import Path
        import os
        media_base_path = os.path.join(os.getcwd(), 'downloads', 'media')
        if args.organization_id is not None:
            media_base_path = os.path.join(media_base_path, "organization_{}".format(args.organization_id))

        for location_id in locations:
            print()
            time.sleep(5)
            location_download_path = os.path.join(media_base_path, "location_{}".format(location_id))
            Path(location_download_path).mkdir(parents=True, exist_ok=True)

            devices = api.get_devices(args.cloud_url, args.admin_key, location_id)
            media = api.get_files(args.cloud_url, args.admin_key, location_id=location_id)
            for m in media:
                device_id = m['deviceId']
                file_id = m['id']
                device_desc = "Unnamed Device"

                for d in devices:
                    if d['id'] == device_id:
                        device_desc = d['desc']

                        # Make the device description filename friendly friendly
                        device_desc = "".join([c for c in device_desc if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
                        device_desc = device_desc.replace("  ", " ")
                        break

                download_url = api.get_file_download_url(args.cloud_url, args.admin_key, location_id, file_id)

                file_download_path = os.path.join(location_download_path, "{} - {}_{}.png".format(device_desc, device_id, file_id))

                urllib.request.urlretrieve(download_url, file_download_path)
                print("Saved: {}".format(file_download_path))

        return

    if args.installations:
        if args.organization_id is None and args.location_id is None:
            print(Color.RED + "Please provide an organization or location ID.\n" + Color.END)
            return

        if args.organization_id is not None:
            locations = api.get_location_ids(args.cloud_url, args.admin_key, args.organization_id)
            print("Locations: {}".format(locations))
        else:
            locations = [args.location_id]

        print(Color.BOLD + "\nDOWNLOADING INSTALLATION DATES" + Color.END)

        empty = 0

        print("LOCATION ID, GATEWAY INSTALL DATE, GATEWAY INSTALL DATE MS, TOTAL GATEWAY, TOTAL ENTRY, TOTAL MOTION, TOTAL BUTTON, TOTAL WATER LEAK, TOTAL DEVICES, TOTAL ONLINE DEVICES")

        for location_id in locations:
            print()
            time.sleep(5)

            # Get active subscriptions
            devices = api.get_devices(args.cloud_url, args.admin_key, location_id)

            gateway = 0
            entry = 0
            motion = 0
            button = 0
            water = 0
            total = 0
            online = 0
            install_date = ""
            install_date_ms = None

            if devices is None:
                # Location does not exist
                devices = []

            total = len(devices)
            for device in devices:
                if 'modelId' not in device:
                    continue
                
                online += device['connected']
                entry += device['modelId'] == "entrySensor"
                motion += device['modelId'] == "motionSensor"
                button += device['modelId'] == "button"
                water += device['modelId'] == "waterSensor"
                gateway += device['modelId'] == "gateway"

                if device['modelId'] == "gateway":
                    if install_date_ms is None:
                        install_date_ms = device['startDateMs']
                        install_date = device['startDate']

                    elif device['startDateMs'] < install_date_ms:
                        install_date_ms = device['startDateMs']
                        install_date = device['startDate']

            print("{}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(location_id, install_date, install_date_ms, gateway, entry, motion, button, water, total, online))

        print("\nTotal locations: {}; Total locations without devices: {}".format(len(locations), empty))
        return

    if args.get_properties:
        if args.organization_id is None:
            print(Color.RED + "Please provide an organization ID.\n" + Color.END)
            return

        print(Color.BOLD + "\nDOWNLOADING ORGANIZATION PROPERTIES" + Color.END)
        properties = api.get_organization_properties(args.cloud_url, args.admin_key, args.organization_id)

        print("{}\n".format(json.dumps(properties, indent=2, sort_keys=True)))
        return

    if args.set_properties:
        if args.organization_id is None:
            print(Color.RED + "Please provide an organization ID.\n" + Color.END)
            return

        properties = json.loads(args.set_properties)
        print(Color.BOLD + "SETTING PROPERTIES: {}".format(properties) + Color.END)
        api.set_organization_properties(args.cloud_url, args.admin_key, args.organization_id, properties)

        return

    if args.properties:
        import importlib
        args.properties = args.properties.replace(".py","").replace("/", ".")
        properties = importlib.import_module(args.properties)
        organization_id = None
        if hasattr(properties, "ORGANIZATION_ID"):
            organization_id = properties.ORGANIZATION_ID

        else:
            if hasattr(properties, "ORGANIZATION_SHORT_NAME"):
                signup_code = properties.ORGANIZATION_SHORT_NAME
            elif hasattr(properties, "ORGANIZATION_SIGNUP_CODE"):
                signup_code = properties.ORGANIZATION_SIGNUP_CODE

            else:
                print("Please add one of the following to your properties module:")
                print("* ORGANIZATION_SHORT_NAME")
                print("* ORGANIZATION_SIGNUP_CODE")
                print("* ORGANIZATION_ID")
                print()
                return

            organization_id = api.get_organization_id_from_signup_code(args.cloud_url, args.admin_key, signup_code)
            if organization_id is None:
                print("Couldn't find an organization on this server for the sign-up code / domain name / short name '{}'".format(signup_code))
                return

        print(Color.GREEN + "Applying properties to organization ID {}".format(organization_id) + Color.END)

        properties_list = [item for item in dir(properties) if not item.startswith("__")]
        for p in properties_list:
            property = {"bot." + p : json.dumps(getattr(properties, p))}
            print(Color.BOLD + "SETTING PROPERTY: " + Color.END + "{}".format(property))
            api.set_organization_properties(args.cloud_url, args.admin_key, organization_id, property)
        return

    if args.generate_ism:
        if args.organization_id is None and args.location_id is None:
            print(Color.RED + "Please provide an organization or location ID.\n" + Color.END)
            return

        if args.organization_id is not None:
            locations = api.get_location_ids(args.cloud_url, args.admin_key, args.organization_id)
            print("Locations: {}".format(locations))
        else:
            locations = [args.location_id]

        print(Color.BOLD + "\nREQUESTING DEVICE DATA" + Color.END)
        index = 0
        for location_id in locations:
            index += 1
            print("({} of {}) Data request for location ID: {}".format(index, len(locations), location_id))
            api.generate_ism(args.cloud_url, args.admin_key, location_id=args.location_id)
            time.sleep(5)

        print(Color.BOLD + "\nISM FILE GENERATED" + Color.END)

    if not args.narratives and not args.data and not args.subscriptions and not args.get_properties and not args.set_properties and not args.generate_ism and not args.properties:
        print_organizations(args.cloud_url, args.admin_key, args.organization_id)
        parser.print_help()
        return 0


def get_subscription_totals(cloud_url, admin_key, organization_id):
    """
    Get subscription totals for the given organization ID and any sub-organizations

    :param cloud_url: Cloud URL
    :param admin_key: Administrative API key
    :param organization_id: Organization ID
    :return:
    """
    orgs = api.get_sub_organizations(cloud_url, admin_key, organization_id)
    print("Organizations: {}".format(json.dumps(orgs, indent=2, sort_keys=True)))

    for o in orgs:
        _print_organization_contact_info(o)
        location_ids = api.get_location_ids(cloud_url, admin_key, o['id'])
        print("Location IDs: {}".format(location_ids))
        for location_id in location_ids:
            try:
                subscription_json = api.get_subscriptions(cloud_url, admin_key, location_id)
            except api.ApiError as e:
                if e.code == 44:
                    time.sleep(5)
                else:
                    print("Can't get subscription information. Make sure this admin account has a Data Access role.")

            plan = "No subscription"
            for s in subscription_json:
                if 'plan' in s:
                    if 'name' in s['plan']:
                        plan = s['plan']['name']

            print("Location {} : {}".format(location_id, plan))
            time.sleep(1)
        print("\n")


def _print_organization_contact_info(organization_json):
    """
    Print the contact information for an organization
    :param organization_json:
    :return:
    """
    street_address_1 = ""
    street_address_2 = ""
    city = ""
    state = ""
    zip = ""
    contact_name_1 = ""
    contact_email_1 = ""
    contact_phone_1 = ""

    if 'addrStreet1' in organization_json:
        street_address_1 = organization_json['addrStreet1']

    if 'addrStreet2' in organization_json:
        street_address_2 = organization_json['addrStreet2']

    if 'addrCity' in organization_json:
        city = organization_json['addrCity']

    if 'state' in organization_json:
        state = organization_json['state']['abbr']

    if 'zip' in organization_json:
        zip = organization_json['zip']

    if 'contactEmail1' in organization_json:
        contact_email_1 = organization_json['contactEmail1']

    if 'contactName1' in organization_json:
        contact_name_1 = organization_json['contactName1']

    if 'contactPhone1' in organization_json:
        contact_phone_1 = organization_json['contactPhone1']

    print(Color.GREEN + organization_json['name'].upper() + Color.END)

    if contact_name_1 != "":
        print("\tAttention: {}".format(contact_name_1))

    if street_address_1 != "":
        print("\t{}".format(street_address_1))
    else:
        print("\tNo address provided")
        print("\n")
        return

    if street_address_2 != "":
        print("\t{}".format(street_address_2))

    if city != "" and state != "" and zip != "":
        print("\t{}, {} {}".format(city, state, zip))

    if contact_phone_1 != "":
        print("\t{}".format(contact_phone_1))

    if contact_email_1 != "":
        print("\t{}".format(contact_email_1))

    print("\n")


def print_organizations(cloud_url, admin_key, organization_id=None):
    """
    Print all organizations you can see, and their hierarchy
    :param cloud_url: Cloud URL
    :param admin_key: Admin key
    :return:
    """
    if organization_id is not None:
        orgs = api.get_sub_organizations(cloud_url, admin_key, organization_id)
    else:
        orgs = api.get_organizations(cloud_url, admin_key)

    top_orgs = {}
    sub_orgs = {}
    for o in orgs:
        if 'parentId' in o:
            sub_orgs[o['id']] = o
        else:
            top_orgs[o['id']] = o

    for org_id in top_orgs:
        try:
            total_locations, active_devices, inactive_devices = api.get_organization_statistics(cloud_url, admin_key, org_id)
        except:
            total_locations, active_devices, inactive_devices = "N/A", "N/A", "N/A"
        print("\n* " + Color.GREEN + top_orgs[org_id]['name'] + Color.END + "\n  id={}; locations={}; active devices={}; inactive devices={}".format(org_id, total_locations, active_devices, inactive_devices))

        for sub_id in sub_orgs:
            if sub_orgs[sub_id]['parentId'] == org_id:
                try:
                    total_locations, active_devices, inactive_devices = api.get_organization_statistics(cloud_url, admin_key, sub_id)
                except:
                    total_locations, active_devices, inactive_devices = "N/A", "N/A", "N/A"
                print("\n\t" + Color.PURPLE + sub_orgs[sub_id]['name'] + Color.END + "\n\tid={}; locations={}; active devices={}; inactive devices={}".format(sub_id, total_locations, active_devices, inactive_devices))

    if len(top_orgs) == 0 and len(sub_orgs) > 0:
        # Edge case: we only request a sub-organization. Print it out.
        for sub_id in sub_orgs:
            try:
                total_locations, active_devices, inactive_devices = api.get_organization_statistics(cloud_url, admin_key, sub_id)
            except:
                total_locations, active_devices, inactive_devices = "N/A", "N/A", "N/A"
            print("\n\t" + Color.PURPLE + sub_orgs[sub_id]['name'] + Color.END + "\n\tid={}; locations={}; active devices={}; inactive devices={}".format(sub_id, total_locations, active_devices, inactive_devices))

    print("\n")

#===============================================================================
# Color Class for CLI
#===============================================================================
class Color:
    """
    Color your command line output text with Color.WHATEVER and Color.END
    """
    # Cross-platform color compatibility. Please see notes at:
    # https://github.com/tartley/colorama
    from colorama import Fore, Style
    PURPLE = Fore.MAGENTA
    CYAN = Fore.CYAN
    BLUE = Fore.BLUE
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    BOLD = Style.BRIGHT
    END = Style.RESET_ALL


# ===============================================================================
# Command Line Interface entry point
# ===============================================================================
if __name__ == "__main__":
    sys.exit(main())

