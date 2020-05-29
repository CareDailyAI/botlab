'''
Created on October 1, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.gateway.gateway import GatewayDevice

# Power status enum
POWER_STATUS_EXTERNAL = 1
POWER_STATUS_BATTERY = 2

# Power status measurement
MEASUREMENT_POWER_STATUS = "powerStatus"

# Cell status enum
CELL_STATUS_DISCONNECTED = 0
CELL_STATUS_CONNECTED = 1

# Cell status measurement
MEASUREMENT_CELL_STATUS = "cellStatus"

class DevelcoSquidlinkDevice(GatewayDevice):
    """
    Develco Squid.link Gateway
    """
        
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [36]
        
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Smart Home Center")

    def stream(self, botengine, address, content, request_id=None):
        """
        Deliver a data stream message to this gateway device
        :param botengine: BotEngine environment
        :param address: Data stream address / event name
        :param content: Content to deliver in JSON format
        :param request_id: Optional request ID for split-phase API calls
        """
        content = {
            "address": address,
            "content": content
        }

        if request_id is not None:
            content['request_id'] = int(request_id)

        import importlib
        try:
            bundle = importlib.import_module("info").BUNDLE
        except:
            bundle = None

        botengine.send_command(self.device_id, "stream", json.dumps(content), index=bundle)

    def did_switch_to_battery_power(self, botengine):
        """
        Did the gateway get unplugged from power and we're now running on battery
        :param botengine:
        :return:
        """
        if MEASUREMENT_POWER_STATUS in self.last_updated_params:
            return self.measurements[MEASUREMENT_POWER_STATUS][0][0] == POWER_STATUS_BATTERY

        return False

    def did_switch_to_external_power(self, botengine):
        """
        Did the gateway get plugged back into power
        :param botengine:
        :return:
        """
        if MEASUREMENT_POWER_STATUS in self.last_updated_params:
            return self.measurements[MEASUREMENT_POWER_STATUS][0][0] == POWER_STATUS_EXTERNAL

        return False

    def is_on_battery(self, botengine):
        """
        Is the gateway plugged into power
        :param botengine:
        :return:
        """
        if MEASUREMENT_POWER_STATUS in self.measurements:
            return self.measurements[MEASUREMENT_POWER_STATUS][0][0] == POWER_STATUS_BATTERY

        return False

    def did_connect_cellular(self, botengine):
        """
        Did the gateway's primary network interface switch to a cellular connection
        :param botengine:
        :return:
        """
        if MEASUREMENT_CELL_STATUS in self.last_updated_params:
            return self.measurements[MEASUREMENT_CELL_STATUS][0][0] == CELL_STATUS_CONNECTED

        return False

    def did_connect_broadband(self, botengine):
        """
        Did the gateway's primary network interface switch to a broadband connection
        :param botengine:
        :return:
        """
        if MEASUREMENT_CELL_STATUS in self.last_updated_params:
            return self.measurements[MEASUREMENT_CELL_STATUS][0][0] == CELL_STATUS_CONNECTED

        return False

    def is_broadband_connected(self, botengine):
        """
        Is the gateway's primary network interface a broadband connection
        :param botengine:
        :return:
        """
        if MEASUREMENT_CELL_STATUS in self.measurements:
            return self.measurements[MEASUREMENT_CELL_STATUS][0][0] == CELL_STATUS_DISCONNECTED

        return self.is_connected

    def is_cellular_connected(self, botengine):
        """
        Is the gateway's primary network interface a cellular connection
        :param botengine:
        :return:
        """
        if MEASUREMENT_CELL_STATUS in self.measurements:
            return self.measurements[MEASUREMENT_CELL_STATUS][0][0] == CELL_STATUS_CONNECTED

        return False

    def get_battery_level(self, botengine):
        """
        Get the current battery level in units of percentage (i.e. 0 - 100)
        :param botengine:
        :return:
        """
        if 'batteryLevel' in self.measurements:
            if len(self.measurements['batteryLevel']) > 0:
                return self.measurements['batteryLevel'][0][0]

        return 100
