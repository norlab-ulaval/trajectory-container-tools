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


class TestToSecondsNanoseconds:

    def test_case_single_input(self):
        assert to_seconds_nanoseconds(int(1e9)) == (1, 000000000)
        assert to_seconds_nanoseconds(1711038330132760208) == (1711038330, 132760208)

    def test_case_array_input(self):
        t_second = np.ones(10, dtype=int) * 1711038330
        t_nano = np.ones(10, dtype=int) * 132760208
        second, nano = to_seconds_nanoseconds(
            np.ones(10, dtype=int) * 1711038330132760208
        )
        assert second.dtype == int
        assert nano.dtype == int
        assert np.array_equal(second, t_second)
        assert np.array_equal(nano, t_nano)

    def test_case_wrong_input_type(self):
        with pytest.raises(TypeError) as exc_info:
            to_seconds_nanoseconds(1e9)

        with pytest.raises(TypeError) as exc_info:
            to_seconds_nanoseconds(np.ones(10, dtype=float) * 1711038330132760208)


class TestToSecond:

    def test_case_single_input(self):
        assert to_seconds(int(1e9)) == 1.0
        assert to_seconds(int(1e8)) == 0.1
        assert isinstance(to_seconds(1711038330132760208), float)
        assert to_seconds(1711038330132760208) == 1711038330.132760208

    def test_case_array_input(self):
        assert np.array_equal(
            to_seconds(np.ones(10, dtype=int) * int(1e9)), np.ones(10) * 1.0
        )
        assert np.array_equal(
            to_seconds(np.ones(10, dtype=int) * int(1e8)), np.ones(10) * 0.1
        )

    def test_case_wrong_input_type(self):
        with pytest.raises(TypeError) as exc_info:
            to_seconds(1e9)

        with pytest.raises(TypeError) as exc_info:
            to_seconds(np.ones(10, dtype=float) * 1711038330132760208)


class TestComputeDeltaTimestamp:

    def test_case_default(self):
        t_time_space = np.arange(100) * 100000000  # Mock timestamp with uniform delta
        t_time_space += 1711038330  # Make trajectory timestamp start at arbitrary time
        t_dt_space = np.ones(99) * 100000000  # Expected delta
        delta_time = compute_delta_timestamp(t_time_space, prepend_zero=False)
        assert np.array_equal(delta_time, t_dt_space)

    def test_case_prepend_zero(self):
        t_time_space = np.arange(100) * 100000000  # Mock timestamp with uniform delta
        t_time_space += 1711038330  # Make trajectory timestamp start at arbitrary time
        t_dt_space = np.ones(100) * 100000000  # Expected delta
        t_dt_space[0] = 0  # Delta array first element should be 0
        delta_time = compute_delta_timestamp(t_time_space)
        assert np.array_equal(delta_time, t_dt_space)
