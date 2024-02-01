import unittest
import requests_mock
from unittest.mock import MagicMock, patch
import logging

# Import module without .py extension (throws warning)
import imp
botengine = imp.load_source('botengine', './botengine')

class TestBotEngine(unittest.TestCase):

    # Setup and teardown methods
    # Use to copy to a filename we can import naturally
    def setup_method(self, method):
        import os
        import shutil
        shutil.copy(os.path.join('./', 'botengine'), 'botengine.py')
        pass
    
    def teardown_method(self, method):
        import os
        try:
            os.remove('botengine.py')
        except:
            pass
    
    def test_botengine_init(self):
        # Import BotEngine class
        from botengine import BotEngine

        # Test missing required parameters
        raw_inputs = {}

        try:
            botengine = BotEngine({})
            assert False, "Expected KeyError exception without the 'apiKey' key"
        except:
            pass
        
        try:
            botengine = BotEngine({'apiKey': '1234567890'})
            assert False, "Expected KeyError exception without the 'apiHost' key"
        except:
            pass

        # Initialize BotEngine
        api_key = '1234567890'
        host = 'https://app.host.com'
        raw_inputs['apiKey'] = api_key
        raw_inputs['apiHost'] = host
        botengine = BotEngine(raw_inputs)
        
        # Test BotEngine attributes
        assert 'apiKey' not in raw_inputs
        assert botengine._BotEngine__key == api_key
        assert botengine._servers == [host]
        assert botengine._server_index == 0
        assert botengine._requests is not None
        assert botengine._cloud == None
        assert botengine.services == None
        assert botengine.all_trigger_types == []
        assert botengine.count == None
        assert botengine.variables == {}
        assert botengine.variables_to_flush == {}
        assert botengine.states == {None: {}}
        assert botengine.states_to_flush == {}
        assert botengine.question_answered == None
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
        assert botengine.cancelled_timers == False
        assert botengine.triggers_total == 0
        assert botengine.triggers_index == 0
        assert botengine._location_users_cache == None
        assert botengine.user_id == None
        assert botengine.local == False
        assert botengine.local_execution_count == None
        assert botengine.playback == False
        assert botengine.bot_instance_id == None
        assert botengine.executing_in_cloud == True
        assert botengine.session is not None

    @requests_mock.mock()
    def test_botengine_download_core_variables(self, mock_for_requests):
        # Import BotEngine class
        from botengine import BotEngine

        # Initialize BotEngine
        api_key = '1234567890'
        host = 'https://app.host.com'
        raw_inputs = {
            'apiKey': api_key,
            'apiHost': host
        }
        botengine = BotEngine(raw_inputs)

        # Add a logger
        add_logger(botengine)

        # Create sample core variable
        from requests import HTTPError
        import dill

        pickles = bytearray()
        v = dill.dumps({"a": 1})
        pickles += v

        mock_for_requests.get(host + "/analytic/variables/-core-", headers={}, content=v)

        # Verify core variables are downloaded and reset
        botengine._download_core_variables()
        assert botengine.variables == {"-core-": {"[c]": 0, "[q]": None, "[t]": None, "a": 1}}

    def test_botengine_get_secret(self):
        # Import BotEngine class
        from botengine import BotEngine

        # Initialize BotEngine
        api_key = '1234567890'
        host = 'https://app.host.com'
        raw_inputs = {
            'apiKey': api_key,
            'apiHost': host
        }
        botengine = BotEngine(raw_inputs)
        
        # Add a logger
        add_logger(botengine)

        s = botengine.get_secret('Test/Secret')

        assert s is None

# Helper functions

def add_logger(botengine):
    """
    Add a logger to the botengine instance
    param botengine: BotEngine instance
    """
    import logging
    logger = logging.getLogger('test')
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    fmt = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console.setFormatter(fmt)
    logger.addHandler(console)

    botengine.get_logger = MagicMock(return_value=logger)