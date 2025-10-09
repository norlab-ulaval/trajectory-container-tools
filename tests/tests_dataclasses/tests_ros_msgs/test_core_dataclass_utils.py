# coding=utf-8
import numpy as np
import pytest

from trajectory_container_tools.dataclasses.ros_msgs.core_dataclass_utils import (
    get_timestamps_slice,
)
from trajectory_container_tools.temporal import Timestamps


class TestGetTimestampsSlice:

    def test_case_single_stamp(self, setup_mock_timestamps):

        t_start_idx = 1
        t_start = int(setup_mock_timestamps[t_start_idx])

        t_slice = get_timestamps_slice(
            timestamps=Timestamps(setup_mock_timestamps), start=t_start
        )

        assert setup_mock_timestamps[t_slice] == t_start

    def test_case_interval(self, setup_mock_timestamps):

        t_start_idx = 1
        t_stop_idx = 4
        t_slice = get_timestamps_slice(
            timestamps=Timestamps(setup_mock_timestamps),
            start=(int(setup_mock_timestamps[t_start_idx])),
            stop=(int(setup_mock_timestamps[t_stop_idx])),
        )

        assert setup_mock_timestamps[t_slice][0] == int(
            setup_mock_timestamps[t_start_idx]
        )
        assert setup_mock_timestamps[t_slice][-1] == int(
            setup_mock_timestamps[t_stop_idx - 1]
        )
        print(t_slice)

    def test_case_out_of_bound_interval(self, setup_mock_timestamps):

        t_start_idx = len(setup_mock_timestamps) - 1
        t_slice = get_timestamps_slice(
            timestamps=Timestamps(setup_mock_timestamps),
            start=(int(setup_mock_timestamps[t_start_idx])),
            stop=(int(setup_mock_timestamps[t_start_idx] + 300)),
        )

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
        )

        print(t_slice)

        assert np.array_equal(
            setup_mock_timestamps[t_slice],
            setup_mock_timestamps[
                slice(t_start_idx + int(not t_startpoint), t_stop_idx + int(t_endpoint))
            ],
        )
