import os
import maestro_cli.maestro as maestro
import maestro_cli.api as api

from maestro_cli.api import DATA_REQUEST_TYPE_DEVICE_PARAMETERS
from maestro_cli.api import DATA_REQUEST_TYPE_DEVICE_ACTIVITIES
from maestro_cli.api import DATA_REQUEST_TYPE_ORGANIZATION_LOCATIONS
from maestro_cli.api import DATA_REQUEST_TYPE_LOCATION_MODES
from maestro_cli.api import DATA_REQUEST_TYPE_LOCATION_NARRATIVES
from maestro_cli.api import DATA_REQUEST_TYPE_ORGANIZATION_DEVICES
from maestro_cli.api import DATA_REQUEST_TYPE_DATA_STREAMS
from maestro_cli.api import DATA_REQUEST_TYPE_DEVICE_ALERTS

from unittest.mock import MagicMock

class TestMaestroCLI():

    def test_maestro_cli_api(self):
        """
        :return:
        """
        api.get_location = MagicMock(return_value={"addrStreet1": "123 Main", "addrCity": "Small Town", "zip": "12345", "id": 123, "name": "My Home", "timezone": {"id": "America/Los_Angeles", "offset": -480, "dst": True, "name": "Pacific Standard Time"}, "organizationId": 123})
        api.get_devices = MagicMock(return_value=[{"id": "abc123", "type": 123, "goalId": -1, "typeCategory": 123, "desc": "Device", "modelId": "devicemodel", "lastDataReceivedDate": "2022-12-12T04:10:03.492Z", "lastDataReceivedDateMs": 1670818203492, "lastMeasureDate": "2022-12-12T04:10:02.046Z", "lastMeasureDateMs": 1670818202046, "connected": False, "newDevice": False, "proxyId": "02000001300001FA", "startDate": "2021-05-23T14:57:19Z", "startDateMs": 1621781839000, "location": api.get_location()}])
        api.get_device_properties = MagicMock(return_value=[])

        tests_dir_path = os.path.join(os.getcwd(), 'tests')
        parameters_file = os.path.join(tests_dir_path, 'resources', 'device_parameters.csv')
        alerts_file = os.path.join(tests_dir_path, 'resources', 'device_alerts.csv')
        datastreams_file = os.path.join(tests_dir_path, 'resources', 'streams_datastreams.csv')
        modes_file = os.path.join(tests_dir_path, 'resources', 'modes_history.csv')
        
        device = api.get_devices()[0]
        
        file_1 = api.transform_device_csv(parameters_file,device,DATA_REQUEST_TYPE_DEVICE_PARAMETERS)
        file_2 = api.transform_device_csv(alerts_file,device,DATA_REQUEST_TYPE_DEVICE_ALERTS)
        file_3 = api.transform_datastreams_csv(datastreams_file, api.get_location())
        file_4 = api.transform_modes_csv(modes_file, api.get_location())
        assert file_1 == os.path.join(tests_dir_path, 'resources', '123_devicemodel_abc123_Device_1.csv')
        assert file_2 == os.path.join(tests_dir_path, 'resources', '123_devicemodel_abc123_Device_9.csv')
        assert file_3 == os.path.join(tests_dir_path, 'resources', 'location_123_datastreams_history.csv')
        assert file_4 == os.path.join(tests_dir_path, 'resources', 'location_123_modes_history.csv')

        cloud_url = "some.cloud.url"
        admin_key = "__key__"
        location_id = api.get_location()["id"]
        transformed_files = [
            file_1,
            file_2,
            file_3,
            file_4,
        ]
        data_request_params_files = []
        data_path = os.path.join(tests_dir_path, 'results')
        start_time_ms = 1670278652022
        end_time_ms = 1670912252000


        saved_files = api._generate_recordings(
            cloud_url,
            admin_key,
            location_id,
            transformed_files,
            data_request_params_files,
            data_path,
            start_time_ms,
            end_time_ms
        )

        assert saved_files == [
            os.path.join(data_path, 'recording-location_123-7_days_of_data.json'), 
            os.path.join(data_path, 'recording__abc123_device_location-123.json')
        ]


        
