
from intelligence.voice_call.location_voice_call_microservice  import LocationVoiceCallMicroservice
from intelligence.voice_call.voice_call_model import Settings, Step, Model, Action

from locations.location import Location

from botengine_pytest import BotEnginePyTest
from botengine_pytest import Question

from unittest.mock import MagicMock

microservice_under_test = None
location_object = None

class TestVoiceCall():


    def test_voice_call_microservice(self):
        """
        :return:
        """
        global microservice_under_test
        global location_object

        self.botengine = BotEnginePyTest({})
        self.location = Location(self.botengine, 0)
        self.location.initialize(self.botengine)

        microservice_under_test = LocationVoiceCallMicroservice(self.botengine, self.location)
        assert microservice_under_test is not None

    def test_voice_call_model(self):
        settings = Settings()
        assert settings is not None
        assert dict(settings) is not None

        action = Action(digits=1, next_step_id=0)
        assert action is not None
        assert dict(action) is not None

        step_1 = Step(1, "Hello World", answer_key="TEST")
        assert step_1 is not None
        assert dict(step_1) is not None

        step_2 = Step(1, "Hello World", actions=[action])
        assert step_2 is not None
        assert dict(step_2) is not None

        model = Model()
        assert model is not None
        assert dict(model) is not None

        model = Model(steps=[step_1, step_2])
        assert model is not None
        assert dict(model) is not None
        