'''
Created on June 28, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import pytz
import datetime
import utilities
import intelligence.index
import importlib
import domain


class Location:
    """This class simply keeps track of our location and figures out the state of the location's security system"""
    def __init__(self, botengine, location_id):
        """Constructor"""
        self.location_id = int(location_id)
        
        # Dictionary of all device objects. { 'device_id': <device_object> }
        self.devices = {}
        
        # Born on date
        self.born_on = botengine.get_timestamp()
        
        # Mode of this location (i.e. "HOME", "AWAY", etc.)
        self.mode = botengine.get_mode(self.location_id)

        # Timestamp of the last time we did a garbage collection
        self.garbage_timetamp_ms = 0
        
        # All Location Intelligence modules
        self.intelligence_modules = {}

        # Try to update our current mode
        self.update_mode(botengine)


        
    def initialize(self, botengine):
        """Mandatory to run with every execution"""
        # Refresh this with every execution

        # Removed May 5, 2018
        if hasattr(self, 'latitude'):
            del(self.latitude)

        # Removed May 5, 2018
        if hasattr(self, 'longitude'):
            del(self.longitude)

        # Removed May 5, 2018
        if hasattr(self, 'sunrise_sunset_enabled'):
            del(self.sunrise_sunset_enabled)

        for d in self.devices:
            self.devices[d].initialize(botengine)
            
        # Synchronize intelligence capabilities
        if len(self.intelligence_modules) != len(intelligence.index.MICROSERVICES['LOCATION_MICROSERVICES']):
            
            # Add more microservices
            # 10014: [{"module": "intelligence.rules.device_entry_intelligence", "class": "EntryRulesIntelligence"}],
            for intelligence_info in intelligence.index.MICROSERVICES['LOCATION_MICROSERVICES']:
                if intelligence_info['module'] not in self.intelligence_modules:
                    try:
                        intelligence_module = importlib.import_module(intelligence_info['module'])
                        class_ = getattr(intelligence_module, intelligence_info['class'])
                        botengine.get_logger().info("Adding location microservice: " + str(intelligence_info['module']))
                        intelligence_object = class_(botengine, self)
                        self.intelligence_modules[intelligence_info['module']] = intelligence_object
                    except Exception as e:
                        botengine.get_logger().error("Could not add location microservice: " + str(intelligence_info))
                        import traceback
                        traceback.print_exc()
                        
                    
            # Remove microservices that no longer exist
            for module_name in self.intelligence_modules.keys():
                found = False
                for intelligence_info in intelligence.index.MICROSERVICES['LOCATION_MICROSERVICES']:
                    if intelligence_info['module'] == module_name:
                        found = True
                        break
                    
                if not found:
                    botengine.get_logger().info("Deleting location microservice: " + str(module_name))
                    del self.intelligence_modules[module_name]
                    
        # Location intelligence execution
        for i in self.intelligence_modules:
            self.intelligence_modules[i].parent = self
            self.intelligence_modules[i].initialize(botengine)
        
        
    
    def garbage_collect(self, botengine):
        """
        Clean up the garbage
        :param botengine: BotEngine environment
        """
        for device_id in self.devices:
            self.devices[device_id].garbage_collect(botengine)
            
    def add_device(self, botengine, device_object):
        """
        Start tracking a new device here.
        Perform any bounds checking, for example with multiple gateways at one location.
        :param device_object: Device object to track
        """
        self.devices[device_object.device_id] = device_object
    
    def delete_device(self, botengine, device_id):
        """
        Delete the given device ID
        :param device_id: Device ID to delete
        """
        device_object = None
        if device_id in self.devices:
            device_object = self.devices[device_id]
            
            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    device_object.intelligence_modules[intelligence_id].destroy(botengine)
            
            del self.devices[device_id]
            
            for intelligence_id in self.intelligence_modules:
                self.intelligence_modules[intelligence_id].device_deleted(botengine, device_object)
    
    def mode_updated(self, botengine, mode):
        """
        Update this location's mode
        """
        self.mode = mode
        botengine.get_logger().info(self.mode + " mode.")
        
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].mode_updated(botengine, mode)

        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    self.devices[device_id].intelligence_modules[intelligence_id].mode_updated(botengine, mode)
    
    def device_measurements_updated(self, botengine, device_object):
        """
        Evaluate a device that was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].device_measurements_updated(botengine, device_object)
    
    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].device_metadata_updated(botengine, device_object)

    def device_alert(self, botengine, device_object, alert_type, alert_params):
        """
        Device sent an alert
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alerts_list: List of alerts
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].device_alert(botengine, device_object, alert_type, alert_params)

    def question_answered(self, botengine, question):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question: Question object
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].question_answered(botengine, question)
        
        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    self.devices[device_id].intelligence_modules[intelligence_id].question_answered(botengine, question)
    
    
    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Updated
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Data Stream content
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].datastream_updated(botengine, address, content)
        
        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    self.devices[device_id].intelligence_modules[intelligence_id].datastream_updated(botengine, address, content)
                    
            
    def schedule_fired(self, botengine, schedule_id):
        """
        Schedule Fired.
        It is this location's responsibility to notify all sub-intelligence modules, including both device and location intelligence modules
        :param botengine: BotEngine environment
        """
        # Location intelligence modules
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].schedule_fired(botengine, schedule_id)
        
        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    self.devices[device_id].intelligence_modules[intelligence_id].schedule_fired(botengine, schedule_id)
                    
        # Garbage collect
        if botengine.get_timestamp() - self.garbage_timetamp_ms > utilities.ONE_WEEK_MS:
            self.garbage_collect(botengine)
        
    def timer_fired(self, botengine, argument):
        """
        Timer fired
        :param botengine: BotEngine environment
        :param argument: Optional argument
        """
        return


    def file_uploaded(self, botengine, device_object, file_id, filesize_bytes, content_type, file_extension):
        """
        A device file has been uploaded
        :param botengine: BotEngine environment
        :param device_object: Device object that uploaded the file
        :param file_id: File ID to reference this file at the server
        :param filesize_bytes: The file size in bytes
        :param content_type: The content type, for example 'video/mp4'
        :param file_extension: The file extension, for example 'mp4'
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].file_uploaded(botengine, device_object, file_id, filesize_bytes, content_type, file_extension)

    #===========================================================================
    # Data Stream Message delivery
    #===========================================================================
    def distribute_datastream_message(self, botengine, address, content, internal=True, external=True):
        """
        Distribute a data stream message both internally to any intelligence module within this bot,
        and externally to any other bots that might be listening.
        :param botengine: BotEngine environment
        :param address: Data stream address
        :param content: Message content
        :param internal: True to deliver this message internally to any intelligence module that's listening (default)
        :param external: True to deliver this message externally to any other bot that's listening (default)
        """
        if internal:
            self.datastream_updated(botengine, address, content)

        if external:
            botengine.send_datastream_message(address, content)

    #===========================================================================
    # Mode helper methods
    #===========================================================================
    def is_present(self, botengine=None):
        """
        Is the person likely physically present in the home?
        :return: True if the person is in HOME, STAY, SLEEP, or TEST mode. False for all others.
        """
        return utilities.MODE_HOME in self.mode or utilities.MODE_TEST in self.mode or utilities.MODE_STAY in self.mode or utilities.MODE_SLEEP in self.mode
    
    def is_present_and_protected(self, botengine=None):
        """
        Is the person at home and wants to be alerted if the perimeter is breached?
        :return: True if the person is in STAY or SLEEP mode
        """
        return utilities.MODE_STAY in self.mode or utilities.MODE_SLEEP in self.mode
    
    def update_mode(self, botengine):
        """
        Extract this location's current mode from our botengine environment
        :param botengine: BotEngine environment
        """
        location_block = botengine.get_location_info(self.location_id)
        if location_block is not None:
            if 'event' in location_block['location']:
                self.mode = str(location_block['location']['event'])

    #===========================================================================
    # Time
    #===========================================================================
    def get_local_datetime(self, botengine):
        """
        Get the datetime in the user's local timezone.
        :param botengine: BotEngine environment
        :param timestamp: Unix timestamp in milliseconds
        :returns: datetime
        """
        return self.get_local_datetime_from_timestamp(botengine, botengine.get_timestamp())
    
    def get_local_datetime_from_timestamp(self, botengine, timestamp_ms):
        """
        Get a datetime in the user's local timezone, based on an input timestamp_ms
        :param botengine: BotEngine environment
        :param timestamp_ms: Timestamp in milliseconds to transform into a timezone-aware datetime object
        """
        return datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, pytz.timezone(self.get_local_timezone_string(botengine)))
        
    def get_local_timezone_string(self, botengine):
        """
        Get the local timezone string
        :param botengine: BotEngine environment
        :return: timezone string
        """
        location_block = botengine.get_location_info(self.location_id)

        # Try to get the user's location's timezone string
        if 'timezone' in location_block['location']:
            return location_block['location']['timezone']['id']

        return domain.DEFAULT_TIMEZONE

    def get_relative_time_of_day(self, botengine, timestamp_ms=None):
        """
        Transform our local datetime into a float hour and minutes
        :param botengine: BotEngine environment
        :param timestamp_ms: Transform this timestamp if given, otherwise transform the current time from botengine.
        :return: Relative time of day - hours.minutes where minutes is divided by 60. 10:15 AM = 10.25
        """
        if timestamp_ms is not None:
            # Use the given timestamp
            dt = self.get_local_datetime_from_timestamp(botengine, timestamp_ms)
        else:
            # Use the current time
            dt = self.get_local_datetime(botengine)

        return dt.hour + (dt.minute / 60.0)

    def get_midnight_last_night(self, botengine):
        """
        Get a datetime of midnight last night in local time
        :param botengine: BotEngine environment
        :return: Datetime object of midnight last night in the local timezone
        """
        return self.get_local_datetime(botengine).replace(hour=0, minute=0, second=0, microsecond=0)

    def get_midnight_tonight(self, botengine):
        """
        Get a datetime of midnight tonight in local time
        :param botengine: BotEngine environment
        :return: Datetime object of midnight tonight in the local timezone
        """
        return self.get_local_datetime(botengine).replace(hour=23, minute=59, second=59, microsecond=999999)


    def local_timestamp_ms_from_relative_hours(self, botengine, weekday, hours):
        """
        Calculate an absolute timestamp from relative day-of-week and hour
        :param botengine: BotEngine environment
        :param dow: day-of-week (Monday is 0)
        :param hours: Relative hours into the day (i.e. 23.5 = 11:30 PM local time)
        :return: Unix epoch timestamp in milliseconds
        """
        from datetime import timedelta

        reference = self.get_local_datetime(botengine)
        hour, minute = divmod(hours, 1)
        minute *= 60
        days = reference.weekday() - weekday
        target_dt = (reference - timedelta(days=days)).replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
        timestamp_ms = self.timezone_aware_datetime_to_unix_timestamp(botengine, target_dt)
        if timestamp_ms < botengine.get_timestamp():
            timestamp_ms += utilities.ONE_WEEK_MS

        return timestamp_ms

    def timezone_aware_datetime_to_unix_timestamp(self, botengine, dt):
        """
        Convert a local datetime / timezone-aware datetime to a unix timestamp
        :param botengine: BotEngine environment
        :param dt: Datetime to convert to unix timestamp
        :return: timestamp in milliseconds
        """
        from tzlocal import get_localzone
        return int((dt.astimezone(get_localzone())).strftime("%s")) * 1000

    def get_local_hour_of_day(self, botengine):
        """
        Get the local hour of the day (float), used in machine learning algorithms.

        Examples:
        * Midnight last night = 0.0
        * Noon = 12.0
        * 9:15 PM = 21.25

        :param botengine: BotEngine environment
        :return: hour of the day (float)
        """
        return (botengine.get_timestamp() - self.timezone_aware_datetime_to_unix_timestamp(botengine, self.get_midnight_last_night(botengine))) / 1000 / 60.0 / 60.0

    def get_local_day_of_week(self, botengine):
        """
        Get the local day of the week (0-6)

        :param botengine: BotEngine environment
        :return: local day of the week (0 - 6)
        """
        return self.get_local_datetime(botengine).weekday()


    #===========================================================================
    # Weather
    #===========================================================================
    def get_weather_forecast(self, botengine, units=None, hours=12):
        """
        Get the weather forecast for this location
        :param units: Default is Metric. 'e'=English; 'm'=Metric; 'h'=Hybrid (UK); 's'=Metric SI units (not available for all APIs)
        :param hours: Forecast depth in hours, default is 12. Available hours are 6, 12.
        :return: Weather JSON data
        """
        return botengine.get_weather_forecast_by_location(self.location_id, units, hours)

    def get_current_weather(self, botengine, units=None):
        """
        Get the current weather by Location ID
        :param units: Default is Metric. 'e'=English; 'm'=Metric; 'h'=Hybrid (UK); 's'=Metric SI units (not available for all APIs)
        :return: Weather JSON data
        """
        return botengine.get_current_weather_by_location(self.location_id, units)


    #===========================================================================
    # CSV methods for machine learning algorithm integrations
    #===========================================================================
    def get_csv(self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None):
        """
        Get a .csv string of all the data
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: oldest timestamp in milliseconds
        :param newest_timestamp_ms: newest timestamp in milliseconds
        :return: .csv string, largely matching the .csv data you would receive from the "botengine --download_device [device_id]" command line interface. Or None if this device doesn't have data.
        """
        output = "location_id,timestamp_ms,timestamp_iso,event,source_type,source_agent\n"

        try:
            modes = botengine.get_mode_history(self.location_id, oldest_timestamp_ms=oldest_timestamp_ms, newest_timestamp_ms=newest_timestamp_ms)
        except:
            # This can happen because this bot may not have read permissions for this device.
            botengine.get_logger().warning("Cannot synchronize modes history for location {}".format(self.location_id))
            return None

        if 'events' not in modes:
            botengine.get_logger().warning("No history of changing modes in location {}".format(self.location_id))
            return None

        for event in modes['events']:
            timestamp_ms = event['eventDateMs']
            dt = self.get_local_datetime_from_timestamp(botengine, timestamp_ms)
            source_agent = ""
            if 'sourceAgent' in event:
                source_agent = event['sourceAgent'].replace(",","_")

            output += "{},{},{},{},{},{}".format(self.location_id, timestamp_ms, dt.isoformat(), event['event'], event['sourceType'], source_agent)
            output += "\n"

        return output
