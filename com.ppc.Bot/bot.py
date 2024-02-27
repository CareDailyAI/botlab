'''
Created on March 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import localization

import json
import utilities.utilities as utilities
import importlib

from startup import StartUpUtil
from controller import Controller

def run(botengine):
    """
    Entry point for bot microservices

    The bot boots up in this order:
        1. Create the `controller` object.

        2. Synchronize with our devices and create a location object and device objects

        3. new_version() - Executes one time when we're running a new version of the bot
            2.a. Microservices and filters are synchronized inside the location object
            2.a. Each device object, microservice, and filter should run its new_version() event

        4. initialize() - This event executes in every location / device object / microservice / filter on every trigger the bot

    :param botengine: BotEngine environment object, our window to the outside world.
    """
    localization.initialize(botengine)

    #===========================================================================
    # print("INPUTS: " + json.dumps(botengine.get_inputs(), indent=2, sort_keys=True))
    #===========================================================================
    trigger_type = botengine.get_trigger_type()
    triggers = botengine.get_triggers()
    botengine.get_logger(f"{__name__}").info(">run() trigger_type=" + str(trigger_type))

    # RESET
    if trigger_type == botengine.TRIGGER_UNPAUSED:
        # This triggers on (a) the first execution of a bot, ever.
        # Or (b) when a bot was cryogenically frozen and is now thawed out and running again.
        # What happens on (b) is the bot used to be in the middle of doing something, and now as it
        # wakes up, it still thinks it is in the middle of that last situation it was tracking.
        # Even though it may be hours or days later. The bot has no idea where it is or what it should be doing now.
        # Since this affects potentially hundreds of microservices, the best bet right now is to blow the
        # bot's brains out and make it restart from scratch. Best practice is to store persistent memories
        # inside separate non-volatile variables or state variables that exist outside of this bot's 'controller' memory.
        # If you'd like to do something more elegant, please be my guest...
        botengine.get_logger(f"{__name__}").info("|run() Unpaused. Deleting all internal memory.")
        botengine.destroy_core_memory()

    # Start up tool to cache the triggers when controller is not ready
    startup = load_startup_tool(botengine)

    if trigger_type & botengine.TRIGGER_DATA_REQUEST == 0:
        startup.queue_triggers((trigger_type, triggers))

    if startup.is_bot_preparing():
        # We are not allowed to save core state when DATA REQUEST get triggered, so lets ignore it.
        if trigger_type & botengine.TRIGGER_DATA_REQUEST == 0:
            if startup.is_something_wrong(botengine):
                startup.reset()

            botengine.save_variable("startup_tool", startup, required_for_each_execution=True)
            # We need to flush immediately cause we may have multiple trigger inputs.
            botengine.flush_binary_variables()

        # Provide a little bit of time for the controller to get ready during playback.
        if botengine.playback:
            botengine.get_logger(f"{__name__}").warning("<run() Controller is not ready...")
            return

    # Grab our non-volatile memory
    botengine.get_logger(f"{__name__}").debug("|run() Loading Controller")
    controller = load_controller(botengine)
    botengine.get_logger(f"{__name__}").debug("|run() Controller Loaded")

    # The controller stores the bot's last version number.
    # If this is a new bot version, this evaluation will automatically trigger the new_version() event in all microservices.
    # Note that the new_version() event is also a bot trigger.
    if controller.is_version_updated(botengine):

        # We are not allowed to save core state when DATA REQUEST get triggered, so lets ignore it.
        if trigger_type & botengine.TRIGGER_DATA_REQUEST != 0:
            return

        startup.start(botengine.get_timestamp())
        botengine.save_variable("startup_tool", startup, required_for_each_execution=True)
        botengine.flush_binary_variables()

        controller.update_version(botengine)

    # INITIALIZE
    controller.initialize(botengine)

    botengine.get_logger(f"{__name__}").info("|bot() Controller is ready now...")
    if trigger_type & botengine.TRIGGER_DATA_REQUEST == 0:
        while len(startup.event_queue) > 0:
            (queue_trigger_type, queue_triggers) = startup.event_queue.pop(0)
            trigger_event(botengine, controller, queue_trigger_type, queue_triggers)

        # Always save your variables!
        botengine.save_variable("controller", controller, required_for_each_execution=True)
        startup.reset()
        botengine.save_variable("startup_tool", startup, required_for_each_execution=True)

    else:
        # DATA REQUEST
        trigger_event(botengine, controller, trigger_type, triggers)
    botengine.get_logger(f"{__name__}").info("<bot()")

def load_controller(botengine):
    """
    Load the Controller object
    :param botengine: Execution environment
    """
    botengine.get_logger(f"{__name__}").debug(">load_controller()")
    try:
        controller = botengine.load_variable("controller")
    except Exception as e:
        controller = None
        botengine.get_logger(f"{__name__}").warning("|load_controller() Unable to load the controller: {}".format(str(e)))

    if controller is None:
        botengine.get_logger(f"{__name__}").info("|load_controller() Creating a new Controller object. Hello.")
        controller = Controller()
        botengine.save_variable("controller", controller, required_for_each_execution=True)

    botengine.get_logger(f"{__name__}").debug("|load_controller() track devices")
    controller.track_new_and_deleted_devices(botengine)
    botengine.get_logger(f"{__name__}").debug("<load_controller()")
    return controller


def load_startup_tool(botengine):
    """
    Load the Controller object
    :param botengine: Execution environment
    """
    botengine.get_logger(f"{__name__}").info(">load_startup_tool()")
    try:
        startup = botengine.load_variable("startup_tool")

    except:
        startup = None
        botengine.get_logger(f"{__name__}").info("|load_startup_tool() Unable to load the startup tool")

    if startup is None:
        botengine.get_logger(f"{__name__}").info("|load_startup_tool() Creating a new startup tool object.")
        startup = StartUpUtil()
    botengine.get_logger(f"{__name__}").info("<load_startup_tool()")
    return startup

def get_intelligence_statistics(botengine):
    """
    Get the microservice statistics
    :param botengine: BotEngine environment
    :return: Microservice statistics
    """
    controller = load_controller(botengine)
    return controller.get_intelligence_statistics(botengine)


def trigger_event(botengine, controller, trigger_type, triggers):
    botengine.get_logger(f"{__name__}").info(">trigger_event() trigger_event={}".format(trigger_event))
    # SCHEDULE TRIGGER
    if trigger_type & botengine.TRIGGER_SCHEDULE != 0:
        schedule_ids = ["DEFAULT"]
        if 'scheduleIds' in botengine.get_inputs():
            schedule_ids = botengine.get_inputs()['scheduleIds']
            botengine.get_logger(f"{__name__}").info(">trigger_event() schedule_ids={}".format(schedule_ids))

        for schedule_id in schedule_ids:
            controller.run_intelligence_schedules(botengine, schedule_id)

    # MODE TRIGGERS
    if trigger_type & botengine.TRIGGER_MODE != 0:
        # Triggered off a change of location
        botengine.get_logger(f"{__name__}").info(">trigger_event() Synchronize Modes")
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
                        all_measurements = measures_static + measures_dict[timestamp_ms]

                        # Filter data
                        controller.filter_measurements(botengine, device_location, device_object, all_measurements)

                        # Update the device directly
                        updated_devices, updated_metadata = device_object.update(botengine, all_measurements)

                        # Update the proxies
                        for updated_device in updated_devices:
                            try:
                                updated_device.device_measurements_updated(botengine)

                                # Ping any proxy devices to let any sub-microservices know that the proxy is still connected and delivering measurements
                                if updated_device.proxy_id is not None:
                                    proxy_object = controller.get_device(updated_device.proxy_id)
                                    if proxy_object is not None:
                                        if proxy_object not in updated_devices:
                                            proxy_object.device_measurements_updated(botengine)

                            except Exception as e:
                                import traceback
                                botengine.get_logger(f"{__name__}").error("|trigger_event() Continuing execution. {}; {}".format(str(e), traceback.format_exc()))

                            # Update the location
                            controller.device_measurements_updated(botengine, device_location, updated_device)

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
                            botengine.get_logger(f"{__name__}").info("|trigger_event() alert=" + json.dumps(alert, sort_keys=True))

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
        botengine.get_logger(f"{__name__}").info("|trigger_event() file=" + json.dumps(file, sort_keys=True))
        if file is not None:
            device_object = controller.get_device(file['deviceId'])

            if device_object is not None:
                controller.file_uploaded(botengine, device_object, file)

    # QUESTIONS ANSWERED
    if trigger_type & botengine.TRIGGER_QUESTION_ANSWER != 0:
        question = botengine.get_answered_question()
        if question is None:
            botengine.get_logger(f"{__name__}").error("|trigger_event() Triggered off a question answer, but no question was answered. triggers={}".format(json.dumps(triggers)))
            return
        botengine.get_logger(f"{__name__}").info("|trigger_event() question.key_identifier=" + str(question.key_identifier))
        botengine.get_logger(f"{__name__}").info("|trigger_event() question.answer={}".format(question.answer))
        controller.sync_question(botengine, question)

    # DATA STREAM TRIGGERS
    if trigger_type & botengine.TRIGGER_DATA_STREAM != 0:
        # Triggered off a data stream message
        data_stream = botengine.get_datastream_block()
        botengine.get_logger(f"{__name__}").info("|trigger_event() data_stream=" + json.dumps(data_stream, sort_keys=True))
        if 'address' not in data_stream:
            botengine.get_logger(f"{__name__}").warn("|trigger_event() Data stream message does not contain an 'address' field. Ignoring the message.")

        else:
            address = data_stream['address']

            if 'feed' in data_stream:
                content = data_stream['feed']
            else:
                content = {}

            if 'fromAppInstanceId' in data_stream:
                if type(content) == type({}):
                    content['sender_bot_id'] = data_stream['fromAppInstanceId']

            # Add the key to the content (if it exists) so we can pass it along to the microservice
            if botengine.get_input_key():
                content['key'] = botengine.get_input_key()

            if address != "schedule":
                controller.sync_datastreams(botengine, address, content)
            else:
                controller.run_intelligence_schedules(botengine)

    # COMMAND RESPONSES
    if trigger_type & botengine.TRIGGER_COMMAND_RESPONSE != 0:
        botengine.get_logger(f"{__name__}").info("|trigger_event() command_responses={}".format(json.dumps(botengine.get_inputs()['commandResponses'])))
        # TODO responses to commands delivered by the bot are available to build out reliable command delivery infrastructure
        pass

    # GOAL / SCENARIO CHANGES
    if trigger_type & botengine.TRIGGER_METADATA != 0:
        # The user changed the goal / scenario for a single sensor
        for trigger in triggers:
            botengine.get_logger(f"{__name__}").info("|trigger_event() Changed device configuration")
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
            botengine.get_logger(f"{__name__}").info("|trigger_event() User changed roles")
            for user in users:
                botengine.get_logger(f"{__name__}").info("|trigger_event() > user={}".format(user))
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

                role = None
                if 'role' in user:
                    role = user['role']

                controller.user_role_updated(botengine, location_id, user_id, role, category, location_access, previous_category, previous_location_access)

        if call_center is not None:
            # Location call center changed status
            botengine.get_logger(f"{__name__}").info("|trigger_event() Emergency Call Center Updated")
            if 'status' in call_center:
                status = call_center['status']

            if 'userId' in call_center:
                user_id = call_center['userId']

            controller.call_center_updated(botengine, location_id, user_id, status)

    # DATA REQUEST
    if trigger_type & botengine.TRIGGER_DATA_REQUEST != 0:
        botengine.get_logger(f"{__name__}").info("|trigger_event() Data request received")
        events = {}
        data = botengine.get_data_block()

        if botengine.playback:
            events['all'] = {}

            for device_id, csv_data in data.items():
                device = controller.get_device(device_id)
                if device is not None:
                    events['all'][device] = csv_data

            for reference in events:
                controller.data_request_ready(botengine, reference, events[reference])

        else:
            imported = False

            import time
            try:
                import lz4.block
                imported = True
            except ImportError:
                botengine.get_logger(f"{__name__}").error("|trigger_event() Attempted to import 'lz4' to uncompress the data request response, but lz4 is not available. Please add 'lz4' to 'pip_install_remotely' in your structure.json.")
                pass

            if imported:
                for d in data:
                    reference = None
                    if 'key' in d:
                        reference = d['key']

                    if reference not in events:
                        events[reference] = {}

                    botengine.get_logger(f"{__name__}").info("|trigger_event() Downloading {} ({} bytes)...".format(d['deviceId'], d['dataLength']))
                    r = botengine.send_data_request(d['url'], timeout=60, stream=True)
                    events[reference][d['deviceId']] = lz4.block.decompress(r.content, uncompressed_size=d['dataLength'])

                data_events = {}

                for reference, value in events.items():
                    if reference not in data_events:
                        data_events[reference] = {}

                    for device_id, decompressed_content in value.items():
                        data_events[reference][controller.get_device(device_id)] = decompressed_content

                for reference in data_events:
                    controller.data_request_ready(botengine, reference, data_events[reference])
    botengine.get_logger(f"{__name__}").info("<trigger_event()")

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
    botengine.get_logger(f"{__name__}").info(">_location_intelligence_fired() argument_tuple={}".format(argument_tuple))
    controller = load_controller(botengine)

    try:
        controller.run_location_intelligence(botengine, argument_tuple[0], argument_tuple[1])
    except Exception as e:
        import traceback
        botengine.get_logger(f"{__name__}").error("|_location_intelligence_fired() {}; {}".format(str(e), traceback.format_exc()))

    botengine.save_variable("controller", controller, required_for_each_execution=True)
    botengine.get_logger(f"{__name__}").info("<_location_intelligence_fired()")

def start_location_intelligence_timer(botengine, seconds, intelligence_id, argument, reference):
    """
    Start a relative location intelligence timer
    :param botengine: BotEngine environment
    :param seconds: Seconds from the start of the current execution to make this timer fire
    :param intelligence_id: ID of the intelligence module to trigger when this timer fires
    :param argument: Arbitrary argument to pass into the intelligence module's timer_fired() method when this timer fires
    :param reference: Unique reference name that lets us later cancel this timer if needed
    """
    botengine.get_logger(f"{__name__}").info(">start_location_intelligence_timer() seconds={} reference={}".format(seconds, reference))
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
    botengine.get_logger(f"{__name__}").info(">start_location_intelligence_timer_ms() milliseconds={} reference={}".format(milliseconds, reference))
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
    botengine.get_logger(f"{__name__}").info(">set_location_intelligence_alarm() timestamp_ms={} intelligence_id={} argument={} reference={}".format(timestamp_ms, intelligence_id, argument, reference))
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
    botengine.get_logger(f"{__name__}").info(">_device_intelligence_fired() argument_tuple={}".format(argument_tuple))
    controller = load_controller(botengine)

    try:
        controller.run_device_intelligence(botengine, argument_tuple[0], argument_tuple[1])
    except Exception as e:
        import traceback
        botengine.get_logger(f"{__name__}").error("|_device_intelligence_fired() {}; {}".format(str(e), traceback.format_exc()))
        if botengine.playback:
            import time
            time.sleep(2)

    botengine.save_variable("controller", controller, required_for_each_execution=True)
    botengine.get_logger(f"{__name__}").info("<_device_intelligence_fired()")
    

def start_device_intelligence_timer(botengine, seconds, intelligence_id, argument, reference):
    """
    Start a relative device intelligence timer
    :param botengine: BotEngine environment
    :param seconds: Seconds from the start of the current execution to make this timer fire
    :param intelligence_id: ID of the intelligence module to trigger when this timer fires
    :param argument: Arbitrary argument to pass into the intelligence module's timer_fired() method when this timer fires
    :param reference: Unique reference name that lets us later cancel this timer if needed
    """
    botengine.get_logger(f"{__name__}").info(">start_device_intelligence_timer() seconds={} reference={}".format(seconds, reference))
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
    botengine.get_logger(f"{__name__}").info(">start_device_intelligence_timer_ms() milliseconds={} reference={}".format(milliseconds, reference))
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
    botengine.get_logger(f"{__name__}").info(">set_device_intelligence_alarm() timestamp_ms={}".format(timestamp_ms))
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