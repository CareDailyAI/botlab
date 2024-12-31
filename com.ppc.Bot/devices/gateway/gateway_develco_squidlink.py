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

# Network type enum
NETWORK_TYPE_ETHERNET = 1
NETWORK_TYPE_WIFI = 2
NETWORK_TYPE_CELLULAR = 3
NETWORK_TYPE_LOOPBACK = "lo"

# Network type measurement
MEASUREMENT_NETWORK_TYPE = "netType"

class DevelcoSquidlinkDevice(GatewayDevice):
    """
    Develco Squid.link Gateway
    """
        
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [36, 37, 38]
        
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

        import json
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
            botengine.get_logger(f'{__name__}.{__class__.__name__}').info("|did_connect_cellular() cellStatus={}".format(self.measurements[MEASUREMENT_CELL_STATUS][0][0]))
            return self.measurements[MEASUREMENT_CELL_STATUS][0][0] == CELL_STATUS_CONNECTED
        elif MEASUREMENT_NETWORK_TYPE in self.last_updated_params:
            botengine.get_logger(f'{__name__}.{__class__.__name__}').info("|did_connect_cellular() netType={}".format(self.measurements[MEASUREMENT_NETWORK_TYPE][0][0]))

            # Retrieve any other measurements with the same timestamp
            current_measurements = [self.measurements[MEASUREMENT_NETWORK_TYPE][0]]
            for measurement in self.measurements[MEASUREMENT_NETWORK_TYPE][1:]:
                if measurement[1] == current_measurements[0][1]:
                    current_measurements += [measurement]
                    break
            if any([measurement[0] in [NETWORK_TYPE_CELLULAR] for measurement in current_measurements]):
                botengine.get_logger(f'{__name__}.{__class__.__name__}').info("|did_connect_cellular() netType={}".format(self.measurements[MEASUREMENT_NETWORK_TYPE]))
                # May have just connected to cellular
                if len(self.measurements[MEASUREMENT_NETWORK_TYPE]) == len(current_measurements):
                    return True
                else:
                    # Check measurements prior to the current timestamp, ignoring `lo` (loopback) measurements.  
                    for measurement in self.measurements[MEASUREMENT_NETWORK_TYPE]:
                        if measurement[1] == current_measurements[0][1] or measurement[0] == NETWORK_TYPE_LOOPBACK:
                            continue
                        # Return True if the previous measurement was not cellular
                        botengine.get_logger(f'{__name__}.{__class__.__name__}').info("|did_connect_cellular() previous_netType={}".format(measurement))
                        return measurement[0] not in [NETWORK_TYPE_CELLULAR]

        return False

    def did_connect_broadband(self, botengine):
        """
        Did the gateway's primary network interface switch to a broadband connection
        :param botengine:
        :return:
        """
        if MEASUREMENT_CELL_STATUS in self.last_updated_params:
            botengine.get_logger(f'{__name__}.{__class__.__name__}').info("|did_connect_broadband() cellStatus={}".format(self.measurements[MEASUREMENT_CELL_STATUS][0][0]))
            return self.measurements[MEASUREMENT_CELL_STATUS][0][0] == CELL_STATUS_DISCONNECTED
        elif MEASUREMENT_NETWORK_TYPE in self.last_updated_params:
            botengine.get_logger(f'{__name__}.{__class__.__name__}').info("|did_connect_broadband() netType={}".format(self.measurements[MEASUREMENT_NETWORK_TYPE][0][0]))

            # Retrieve any other measurements with the same timestamp
            current_measurements = [self.measurements[MEASUREMENT_NETWORK_TYPE][0]]
            for measurement in self.measurements[MEASUREMENT_NETWORK_TYPE][1:]:
                if measurement[1] == current_measurements[0][1]:
                    current_measurements += [measurement]
                    break

            if any([measurement[0] in [NETWORK_TYPE_ETHERNET, NETWORK_TYPE_WIFI] for measurement in current_measurements]):
                botengine.get_logger(f'{__name__}.{__class__.__name__}').info("|did_connect_broadband() netType={}".format(self.measurements[MEASUREMENT_NETWORK_TYPE]))
                # May have just connected to broadband
                if len(self.measurements[MEASUREMENT_NETWORK_TYPE]) == len(current_measurements):
                    return True
                else:
                    # Check measurements prior to the current timestamp, ignoring `lo` (loopback) measurements.  
                    for measurement in self.measurements[MEASUREMENT_NETWORK_TYPE]:
                        if measurement[1] == current_measurements[0][1] or measurement[0] == NETWORK_TYPE_LOOPBACK:
                            continue
                        # Return True if the previous measurement was not broadband
                        botengine.get_logger(f'{__name__}.{__class__.__name__}').info("|did_connect_broadband() previous_netType={}".format(measurement))
                        return measurement[0] not in [NETWORK_TYPE_ETHERNET, NETWORK_TYPE_WIFI]

        return False

    def is_broadband_connected(self, botengine):
        """
        Is the gateway's primary network interface a broadband connection
        :param botengine:
        :return:
        """
        if MEASUREMENT_CELL_STATUS in self.measurements:
            return self.measurements[MEASUREMENT_CELL_STATUS][0][0] == CELL_STATUS_DISCONNECTED
        if MEASUREMENT_NETWORK_TYPE in self.measurements:
            # Retrieve the latest measurement that is not `lo` (loopback)
            for measurement in self.measurements[MEASUREMENT_NETWORK_TYPE]:
                if measurement[0] != NETWORK_TYPE_LOOPBACK:
                    return measurement[0] in [NETWORK_TYPE_ETHERNET, NETWORK_TYPE_WIFI]

        return False

    def is_cellular_connected(self, botengine):
        """
        Is the gateway's primary network interface a cellular connection
        :param botengine:
        :return:
        """
        if MEASUREMENT_CELL_STATUS in self.measurements:
            return self.measurements[MEASUREMENT_CELL_STATUS][0][0] == CELL_STATUS_CONNECTED
        if MEASUREMENT_NETWORK_TYPE in self.measurements:
            # Retrieve the latest measurement that is not `lo` (loopback)
            for measurement in self.measurements[MEASUREMENT_NETWORK_TYPE]:
                if measurement[0] != NETWORK_TYPE_LOOPBACK:
                    return measurement[0] in [NETWORK_TYPE_CELLULAR]

        return False

    def get_battery_level(self, botengine):
        """
        Get the current battery level in units of percentage (i.e. 0 - 100)
        :param botengine:
        :return:
        """
        return self.battery_level
