import logging
from logging import Logger
import unittest
from unittest.mock import MagicMock, patch

import pytest
import requests_mock


class TestBotEngine(unittest.TestCase):
    # Setup and teardown methods
    # Use to copy to a filename we can import naturally
    def setup_method(self, method):
        import os
        import shutil

        shutil.copy(os.path.join("./", "botengine"), "botengine.py")
        pass

    def teardown_method(self, method):
        import os

        try:
            os.remove("botengine.py")
        except Exception:
            pass

    @requests_mock.mock()
    @patch("botengine.BotEngine.get_logger")
    @patch("botengine.BotEngine.get_bundle_id")
    @patch("botengine.BotEngine.get_cloud_address")
    @patch("botengine.BotEngine.get_bot_type")
    def test_botengine_init(
        self,
        mock_for_requests,
        mock_get_bot_type,
        mock_get_cloud_address,
        mock_get_bundle_id,
        mock_get_logger,
    ):
        mock_get_bot_type.return_value = 0
        mock_get_cloud_address.return_value = "https://app.host.com"
        mock_get_bundle_id.return_value = "com.ppc.Tests"
        add_logger(mock_get_logger)
        # Import BotEngine class
        from botengine import BotEngine

        # Test missing required parameters
        raw_inputs = {}

        try:
            botengine = BotEngine({})
            assert False, "Expected KeyError exception without the 'apiKey' key"
        except Exception:
            pass

        try:
            botengine = BotEngine({"apiKey": "1234567890"})
            assert False, "Expected KeyError exception without the 'apiHost' key"
        except Exception:
            pass

        # Initialize BotEngine
        api_key = "1234567890"
        hosts = [
            "https://app.host.com",
            "https://app2.host.com",
        ]
        start_key = 1
        raw_inputs = {"apiKey": api_key, "apiHosts": hosts, "startKey": start_key}
        for host in hosts:
            mock_for_requests.post(
                host + "/analytic/start", headers={}, json={"resultCode": 0}
            )
        botengine = BotEngine(raw_inputs)

        # Test BotEngine attributes
        assert "apiKey" not in raw_inputs
        assert botengine._BotEngine__key == api_key
        assert botengine._servers == hosts
        assert botengine._server_index == 0
        assert botengine._requests is not None
        assert botengine._cloud is None
        assert botengine.services is None
        assert botengine.all_trigger_types == []
        assert botengine.count is None
        assert botengine.variables == {}
        assert botengine.variables_to_flush == {}
        assert botengine.states == {None: {}}
        assert botengine.states_to_flush == {}
        assert botengine.question_answered is None
        assert botengine.commands_to_flush == []
        assert botengine.data_requests == []
        assert botengine.tags_to_create == []
        assert botengine.tags_to_delete == []
        assert botengine.tags_to_create_by_user == {}
        assert botengine.tags_to_delete_by_user == {}
        assert botengine.rules == {}
        assert botengine.questions_to_ask == {}
        assert botengine.questions_to_delete == {}
        assert botengine.organization_properties == {}
        assert botengine.cancelled_timers is False
        assert botengine.triggers_total == 0
        assert botengine.triggers_index == 0
        assert botengine._location_users_cache is None
        assert botengine.user_id is None
        assert botengine.local is False
        assert botengine.local_execution_count is None
        assert botengine.playback is False
        assert botengine.bot_instance_id is None
        assert botengine.executing_in_cloud is True
        assert botengine.session is not None

        # Test BotEngine startKey server selection
        import requests

        mock_for_requests.post(
            hosts[0] + "/analytic/start", exc=requests.exceptions.ConnectTimeout
        )
        raw_inputs = {"apiKey": api_key, "apiHosts": hosts, "startKey": start_key}
        botengine = BotEngine(raw_inputs)

        assert botengine._server_index == 1

        mock_for_requests.post(
            hosts[1] + "/analytic/start", exc=requests.exceptions.ReadTimeout
        )

        # Test server selection is locked
        with pytest.raises(Exception) as e:
            botengine._http_post("/analytic/start")
        assert e.type == requests.exceptions.Timeout

    @requests_mock.mock()
    @patch("botengine.BotEngine.get_logger")
    @patch("botengine.BotEngine.get_bundle_id")
    @patch("botengine.BotEngine.get_cloud_address")
    @patch("botengine.BotEngine.get_bot_type")
    def test_botengine_download_core_variables(
        self,
        mock_for_requests,
        mock_get_bot_type,
        mock_get_cloud_address,
        mock_get_bundle_id,
        mock_get_logger,
    ):
        mock_get_bot_type.return_value = 0
        mock_get_cloud_address.return_value = "https://app.host.com"
        mock_get_bundle_id.return_value = "com.ppc.Tests"
        add_logger(mock_get_logger)
        # Import BotEngine class
        from botengine import BotEngine

        # Initialize BotEngine
        api_key = "1234567890"
        host = "https://app.host.com"
        startKey = 1
        raw_inputs = {"apiKey": api_key, "apiHost": host, "startKey": startKey}
        mock_for_requests.post(
            host + "/analytic/start", headers={}, json={"resultCode": 0}
        )
        botengine = BotEngine(raw_inputs)

        # Create sample core variable
        import dill

        pickles = bytearray()
        v = dill.dumps({"a": 1})
        pickles += v

        mock_for_requests.get(
            host + "/analytic/variables/-core-", headers={}, content=v
        )

        # Verify core variables are downloaded and reset
        botengine._download_core_variables()
        assert botengine.variables == {
            "-core-": {"[c]": 0, "[q]": None, "[t]": None, "a": 1}
        }

    @requests_mock.mock()
    @patch("botengine.BotEngine.get_logger")
    @patch("botengine.BotEngine.get_bundle_id")
    @patch("botengine.BotEngine.get_cloud_address")
    @patch("botengine.BotEngine.get_bot_type")
    def test_botengine_get_secret(
        self,
        mock_for_requests,
        mock_get_bot_type,
        mock_get_cloud_address,
        mock_get_bundle_id,
        mock_get_logger,
    ):
        mock_get_bot_type.return_value = 0
        mock_get_cloud_address.return_value = "https://app.host.com"
        mock_get_bundle_id.return_value = "com.ppc.Tests"
        add_logger(mock_get_logger)
        # Import BotEngine class
        from botengine import BotEngine

        # Initialize BotEngine
        api_key = "1234567890"
        host = "https://app.host.com"
        start_key = 1
        raw_inputs = {"apiKey": api_key, "apiHost": host, "startKey": start_key}
        mock_for_requests.post(
            host + "/analytic/start", headers={}, json={"resultCode": 0}
        )
        mock_for_requests.get(
            host + "/analytic/secrets", headers={}, json={"resultCode": 0, "secretValue": None}
        )
        botengine = BotEngine(raw_inputs)

        s = botengine.get_secret_value("Test/Secret")
        
        assert s is None

    @requests_mock.mock()
    @patch("botengine.BotEngine.get_logger")
    @patch("botengine.BotEngine.get_bundle_id")
    @patch("botengine.BotEngine.get_cloud_address")
    @patch("botengine.BotEngine.get_bot_type")
    def test_botengine_playback_module_loader(
        self,
        mock_for_requests,
        mock_get_bot_type,
        mock_get_cloud_address,
        mock_get_bundle_id,
        mock_get_logger,
    ):
        mock_get_bot_type.return_value = 0
        mock_get_cloud_address.return_value = "https://app.host.com"
        mock_get_bundle_id.return_value = "com.ppc.Tests"
        add_logger(mock_get_logger)
        # Import BotEngine class
        import botengine
        from botengine import BotEngine
        
        # Initialize BotEngine
        api_key = "1234567890"
        host = "https://app.host.com"
        start_key = 1
        raw_inputs = {"apiKey": api_key, "apiHost": host, "startKey": start_key}
        mock_for_requests.post(
            host + "/analytic/start", headers={}, json={"resultCode": 0}
        )
        mut = BotEngine(raw_inputs)

        assert isinstance(mut, BotEngine)

        import importlib
        importlib.reload(botengine)

        import botengine
        from botengine import BotEngine
        assert not isinstance(mut, BotEngine)
        assert mut.__module__ == BotEngine.__module__

    @requests_mock.mock()
    @patch("botengine.BotEngine.get_logger")
    @patch("botengine._bot_loggers")
    @patch("botengine.BotEngine.get_bundle_id")
    @patch("botengine.BotEngine.get_cloud_address")
    @patch("botengine.BotEngine.get_bot_type")
    def test_botengine_execute_timers(
        self,
        mock_for_requests,
        mock_get_bot_type,
        mock_get_cloud_address,
        mock_get_bundle_id,
        mock__bot_loggers,
        mock_get_logger,
    ):
        mock_get_bot_type.return_value = 0
        mock_get_cloud_address.return_value = "https://app.host.com"
        mock_get_bundle_id.return_value = "com.ppc.Tests"
        logger = add_logger(mock_get_logger)

        # Import BotEngine class
        from botengine import (  # type: ignore
            _execute_timers,
            BotEngine,
            MAXINT,
        )
        mock__bot_loggers.return_value = logger

        # Initialize BotEngine
        api_key = "1234567890"
        hosts = [
            "https://app.host.com",
        ]
        start_key = 1
        raw_inputs = {"apiKey": api_key, "apiHosts": hosts, "startKey": start_key}
        for host in hosts:
            mock_for_requests.post(
                host + "/analytic/start", headers={}, json={"resultCode": 0}
            )
        botengine = BotEngine(raw_inputs)

        # Create sample core variable
        import dill

        pickles = bytearray()
        v = dill.dumps({"a": 1})
        pickles += v

        mock_for_requests.get(
            host + "/analytic/variables/-core-", headers={}, content=v
        )

        # Verify core variables are downloaded and reset
        botengine._download_core_variables()
        assert botengine.variables == {
            "-core-": {"[c]": 0, "[q]": None, "[t]": None, "a": 1}
        }

        botengine.set_inputs({
                "time": 1687373406646,
                "trigger": 0,
                "source": 0,
                "locationId": 0,
            })

        def timer_function(mut, arg):
            logger.info(f"Timer executed with arg: {arg}")
            pass

        timer_duration = 10 * 1000
        botengine.start_timer_ms(timer_duration, timer_function, "timer1")

        timers = botengine.variables['-core-']['[t]']
        logger.info("Timers before execution" + str(timers))
        assert len(timers) == 2
        assert timers[0][0] == botengine.get_timestamp() + timer_duration
        assert timers[-1][0] == MAXINT

        _execute_timers(botengine, botengine.get_timestamp(), botengine.get_timestamp())

        timers = botengine.variables['-core-']['[t]']
        logger.info("Timers after execution" + str(timers))
        assert len(timers) == 2
        assert timers[0][0] == botengine.get_timestamp() + timer_duration
        
        _execute_timers(botengine, botengine.get_timestamp(), botengine.get_timestamp() + timer_duration)
        
        timers = botengine.variables['-core-']['[t]']
        logger.info("Timers after execution" + str(timers))
        assert len(timers) == 1
        assert timers[0][0] == MAXINT

    @requests_mock.mock()
    @patch("botengine.BotEngine.get_logger")
    @patch("botengine._bot_loggers")
    @patch("botengine.BotEngine.get_bundle_id")
    @patch("botengine.BotEngine.get_cloud_address")
    @patch("botengine.BotEngine.get_bot_type")
    def test_botengine_schedule_next_timer(
        self,
        mock_for_requests,
        mock_get_bot_type,
        mock_get_cloud_address,
        mock_get_bundle_id,
        mock__bot_loggers,
        mock_get_logger,
    ):
        mock_get_bot_type.return_value = 0
        mock_get_cloud_address.return_value = "https://app.host.com"
        mock_get_bundle_id.return_value = "com.ppc.Tests"
        logger = add_logger(mock_get_logger)

        # Import BotEngine class
        from botengine import (  # type: ignore
            _schedule_next_timer,
            BotEngine,
            MAXINT,
        )
        mock__bot_loggers.return_value = logger

        # Initialize BotEngine
        api_key = "1234567890"
        hosts = [
            "https://app.host.com",
        ]
        start_key = 1
        raw_inputs = {"apiKey": api_key, "apiHosts": hosts, "startKey": start_key}
        for host in hosts:
            mock_for_requests.post(
                host + "/analytic/start", headers={}, json={"resultCode": 0}
            )
        botengine = BotEngine(raw_inputs)

        # Create sample core variable
        import dill

        pickles = bytearray()
        v = dill.dumps({"a": 1})
        pickles += v

        mock_for_requests.get(
            host + "/analytic/variables/-core-", headers={}, content=v
        )

        # Verify core variables are downloaded and reset
        botengine._download_core_variables()
        assert botengine.variables == {
            "-core-": {"[c]": 0, "[q]": None, "[t]": None, "a": 1}
        }

        botengine.set_inputs({
                "time": 1687373406646,
                "trigger": 0,
                "source": 0,
                "locationId": 0,
            })
        

        def timer_function(mut, arg):
            logger.info(f"Timer executed with arg: {arg}")
            pass

        timer_duration = 10 * 1000
        botengine.start_timer_ms(timer_duration, timer_function, "timer1")

        timers = botengine.variables['-core-']['[t]']
        logger.info("Timers before execution" + str(timers))
        assert len(timers) == 2
        assert timers[0][0] == botengine.get_timestamp() + timer_duration
        assert timers[-1][0] == MAXINT

        # Mock cloud success to schedule next timer
        mock_for_requests.put(
            host + "/analytic/execute", headers={}, json={"resultCode": 0, "timer": botengine.get_timestamp() + 10000}
        )
        _schedule_next_timer(botengine, botengine.get_timestamp())

        timers = botengine.variables['-core-']['[t]']
        logger.info("Timers after execution" + str(timers))
        assert len(timers) == 2
        assert timers[0][0] == botengine.get_timestamp() + timer_duration
        
        # Mock cloud failure to schedule next timer
        mock_for_requests.put(
            host + "/analytic/execute", headers={}, json={"resultCode": 0, "timer": 0}
        )
        _schedule_next_timer(botengine, None)
        
        timers = botengine.variables['-core-']['[t]']
        logger.info("Timers after execution" + str(timers))
        assert len(timers) == 1
        assert timers[0][0] == MAXINT
        
# Helper functions

def add_logger(mock_get_logger) -> Logger:
    """
    Add a logger to the botengine instance
    param botengine: BotEngine instance
    """
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    console.setFormatter(fmt)
    logger.addHandler(console)

    mock_get_logger.return_value = MagicMock(return_value=logger)

    return logger