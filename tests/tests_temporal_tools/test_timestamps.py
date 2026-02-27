# coding=utf-8
import numpy as np
import pytest

from trajectory_container_tools.temporal.timestamps import (
    TimestampCausalOrderingError,
    TimestampMissingError,
    TimestampOutOfBoundError,
    Timestamps,
    TimestampsInt,
    TimestampsFloat,
    create_timestamps,
)
from trajectory_container_tools.temporal import to_seconds_nanoseconds
from trajectory_container_tools.temporal.trajectory_timestamps_metadata import (
    RateMetric,
)


class TestTimestampsIntCore:
    def test_instanciation(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)

        assert isinstance(ts.stamps, np.ndarray)
        assert isinstance(ts.delta_stamps, np.ndarray)

    def test_instanciation_pre_condition_check(self, setup_mock_timestamps):
        # Case input array is empty
        with pytest.raises(ValueError) as exc_info:
            ts = TimestampsInt(stamps=np.array([]))

        print(f"{exc_info=}")
        assert exc_info.value.args == ("[TCT error] stamps array is empty!",)

        # Case input array as negative value
        mock_ts_array = setup_mock_timestamps
        mock_ts_array[1] = -mock_ts_array[1]

        with pytest.raises(ValueError) as exc_info:
            ts = TimestampsInt(stamps=mock_ts_array)

        print(f"{exc_info=}")
        assert exc_info.value.args == ("[TCT error] stamps must be positive values",)

    def test_stamps_property_getter(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)

        assert np.allclose(ts.stamps, mock_ts_array)

    def test_delta_stamps_property_getter(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)

        assert ts.delta_stamps.size == mock_ts_array.size

    def test_stamps_shape(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)

        assert ts.shape, mock_ts_array.shape

    def test_len(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)
        assert len(ts) == len(mock_ts_array)

    def test_str_representation(self, setup_mock_timestamps):
        # Test string representation
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)
        print(ts)

        ts = TimestampsInt(stamps=mock_ts_array, single_source=False)
        print(ts)

    def test_causal_ordering_sanity_check(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps

        # Case pass
        assert TimestampsInt(stamps=mock_ts_array).causal_ordering_sanity_check() == []

        # Case expect failure
        mock_ts_array[5] = 1711038330132760208
        mock_ts_array[9] = 1711038330177285488

        with pytest.raises(TimestampCausalOrderingError) as exc_info:
            assert TimestampsInt(stamps=mock_ts_array).causal_ordering_sanity_check() == [
                5,
                9,
            ]

        assert TimestampsInt(stamps=mock_ts_array).causal_ordering_sanity_check(
            fail_causal_ordering_violation=False
        ) == [5, 9]

    def test_compute_frequency_metric(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps

        t_rate_metric = TimestampsInt(stamps=mock_ts_array).compute_frequency_metric()

        assert t_rate_metric.min_hz <= t_rate_metric.max_hz
        assert t_rate_metric.min_hz <= t_rate_metric.mean_hz <= t_rate_metric.max_hz

        # Case pass
        assert isinstance(t_rate_metric, RateMetric)
        print(t_rate_metric)

        with pytest.raises(ValueError) as exc_info:
            TimestampsInt(
                stamps=mock_ts_array, single_source=False
            ).compute_frequency_metric()

        print(f"{exc_info=}")
        # assert exc_info.value.args == ('<The error message>',)

    def test_is_timestamps_in_bounds(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)

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
        ts = TimestampsInt(stamps=mock_ts_array)

        assert ts.min() == mock_ts_array[0]
        assert ts.max() == mock_ts_array[-1]

    def test_seconds_nanoseconds(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)

        # Case individual key
        assert ts.seconds_nanoseconds(0) == to_seconds_nanoseconds(mock_ts_array[0])

    def test_empty(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)
        # print(ts)
        ts_empty = ts.empty()

        assert np.array_equal(ts_empty.stamps, np.array([], dtype=np.int64))
        assert np.array_equal(ts_empty.delta_stamps, np.array([], dtype=np.int64))
        assert len(ts_empty) == 0


class TestTimestampsIterableMethods:

    def test_indexing(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)

        # Case individual key
        assert ts[0].stamps == mock_ts_array[0]
        assert ts[-1].stamps == mock_ts_array[-1]

        # Case slicing
        assert np.allclose(ts[0:2].stamps, mock_ts_array[0:2])

    def test_iterator(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)

        for idx, value in enumerate(ts):
            assert value.stamps == mock_ts_array[idx]

    def test_contains_case_input_single_value(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)
        t_timestamp_in: int = mock_ts_array[0]
        t_timestamp_not_in = 1711038330290158992

        # sanity check
        assert not np.all(t_timestamp_not_in == mock_ts_array)

        # test casses
        assert t_timestamp_in in ts
        assert t_timestamp_not_in not in ts

    def test_contains_case_input_list(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)
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
        ts = TimestampsInt(stamps=mock_ts_array)
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
        ts = TimestampsInt(stamps=mock_ts_array)
        # print(ts)
        for idx, each_stamp in enumerate(mock_ts_array):
            print(f"idx: {idx}, each_stamp: {each_stamp}")
            assert isinstance(ts.get_indexes(each_stamp), int)
            assert ts.get_indexes(each_stamp) == idx

    def test_get_indexes_case_input_array_or_list(self, setup_mock_timestamps):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)
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
        ts = TimestampsInt(stamps=mock_ts_array)
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
        ts = TimestampsInt(stamps=mock_ts_array)
        assert ts.get_nearest_futur_stamp(mock_ts_array[0]) == mock_ts_array[1]

    # .... Get nearest futur stamp ................................................................
    def test_get_nearest_futur_stamp_case_input_stamp_not_exist(
        self, setup_mock_timestamps
    ):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)
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
        ts = TimestampsInt(stamps=mock_ts_array)
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
        ts = TimestampsInt(stamps=mock_ts_array)
        assert ts.get_nearest_past_stamp(int(mock_ts_array[9])) == mock_ts_array[8]

    def test_get_nearest_past_stamp_case_input_stamp_not_exist(
        self, setup_mock_timestamps
    ):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)
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
        ts = TimestampsInt(stamps=mock_ts_array)
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
        ts = TimestampsInt(stamps=mock_ts_array)

        if t_include:
            t_expected = mock_ts_array[1]
        elif not t_future:
            t_expected = mock_ts_array[0]
        else:
            t_expected = mock_ts_array[2]

        assert (
            ts.get_nearest_stamp(
                int(mock_ts_array[1]), future=t_future, include=t_include
            )
            == t_expected
        )

    def test_get_nearest_stamp_case_stamp_at_bound_limit(
        self, setup_mock_timestamps, t_future
    ):
        mock_ts_array = setup_mock_timestamps
        ts = TimestampsInt(stamps=mock_ts_array)

        if t_future:
            t_idx_bound = -1
        else:
            t_idx_bound = 0

        assert (
            ts.get_nearest_stamp(
                int(mock_ts_array[t_idx_bound]), future=t_future, include=True
            )
            == mock_ts_array[t_idx_bound]
        )
        with pytest.raises(IndexError) as exc_info:
            ts.get_nearest_stamp(
                int(mock_ts_array[t_idx_bound]), future=t_future, include=False
            )


# =================================================================================================
# TimestampsFloat tests
# =================================================================================================
class TestTimestampsFloatCore:
    def test_instanciation(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        assert isinstance(ts.stamps, np.ndarray)
        assert isinstance(ts.delta_stamps, np.ndarray)
        assert np.issubdtype(ts.stamps.dtype, np.floating)

    def test_instanciation_from_list(self):
        stamps_list = [1.0, 2.0, 3.0, 4.0]
        ts = TimestampsFloat(stamps=stamps_list)
        assert isinstance(ts, TimestampsFloat)
        assert np.issubdtype(ts.stamps.dtype, np.floating)
        assert len(ts) == 4

    def test_instanciation_pre_condition_check(self):
        with pytest.raises(ValueError):
            TimestampsFloat(stamps=np.array([]))

        with pytest.raises(ValueError):
            TimestampsFloat(stamps=np.array([-1.0, 2.0, 3.0]))

    def test_stamps_property_getter(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        assert np.allclose(ts.stamps, setup_mock_float_timestamps)

    def test_delta_stamps_property_getter(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        assert ts.delta_stamps.size == setup_mock_float_timestamps.size

    def test_len(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        assert len(ts) == len(setup_mock_float_timestamps)

    def test_str_representation(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        ts_str = str(ts)
        assert "TimestampsFloat" in ts_str

        ts = TimestampsFloat(stamps=setup_mock_float_timestamps, single_source=False)
        ts_str = str(ts)
        assert "n.a." in ts_str

    def test_causal_ordering_sanity_check(self, setup_mock_float_timestamps):
        assert TimestampsFloat(stamps=setup_mock_float_timestamps).causal_ordering_sanity_check() == []

        bad_stamps = setup_mock_float_timestamps.copy()
        bad_stamps[5] = bad_stamps[3]
        with pytest.raises(TimestampCausalOrderingError):
            TimestampsFloat(stamps=bad_stamps).causal_ordering_sanity_check()

    def test_compute_frequency_metric(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        rate = ts.compute_frequency_metric()
        assert isinstance(rate, RateMetric)
        assert rate.min_hz <= rate.max_hz
        assert rate.min_hz <= rate.mean_hz <= rate.max_hz

        with pytest.raises(ValueError):
            TimestampsFloat(
                stamps=setup_mock_float_timestamps, single_source=False
            ).compute_frequency_metric()

    def test_min_and_max_methods(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        assert ts.min() == setup_mock_float_timestamps[0]
        assert ts.max() == setup_mock_float_timestamps[-1]

    def test_empty(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        ts_empty = ts.empty()
        assert ts_empty.stamps.size == 0
        assert ts_empty.delta_stamps.size == 0

    def test_is_timestamps_in_bounds(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        assert ts.is_timestamps_in_bounds(setup_mock_float_timestamps[0]) is True
        assert ts.is_timestamps_in_bounds(setup_mock_float_timestamps[-1]) is True
        assert ts.is_timestamps_in_bounds(0.0) is False
        assert ts.is_timestamps_in_bounds(999.0) is False

    def test_contains(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        assert setup_mock_float_timestamps[0] in ts
        assert 999.999 not in ts

    def test_get_indexes(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        idx = ts.get_indexes(setup_mock_float_timestamps[3])
        assert idx == 3

    def test_getitem(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        ts_slice = ts[2:5]
        assert len(ts_slice) == 3

    def test_iteration(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        count = 0
        for _ in ts:
            count += 1
        assert count == len(setup_mock_float_timestamps)

    def test_get_nearest_futur_stamp(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        result = ts.get_nearest_futur_stamp(setup_mock_float_timestamps[0])
        assert result == setup_mock_float_timestamps[1]

    def test_get_nearest_past_stamp(self, setup_mock_float_timestamps):
        ts = TimestampsFloat(stamps=setup_mock_float_timestamps)
        result = ts.get_nearest_past_stamp(setup_mock_float_timestamps[-1])
        assert result == setup_mock_float_timestamps[-2]


# =================================================================================================
# create_timestamps factory function tests
# =================================================================================================
class TestCreateTimestamps:

    def test_create_from_int_array(self):
        stamps = np.array([1000000000, 2000000000, 3000000000], dtype=int)
        ts = create_timestamps(stamps)
        assert isinstance(ts, TimestampsInt)

    def test_create_from_float_array(self):
        stamps = np.array([1.0, 2.0, 3.0], dtype=np.float64)
        ts = create_timestamps(stamps)
        assert isinstance(ts, TimestampsFloat)

    def test_create_from_float32_array(self):
        stamps = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        ts = create_timestamps(stamps)
        assert isinstance(ts, TimestampsFloat)

    def test_create_from_int_list(self):
        stamps = [1000000000, 2000000000, 3000000000]
        ts = create_timestamps(stamps)
        assert isinstance(ts, TimestampsInt)

    def test_create_from_float_list(self):
        stamps = [1.0, 2.0, 3.0]
        ts = create_timestamps(stamps)
        assert isinstance(ts, TimestampsFloat)

    def test_single_source_parameter(self):
        stamps = np.array([1.0, 2.0, 3.0], dtype=np.float64)
        ts = create_timestamps(stamps, single_source=False)
        assert isinstance(ts, TimestampsFloat)
        assert ts._single_source is False

    def test_isinstance_timestamps(self):
        """Both TimestampsInt and TimestampsFloat should be instances of Timestamps."""
        int_ts = TimestampsInt(stamps=np.array([1000000000, 2000000000], dtype=int))
        float_ts = TimestampsFloat(stamps=np.array([1.0, 2.0], dtype=np.float64))
        assert isinstance(int_ts, Timestamps)
        assert isinstance(float_ts, Timestamps)
