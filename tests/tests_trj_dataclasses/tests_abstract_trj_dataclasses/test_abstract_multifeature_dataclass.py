# coding=utf-8
import datetime
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pytest

from trajectory_container_tools import (
    AbstractMultifeatureDataclass,
    BaseTrajectoryDataclass,
)
from trajectory_container_tools.dataclasses.ros2_feature_dataclass import (
    RosStampedDataclass,
)
from trajectory_container_tools.dataclasses.ros2_primitive_dataclass import Header
from trajectory_container_tools.utils.temporal_tools.timestamps import Timestamps
from trajectory_container_tools.utils.typing import TrajectoryDataclass


@dataclass
class MockMultifeatureDataclass(AbstractMultifeatureDataclass):
    topic_mock_1: RosStampedDataclass
    topic_mock_2: RosStampedDataclass


class TestAbstractMultifeatureDataclass:

    @pytest.fixture(scope="function")
    def setup_mock_topic_container(
        self,
    ) -> Tuple[RosStampedDataclass, RosStampedDataclass]:
        topic_mock_1 = RosStampedDataclass(
            feature_name="Mock topic 1",
            header=Header(frame_id="topic_1", timestamps=np.arange(20) * 1e9),
        )

        topic_mock_2 = RosStampedDataclass(
            feature_name="Mock topic 2",
            header=Header(frame_id="topic_2", timestamps=np.arange(20) * 1e9),
        )
        return topic_mock_1, topic_mock_2

    def test_instanciation_base_case(self, setup_mock_topic_container):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container

        mf_container = MockMultifeatureDataclass(
            dataset_info="Mock",
            topic_mock_1=topic_mock_1,
            topic_mock_2=topic_mock_2,
            bag_timestamps=None,
        )

        assert isinstance(mf_container.aggregated_date, datetime.datetime)
        assert mf_container.dataset_info == "Mock"
        assert isinstance(mf_container.topic_mock_1, RosStampedDataclass)
        assert isinstance(mf_container.topic_mock_2, RosStampedDataclass)
        assert mf_container.topic_mock_1.feature_name == "Mock topic 1"
        assert mf_container.topic_mock_2.feature_name == "Mock topic 2"

    def test_string_representation(self, setup_mock_topic_container):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container

        mf_container = MockMultifeatureDataclass(
            dataset_info="Mock",
            topic_mock_1=topic_mock_1,
            topic_mock_2=topic_mock_2,
            bag_timestamps=None,
        )

        # Minimum logic to validate run success
        print(mf_container)

        mf_container.summary

    def test_case_no_bag_level_timestamps(
        self, setup_mock_topic_container
    ):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container
        mf_container = MockMultifeatureDataclass(
            dataset_info="Mock",
            topic_mock_1=topic_mock_1,
            topic_mock_2=topic_mock_2,
            bag_timestamps=None,
        )

        assert mf_container.bag_timestamps is None

    def test_case_bag_level_timestamps(
        self, setup_mock_topic_container
    ):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container

        mock_bag_timestamps = Timestamps(stamps=np.arange(20) * 1e9)

        mf_container = MockMultifeatureDataclass(
            dataset_info="Mock",
            topic_mock_1=topic_mock_1,
            topic_mock_2=topic_mock_2,
            bag_timestamps=mock_bag_timestamps,
        )

        assert isinstance(mf_container.bag_timestamps, Timestamps)

    def test_topic_key_list(
        self, setup_mock_topic_container
    ):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container

        mock_bag_timestamps = Timestamps(stamps=np.arange(20) * 1e9)

        mf_container = MockMultifeatureDataclass(
            dataset_info="Mock",
            topic_mock_1=topic_mock_1,
            topic_mock_2=topic_mock_2,
            bag_timestamps=mock_bag_timestamps,
        )

        topic_key_list = mf_container.topic_key_list
        assert isinstance(topic_key_list, list)
        assert isinstance(topic_key_list[0], str)
        assert len(topic_key_list) == 2
        assert "topic_mock_1" in topic_key_list
        assert "topic_mock_2" in topic_key_list
