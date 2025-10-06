# coding=utf-8
from dataclasses import dataclass

import pytest

import numpy as np

from trajectory_container_tools.dataclasses import (
    Header,
    NestedRosStampedDataclass,
    RosDataclass,
    RosStampedDataclass,
)
from trajectory_container_tools.dataclasses.ros_msgs.core_dataclass import (
    get_timestamps_slice,
)
from trajectory_container_tools.temporal import Timestamps


@dataclass()
class MockSubRosStampedDataclass(RosStampedDataclass):
    mock_attribute: np.ndarray


@dataclass()
class MockSubNestedRosStampedDataclass(NestedRosStampedDataclass):
    mock_attribute: np.ndarray


@dataclass()
class MockSubRosDataclass(RosDataclass):
    mock_attribute: np.ndarray


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


# ==== Dataclasses ================================================================================


class TestRosStampedDataclass:

    @pytest.fixture(scope="function")
    def setup_mock_dataclass(self, setup_mock_timestamps):
        t_mock_attribute = np.arange(setup_mock_timestamps.size)

        t_container = MockSubRosStampedDataclass(
            feature_name="mock",
            header=Header(
                frame_id="mock_frame_id",
                timestamps=setup_mock_timestamps,
            ),
            mock_attribute=t_mock_attribute,
        )
        return t_container, t_mock_attribute

    def test_instanciation(self, setup_mock_dataclass, setup_mock_timestamps):
        t_container, t_mock_attribute = setup_mock_dataclass

        assert t_container.feature_name == "mock"
        assert np.array_equal(
            t_container.header.timestamps.stamps, setup_mock_timestamps
        )
        assert np.array_equal(t_container.mock_attribute, t_mock_attribute)
        # print(t_container)

    def test_get_timestamp_case_single_stamp(
        self, setup_mock_dataclass, setup_mock_timestamps
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_start_idx = 1
        t_start = int(setup_mock_timestamps[t_start_idx])

        t_container_interval = t_container.get_timestamps(start=t_start)

        assert t_container_interval.header.timestamps.stamps == t_start
        assert t_container_interval.mock_attribute == t_mock_attribute[t_start_idx]
        print(t_container_interval)

    def test_get_timestamp_case_interval(
        self, setup_mock_dataclass, setup_mock_timestamps
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_start_idx = 1
        t_stop_idx = 4
        t_container_interval = t_container.get_timestamps(
            start=(int(setup_mock_timestamps[t_start_idx])),
            stop=(int(setup_mock_timestamps[t_stop_idx])),
        )

        assert t_container_interval.header.timestamps.stamps[0] == int(
            setup_mock_timestamps[t_start_idx]
        )
        assert t_container_interval.header.timestamps.stamps[-1] == int(
            setup_mock_timestamps[t_stop_idx - 1]
        )
        assert np.array_equal(
            t_container_interval.mock_attribute,
            t_mock_attribute[slice(t_start_idx, t_stop_idx)],
        )
        print(t_container_interval)

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
    def test_get_timestamp_case_endpoint(
        self, setup_mock_dataclass, setup_mock_timestamps, t_startpoint, t_endpoint
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_start_idx = 0
        t_stop_idx = 4
        t_container_interval = t_container.get_timestamps(
            start=int(setup_mock_timestamps[t_start_idx]),
            stop=int(setup_mock_timestamps[t_stop_idx]),
            startpoint=t_startpoint,
            endpoint=t_endpoint,
        )

        print(t_container_interval)

        assert np.array_equal(
            t_container_interval.header.timestamps.stamps,
            setup_mock_timestamps[
                slice(t_start_idx + int(not t_startpoint), t_stop_idx + int(t_endpoint))
            ],
        )
        assert np.array_equal(
            t_container_interval.mock_attribute,
            t_mock_attribute[
                slice(t_start_idx + int(not t_startpoint), t_stop_idx + int(t_endpoint))
            ],
        )


class TestNestedRosStampedDataclass:
    def test_instanciation(self):

        t_container = MockSubNestedRosStampedDataclass(
            header=Header(
                frame_id="mock_frame_id",
                timestamps=np.arange(10),
            ),
            mock_attribute=np.ones(10),
        )
        assert t_container.feature_name is None
        assert t_container._nested == True
        assert np.array_equal(t_container.header.timestamps.stamps, np.arange(10))
        assert np.array_equal(t_container.mock_attribute, np.ones(10))

        with pytest.raises(TypeError) as exc_info:
            # The 'feature_name' parameter should not exist
            t_container = MockSubNestedRosStampedDataclass(
                feature_name="mock",
                header=Header(
                    frame_id="mock_frame_id",
                    timestamps=np.arange(10),
                ),
                mock_attribute=np.ones(10),
            )


class TestRosDataclass:

    def test_instanciation(self):

        t_container = MockSubRosDataclass(
            feature_name="mock", mock_attribute=np.ones(10)
        )

        assert t_container.feature_name == "mock"
        assert np.array_equal(t_container.mock_attribute, np.ones(10))

        with pytest.raises(AttributeError) as exc_info:
            # The 'timestamps' attribute should not exist
            assert t_container.__getattribute__("header")
