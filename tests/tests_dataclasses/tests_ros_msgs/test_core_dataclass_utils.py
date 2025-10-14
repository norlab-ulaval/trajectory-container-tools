# coding=utf-8
from typing import NamedTuple

import numpy as np
import pytest

from trajectory_container_tools.dataclasses.ros_msgs.core_dataclass_utils import (
    get_timestamps_slice,
)
from trajectory_container_tools.temporal import Timestamps
from trajectory_container_tools.temporal.timestamps import TimestampOutOfBoundError


class ExpectedInterval(NamedTuple):
    start: int
    end: int


class TestGetTimestampsSlice:

    @pytest.mark.parametrize(
        argnames="t_start, t_stop, t_startpoint, t_endpoint, t_resolve_out_of_bounds, t_expected",
        argvalues=[
            (10, 100, True, True, True, ExpectedInterval(10, 100)),
            (10, 100, False, False, True, ExpectedInterval(20, 90)),
            (15, 95, True, True, True, ExpectedInterval(20, 90)),
            (15, 95, False, False, True, ExpectedInterval(20, 90)),
            (5, 105, True, False, False, None),
            (5, 105, False, True, False, None),
            (5, 105, False, False, True, ExpectedInterval(10, 100)),
        ],
        ids=[
            "start=10, stop=100, startpoint=True, endpoint=True, resolve-OOB=True, expect [10:100]",
            "start=10, stop=100, startpoint=False, endpoint=False, resolve-OOB=True, expect [20:90]",
            "start=15, stop=95, startpoint=True, endpoint=True, resolve-OOB=True, expect [20:90]",
            "start=15, stop=95, startpoint=False, endpoint=False, resolve-OOB=True, expect [20:90]",
            "start=5, stop=105, startpoint=True, endpoint=False, resolve-OOB=False, expect error",
            "start=5, stop=105, startpoint=False, endpoint=True, resolve-OOB=False, expect error",
            "start=5, stop=105, startpoint=False, endpoint=False, resolve-OOB=True, expect [10:100]",
        ],
    )
    def test_beaviour(
        self,
        setup_simple_stamps,
        t_start,
        t_stop,
        t_startpoint,
        t_endpoint,
        t_resolve_out_of_bounds,
        t_expected,
    ):
        t_timestamps = Timestamps(setup_simple_stamps)

        if t_resolve_out_of_bounds:
            t_slice = get_timestamps_slice(
                timestamps=t_timestamps,
                start=t_start,
                stop=t_stop,
                startpoint=t_startpoint,
                endpoint=t_endpoint,
                resolve_out_of_bounds=t_resolve_out_of_bounds,
            )
            print(t_timestamps)
            print(f"{t_slice=}")
            assert setup_simple_stamps[t_slice][0] == t_expected.start
            assert setup_simple_stamps[t_slice][-1] == t_expected.end
        else:
            with pytest.raises(TimestampOutOfBoundError) as exc_info:
                get_timestamps_slice(
                    timestamps=t_timestamps,
                    start=t_start,
                    stop=t_stop,
                    startpoint=t_startpoint,
                    endpoint=t_endpoint,
                    resolve_out_of_bounds=t_resolve_out_of_bounds,
                )

            print(f"{exc_info=}")
            if not t_startpoint:
                assert (
                    f"timestamps={t_start} is out of stamps bounds"
                    in exc_info.value.args[0]
                )
            if not t_endpoint:
                assert (
                    f"timestamps={t_stop} is out of stamps bounds"
                    in exc_info.value.args[0]
                )

    def test_case_single_stamp(self, setup_mock_timestamps):

        t_start_idx = 1
        t_start = int(setup_mock_timestamps[t_start_idx])

        t_slice = get_timestamps_slice(
            timestamps=Timestamps(setup_mock_timestamps), start=t_start
        )

        assert t_slice.start == t_start_idx
        assert t_slice.stop == t_start_idx + 1

        assert setup_mock_timestamps[t_slice] == t_start

    def test_case_interval(self, setup_mock_timestamps):

        t_start_idx = 1
        t_stop_idx = 4
        t_slice = get_timestamps_slice(
            timestamps=Timestamps(setup_mock_timestamps),
            start=int(setup_mock_timestamps[t_start_idx]),
            stop=int(setup_mock_timestamps[t_stop_idx]),
        )

        assert t_slice.start == t_start_idx
        assert t_slice.stop == t_stop_idx

        assert setup_mock_timestamps[t_slice][0] == int(
            setup_mock_timestamps[t_start_idx]
        )
        assert setup_mock_timestamps[t_slice][-1] == int(
            setup_mock_timestamps[t_stop_idx - 1]
        )
        print(t_slice)

    def test_case_resolve_upper_out_of_bound_interval(self, setup_mock_timestamps):

        t_start_idx = len(setup_mock_timestamps) - 1
        t_slice = get_timestamps_slice(
            timestamps=Timestamps(setup_mock_timestamps),
            start=int(setup_mock_timestamps[t_start_idx]),
            stop=int(setup_mock_timestamps[t_start_idx] + 300),
            startpoint=True,
            endpoint=True,
            resolve_out_of_bounds=True,
        )

        assert t_slice.start == t_start_idx
        assert t_slice.stop == t_start_idx + 1

        assert setup_mock_timestamps[t_slice][0] == int(
            setup_mock_timestamps[t_start_idx]
        )
        assert setup_mock_timestamps[t_slice][-1] == int(
            setup_mock_timestamps[t_start_idx]
        )
        print(t_slice)

    def test_case_resolve_lower_out_of_bound_interval(self, setup_mock_timestamps):

        t_start_idx = 0
        t_slice = get_timestamps_slice(
            timestamps=Timestamps(setup_mock_timestamps),
            start=int(setup_mock_timestamps[t_start_idx] - 300),
            stop=int(setup_mock_timestamps[t_start_idx]),
            startpoint=True,
            endpoint=True,
            resolve_out_of_bounds=True,
        )

        assert t_slice.start == t_start_idx
        assert t_slice.stop == t_start_idx + 1

        assert setup_mock_timestamps[t_slice][0] == int(
            setup_mock_timestamps[t_start_idx]
        )
        assert setup_mock_timestamps[t_slice][-1] == int(
            setup_mock_timestamps[t_start_idx]
        )
        print(t_slice)

    def test_case_start_and_stop_stamps_are_smaller_than_next_stamp(
        self, setup_mock_timestamps
    ):
        # Test case: previous_stamp <= start < next_stamp and start < stop < next_stamp

        t_start_idx = 1
        t_start = int(setup_mock_timestamps[t_start_idx])
        t_stop = int(setup_mock_timestamps[t_start_idx] + 300)
        t_next_stamp = int(setup_mock_timestamps[t_start_idx + 1])
        assert t_start < t_stop < t_next_stamp, "failed test setup sanity check"

        t_slice = get_timestamps_slice(
            timestamps=Timestamps(setup_mock_timestamps),
            start=t_start,
            stop=t_stop,
            startpoint=True,
            endpoint=True,
        )

        assert t_slice.start == 1
        assert t_slice.stop == 2

        assert setup_mock_timestamps[t_slice][0] == int(
            setup_mock_timestamps[t_start_idx]
        )
        assert setup_mock_timestamps[t_slice][-1] == int(
            setup_mock_timestamps[t_start_idx]
        )
        print(t_slice)

    @pytest.mark.parametrize(
        argnames="t_startpoint, t_endpoint",
        argvalues=[(True, False), (False, True), (True, True), (False, False)],
        ids=[
            "startpoint=True, endpoint=False",
            "startpoint=False, endpoint=True",
            "startpoint=True, endpoint=True",
            "startpoint=False, endpoint=False",
        ],
    )
    def test_case_start_and_end_points(
        self, setup_mock_timestamps, t_startpoint, t_endpoint
    ):

        t_start_idx = 0
        t_stop_idx = 4
        t_slice = get_timestamps_slice(
            timestamps=Timestamps(setup_mock_timestamps),
            start=int(setup_mock_timestamps[t_start_idx]),
            stop=int(setup_mock_timestamps[t_stop_idx]),
            startpoint=t_startpoint,
            endpoint=t_endpoint,
            resolve_out_of_bounds=True,
        )

        print(t_slice)

        assert t_slice.start == t_start_idx + int(not t_startpoint)
        assert t_slice.stop == t_stop_idx + 1 - int(not t_endpoint)

        assert np.array_equal(
            setup_mock_timestamps[t_slice],
            setup_mock_timestamps[
                slice(
                    t_start_idx + int(not t_startpoint),
                    t_stop_idx + 1 - int(not t_endpoint),
                )
            ],
        )
