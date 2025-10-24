# coding=utf-8
import numpy as np
import pytest

from trajectory_container_tools.temporal.timestamps import (
    TimestampCausalOrderingError,
    TimestampMissingError,
    TimestampOutOfBoundError,
    Timestamps,
)
from trajectory_container_tools.temporal import to_seconds_nanoseconds


class TestTimestampsCore:
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

    def test_str_representation(self, setup_mock_timestamps):
        # Test string representation
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        print(ts)

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

    def test_is_timestamps_in_bounds(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        # Case pass
        assert ts.is_timestamps_in_bounds(int(mock_ts_array[0])) == True
        assert ts.is_timestamps_in_bounds(mock_ts_array[0]) == True
        assert ts.is_timestamps_in_bounds(mock_ts_array[0:6]) == True
        assert ts.is_timestamps_in_bounds(mock_ts_array[0:6].tolist()) == True
        assert ts.is_timestamps_in_bounds(mock_ts_array) == True

        # Case not in bound
        mock_ts_array[5] = 1711038330132760208
        mock_ts_array[9] = 1711038330177285488

        assert ts.is_timestamps_in_bounds(int(mock_ts_array[5])) == False
        assert ts.is_timestamps_in_bounds(mock_ts_array[5]) == False
        assert ts.is_timestamps_in_bounds(mock_ts_array[0:6]) == False
        assert ts.is_timestamps_in_bounds(mock_ts_array[0:6].tolist()) == False
        assert ts.is_timestamps_in_bounds(mock_ts_array) == False

    def test_min_and_max_methods(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        assert ts.min() == mock_ts_array[0]
        assert ts.max() == mock_ts_array[-1]

    def test_seconds_nanoseconds(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        # Case individual key
        assert ts.seconds_nanoseconds(0) == to_seconds_nanoseconds(mock_ts_array[0])

    def test_empty(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        # print(ts)
        ts_empty = ts.empty()

        assert np.array_equal(ts_empty.stamps, np.array([], dtype=np.int64))
        assert np.array_equal(ts_empty.delta_stamps, np.array([], dtype=np.int64))
        assert len(ts_empty) == 0


class TestTimestampsIterableMethods:

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

    def test_contains_case_input_single_value(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        t_timestamp_in: int = mock_ts_array[0]
        t_timestamp_not_in = 1711038330290158992

        # sanity check
        assert not np.all(t_timestamp_not_in == mock_ts_array)

        # test casses
        assert t_timestamp_in in ts
        assert t_timestamp_not_in not in ts

    def test_contains_case_input_list(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        t_timestamp_in = mock_ts_array[0:2].tolist()
        t_timestamp_not_in = [1711038330290158992, 1711038330462958992]

        # sanity check
        assert not np.all(t_timestamp_not_in[0] == mock_ts_array)
        assert not np.all(t_timestamp_not_in[1] == mock_ts_array)

        # test casses
        assert t_timestamp_in in ts
        assert t_timestamp_not_in not in ts

    def test_contains_case_input_array(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        t_timestamp_in = mock_ts_array[0:2]
        t_timestamp_not_in = np.array([1711038330290158992, 1711038330462958992])

        # sanity check
        assert not np.all(t_timestamp_not_in[0] == mock_ts_array)
        assert not np.all(t_timestamp_not_in[1] == mock_ts_array)

        # test casses
        assert t_timestamp_in in ts
        assert t_timestamp_not_in not in ts


class TestTimestampsGetIndexesMethod:
    def test_get_indexes_case_input_single_stamp(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        # print(ts)
        for idx, each_stamp in enumerate(mock_ts_array):
            print(f"idx: {idx}, each_stamp: {each_stamp}")
            assert isinstance(ts.get_indexes(each_stamp), int)
            assert ts.get_indexes(each_stamp) == idx

    def test_get_indexes_case_input_array_or_list(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        # print(ts)

        # Case input is numpy array or stamp
        t_output = ts.get_indexes(mock_ts_array[0:3])
        assert isinstance(t_output, list)
        assert isinstance(t_output[0], int)
        assert t_output == [0, 1, 2]

        # Case input is list of stamp
        t_output = ts.get_indexes(mock_ts_array[0:3].tolist())
        assert isinstance(t_output, list)
        assert isinstance(t_output[0], int)
        assert t_output == [0, 1, 2]

    def test_get_indexes_case_stamp_not_in_storage(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        # print(ts)
        t_timestamp_not_in = mock_ts_array[5] + 300
        t_timestamp_out_of_bound = mock_ts_array[-1] + 300

        # .... Case: is not in stamps .............................................................
        with pytest.raises(TimestampMissingError) as exc_info:
            ts.get_indexes(t_timestamp_not_in)

        # print(f"{exc_info=}")
        assert "is not in stamps" in exc_info.value.args[0]

        # .... Case: out of bound .................................................................
        with pytest.raises(TimestampOutOfBoundError) as exc_info:
            ts.get_indexes(t_timestamp_out_of_bound)

        # print(f"{exc_info=}")
        assert "is out of stamps bounds" in exc_info.value.args[0]


class TestTimestampsGetNearestMethodsPastAndFutur:
    def test_get_nearest_futur_stamp_case_input_stamp_exist(
        self, setup_mock_timestamps
    ):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        assert ts.get_nearest_futur_stamp(mock_ts_array[0]) == mock_ts_array[1]

    # .... Get nearest futur stamp ................................................................
    def test_get_nearest_futur_stamp_case_input_stamp_not_exist(
        self, setup_mock_timestamps
    ):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        t_timestamp_in = 1711038330346603696  # the one at index 0
        t_timestamp_not_in = t_timestamp_in + 300

        # sanity check
        assert t_timestamp_in == mock_ts_array[0]
        assert not np.all(t_timestamp_not_in == mock_ts_array)
        assert mock_ts_array[0] < t_timestamp_not_in
        assert t_timestamp_not_in < mock_ts_array[1]

        assert ts.get_nearest_futur_stamp(t_timestamp_not_in) == mock_ts_array[1]

    def test_get_nearest_futur_stamp_case_input_stamp_out_of_bound(
        self, setup_mock_timestamps
    ):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        t_timestamp_in = 1711038330436485488  # the one at index -1
        t_timestamp_not_in = t_timestamp_in + 300

        # sanity check
        assert t_timestamp_in == mock_ts_array[-1]
        assert not np.all(t_timestamp_not_in == mock_ts_array)
        assert mock_ts_array[-1] < t_timestamp_not_in

        with pytest.raises(IndexError) as exc_info:
            ts.get_nearest_futur_stamp(t_timestamp_not_in)

        print(f"{exc_info=}")
        assert exc_info.value.args == (
            f"timestamp={t_timestamp_not_in} as no nearest futur candidat stamp in Timestamps object",
        )

    # .... Get nearest past stamp .................................................................
    def test_get_nearest_past_stamp_case_input_stamp_exist(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        assert ts.get_nearest_past_stamp(int(mock_ts_array[9])) == mock_ts_array[8]

    def test_get_nearest_past_stamp_case_input_stamp_not_exist(
        self, setup_mock_timestamps
    ):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        t_timestamp_in = 1711038330346603696  # the one at index 0
        t_timestamp_not_in = t_timestamp_in + 300

        # sanity check
        assert t_timestamp_in == mock_ts_array[0]
        assert not np.all(t_timestamp_not_in == mock_ts_array)
        assert mock_ts_array[0] < t_timestamp_not_in
        assert t_timestamp_not_in < mock_ts_array[1]

        assert ts.get_nearest_past_stamp(t_timestamp_not_in) == mock_ts_array[0]

    def test_get_nearest_past_stamp_case_input_stamp_out_of_bound(
        self, setup_mock_timestamps
    ):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)
        t_timestamp_in = 1711038330346603696  # the one at index 0
        t_timestamp_not_in = t_timestamp_in - 300

        # sanity check
        assert t_timestamp_in == mock_ts_array[0]
        assert not np.all(t_timestamp_not_in == mock_ts_array)
        assert t_timestamp_not_in < mock_ts_array[0]

        with pytest.raises(IndexError) as exc_info:
            ts.get_nearest_past_stamp(t_timestamp_not_in)

        print(f"{exc_info=}")
        assert exc_info.value.args == (
            f"timestamp={t_timestamp_not_in} as no nearest past candidat stamp in Timestamps object",
        )


@pytest.mark.parametrize(
    argnames="t_future", argvalues=[True, False], ids=["future=True", "future=False"]
)
class TestTimestampsGetNearestMethods:

    @pytest.mark.parametrize(
        argnames="t_include",
        argvalues=[True, False],
        ids=["include=True", "include=False"],
    )
    def test_get_nearest_stamp_case_stamp_in_bound(
        self, setup_mock_timestamps, t_include, t_future
    ):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        if t_include:
            t_expected = mock_ts_array[1]
        elif not t_future:
            t_expected = mock_ts_array[0]
        else:
            t_expected = mock_ts_array[2]

        assert (ts.get_nearest_stamp(int(mock_ts_array[1]), future=t_future, include=t_include) == t_expected)

    def test_get_nearest_stamp_case_stamp_at_bound_limit(
        self, setup_mock_timestamps, t_future
    ):
        mock_ts_array = setup_mock_timestamps
        ts = Timestamps(stamps=mock_ts_array)

        if t_future:
            t_idx_bound = -1
        else:
            t_idx_bound = 0

        assert (
            ts.get_nearest_stamp(int(mock_ts_array[t_idx_bound]), future=t_future, include=True)
            == mock_ts_array[t_idx_bound]
        )
        with pytest.raises(IndexError) as exc_info:
            ts.get_nearest_stamp(int(mock_ts_array[t_idx_bound]), future=t_future, include=False)
