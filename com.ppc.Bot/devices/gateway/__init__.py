from devices.gateway.gateway import GatewayDevice
from devices.gateway.gateway_develco_squidlink import DevelcoSquidlinkDevice
from devices.gateway.gateway_dsr_sgw import DsrSgwGatewayDevice
from devices.gateway.gateway_peoplepower_edge import PeoplePowerEdgeDevice
from devices.gateway.gateway_peoplepower_iotgateway import PeoplePowerIotGatewayDevice
from devices.gateway.gateway_peoplepower_mseries import PeoplePowerMSeriesDevice
from devices.gateway.gateway_peoplepower_xseries import PeoplePowerXSeriesDevice
from devices.gateway.gateway_qorvo_lcgw import QorvoLcgwGatewayDevice

__all__ = [
    "GatewayDevice",
    "DevelcoSquidlinkDevice",
    "DsrSgwGatewayDevice",
    "PeoplePowerEdgeDevice",
    "PeoplePowerIotGatewayDevice",
    "PeoplePowerMSeriesDevice",
    "PeoplePowerXSeriesDevice",
    "QorvoLcgwGatewayDevice",
]
