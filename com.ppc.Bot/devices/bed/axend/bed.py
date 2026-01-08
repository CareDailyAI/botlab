'''
Created on November 26, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
'''
from devices.bed.bed import BedDevice

class BedWavveDevice(BedDevice):
    """
    AeroSense Wavve Device
    """
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2021, 2022]

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        BedDevice.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

    def new_version(self, botengine):
        """
        New version
        :param botengine: BotEngine environment
        """
        BedDevice.new_version(self, botengine)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Sleep Signal")

    def get_icon_font(self):
        """
        Get the icon font package from which to render an icon
        As most of the device icons come from the "People Power Regular" icon font, this is currently the default.
        You can override this method in a specific device class.
        :return: The name of the icon font package
        """
        import utilities.utilities as utilities
        return utilities.ICON_FONT_FONTAWESOME_REGULAR

    def is_in_bed(self, botengine=None):
        """
        :return: True if the bed is occupied
        """
        return self.is_detecting_occupancy(botengine)

    def did_update_bed_status(self, botengine):
        """
        Wavve uses 'occupancy' instead of 'bedStatus'... Normalize the language

        Determine if we updated the bed status in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the bed status in this execution
        """
        return BedDevice.MEASUREMENT_NAME_OCCUPANCY in self.last_updated_params
    
    def did_change_room_type(self, botengine=None):
        """
        :param botengine:
        :return: True if the room type changed
        """
        return BedDevice.MEASUREMENT_NAME_ROOM_TYPE in self.last_updated_params
    
    
    def update(self, botengine, measures):
        """
        Intercept the parent Device.update() method to add occupancy correction logic.
        If heartrate or breathing is detected but occupancy is 0, force occupancy to 1.
        :param botengine: BotEngine environment
        :param measures: Full or partial measurement block from bot inputs
        :return: Tuple of (updated_devices, updated_metadata) from parent update
        """
        # Call parent BedDevice.update() and capture the return value
        result = BedDevice.update(self, botengine, measures)
        
        # Check if we need to correct occupancy
        # Only proceed if we have heartrate or breathing measurements in this execution
        heartrate_updated = self.did_update_heart_rate(botengine)
        breathing_updated = self.did_update_breathing_rate(botengine)
        
        if heartrate_updated or breathing_updated:
            # Check current occupancy status
            current_occupancy = 0
            
            # Check both occupancy measurements
            if BedDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
                if len(self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                    current_occupancy = self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY][0][0]
            
            # If occupancy is 0 (unoccupied) but we have heartrate or breathing, force occupancy to 1
            if current_occupancy == 0:
                # Add occupancy measurement with value 1
                self.add_measurement(botengine, BedDevice.MEASUREMENT_NAME_OCCUPANCY, 1, botengine.get_timestamp())
                
                # Add to last_updated_params so did_update_bed_status() will return True
                if BedDevice.MEASUREMENT_NAME_OCCUPANCY not in self.last_updated_params:
                    self.last_updated_params.append(BedDevice.MEASUREMENT_NAME_OCCUPANCY)
        
        return result

    def last_out_of_bed_timestamp_ms(self, botengine):
        """
        Get the last timestamp when this BedDevice reported being out of bed (occupancy = 0).
        :param botengine: BotEngine environment
        :return: Timestamp in milliseconds when someone last got out of bed, or None if no bed exit found
        """
        if BedDevice.MEASUREMENT_NAME_OCCUPANCY not in self.measurements:
            return None
        
        if len(self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY]) == 0:
            return None
        
        last_out_of_bed_timestamp = None
        
        for measurement in self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY]:
            value, timestamp = measurement[0], measurement[1]
            # Check if this measurement shows no occupancy (value = 0)
            if value == 0:
                if last_out_of_bed_timestamp is None or timestamp > last_out_of_bed_timestamp:
                    last_out_of_bed_timestamp = timestamp
        
        return last_out_of_bed_timestamp
        
    def get_room_type(self, botengine=None):
        """
        :param botengine:
        :return: room type. None if it's not available.
        """
        if BedDevice.MEASUREMENT_NAME_ROOM_TYPE in self.measurements:
            return self.measurements[BedDevice.MEASUREMENT_NAME_ROOM_TYPE][0][0]

        return None


    def is_detecting_occupancy(self, botengine):
        """
        True if this device is detecting an occupant, as indicated by the 'occupancy' parameter and not our targets
        :param botengine:
        :return:
        """
        if BedDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if len(self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                return self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY][0][0] == 1
        return False

    def did_start_detecting_occupancy(self, botengine):
        """
        Did the Radar device start detecting occupancy in this room
        :param botengine:
        :return: True if occupants have entered the room
        """
        if BedDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if BedDevice.MEASUREMENT_NAME_OCCUPANCY in self.last_updated_params:
                if len(self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                    return (self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY][0][0] == 1)

        return False

    def did_stop_detecting_occupancy(self, botengine):
        """
        Did the Radar device stop detecting occupancy in this room
        :param botengine:
        :return: True if occupants have left the room
        """
        if BedDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if BedDevice.MEASUREMENT_NAME_OCCUPANCY in self.last_updated_params:
                if len(self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                    return (self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY][0][0] == 0)

        return False 