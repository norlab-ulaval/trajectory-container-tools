# coding=utf-8
import numpy as np
import pytest
from rclpy.time import Time as ROSTime

from trajectory_container_tools.temporal.timestamps import (
    TimestampCausalOrderingError,
    Timestamps,
    compute_delta_timestamp,
    to_seconds,
    validate_timestamps_ordering,
    to_seconds_nanoseconds,
)


@pytest.fixture
def setup_mock_timestamps() -> np.ndarray:
    mock_timestamps = [
        1711038330346603696,
        1711038330351773872,
        1711038330362038128,
        1711038330376558992,
        1711038330381711344,
        1711038330391960208,
        1711038330406476944,
        1711038330411627056,
        1711038330421882896,
        1711038330436485488,
    ]

    return np.array(mock_timestamps)


@pytest.fixture
def setup_Timestamps_object(setup_mock_timestamps) -> Timestamps:
    return Timestamps(setup_mock_timestamps)


@pytest.fixture
def setup_mock_ros_timestamps():
    mock_timestamps = [
        1711038330346603696,
        1711038330351773872,
        1711038330362038128,
        1711038330376558992,
        1711038330381711344,
        1711038330391960208,
        1711038330406476944,
        1711038330411627056,
        1711038330421882896,
        1711038330436485488,
    ]

    mock_timestamps = [ROSTime(nanoseconds=each) for each in mock_timestamps]

    mock_container = {
        "feature_name": "/mock_topic",
        "timestamps": np.array(mock_timestamps),
    }

    return mock_container


class TestTimestamps:
    def test_instanciation(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        print(ts)

        assert isinstance(ts.stamps, np.ndarray)
        assert isinstance(ts.delta_stamps, np.ndarray)

    def test_instanciation_pre_condition_check(self, setup_mock_timestamps):
        # Case input array is empty
        with pytest.raises(ValueError) as exc_info:
            ts = Timestamps(stamps=np.array([]))

        print(f"{exc_info=}")
        assert exc_info.value.args == ("[TCT error] stamps array is empty!",)

        # Case input array as negative value
        mock_ts_array = setup_mock_timestamps
        mock_ts_array[1] = -mock_ts_array[1]

        with pytest.raises(ValueError) as exc_info:
            ts = Timestamps(stamps=mock_ts_array)

        print(f"{exc_info=}")
        assert exc_info.value.args == ("[TCT error] stamps must be positive values",)

    def test_stamps_property_getter(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        assert np.allclose(ts.stamps, mock_ts_array)

    def test_delta_stamps_property_getter(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        assert ts.delta_stamps.size == mock_ts_array.size

    def test_stamps_shape(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        assert ts.shape, mock_ts_array.shape

    def test_len(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        assert len(ts) == len(mock_ts_array)

    def test_indexing(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        # Case individual key
        assert ts[0].stamps == mock_ts_array[0]
        assert ts[-1].stamps == mock_ts_array[-1]

        # Case slicing
        assert np.allclose(ts[0:2].stamps, mock_ts_array[0:2])

    def test_iterator(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        for idx, value in enumerate(ts):
            assert value.stamps == mock_ts_array[idx]

    def test_seconds_nanoseconds(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        # Case individual key
        assert ts.seconds_nanoseconds(0) == to_seconds_nanoseconds(mock_ts_array[0])

    def test_causal_ordering_sanity_check(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps

        # Case pass
        assert Timestamps(stamps=mock_ts_array).causal_ordering_sanity_check() == []

        # Case expect failure
        mock_ts_array[5] = 1711038330132760208
        mock_ts_array[9] = 1711038330177285488

        with pytest.raises(TimestampCausalOrderingError) as exc_info:
            assert Timestamps(stamps=mock_ts_array).causal_ordering_sanity_check() == [
                5,
                9,
            ]


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

    def test_to_seconds(self):

        assert to_seconds(int(1e9)) == 1.0
        assert to_seconds(int(1e8)) == 0.1
        assert to_seconds(1711038330132760208) == 1711038330.132760208

    def test_compute_delta_timestamp(self):
        t_time_space = np.arange(100) * 100000000  # Mock timestamp with uniform delta
        t_time_space += 1711038330  # Make trajectory timestamp start at arbitrary time
        t_dt_space = np.ones(100) * 100000000  # Expected delta
        t_dt_space[0] = 0  # Delta array first element should be 0
        delta_time = compute_delta_timestamp(t_time_space)
        assert delta_time == pytest.approx(t_dt_space)
