'''
Created on July 31, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

DEPRECATED SEPTEMBER 23, 2020

@author: David Moss
'''

from devices.gateway.gateway import GatewayDevice
import json

class PeoplePowerXSeriesDevice(GatewayDevice):
    """
    X-Series Gateway
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [] # [] < Deprecated, see gateway_peoplepower_xseries.py >

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
