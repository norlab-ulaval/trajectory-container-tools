# coding=utf-8
import numpy as np
import pytest

from trajectory_container_tools.temporal.timestamps import (
    TimestampCausalOrderingError,
    Timestamps,
    to_seconds_nanoseconds,
)


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


