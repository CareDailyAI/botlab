

from re import L
from confidence.confidence_state import CONFIDENCE_OFFLINE
from confidence.confidence_state import CONFIDENCE_LOW
from confidence.confidence_state import CONFIDENCE_MEDIUM
from confidence.confidence_state import CONFIDENCE_HIGH
from confidence.sleep_confidence_machine import SleepConfidenceStateMachine

from locations.location import Location

from devices.device import SPACE_TYPE
from devices.motion.motion import MotionDevice
from devices.entry.entry import EntryDevice
from devices.vayyar.vayyar import VayyarDevice
from devices.lock.lock import LockDevice

from botengine_pytest import BotEnginePyTest


microservice_under_test = None
location_object = None

class TestConfidence():


    def test_confidence_occupancy_initialization(self):
        """
        :return:
        """
        global model_under_test
        global location_object
        global botengine 
        
        botengine = BotEnginePyTest({})
        
        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        from confidence.occupancy_confidence_machine import OccupancyConfidenceStateMachine
        model_under_test = OccupancyConfidenceStateMachine()

        assert model_under_test is not None, "Missing model"
        assert model_under_test.current_away_confidence() == (None, None), "Occupancy CSM initializaed prematurely"


    def test_confidence_occupancy_offline(self):
        """
        :return:
        """
        global model_under_test
        global location_object
        global botengine 
        
        botengine = BotEnginePyTest({})
        
        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        from confidence.occupancy_confidence_machine import OccupancyConfidenceStateMachine
        model_under_test = OccupancyConfidenceStateMachine()

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_OFFLINE, "We don't have enough Motion or Vayyar devices for occupancy away service to work.")

        # 1 Motion (disconnected)
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = False

        location_object.devices = {motion_device.device_id: motion_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_OFFLINE, "We don't have enough Motion or Vayyar devices for occupancy away service to work.")

        # 1 Entry (disconnected)
        entry_device = EntryDevice(botengine, location_object, "B", 10014, "")
        entry_device.is_connected = False

        location_object.devices = {entry_device.device_id: entry_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_OFFLINE, "We don't have enough Motion or Vayyar devices for occupancy away service to work.")

        # 1 Vayyar (disconnected)
        vayyar_device = VayyarDevice(botengine, location_object, "C", 2000, "")
        vayyar_device.is_connected = False

        location_object.devices = {vayyar_device.device_id: vayyar_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_OFFLINE, "We don't have enough Motion or Vayyar devices for occupancy away service to work.")

        # 1 Lock (disconnected)
        lock_device = LockDevice(botengine, location_object, "D", 9010, "")
        lock_device.is_connected = False

        location_object.devices = {lock_device.device_id: lock_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_OFFLINE, "We don't have enough Motion or Vayyar devices for occupancy away service to work.")



    def test_confidence_occupancy_low(self):
        """
        :return:
        """
        global model_under_test
        global location_object
        global botengine 
        
        botengine = BotEnginePyTest({})
        
        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        from confidence.occupancy_confidence_machine import OccupancyConfidenceStateMachine
        model_under_test = OccupancyConfidenceStateMachine()

        # 0 Motion / 0 Vayyar / 1 Entry / 0 Lock
        entry_device = EntryDevice(botengine, location_object, "B", 10014, "")
        entry_device.is_connected = True

        location_object.devices = {entry_device.device_id: entry_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_LOW, "Add 1 Motion or Vayyar device to improve the confidence.")

        # 0 Motion / 0 Vayyar / 2 Entry / 0 Lock
        entry_device_2 = EntryDevice(botengine, location_object, "B", 10014, "")
        entry_device_2.is_connected = True

        location_object.devices = {entry_device.device_id: entry_device, entry_device_2.device_id: entry_device_2}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_LOW, "Add 1 Motion or Vayyar device to improve the confidence.")

        # 0 Motion / 0 Vayyar / 0 Entry / 1 Lock
        lock_device = LockDevice(botengine, location_object, "D", 9010, "")
        lock_device.is_connected = True

        location_object.devices = {lock_device.device_id: lock_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_LOW, "Add 1 Motion or Vayyar device to improve the confidence.")

        # 0 Motion / 0 Vayyar / 0 Entry / 2 Lock
        lock_device_2 = LockDevice(botengine, location_object, "D", 9010, "")
        lock_device_2.is_connected = True

        location_object.devices = {lock_device.device_id: lock_device, lock_device_2.device_id: lock_device_2}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_LOW, "Add 1 Motion or Vayyar device to improve the confidence.")

        # 1 Motion / 0 Vayyar / 0 Entry / 0 Lock
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_LOW, "Add 1 Entry device to improve the confidence.")

        # 0 Motion / 1 Vayyar / 0 Entry / 0 Lock
        vayyar_device = VayyarDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True

        location_object.devices = {vayyar_device.device_id: vayyar_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_LOW, "Add 1 Entry device to improve the confidence.")

    def test_confidence_occupancy_medium(self):
        """
        :return:
        """
        global model_under_test
        global location_object
        global botengine 
        
        botengine = BotEnginePyTest({})
        
        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        from confidence.occupancy_confidence_machine import OccupancyConfidenceStateMachine
        model_under_test = OccupancyConfidenceStateMachine()

        # 1 Motion / 0 Vayyar / 1 Entry / 0 Lock
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True

        entry_device = EntryDevice(botengine, location_object, "B", 10014, "")
        entry_device.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, entry_device.device_id: entry_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_MEDIUM, "Add 1 more Motion or Vayyar device to improve the confidence.")

        # 1 Motion / 0 Vayyar / 0 Entry / 1 Lock
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True

        lock_device = LockDevice(botengine, location_object, "B", 9010, "")
        lock_device.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, lock_device.device_id: lock_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_MEDIUM, "Add 1 more Motion or Vayyar device to improve the confidence.")

        # 0 Motion / 1 Vayyar / 1 Entry / 0 Lock
        vayyar_device = MotionDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True

        entry_device = EntryDevice(botengine, location_object, "B", 10014, "")
        entry_device.is_connected = True

        location_object.devices = {vayyar_device.device_id: vayyar_device, entry_device.device_id: entry_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_MEDIUM, "Add 1 more Motion or Vayyar device to improve the confidence.")

        # 0 Motion / 1 Vayyar / 0 Entry / 1 Lock
        vayyar_device = MotionDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True

        lock_device = LockDevice(botengine, location_object, "B", 9010, "")
        lock_device.is_connected = True

        location_object.devices = {vayyar_device.device_id: vayyar_device, lock_device.device_id: lock_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_MEDIUM, "Add 1 more Motion or Vayyar device to improve the confidence.")

        # 2 Motion / 0 Vayyar / 0 Entry / 0 Lock
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True

        motion_device_2 = MotionDevice(botengine, location_object, "B", 10038, "")
        motion_device_2.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, motion_device_2.device_id: motion_device_2}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_MEDIUM, "Add 1 more entry device to improve the confidence.")

        # 1 Motion / 1 Vayyar / 0 Entry / 0 Lock
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True

        vayyar_device = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, vayyar_device.device_id: vayyar_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_MEDIUM, "Add 1 more entry device to improve the confidence.")

        # 0 Motion / 2 Vayyar / 0 Entry / 0 Lock
        vayyar_device = MotionDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True

        vayyar_device_2 = MotionDevice(botengine, location_object, "B", 2000, "")
        vayyar_device_2.is_connected = True

        location_object.devices = {vayyar_device.device_id: vayyar_device, vayyar_device_2.device_id: vayyar_device_2}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_MEDIUM, "Add 1 more entry device to improve the confidence.")

    def test_confidence_occupancy_high(self):
        """
        :return:
        """
        global model_under_test
        global location_object
        global botengine 
        
        botengine = BotEnginePyTest({})
        
        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        from confidence.occupancy_confidence_machine import OccupancyConfidenceStateMachine
        model_under_test = OccupancyConfidenceStateMachine()

        # 2 Motion / 0 Vayyar / 1 Entry / 0 Lock
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True

        motion_device_2 = MotionDevice(botengine, location_object, "B", 10038, "")
        motion_device_2.is_connected = True

        entry_device = EntryDevice(botengine, location_object, "C", 10014, "")
        entry_device.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, motion_device_2.device_id: motion_device_2, entry_device.device_id: entry_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_HIGH, "We have high confidence on the occupancy away service.")

        # 2 Motion / 0 Vayyar / 0 Entry / 1 Lock
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True

        motion_device_2 = MotionDevice(botengine, location_object, "B", 10038, "")
        motion_device_2.is_connected = True

        lock_device = EntryDevice(botengine, location_object, "C", 9010, "")
        lock_device.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, motion_device_2.device_id: motion_device_2, lock_device.device_id: lock_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_HIGH, "We have high confidence on the occupancy away service.")

        # 0 Motion / 2 Vayyar / 1 Entry / 0 Lock
        vayyar_device = VayyarDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True

        vayyar_device_2 = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device_2.is_connected = True

        entry_device = EntryDevice(botengine, location_object, "C", 10014, "")
        entry_device.is_connected = True

        location_object.devices = {vayyar_device.device_id: vayyar_device, vayyar_device_2.device_id: vayyar_device_2, entry_device.device_id: entry_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_HIGH, "We have high confidence on the occupancy away service.")

        # 0 Motion / 2 Vayyar / 0 Entry / 1 Lock
        vayyar_device = VayyarDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True

        vayyar_device_2 = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device_2.is_connected = True

        lock_device = EntryDevice(botengine, location_object, "C", 9010, "")
        lock_device.is_connected = True

        location_object.devices = {vayyar_device.device_id: vayyar_device, vayyar_device_2.device_id: vayyar_device_2, lock_device.device_id: lock_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_HIGH, "We have high confidence on the occupancy away service.")

        # 0 Motion / 2 Vayyar / 0 Entry / 1 Lock
        motion_device = VayyarDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True

        vayyar_device = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device.is_connected = True

        lock_device = EntryDevice(botengine, location_object, "C", 9010, "")
        lock_device.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, vayyar_device.device_id: vayyar_device, lock_device.device_id: lock_device}

        model_under_test.update_away_confidence_state(botengine, location_object)

        assert model_under_test.current_away_confidence() == (CONFIDENCE_HIGH, "We have high confidence on the occupancy away service.")


    def test_confidence_sleep_initialization(self):
        """
        :return:
        """
        global model_under_test
        global location_object
        global botengine

        botengine = BotEnginePyTest({})

        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        from confidence.sleep_confidence_machine import SleepConfidenceStateMachine
        model_under_test = SleepConfidenceStateMachine()

        assert model_under_test is not None, "Missing model"
        assert model_under_test.current_confidence() == (None, None), "Sleep CSM initializaed prematurely"


    def test_confidence_sleep_offline(self):
        """
        :return:
        """
        global model_under_test
        global location_object
        global botengine

        botengine = BotEnginePyTest({})

        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        from confidence.sleep_confidence_machine import SleepConfidenceStateMachine
        model_under_test = SleepConfidenceStateMachine()

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_state() == CONFIDENCE_OFFLINE

        # 1 Motion (disconnected)
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = False

        location_object.devices = {motion_device.device_id: motion_device}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_state() == CONFIDENCE_OFFLINE

        # 1 Vayyar (disconnected)
        vayyar_device = VayyarDevice(botengine, location_object, "C", 2000, "")
        vayyar_device.is_connected = False

        location_object.devices = {vayyar_device.device_id: vayyar_device}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_state() == CONFIDENCE_OFFLINE

    def test_confidence_sleep_low(self):
        """
        :return:
        """
        global model_under_test
        global location_object
        global botengine

        botengine = BotEnginePyTest({})

        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        from confidence.sleep_confidence_machine import SleepConfidenceStateMachine
        model_under_test = SleepConfidenceStateMachine()

        # 1 Motion / 0 Vayyar
        # 0 In Bedroom / 0 Out Bedroom
        # 0 Measured / 1 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_LOW, "Add more Motion or Vayyar devices installed inside bedroom to improve the confidence.")

        # 0 Motion / 1 Vayyar
        # 0 In Bedroom / 0 Out Bedroom
        # 0 Measured / 1 Not Measured
        vayyar_device = VayyarDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True

        location_object.devices = {vayyar_device.device_id: vayyar_device}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_LOW, "Add more Motion or Vayyar devices installed inside bedroom to improve the confidence.")

        # 1 Motion / 0 Vayyar
        # 1 In Bedroom / 0 Out Bedroom
        # 0 Measured / 1 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]

        location_object.devices = {motion_device.device_id: motion_device}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_LOW, "Add more Motion or Vayyar devices installed outside bedroom to improve the confidence.")

        # 0 Motion / 1 Vayyar
        # 1 In Bedroom / 0 Out Bedroom
        # 0 Measured / 1 Not Measured
        vayyar_device = VayyarDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True
        vayyar_device.goal_id = VayyarDevice.BEHAVIOR_TYPE_BEDROOM

        location_object.devices = {vayyar_device.device_id: vayyar_device}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_LOW, "Add more Motion or Vayyar devices installed outside bedroom to improve the confidence.")

        # 2 Motion / 0 Vayyar
        # 1 In Bedroom / 1 Out Bedroom
        # 0 Measured / 2 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]

        motion_device_2 = MotionDevice(botengine, location_object, "B", 10038, "")
        motion_device_2.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, motion_device_2.device_id: motion_device_2}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_LOW, "We have low confidence on the sleep service due to lack of recent measurements.")

        # 1 Motion / 1 Vayyar
        # 1 In Bedroom / 1 Out Bedroom
        # 0 Measured / 2 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]

        vayyar_device = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, vayyar_device.device_id: vayyar_device}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_LOW, "We have low confidence on the sleep service due to lack of recent measurements.")

        # 0 Motion / 2 Vayyar
        # 1 In Bedroom / 1 Out Bedroom
        # 0 Measured / 2 Not Measured
        vayyar_device = VayyarDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True
        vayyar_device.goal_id = VayyarDevice.BEHAVIOR_TYPE_BEDROOM

        vayyar_device_2 = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device_2.is_connected = True

        location_object.devices = {vayyar_device.device_id: vayyar_device, vayyar_device_2.device_id: vayyar_device_2}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_LOW, "We have low confidence on the sleep service due to lack of recent measurements.")


    def test_confidence_sleep_medium(self):
        """
        :return:
        """
        global model_under_test
        global location_object
        global botengine

        botengine = BotEnginePyTest({})

        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        from confidence.sleep_confidence_machine import SleepConfidenceStateMachine
        model_under_test = SleepConfidenceStateMachine()

        model_under_test.update_confidence_state(botengine, location_object)

        # 2 Motion / 0 Vayyar
        # 1 In bedroom / 1 Out bedroom
        # 2 Measured / 0 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]
        motion_device.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        motion_device_2 = MotionDevice(botengine, location_object, "B", 10038, "")
        motion_device_2.is_connected = True
        motion_device_2.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]

        location_object.devices = {motion_device.device_id: motion_device, motion_device_2.device_id: motion_device_2}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_MEDIUM, "Add 1 more Motion or Vayyar device to improve the confidence.")

        # 1 Motion / 1 Vayyar
        # 1 In bedroom / 1 Out bedroom
        # 2 Measured / 0 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]
        motion_device.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]

        vayyar_device = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device.is_connected = True
        vayyar_device.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]

        location_object.devices = {motion_device.device_id: motion_device, vayyar_device.device_id: vayyar_device}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_MEDIUM, "Add 1 more Motion or Vayyar device to improve the confidence.")

        # 0 Motion / 2 Vayyar
        # 1 In bedroom / 1 Out bedroom
        # 2 Measured / 0 Not Measured
        vayyar_device = VayyarDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True
        vayyar_device.goal_id = VayyarDevice.BEHAVIOR_TYPE_BEDROOM
        vayyar_device.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]

        vayyar_device_2 = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device_2.is_connected = True
        vayyar_device_2.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]

        location_object.devices = {vayyar_device.device_id: vayyar_device, vayyar_device_2.device_id: vayyar_device_2}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_MEDIUM, "Add 1 more Motion or Vayyar device to improve the confidence.")

        # 3 Motion / 0 Vayyar
        # 1 In bedroom / 2 Out bedroom
        # 2 Measured / 1 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]
        motion_device.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        motion_device_2 = MotionDevice(botengine, location_object, "B", 10038, "")
        motion_device_2.is_connected = True
        motion_device_2.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        motion_device_3 = MotionDevice(botengine, location_object, "C", 10038, "")
        motion_device_3.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, motion_device_2.device_id: motion_device_2, motion_device_3.device_id: motion_device_3}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_MEDIUM, "We have medium confidence on the sleep service due to lack of recent measurements.")

        # 2 Motion / 1 Vayyar
        # 1 In bedroom / 2 Out bedroom
        # 2 Measured / 1 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]
        motion_device.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        motion_device_2 = MotionDevice(botengine, location_object, "B", 10038, "")
        motion_device_2.is_connected = True
        motion_device_2.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        vayyar_device = VayyarDevice(botengine, location_object, "C", 2000, "")
        vayyar_device.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, motion_device_2.device_id: motion_device_2, vayyar_device.device_id: vayyar_device}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_MEDIUM, "We have medium confidence on the sleep service due to lack of recent measurements.")

        # 1 Motion / 2 Vayyar
        # 1 In bedroom / 2 Out bedroom
        # 2 Measured / 1 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]
        motion_device.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        vayyar_device = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device.is_connected = True
        vayyar_device.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]
        
        vayyar_device_2 = VayyarDevice(botengine, location_object, "C", 2000, "")
        vayyar_device_2.is_connected = True

        location_object.devices = {motion_device.device_id: motion_device, vayyar_device.device_id: vayyar_device, vayyar_device_2.device_id: vayyar_device_2}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_MEDIUM, "We have medium confidence on the sleep service due to lack of recent measurements.")

        # 0 Motion / 3 Vayyar
        # 1 In bedroom / 2 Out bedroom
        # 2 Measured / 1 Not Measured
        vayyar_device = VayyarDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True
        vayyar_device.goal_id = VayyarDevice.BEHAVIOR_TYPE_BEDROOM
        vayyar_device.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]
        
        vayyar_device_2 = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device_2.is_connected = True
        vayyar_device_2.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]
        
        vayyar_device_3 = VayyarDevice(botengine, location_object, "C", 2000, "")
        vayyar_device_3.is_connected = True

        location_object.devices = {vayyar_device.device_id: vayyar_device, vayyar_device_2.device_id: vayyar_device_2, vayyar_device_3.device_id: vayyar_device_3}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_MEDIUM, "We have medium confidence on the sleep service due to lack of recent measurements.")

    def test_confidence_sleep_high(self):
        """
        :return:
        """
        global model_under_test
        global location_object
        global botengine

        botengine = BotEnginePyTest({})

        location_object = Location(botengine, 0)
        location_object.initialize(botengine)

        from confidence.sleep_confidence_machine import SleepConfidenceStateMachine
        model_under_test = SleepConfidenceStateMachine()

        # 3 Motion / 0 Vayyar
        # 1 In bedroom / 2 Out bedroom
        # 3 Measured / 0 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]
        motion_device.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        motion_device_2 = MotionDevice(botengine, location_object, "B", 10038, "")
        motion_device_2.is_connected = True
        motion_device_2.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        motion_device_3 = MotionDevice(botengine, location_object, "C", 10038, "")
        motion_device_3.is_connected = True
        motion_device_3.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]

        location_object.devices = {motion_device.device_id: motion_device, motion_device_2.device_id: motion_device_2, motion_device_3.device_id: motion_device_3}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_HIGH, "We have high confidence on the sleep service.")

        # 2 Motion / 1 Vayyar
        # 1 In bedroom / 2 Out bedroom
        # 2 Measured / 1 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]
        motion_device.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        motion_device_2 = MotionDevice(botengine, location_object, "B", 10038, "")
        motion_device_2.is_connected = True
        motion_device_2.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        vayyar_device = VayyarDevice(botengine, location_object, "C", 2000, "")
        vayyar_device.is_connected = True
        vayyar_device.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]

        location_object.devices = {motion_device.device_id: motion_device, motion_device_2.device_id: motion_device_2, vayyar_device.device_id: vayyar_device}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_HIGH, "We have high confidence on the sleep service.")

        # 1 Motion / 2 Vayyar
        # 1 In bedroom / 2 Out bedroom
        # 2 Measured / 1 Not Measured
        motion_device = MotionDevice(botengine, location_object, "A", 10038, "")
        motion_device.is_connected = True
        motion_device.spaces = [{
            "name": "Bedroom",
            "spaceId": 0,
            "spaceType": SPACE_TYPE["bedroom"]
        }]
        motion_device.measurements[MotionDevice.MEASUREMENT_NAME_STATUS] = [[0, botengine.get_timestamp()]]
        
        vayyar_device = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device.is_connected = True
        vayyar_device.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]
        
        vayyar_device_2 = VayyarDevice(botengine, location_object, "C", 2000, "")
        vayyar_device_2.is_connected = True
        vayyar_device_2.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]

        location_object.devices = {motion_device.device_id: motion_device, vayyar_device.device_id: vayyar_device, vayyar_device_2.device_id: vayyar_device_2}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_HIGH, "We have high confidence on the sleep service.")

        # 0 Motion / 3 Vayyar
        # 1 In bedroom / 2 Out bedroom
        # 2 Measured / 1 Not Measured
        vayyar_device = VayyarDevice(botengine, location_object, "A", 2000, "")
        vayyar_device.is_connected = True
        vayyar_device.goal_id = VayyarDevice.BEHAVIOR_TYPE_BEDROOM
        vayyar_device.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]
        
        vayyar_device_2 = VayyarDevice(botengine, location_object, "B", 2000, "")
        vayyar_device_2.is_connected = True
        vayyar_device_2.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]
        
        vayyar_device_3 = VayyarDevice(botengine, location_object, "C", 2000, "")
        vayyar_device_3.is_connected = True
        vayyar_device_3.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET] = [[0, botengine.get_timestamp()]]

        location_object.devices = {vayyar_device.device_id: vayyar_device, vayyar_device_2.device_id: vayyar_device_2, vayyar_device_3.device_id: vayyar_device_3}

        model_under_test.update_confidence_state(botengine, location_object)

        assert model_under_test.current_confidence() == (CONFIDENCE_HIGH, "We have high confidence on the sleep service.")
