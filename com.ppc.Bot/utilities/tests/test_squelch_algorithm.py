

from botengine_pytest import BotEnginePyTest

from utilities.squelch import Squelch

import utilities.utilities as utilities

class TestLocationSleepIntelligence:

    def test_squelch(self):
        """
        Test the squelch algorithm
        """
        botengine = BotEnginePyTest({})

        squelch = Squelch(averaging_window=100,
                          minimum_signal_samples=2,
                          default_periodicity_s=60,
                          signal_threshold_stdevs=2.0,
                          minimum_required_datapoints=10,
                          rate_of_change_threshold=None,
                          minimum_signal_value=None)

        # Initialize the data set
        now = 0
        botengine.set_timestamp(now)
        assert squelch.is_signal_detected(botengine, 50) == False

        # Test that our data set increases properly
        now += utilities.ONE_MINUTE_MS
        botengine.set_timestamp(now)
        assert squelch.is_signal_detected(botengine, 50) == False
        assert len(squelch.data_points) == 2

        # Test that skipping a measurement fills in gaps in the data
        now += utilities.ONE_MINUTE_MS * 2
        botengine.set_timestamp(now)
        assert squelch.is_signal_detected(botengine, 50) == False
        assert len(squelch.data_points) == 4

        # Test that some internet delays still give us the same periodicity
        now += utilities.ONE_MINUTE_MS * 2 + 10000
        botengine.set_timestamp(now)
        assert squelch.is_signal_detected(botengine, 50) == False
        assert len(squelch.data_points) == 6

        # Fill up a bunch of data
        now += utilities.ONE_MINUTE_MS * 50
        botengine.set_timestamp(now)
        assert squelch.is_signal_detected(botengine, 50) == False
        assert len(squelch.data_points) == 56

        # Add some signal
        now += utilities.ONE_MINUTE_MS
        botengine.set_timestamp(now)
        assert squelch.is_signal_detected(botengine, 60) == False
        assert len(squelch.data_points) == 57

        # Add some signal. This would make for 58 data points, but because we remove signal, the window decreases
        now += utilities.ONE_MINUTE_MS
        botengine.set_timestamp(now)
        assert squelch.is_signal_detected(botengine, 70) == True
        assert len(squelch.data_points) == 56










