# coding=utf-8
from dataclasses import dataclass
from typing import Optional

import pytest

import numpy as np
from deprecated import deprecated

from trajectory_container_tools.dataclasses import (
    StdMsgsHeader,
    RosFeatureArray,
    RosStampedFeature,
    RosFeature,
)
from trajectory_container_tools.dataclasses.ros_msgs.core_dataclass import (
    NestedRosStampedFeature,
)


@dataclass()
class MockRosFeature(RosFeature):
    mock_attribute: np.ndarray


@dataclass()
class MockRosFeatureNestedRosFeature(RosFeature):
    mock_nested: RosFeature


@dataclass()
class MockRosStampedFeature(RosStampedFeature):
    mock_attribute: np.ndarray


@dataclass()
class MockRosFeatureArray(RosFeatureArray):
    mock_attribute: np.ndarray
    mock_array: list[RosStampedFeature]

    @property
    def registred_trajectory_object_list(self) -> Optional[str]:
        return "mock_array"


@deprecated(
    reason="NestedRosStampedFeature dataclass is deprecated now that all TrajectoryFeature dataclass "
    "support parent container reference tracking. Use `is_nested()` method to test if a "
    "trajectory dataclass is nested or not."
)
@dataclass()
class MockNestedRosStampedFeature(NestedRosStampedFeature):
    mock_attribute: np.ndarray


class TestRosFeature:

    @pytest.fixture(scope="function")
    def setup_mock_dataclass(self, setup_real_timestamps):
        t_mock_attribute = np.arange(setup_real_timestamps.size)

        t_container = MockRosFeature(
            feature_name="mock",
            bag_recorded_timestamps=setup_real_timestamps,
            mock_attribute=t_mock_attribute,
        )
        return t_container, t_mock_attribute

    def test_instanciation(self, setup_mock_dataclass, setup_real_timestamps):
        t_container, t_mock_attribute = setup_mock_dataclass

        assert t_container.feature_name == "mock"
        assert np.array_equal(
            t_container.bag_recorded_timestamps.stamps, setup_real_timestamps
        )
        assert np.array_equal(t_container.mock_attribute, t_mock_attribute)
        # print(t_container)

    @pytest.mark.parametrize(
        argnames="t_startpoint",
        argvalues=[True, False],
        ids=["startpoint=True", "startpoint=False"],
    )
    def test_get_timestamp_case_single_stamp(
        self, setup_mock_dataclass, setup_real_timestamps, t_startpoint
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_start_idx = 1
        t_start = int(setup_real_timestamps[t_start_idx])

        t_container_interval = t_container.get_timestamps(
            start=t_start, startpoint=t_startpoint
        )
        print(t_container_interval)

        assert t_container_interval.bag_recorded_timestamps.stamps.size == 1
        assert t_container_interval.bag_recorded_timestamps.stamps[0] == int(
            setup_real_timestamps[t_start_idx + int(not t_startpoint)]
        )
        assert (
            t_container_interval.mock_attribute[0]
            == t_mock_attribute[t_start_idx + int(not t_startpoint)]
        )

    def test_get_timestamp_case_interval(
        self, setup_mock_dataclass, setup_real_timestamps
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_start_idx = 1
        t_stop_idx = 4
        t_container_interval = t_container.get_timestamps(
            start=(int(setup_real_timestamps[t_start_idx])),
            stop=(int(setup_real_timestamps[t_stop_idx])),
        )

        assert t_container_interval.bag_recorded_timestamps.stamps[0] == int(
            setup_real_timestamps[t_start_idx]
        )
        assert t_container_interval.bag_recorded_timestamps.stamps[-1] == int(
            setup_real_timestamps[t_stop_idx - 1]
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
        self, setup_mock_dataclass, setup_real_timestamps, t_startpoint, t_endpoint
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_start_idx = 0
        t_stop_idx = 4
        t_container_interval = t_container.get_timestamps(
            start=int(setup_real_timestamps[t_start_idx]),
            stop=int(setup_real_timestamps[t_stop_idx]),
            startpoint=t_startpoint,
            endpoint=t_endpoint,
        )

        print(t_container_interval)

        assert np.array_equal(
            t_container_interval.bag_recorded_timestamps.stamps,
            setup_real_timestamps[
                slice(
                    t_start_idx + int(not t_startpoint),
                    t_stop_idx + 1 - int(not t_endpoint),
                )
            ],
        )
        assert np.array_equal(
            t_container_interval.mock_attribute,
            t_mock_attribute[
                slice(
                    t_start_idx + int(not t_startpoint),
                    t_stop_idx + 1 - int(not t_endpoint),
                )
            ],
        )


class TestRosFeatureCaseNoNestedBagStamps:

    @pytest.fixture(scope="function")
    def setup_mock_nested_dataclass(self, setup_real_timestamps):
        t_mock_attribute = np.arange(setup_real_timestamps.size)

        t_container = MockRosFeatureNestedRosFeature(
            bag_recorded_timestamps=setup_real_timestamps,
            mock_nested=MockRosFeature(
                bag_recorded_timestamps=None,
                feature_name="mock",
                mock_attribute=t_mock_attribute,
            ),
        )
        return t_container, t_mock_attribute

    def test_instanciation_case_no_nested_bag_stamps(
        self, setup_mock_nested_dataclass, setup_real_timestamps
    ):
        t_container, t_mock_attribute = setup_mock_nested_dataclass

        assert np.array_equal(
            t_container.bag_recorded_timestamps.stamps, setup_real_timestamps
        )
        assert t_container.mock_nested.bag_recorded_timestamps is None
        # print(t_container)

    @pytest.mark.parametrize(
        argnames="t_startpoint",
        argvalues=[True, False],
        ids=["startpoint=True", "startpoint=False"],
    )
    def test_get_timestamp_case_single_stamp(
        self, setup_mock_nested_dataclass, setup_real_timestamps, t_startpoint
    ):
        t_container, t_mock_attribute = setup_mock_nested_dataclass

        t_start_idx = 1
        t_start = int(setup_real_timestamps[t_start_idx])

        t_container_interval = t_container.get_timestamps(
            start=t_start, startpoint=t_startpoint
        )
        print(t_container_interval)

        assert t_container_interval.bag_recorded_timestamps.stamps.size == 1
        assert t_container_interval.bag_recorded_timestamps.stamps[0] == int(
            setup_real_timestamps[t_start_idx + int(not t_startpoint)]
        )
        assert (
            t_container_interval.mock_nested.mock_attribute[0]
            == t_mock_attribute[t_start_idx + int(not t_startpoint)]
        )

    def test_get_timestamp_case_interval(
        self, setup_mock_nested_dataclass, setup_real_timestamps
    ):
        t_container, t_mock_attribute = setup_mock_nested_dataclass

        t_start_idx = 1
        t_stop_idx = 4
        t_container_interval = t_container.get_timestamps(
            start=(int(setup_real_timestamps[t_start_idx])),
            stop=(int(setup_real_timestamps[t_stop_idx])),
        )

        assert t_container_interval.bag_recorded_timestamps.stamps[0] == int(
            setup_real_timestamps[t_start_idx]
        )
        assert t_container_interval.bag_recorded_timestamps.stamps[-1] == int(
            setup_real_timestamps[t_stop_idx - 1]
        )
        assert np.array_equal(
            t_container_interval.mock_nested.mock_attribute,
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
        self, setup_mock_nested_dataclass, setup_real_timestamps, t_startpoint, t_endpoint
    ):
        t_container, t_mock_attribute = setup_mock_nested_dataclass

        t_start_idx = 0
        t_stop_idx = 4
        t_container_interval = t_container.get_timestamps(
            start=int(setup_real_timestamps[t_start_idx]),
            stop=int(setup_real_timestamps[t_stop_idx]),
            startpoint=t_startpoint,
            endpoint=t_endpoint,
        )

        print(t_container_interval)

        assert np.array_equal(
            t_container_interval.bag_recorded_timestamps.stamps,
            setup_real_timestamps[
                slice(
                    t_start_idx + int(not t_startpoint),
                    t_stop_idx + 1 - int(not t_endpoint),
                )
            ],
        )
        assert np.array_equal(
            t_container_interval.mock_nested.mock_attribute,
            t_mock_attribute[
                slice(
                    t_start_idx + int(not t_startpoint),
                    t_stop_idx + 1 - int(not t_endpoint),
                )
            ],
        )


class TestRosStampedFeature:

    @pytest.fixture(scope="function")
    def setup_mock_dataclass(self, setup_real_timestamps, setup_mock_timestamps):
        t_mock_attribute = np.arange(setup_real_timestamps.size)

        t_container = MockRosStampedFeature(
            feature_name="mock",
            bag_recorded_timestamps=setup_mock_timestamps,
            header=StdMsgsHeader(
                frame_id="mock_frame_id",
                timestamps=setup_real_timestamps,
            ),
            mock_attribute=t_mock_attribute,
        )
        return t_container, t_mock_attribute

    def test_instanciation(
        self, setup_mock_dataclass, setup_real_timestamps, setup_mock_timestamps
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        assert t_container.feature_name == "mock"
        assert np.array_equal(
            t_container.header.timestamps.stamps, setup_real_timestamps
        )
        assert np.array_equal(
            t_container.bag_recorded_timestamps.stamps, setup_mock_timestamps
        )
        assert np.array_equal(t_container.mock_attribute, t_mock_attribute)
        # print(t_container)

    @pytest.mark.parametrize(
        argnames="t_startpoint",
        argvalues=[True, False],
        ids=["startpoint=True", "startpoint=False"],
    )
    @pytest.mark.parametrize(
        argnames="t_use_msg_publishing_timestamps",
        argvalues=[True, False],
        ids=[
            "t_use_msg_publishing_timestamps=True",
            "t_use_msg_publishing_timestamps=False",
        ],
    )
    def test_get_timestamp_case_single_stamp(
        self,
        setup_mock_dataclass,
        setup_real_timestamps,
        t_startpoint,
        setup_mock_timestamps,
        t_use_msg_publishing_timestamps,
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_stamps = setup_real_timestamps
        if not t_use_msg_publishing_timestamps:
            t_stamps = setup_mock_timestamps

        t_start_idx = 1
        t_start = int(t_stamps[t_start_idx])

        t_container_interval = t_container.get_timestamps(
            start=t_start,
            startpoint=t_startpoint,
            use_msg_publishing_timestamps=t_use_msg_publishing_timestamps,
        )
        print(t_container_interval)

        assert t_container_interval.header.timestamps.stamps.size == 1
        assert t_container_interval.header.timestamps.stamps[0] == int(
            setup_real_timestamps[t_start_idx + int(not t_startpoint)]
        )

        assert t_container_interval.bag_recorded_timestamps.stamps.size == 1
        assert t_container_interval.bag_recorded_timestamps.stamps[0] == int(
            setup_mock_timestamps[t_start_idx + int(not t_startpoint)]
        )

        assert (
            t_container_interval.mock_attribute[0]
            == t_mock_attribute[t_start_idx + int(not t_startpoint)]
        )

    @pytest.mark.parametrize(
        argnames="t_use_msg_publishing_timestamps",
        argvalues=[True, False],
        ids=[
            "t_use_msg_publishing_timestamps=True",
            "t_use_msg_publishing_timestamps=False",
        ],
    )
    def test_get_timestamp_case_interval(
        self,
        setup_mock_dataclass,
        setup_real_timestamps,
        setup_mock_timestamps,
        t_use_msg_publishing_timestamps,
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_stamps = setup_real_timestamps
        if not t_use_msg_publishing_timestamps:
            t_stamps = setup_mock_timestamps

        t_start_idx = 1
        t_stop_idx = 4
        t_container_interval = t_container.get_timestamps(
            start=(int(t_stamps[t_start_idx])),
            stop=(int(t_stamps[t_stop_idx])),
            use_msg_publishing_timestamps=t_use_msg_publishing_timestamps,
        )

        assert t_container_interval.header.timestamps.stamps[0] == int(
            setup_real_timestamps[t_start_idx]
        )
        assert t_container_interval.header.timestamps.stamps[-1] == int(
            setup_real_timestamps[t_stop_idx - 1]
        )

        assert t_container_interval.bag_recorded_timestamps.stamps[0] == int(
            setup_mock_timestamps[t_start_idx]
        )
        assert t_container_interval.bag_recorded_timestamps.stamps[-1] == int(
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
        self, setup_mock_dataclass, setup_real_timestamps, t_startpoint, t_endpoint
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_start_idx = 0
        t_stop_idx = 4

        # Note: Use 'use_msg_publishing_timestamps' param default.
        t_container_interval = t_container.get_timestamps(
            start=int(setup_real_timestamps[t_start_idx]),
            stop=int(setup_real_timestamps[t_stop_idx]),
            startpoint=t_startpoint,
            endpoint=t_endpoint,
        )

        print(t_container_interval)

        assert np.array_equal(
            t_container_interval.header.timestamps.stamps,
            setup_real_timestamps[
                slice(
                    t_start_idx + int(not t_startpoint),
                    t_stop_idx + 1 - int(not t_endpoint),
                )
            ],
        )
        assert np.array_equal(
            t_container_interval.mock_attribute,
            t_mock_attribute[
                slice(
                    t_start_idx + int(not t_startpoint),
                    t_stop_idx + 1 - int(not t_endpoint),
                )
            ],
        )


class TestRosFeatureArray:

    @pytest.fixture(scope="function")
    def setup_mock_dataclass(self, setup_real_timestamps, setup_mock_timestamps):
        t_mock_attribute = np.arange(setup_real_timestamps.size)

        t_container = MockRosFeatureArray(
            feature_name="mock",
            bag_recorded_timestamps=setup_mock_timestamps,
            mock_array=[
                RosStampedFeature(
                    feature_name="mock array member 1",
                    bag_recorded_timestamps=setup_mock_timestamps,
                    header=StdMsgsHeader(
                        frame_id="mock_frame_id_one",
                        timestamps=setup_real_timestamps,
                    ),
                ),
                RosStampedFeature(
                    feature_name="mock array member 2",
                    bag_recorded_timestamps=setup_mock_timestamps + 999,
                    header=StdMsgsHeader(
                        frame_id="mock_frame_id_two",
                        timestamps=setup_real_timestamps + 999,
                    ),
                ),
            ],
            mock_attribute=t_mock_attribute,
        )
        return t_container, t_mock_attribute

    def test_instanciation(
        self, setup_mock_dataclass, setup_real_timestamps, setup_mock_timestamps
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        assert t_container.feature_name == "mock"
        assert np.array_equal(
            t_container.bag_recorded_timestamps.stamps, setup_mock_timestamps
        )
        assert np.array_equal(
            t_container.mock_array[0].bag_recorded_timestamps.stamps,
            setup_mock_timestamps,
        )
        assert np.array_equal(
            t_container.mock_array[1].bag_recorded_timestamps.stamps,
            setup_mock_timestamps + 999,
        )
        assert np.array_equal(
            t_container.mock_array[0].header.timestamps.stamps, setup_real_timestamps
        )
        assert np.array_equal(
            t_container.mock_array[1].header.timestamps.stamps,
            setup_real_timestamps + 999,
        )

        assert np.array_equal(t_container.mock_attribute, t_mock_attribute)
        # print(t_container)

        with pytest.raises(AttributeError) as exc_info:
            # The 'timestamps' attribute should not exist
            assert t_container.__getattribute__("header")

    @pytest.mark.skip(reason="ToDo: implement test case (ref task TCT-87)")
    @pytest.mark.parametrize(
        argnames="t_startpoint",
        argvalues=[True, False],
        ids=["startpoint=True", "startpoint=False"],
    )
    def test_get_timestamp_case_single_stamp(
        self,
        setup_mock_dataclass,
        setup_real_timestamps,
        setup_mock_timestamps,
        t_startpoint,
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_start_idx = 1
        t_start = int(setup_real_timestamps[t_start_idx])

        t_container_interval = t_container.get_timestamps(
            start=t_start, startpoint=t_startpoint
        )
        print(t_container_interval)

        assert t_container_interval.bag_recorded_timestamps.stamps.size == 1
        assert t_container_interval.bag_recorded_timestamps.stamps[0] == int(
            setup_real_timestamps[t_start_idx + int(not t_startpoint)]
        )
        assert (
            t_container_interval.mock_attribute[0]
            == t_mock_attribute[t_start_idx + int(not t_startpoint)]
        )

    @pytest.mark.skip(reason="ToDo: implement test case (ref task TCT-87)")
    def test_get_timestamp_case_interval(
        self, setup_mock_dataclass, setup_real_timestamps, setup_mock_timestamps
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_start_idx = 1
        t_stop_idx = 4
        t_container_interval = t_container.get_timestamps(
            start=(int(setup_real_timestamps[t_start_idx])),
            stop=(int(setup_real_timestamps[t_stop_idx])),
        )

        assert t_container_interval.bag_recorded_timestamps.stamps[0] == int(
            setup_real_timestamps[t_start_idx]
        )
        assert t_container_interval.bag_recorded_timestamps.stamps[-1] == int(
            setup_real_timestamps[t_stop_idx - 1]
        )
        assert np.array_equal(
            t_container_interval.mock_attribute,
            t_mock_attribute[slice(t_start_idx, t_stop_idx)],
        )
        print(t_container_interval)

    @pytest.mark.skip(reason="ToDo: implement test case (ref task TCT-87)")
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
        self,
        setup_mock_dataclass,
        setup_real_timestamps,
        setup_mock_timestamps,
        t_startpoint,
        t_endpoint,
    ):
        t_container, t_mock_attribute = setup_mock_dataclass

        t_start_idx = 0
        t_stop_idx = 4
        t_container_interval = t_container.get_timestamps(
            start=int(setup_real_timestamps[t_start_idx]),
            stop=int(setup_real_timestamps[t_stop_idx]),
            startpoint=t_startpoint,
            endpoint=t_endpoint,
        )

        print(t_container_interval)

        assert np.array_equal(
            t_container_interval.bag_recorded_timestamps.stamps,
            setup_real_timestamps[
                slice(
                    t_start_idx + int(not t_startpoint),
                    t_stop_idx + 1 - int(not t_endpoint),
                )
            ],
        )
        assert np.array_equal(
            t_container_interval.mock_attribute,
            t_mock_attribute[
                slice(
                    t_start_idx + int(not t_startpoint),
                    t_stop_idx + 1 - int(not t_endpoint),
                )
            ],
        )


@pytest.mark.deprecated(
    "Dataclass NestedRosStampedFeature is marked as deprecated (ref task TCT-87)"
)
class TestRosStampedFeatureCaseNested:
    def test_instanciation(self):

        t_container = MockNestedRosStampedFeature(
            header=StdMsgsHeader(
                frame_id="mock_frame_id",
                timestamps=np.arange(10),
            ),
            mock_attribute=np.ones(10),
        )

        assert t_container.feature_name is None
        assert t_container.is_nested() == False
        assert t_container.header.is_nested() == True
        assert t_container.header.feature_name is None
        assert np.array_equal(t_container.header.timestamps.stamps, np.arange(10))
        assert np.array_equal(t_container.mock_attribute, np.ones(10))
