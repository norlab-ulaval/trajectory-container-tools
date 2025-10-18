# coding=utf-8
from dataclasses import dataclass

import pytest

import numpy as np

from trajectory_container_tools.dataclasses import (
    StdMsgsHeader,
    NestedRosStampedDataclass,
    RosDataclass,
    RosStampedDataclass,
)


@dataclass()
class MockSubRosStampedDataclass(RosStampedDataclass):
    mock_attribute: np.ndarray


@dataclass()
class MockSubNestedRosStampedDataclass(NestedRosStampedDataclass):
    mock_attribute: np.ndarray


@dataclass()
class MockSubRosDataclass(RosDataclass):
    mock_attribute: np.ndarray


class TestRosStampedDataclass:

    @pytest.fixture(scope="function")
    def setup_mock_dataclass(self, setup_real_timestamps):
        t_mock_attribute = np.arange(setup_real_timestamps.size)

        t_container = MockSubRosStampedDataclass(
            feature_name="mock",
            header=StdMsgsHeader(
                frame_id="mock_frame_id",
                timestamps=setup_real_timestamps,
            ),
            mock_attribute=t_mock_attribute,
        )
        return t_container, t_mock_attribute

    def test_instanciation(self, setup_mock_dataclass, setup_real_timestamps):
        t_container, t_mock_attribute = setup_mock_dataclass

        assert t_container.feature_name == "mock"
        assert np.array_equal(
            t_container.header.timestamps.stamps, setup_real_timestamps
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

        assert t_container_interval.header.timestamps.stamps.size == 1
        assert t_container_interval.header.timestamps.stamps[0] == int(
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

        assert t_container_interval.header.timestamps.stamps[0] == int(
            setup_real_timestamps[t_start_idx]
        )
        assert t_container_interval.header.timestamps.stamps[-1] == int(
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


class TestNestedRosStampedDataclass:
    def test_instanciation(self):

        t_container = MockSubNestedRosStampedDataclass(
            header=StdMsgsHeader(
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
                header=StdMsgsHeader(
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
