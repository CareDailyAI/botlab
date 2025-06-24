import unittest
from datetime import timedelta

import utilities.utilities as utilities
from locations.location import (
    Location,
)

from botengine_pytest import BotEnginePyTest


class TestLocation(unittest.TestCase):
    def test_location_constructor(self):
        # Initial setup
        botengine = BotEnginePyTest({})
        botengine.users = []
        mut = Location(botengine, 0)

        assert mut is not None
        assert mut.location_id == 0

        assert mut.born_on == botengine.get_timestamp()
        assert mut.filters == {}
        assert mut.devices == {}
        assert mut.intelligence_modules == {}
        assert mut.mode == botengine.get_mode(mut.location_id)
        assert mut.conversational_ui is None
        assert mut.security_state == Location.SECURITY_STATE_DISARMED
        assert mut.occupancy_status == ""
        assert mut.occupancy_reason == ""
        assert mut.properties_timestamp_ms == 0
        assert mut.location_properties == {}
        assert mut.location_narratives == {}
        assert mut.org_narratives == {}
        assert mut.latitude is None
        assert mut.longitude is None
        assert mut.is_daylight is None
        assert mut.language == botengine.get_language()
        assert mut.users == {}
        # assert mut.synchronize_users(botengine)
        assert not mut.deviceless_trends

    def test_location_new_version(self):
        # Initial setup
        botengine = BotEnginePyTest({})
        mut = Location(botengine, 0)

        # Get the total time it takes to execute the new_version() function in milliseconds
        import time

        t = time.time()
        mut.new_version(botengine)
        x = (time.time() - t) * 1000

        # Get the reported time from each microservice that it takes to execute the new_version() function in milliseconds
        dt = 0.0
        # print("Time to create a new version: {}".format(x))
        for i in mut.intelligence_modules.values():
            # print("Time to create a new version for {}: {}".format(i.__class__.__name__, i.statistics["time"]))
            dt += i.statistics["time"]
        # print("Total time described by microservices: {}".format(dt))

        # The reported time should be relatively close to the total time
        assert abs(dt - x) < 1000  # Allow for some error in the timing

    def test_location_local_timestamp_ms_from_relative_hours(self):
        # Initial setup
        botengine = BotEnginePyTest({})
        mut = Location(botengine, 0)

        # Mon Jun 05 2023 12:00:00 GMT-0700 (Pacific Daylight Time)
        botengine.set_timestamp(1685991600000)
        for i in range(0, 7):
            weekday = mut.get_local_datetime(botengine).weekday() + i
            # hours = mut.get_relative_time_of_day(botengine)
            # assert mut.local_timestamp_ms_from_relative_hours(botengine, weekday, hours, future=False) == botengine.get_timestamp()
            # assert mut.local_timestamp_ms_from_relative_hours(botengine, weekday, hours, future=True) == botengine.get_timestamp() + utilities.ONE_WEEK_MS
            for j in range(-12, 12):
                hours = mut.get_relative_time_of_day(botengine) + j
                # print(
                #     "Weekday: {} hour: {} future: {}".format(weekday, hours, hours > 0)
                # )
                assert (
                    mut.local_timestamp_ms_from_relative_hours(
                        botengine, weekday, hours, future=False
                    )
                    == botengine.get_timestamp()
                    + i * utilities.ONE_DAY_MS
                    + j * utilities.ONE_HOUR_MS
                )
                if j > 0 or i > 0:
                    assert (
                        mut.local_timestamp_ms_from_relative_hours(
                            botengine, weekday, hours, future=True
                        )
                        == botengine.get_timestamp()
                        + i * utilities.ONE_DAY_MS
                        + j * utilities.ONE_HOUR_MS
                    )
                else:
                    assert (
                        mut.local_timestamp_ms_from_relative_hours(
                            botengine, weekday, hours, future=True
                        )
                        == botengine.get_timestamp()
                        + utilities.ONE_WEEK_MS
                        + i * utilities.ONE_DAY_MS
                        + j * utilities.ONE_HOUR_MS
                    )

        # Sun Jun 11 2023 12:00:00 GMT-0700 (Pacific Daylight Time)
        botengine.set_timestamp(1686510000000)
        for i in range(0, 7):
            weekday = mut.get_local_datetime(botengine).weekday() + i
            if weekday > 6:
                weekday -= 7
            for j in range(-12, 12):
                hours = mut.get_relative_time_of_day(botengine) + j
                # print(
                #     "Weekday: {} hour: {} future: {}".format(weekday, hours, hours > 0)
                # )
                if i == 0:
                    assert (
                        mut.local_timestamp_ms_from_relative_hours(
                            botengine, weekday, hours, future=False
                        )
                        == botengine.get_timestamp()
                        + i * utilities.ONE_DAY_MS
                        + j * utilities.ONE_HOUR_MS
                    )
                    if j > 0:
                        assert (
                            mut.local_timestamp_ms_from_relative_hours(
                                botengine, weekday, hours, future=True
                            )
                            == botengine.get_timestamp()
                            + i * utilities.ONE_DAY_MS
                            + j * utilities.ONE_HOUR_MS
                        )
                    else:
                        assert (
                            mut.local_timestamp_ms_from_relative_hours(
                                botengine, weekday, hours, future=True
                            )
                            == botengine.get_timestamp()
                            + utilities.ONE_WEEK_MS
                            + i * utilities.ONE_DAY_MS
                            + j * utilities.ONE_HOUR_MS
                        )
                else:
                    assert (
                        mut.local_timestamp_ms_from_relative_hours(
                            botengine, weekday, hours, future=False
                        )
                        == botengine.get_timestamp()
                        - utilities.ONE_WEEK_MS
                        + i * utilities.ONE_DAY_MS
                        + j * utilities.ONE_HOUR_MS
                    )
                    if j > 0:
                        assert (
                            mut.local_timestamp_ms_from_relative_hours(
                                botengine, weekday, hours, future=True
                            )
                            == botengine.get_timestamp()
                            + i * utilities.ONE_DAY_MS
                            + j * utilities.ONE_HOUR_MS
                        )
                    else:
                        assert (
                            mut.local_timestamp_ms_from_relative_hours(
                                botengine, weekday, hours, future=True
                            )
                            == botengine.get_timestamp()
                            + i * utilities.ONE_DAY_MS
                            + j * utilities.ONE_HOUR_MS
                        )

    def test_location_timezone_aware_datetime_to_unix_timestamp(self):
        timezones = [
            "US/Pacific",
            "US/Mountain",
            "US/Central",
            "US/Eastern",
            "Europe/London",
            "Europe/Paris",
            "Asia/Tokyo",
        ]
        location_access = {
            "category": 1,
            "location": {"timezone": {"id": "US/Pacific"}},
        }
        for timezone in timezones:
            location_access["location"]["timezone"]["id"] = timezone
            botengine = BotEnginePyTest({"access": [location_access]})
            mut = Location(botengine, 0)

            # Mon Jun 05 2023 12:00:00 GMT-0700 (Pacific Daylight Time)
            botengine.set_timestamp(1685991600000)
            dt = mut.get_local_datetime(botengine)
            botengine.get_logger().info("Testing timezone: {}".format(timezone))
            botengine.get_logger().info("Local time: {}".format(dt))
            for i in range(0, 7):
                for j in range(-12, 12):
                    dt_tmp = dt + timedelta(days=i, hours=j)
                    timestamp = mut.timezone_aware_datetime_to_unix_timestamp(
                        botengine, dt_tmp
                    )
                    botengine.get_logger().info(
                        "\tLocal time: {} timestamp: {}".format(dt_tmp, timestamp)
                    )
                    assert (
                        timestamp
                        == botengine.get_timestamp()
                        + i * utilities.ONE_DAY_MS
                        + j * utilities.ONE_HOUR_MS
                    )
