# coding=utf-8
import numpy as np
import pytest

from trajectory_container_tools.temporal import (
    TimestampCausalOrderingError,
    Timestamps,
    compute_delta_timestamp,
    to_seconds,
    to_seconds_nanoseconds,
    validate_timestamps_ordering,
)


class TestTimestampCausalOrderingSanityCheck:
    def test_base_case_pass(self, setup_Timestamps_object):
        assert validate_timestamps_ordering(setup_Timestamps_object) == []

    def test_case_non_causal_ordering_detected(self, setup_mock_timestamps):
        setup_mock_timestamps[5] = 1711038330132760208
        setup_mock_timestamps[9] = 1711038330177285488

        with pytest.raises(TimestampCausalOrderingError) as exc_info:
            assert validate_timestamps_ordering(Timestamps(setup_mock_timestamps)) == [
                5,
                9,
            ]

        print(f"{exc_info=}")
        expected_error_msg = (
            f"Timestamp causal ordering violations:\n"
            f"    Number of offending timestamps 2/10\n\n"
        )
        assert expected_error_msg in exc_info.value.args[0]


class TestTimestampConversionHelper:

    def test_to_seconds_nanoseconds(self):

        assert to_seconds_nanoseconds(int(1e9)) == (1, 000000000)
        assert to_seconds_nanoseconds(1711038330132760208) == (1711038330, 132760208)

        t_second, t_nano = to_seconds_nanoseconds(np.ones(10) * 1711038330132760208)
        assert t_second == pytest.approx(np.ones(10) * 1711038330)
        assert t_nano == pytest.approx(np.ones(10) * 132760208)

    def test_to_seconds(self):

        assert to_seconds(int(1e9)) == 1.0
        assert to_seconds(int(1e8)) == 0.1
        assert to_seconds(1711038330132760208) == 1711038330.132760208

        assert to_seconds(np.ones(10) * int(1e9)) == pytest.approx(np.ones(10) * 1.0)
        assert to_seconds(np.ones(10) * int(1e8)) == pytest.approx(np.ones(10) * 0.1)

    def test_compute_delta_timestamp(self):
        t_time_space = np.arange(100) * 100000000  # Mock timestamp with uniform delta
        t_time_space += 1711038330  # Make trajectory timestamp start at arbitrary time
        t_dt_space = np.ones(100) * 100000000  # Expected delta
        t_dt_space[0] = 0  # Delta array first element should be 0
        delta_time = compute_delta_timestamp(t_time_space)
        assert delta_time == pytest.approx(t_dt_space)
