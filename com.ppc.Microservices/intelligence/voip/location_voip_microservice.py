"""
Created on July 16, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

import properties  # type: ignore
from devices.audio.develco.audio import (  # type: ignore
    BUTTON_INDEXES,
    DevelcoAudioAssistantDevice,
)
from devices.gateway.gateway_develco_squidlink import (  # type: ignore
    DevelcoSquidlinkDevice,
    VOIP_CALL_STATE_ACTIVE,
    VOIP_CALL_STATE_ALL_LINES_BUSY,
    VOIP_CALL_STATE_BUSY_HERE,
    VOIP_CALL_STATE_DISCONNECTED,
    VOIP_CALL_STATE_HANGUP_LOCAL,
    VOIP_CALL_STATE_HANGUP_REMOTE,
    VOIP_CALL_STATE_NOT_FOUND,
    VOIP_CALL_STATE_SERVICE_UNAVAILABLE,
    VOIP_CALL_STATE_TERMINATED,
)
from intelligence.intelligence import Intelligence  # type: ignore
from utilities import utilities  # type: ignore


class LocationVoIPMicroservice(Intelligence):
    """
    Provides an interface to initiate VoIP calls at a given location, simultaneously for all devices at that location.

    If a device is actively calling then wait until it completes before starting a new call.

    Allow canceling out of all current and future calls by pressing the CONFIG button on the Develco Audio Assistant Device.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # Actively calling VoIP devices. {device_object: (timestamp_start, timestamp_end)}
        self.active_call_devices = {}

        # Pending VoIP call
        self.pending_voip_call = False
        pass

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        pass

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        pass

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        if hasattr(self, address):
            return getattr(self, address)(botengine, content)

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        if utilities._isinstance(device_object, DevelcoSquidlinkDevice):
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                ">device_measurements_updated()"
            )
            # Handle the VoIP call state for the develco gateway device
            if device_object.did_update_voip_call_state(botengine):
                voip_call_state = device_object.get_voip_call_state(botengine)
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    f"|device_measurements_updated() Device {device_object.device_id} ({device_object.description}) updated VoIP call state: {voip_call_state}"
                )
                if voip_call_state == VOIP_CALL_STATE_ACTIVE:
                    # Started calling
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                        f"|device_measurements_updated() Device {device_object.device_id} ({device_object.description}) is now active in a VoIP call."
                    )
                    self.active_call_devices[device_object] = (
                        botengine.get_timestamp(),
                        None,
                    )
                elif voip_call_state in (
                    VOIP_CALL_STATE_HANGUP_LOCAL,
                    VOIP_CALL_STATE_HANGUP_REMOTE,
                    VOIP_CALL_STATE_DISCONNECTED,
                    VOIP_CALL_STATE_ALL_LINES_BUSY,
                    VOIP_CALL_STATE_NOT_FOUND,
                    VOIP_CALL_STATE_SERVICE_UNAVAILABLE,
                    VOIP_CALL_STATE_BUSY_HERE,
                    VOIP_CALL_STATE_TERMINATED,
                ):
                    # Call ended
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                        f"|device_measurements_updated() Device {device_object.device_id} ({device_object.description}) call ended."
                    )
                    if device_object in self.active_call_devices:
                        start_time, _ = self.active_call_devices[device_object]
                        self.active_call_devices[device_object] = (
                            start_time,
                            botengine.get_timestamp(),
                        )

                    # Check if we have a pending VoIP call
                    if self.pending_voip_call:
                        # Check that all devices have completed their calls
                        if all(
                            device in self.active_call_devices
                            and self.active_call_devices[device][1] is not None
                            for device in self.parent.devices.values()
                            if utilities._isinstance(
                                device, DevelcoAudioAssistantDevice
                            )
                        ):
                            # All devices have completed their calls, we can initiate a new call
                            botengine.get_logger(
                                f"{__name__}.{__class__.__name__}"
                            ).info(
                                f"|device_measurements_updated() All devices have completed their calls: {self.active_call_devices}"
                            )
                            self.initiate_call(botengine)
                            self.pending_voip_call = False
                        else:
                            botengine.get_logger(
                                f"{__name__}.{__class__.__name__}"
                            ).info(
                                f"|device_measurements_updated() Not all devices have completed their calls: {self.active_call_devices}"
                            )
                    else:
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                            f"|device_measurements_updated() No pending VoIP call, active calls: {self.active_call_devices}"
                        )
                        self.active_call_devices.clear()

            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "<device_measurements_updated()"
            )

        if utilities._isinstance(device_object, DevelcoAudioAssistantDevice):
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                ">device_measurements_updated()"
            )
            if len(self.active_call_devices) == 0:
                # Not initiated
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    f"<device_measurements_updated() Device {device_object.device_id} ({device_object.description}) is not actively calling."
                )
                return
            # Handle the VoIP call state for the audio assistant device
            if device_object.is_short_button_pressed(
                botengine, index=BUTTON_INDEXES["CONFIG"]
            ):
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    "|device_measurements_updated() Did enter 'CONFIG' mode (short press)"
                )
                self.pending_voip_call = False
                self.active_call_devices.clear()
                botengine.hang_up_voip_call(device_object.proxy_id)

            elif device_object.is_long_button_pressed(
                botengine, index=BUTTON_INDEXES["CONFIG"]
            ):
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    "|device_measurements_updated() Did enter 'CONFIG' mode (long press)"
                )
                self.pending_voip_call = False
                self.active_call_devices.clear()
                botengine.hang_up_voip_call(device_object.proxy_id)

            elif device_object.is_short_button_pressed(
                botengine
            ) or device_object.is_long_button_pressed(botengine):
                # If the button was pressed, we should initiate a VoIP call
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    f"|device_measurements_updated() Device {device_object.device_id} ({device_object.description}) button pressed not managed by this service."
                )
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "<device_measurements_updated()"
            )

    def VOIP(self, botengine, content):
        """
        VOIP Message received
        :param botengine:
        :param content: Content of the VOIP message
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">VOIP()")
        self.pending_voip_call = True

        if len(self.active_call_devices) > 0:
            # If we are already in a call, we should not start a new one
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                "|VOIP() Active call in progress, ignoring new VOIP message."
            )
            return

        self.initiate_call(botengine)

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<VOIP()")
        pass

    def initiate_call(self, botengine):
        """
        Initiate a VoIP call to all devices at this location.
        This will start a VoIP call for each device, simultaneously.
        :param botengine: BotEngine environment
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">initiate_call()"
        )
        address_name = properties.get_property(botengine, "VOIP_ADDRESS_NAME")

        # Start a VoIP call for each device, simultaneously
        audio_assistant_devices = [
            device
            for device in self.parent.devices.values()
            if utilities._isinstance(device, DevelcoAudioAssistantDevice)
        ]
        self.active_call_devices = {
            device_id: (None, None) for device_id in audio_assistant_devices
        }
        for device_object in audio_assistant_devices:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                f"|initiate_call() Starting VoIP call for device {device_object.device_id} ({device_object.description})"
            )
            botengine.make_voip_call(
                device_object.proxy_id,
                address_name=address_name,
                audio_device_id=device_object.device_id,
            )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "<initiate_call()"
        )
        pass
