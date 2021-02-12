'''
Created on March 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import json
import utilities.utilities as utilities
import domain

import localization

from controller import Controller

def run(botengine):
    """
    Entry point for bot microservices
    :param botengine: BotEngine environment object, our window to the outside world.
    """
    localization.initialize(botengine)

    #===========================================================================
    # print("INPUTS: " + json.dumps(botengine.get_inputs(), indent=2, sort_keys=True))
    #===========================================================================
    trigger_type = botengine.get_trigger_type()
    triggers = botengine.get_triggers()
    print("\n\n")
    botengine.get_logger().info("TRIGGER : " + str(trigger_type))
    
    # Grab our non-volatile memory
    controller = load_controller(botengine)

    # RESET
    if trigger_type == 0:
        # Reset or new version!
        controller.new_version(botengine)

    # SCHEDULE TRIGGER
    if trigger_type & botengine.TRIGGER_SCHEDULE != 0:
        schedule_id = "DEFAULT"
        if 'scheduleId' in botengine.get_inputs():
            schedule_id = botengine.get_inputs()['scheduleId']
            botengine.get_logger().info("Schedule fired: {}".format(schedule_id))

        controller.run_intelligence_schedules(botengine, schedule_id)
        
    # MODE TRIGGERS
    if trigger_type & botengine.TRIGGER_MODE != 0:
        # Triggered off a change of location
        botengine.get_logger().info("Trigger: Mode")
        for trigger in triggers:
            if 'location' in trigger:
                mode = trigger['location']['event']
                location_id = trigger['location']['locationId']
                controller.sync_mode(botengine, mode, location_id)

    # MEASUREMENT TRIGGERS
    if trigger_type & botengine.TRIGGER_DEVICE_MEASUREMENT != 0:
        # Triggered off a device measurement
        for trigger in triggers:
            if 'device' in trigger:
                device_id = trigger['device']['deviceId']
                device_object = controller.get_device(device_id)
                
                if device_object is not None:
                    device_location = trigger['device']['locationId']

                    # Measurement dictionary by updated timestamp { timestamp : [ {measure}, {measure}, {measure} ] }
                    measures_dict = {}

                    # List of measurements that were not updated
                    measures_static = []

                    # Measurements are provided in 1-second granularity, so 2 measurements may have the same timestamp
                    # This is a list of parameters and the newest time they were updated so we don't have 2 measurements for a single timestamp
                    # { "param_name": newest_updated_timestamp_ms }
                    updated_ts = {}

                    for m in botengine.get_measures_block():
                        if m['deviceId'] == device_id:
                            if not m['updated']:
                                # Not updated
                                measures_static.append(m)

                            else:
                                # Updated parameter
                                # First apply 1 ms corrections for the same parameter at the same time
                                if m['name'] in updated_ts:
                                    if updated_ts[m['name']] == m['time']:
                                        m['time'] = updated_ts[m['name']] + 1

                                # Then add it to our list of measurements we need to trigger upon
                                if m['time'] not in measures_dict:
                                    measures_dict[m['time']] = []

                                updated_ts[m['name']] = m['time']
                                measures_dict[m['time']].append(m)

                    # For each unique timestamp, trigger the microservices from the oldest timestamp to the newest
                    # Also modify the botengine's concept of time to match the current input parameter's time we are executing against, and restore it later.
                    execution_time_ms = botengine.get_timestamp()
                    for timestamp_ms in sorted(list(measures_dict.keys())):
                        botengine.inputs['time'] = timestamp_ms
                        updated_devices, updated_metadata = device_object.update(botengine, measures_static + measures_dict[timestamp_ms])

                        for updated_device in updated_devices:
                            try:
                                updated_device.device_measurements_updated(botengine)

                                # Ping any proxy devices to let any sub-microservices know that the proxy is still connected and delivering measurements
                                if updated_device.proxy_id is not None:
                                    proxy_object = controller.get_device(updated_device.proxy_id)
                                    if proxy_object is not None:
                                        if proxy_object not in updated_devices:
                                            proxy_object.device_measurements_updated(botengine)

                                controller.device_measurements_updated(botengine, device_location, updated_device)

                            except Exception as e:
                                import traceback
                                botengine.get_logger().error("bot.device_measurements_updated(): {}; {}. Continuing execution.".format(str(e), traceback.format_exc()))


                    botengine.inputs['time'] = execution_time_ms

    # DEVICE ALERTS
    if trigger_type & botengine.TRIGGER_DEVICE_ALERT != 0:
        # Triggered off a device alert
        for trigger in triggers:
            if 'device' in trigger:
                device_id = trigger['device']['deviceId']
                device_object = controller.get_device(device_id)

                if device_object is not None:
                    device_location = trigger['device']['locationId']
                    alerts = botengine.get_alerts_block()
                    if alerts is not None:
                        for alert in alerts:
                            botengine.get_logger().info("Alert: " + json.dumps(alert, indent=2, sort_keys=True))

                            # Reformat to extract value
                            alert_params = {}
                            if 'params' in alert:
                                for p in alert['params']:
                                    alert_params[p['name']] = p['value']

                            if alert is not None:
                                device_object.device_alert(botengine, alert['alertType'], alert_params)
                                controller.device_alert(botengine, device_location, device_object, alert['alertType'], alert_params)

    # FILE UPLOAD TRIGGERS
    if trigger_type & botengine.TRIGGER_DEVICE_FILES != 0:
        # Triggered off an uploaded file
        file = botengine.get_file_block()
        botengine.get_logger().info("File: " + json.dumps(file, indent=2, sort_keys=True))
        if file is not None:
            device_object = controller.get_device(file['deviceId'])

            if device_object is not None:
                controller.file_uploaded(botengine, device_object, file)
        
    # QUESTIONS ANSWERED
    if trigger_type & botengine.TRIGGER_QUESTION_ANSWER != 0:
        question = botengine.get_answered_question()
        botengine.get_logger().info("Answered: " + str(question.key_identifier))
        botengine.get_logger().info("Answer = {}".format(question.answer))
        controller.sync_question(botengine, question)
        
    # DATA STREAM TRIGGERS
    if trigger_type & botengine.TRIGGER_DATA_STREAM != 0:
        # Triggered off a data stream message
        data_stream = botengine.get_datastream_block()
        botengine.get_logger().info("Data Stream: " + json.dumps(data_stream, indent=2, sort_keys=True))
        if 'address' not in data_stream:
            botengine.get_logger().warn("Data stream message does not contain an 'address' field. Ignoring the message.")
            
        else:
            address = data_stream['address']

            if 'feed' in data_stream:
                content = data_stream['feed']
            else:
                content = None
            
            if address != "schedule":
                controller.sync_datastreams(botengine, address, content)
            else:
                controller.run_intelligence_schedules(botengine)

    # COMMAND RESPONSES
    if trigger_type & botengine.TRIGGER_COMMAND_RESPONSE != 0:
        botengine.get_logger().info("Command Responses: {}".format(json.dumps(botengine.get_inputs()['commandResponses'])))
        # TODO responses to commands delivered by the bot are available to build out reliable command delivery infrastructure
        pass

    # GOAL / SCENARIO CHANGES
    if trigger_type & botengine.TRIGGER_METADATA != 0:
        # The user changed the goal / scenario for a single sensor
        for trigger in triggers:
            botengine.get_logger().info("Changed device configuration")
            if 'device' in trigger:
                device_id = trigger['device']['deviceId']

                device_object = controller.get_device(device_id)
                if device_object is not None:
                    device_location = trigger['device']['locationId']

                    if 'spaces' in trigger['device']:
                        device_object.spaces = trigger['device']['spaces']
                    else:
                        device_object.spaces = []

                    updated_devices, updated_metadata = device_object.update(botengine, botengine.get_measures_block())

                    for updated_device in updated_metadata:
                        controller.sync_device(botengine, device_location, device_id, updated_device)
                        updated_device.device_metadata_updated(botengine)
                        controller.device_metadata_updated(botengine, device_location, updated_device)

    # LOCATION CONFIGURATION CHANGES
    if trigger_type & botengine.TRIGGER_LOCATION_CONFIGURATION != 0:
        # The user changed location configuration settings, such as adding/removing/changing a user role in the location
        category = None
        previous_category = None
        location_access = None
        previous_location_access = None
        user_id = None
        location_id = botengine.get_location_id()
        users = botengine.get_users_block()
        call_center = botengine.get_callcenter_block()

        if users is not None:
            # User changed roles
            botengine.get_logger().info("User changed roles")
            for user in users:
                botengine.get_logger().info("User: {}".format(user))
                if 'category' in user:
                    category = user['category']

                if 'prevCategory' in user:
                    previous_category = user['prevCategory']

                if 'locationAccess' in user:
                    location_access = user['locationAccess']

                if 'prevLocationAccess' in user:
                    previous_location_access = user['prevLocationAccess']

                if 'userId' in user:
                    user_id = user['userId']

                controller.user_role_updated(botengine, location_id, user_id, category, location_access, previous_category, previous_location_access)

        if call_center is not None:
            # Location call center changed status
            botengine.get_logger().info("Emergency Call Center Updated")
            if 'status' in call_center:
                status = call_center['status']

            if 'userId' in call_center:
                user_id = call_center['userId']

            controller.call_center_updated(botengine, location_id, user_id, status)

    # DATA REQUEST
    if trigger_type & botengine.TRIGGER_DATA_REQUEST != 0:
        # Response to botengine.request_data()
        botengine.get_logger().info("Data request received")
        data = botengine.get_data_block()
        events = {}
        imported = False

        import importlib
        try:
            import lz4.block
            imported = True
        except ImportError:
            botengine.get_logger().error("Attempted to import 'lz4' to uncompress the data request response, but lz4 is not available. Please add 'lz4' to 'pip_install_remotely' in your structure.json.")
            pass

        if imported:
            for d in data:
                reference = None
                if 'key' in d:
                    reference = d['key']

                if reference not in events:
                    events[reference] = {}

                botengine.get_logger().info("Downloading {} ({} bytes)...".format(d['deviceId'], d['compressedLength']))
                r = botengine._requests.get(d['url'], timeout=60, stream=True)
                events[reference][controller.get_device(d['deviceId'])] = lz4.block.decompress(r.content, uncompressed_size=d['dataLength'])

            for reference in events:
                controller.data_request_ready(botengine, reference, events[reference])

        # DO NOT SAVE CORE VARIABLES HERE.
        return

    # Always save your variables!
    botengine.save_variable("controller", controller, required_for_each_execution=True)
    botengine.get_logger().info("<< bot")
    
    
    
def load_controller(botengine):
    """
    Load the Controller object
    :param botengine: Execution environment
    """
    logger = botengine.get_logger()
    try:
        controller = botengine.load_variable("controller")
        logger.info("Loaded the controller")

    except:
        controller = None
        logger.info("Unable to load the controller")

    if controller == None:
        botengine.get_logger().info("Bot : Creating a new Controller object. Hello.")
        controller = Controller()
        botengine.save_variable("controller", controller, required_for_each_execution=True)

    controller.track_new_and_deleted_devices(botengine)
    controller.initialize(botengine)
    return controller



#===============================================================================
# Location Intelligence Timers
#===============================================================================
def _location_intelligence_fired(botengine, argument_tuple):
    """
    Entry point into this bot
    Location intelligence timer or alarm fired
    :param botengine: BotEngine Environment
    :param argument_tuple: (intelligence_id, argument)
    """
    botengine.get_logger().info("\n\nTRIGGER : _location_intelligence_fired()")
    controller = load_controller(botengine)

    try:
        controller.run_location_intelligence(botengine, argument_tuple[0], argument_tuple[1])
    except Exception as e:
        import traceback
        botengine.get_logger().error("{}; {}".format(str(e), traceback.format_exc()))

    botengine.save_variable("controller", controller, required_for_each_execution=True)
    botengine.get_logger().info("<< bot (location timer)")

def start_location_intelligence_timer(botengine, seconds, intelligence_id, argument, reference):
    """
    Start a relative location intelligence timer
    :param botengine: BotEngine environment
    :param seconds: Seconds from the start of the current execution to make this timer fire
    :param intelligence_id: ID of the intelligence module to trigger when this timer fires
    :param argument: Arbitrary argument to pass into the intelligence module's timer_fired() method when this timer fires
    :param reference: Unique reference name that lets us later cancel this timer if needed
    """
    botengine.get_logger().info(">start_location_intelligence_timer({}, {})".format(seconds, reference))
    if reference is not None and reference != "":
        botengine.cancel_timers(reference)
    botengine.start_timer_s(int(seconds), _location_intelligence_fired, (intelligence_id, argument), reference)

def start_location_intelligence_timer_ms(botengine, milliseconds, intelligence_id, argument, reference):
    """
    Start a relative location intelligence timer
    :param botengine: BotEngine environment
    :param milliseconds: Milliseconds from the start of the current execution to make this timer fire
    :param intelligence_id: ID of the intelligence module to trigger when this timer fires
    :param argument: Arbitrary argument to pass into the intelligence module's timer_fired() method when this timer fires
    :param reference: Unique reference name that lets us later cancel this timer if needed
    """
    botengine.get_logger().info(">start_location_intelligence_timer_ms({}, {})".format(milliseconds, reference))
    if reference is not None and reference != "":
        botengine.cancel_timers(reference)
    botengine.start_timer_ms(int(milliseconds), _location_intelligence_fired, (intelligence_id, argument), reference)

def set_location_intelligence_alarm(botengine, timestamp_ms, intelligence_id, argument, reference):
    """
    Set an absolute location intelligence alarm
    :param botengine: BotEngine environment
    :param timestamp: Absolute timestamp in milliseconds at which to trigger this alarm
    :param intelligence_id: ID of the intelligence module to trigger when this alarm fires
    :param argument: Arbitrary argument to pass into the intelligence module's timer_fired() method when this timer fires
    :param reference: Unique reference name that lets us later cancel this timer if needed
    """
    botengine.get_logger().info(">set_location_intelligence_alarm({})".format(timestamp_ms))
    if reference is not None and reference != "":
        botengine.cancel_timers(reference)
    botengine.set_alarm(int(timestamp_ms), _location_intelligence_fired, (intelligence_id, argument), reference)
    
def cancel_location_intelligence_timers(botengine, reference):
    """
    Cancel all location intelligence timers and alarms with the given reference
    :param botengine: BotEngine environment
    :param reference: Unique reference name for which to cancel all timers and alarms
    """
    botengine.cancel_timers(reference)

def is_location_timer_running(botengine, reference):
    """
    Determine if the timer with the given reference is running
    :param botengine: BotEngine environment
    :param reference: Unique reference name for the timer
    :return: True if the timer is running
    """
    return botengine.is_timer_running(reference)

#===============================================================================
# Device Intelligence Timers
#===============================================================================
def _device_intelligence_fired(botengine, argument_tuple):
    """
    Entry point into this bot
    Device intelligence timer or alarm fired
    :param botengine: BotEngine Environment
    :param argument_tuple: (intelligence_id, argument)
    """
    botengine.get_logger().info("\n\nTRIGGER : _device_intelligence_fired()")
    controller = load_controller(botengine)

    try:
        controller.run_device_intelligence(botengine, argument_tuple[0], argument_tuple[1])
    except Exception as e:
        import traceback
        botengine.get_logger().error("{}; {}".format(str(e), traceback.format_exc()))

    botengine.save_variable("controller", controller, required_for_each_execution=True)
    botengine.get_logger().info("<< bot (device timer)")
    

def start_device_intelligence_timer(botengine, seconds, intelligence_id, argument, reference):
    """
    Start a relative device intelligence timer
    :param botengine: BotEngine environment
    :param seconds: Seconds from the start of the current execution to make this timer fire
    :param intelligence_id: ID of the intelligence module to trigger when this timer fires
    :param argument: Arbitrary argument to pass into the intelligence module's timer_fired() method when this timer fires
    :param reference: Unique reference name that lets us later cancel this timer if needed
    """
    botengine.get_logger().info(">start_device_intelligence_timer({}, {})".format(seconds, reference))
    if reference is not None and reference != "":
        botengine.cancel_timers(reference)
    botengine.start_timer_s(int(seconds), _device_intelligence_fired, (intelligence_id, argument), reference)

def start_device_intelligence_timer_ms(botengine, milliseconds, intelligence_id, argument, reference):
    """
    Start a relative device intelligence timer
    :param botengine: BotEngine environment
    :param milliseconds: Milliseconds from the start of the current execution to make this timer fire
    :param intelligence_id: ID of the intelligence module to trigger when this timer fires
    :param argument: Arbitrary argument to pass into the intelligence module's timer_fired() method when this timer fires
    :param reference: Unique reference name that lets us later cancel this timer if needed
    """
    botengine.get_logger().info(">start_device_intelligence_timer_ms({}, {})".format(milliseconds, reference))
    if reference is not None and reference != "":
        botengine.cancel_timers(reference)
    botengine.start_timer_ms(int(milliseconds), _device_intelligence_fired, (intelligence_id, argument), reference)


def set_device_intelligence_alarm(botengine, timestamp_ms, intelligence_id, argument, reference):
    """
    Set an absolute device intelligence alarm
    :param botengine: BotEngine environment
    :param timestamp: Absolute timestamp in milliseconds at which to trigger this alarm
    :param intelligence_id: ID of the intelligence module to trigger when this alarm fires
    :param argument: Arbitrary argument to pass into the intelligence module's timer_fired() method when this timer fires
    :param reference: Unique reference name that lets us later cancel this timer if needed
    """
    botengine.get_logger().info(">set_device_intelligence_alarm({})".format(timestamp_ms))
    if reference is not None and reference != "":
        botengine.cancel_timers(reference)
    botengine.set_alarm(int(timestamp_ms), _device_intelligence_fired, (intelligence_id, argument), reference)
    
def cancel_device_intelligence_timers(botengine, reference):
    """
    Cancel all device intelligence timers and alarms with the given reference
    :param botengine: BotEngine environment
    :param reference: Unique reference name for which to cancel all timers and alarms
    """
    botengine.cancel_timers(reference)

def is_device_timer_running(botengine, reference):
    """
    Determine if the timer with the given reference is running
    :param botengine: BotEngine environment
    :param reference: Unique reference name for the timer
    :return: True if the timer is running
    """
    return botengine.is_timer_running(reference)