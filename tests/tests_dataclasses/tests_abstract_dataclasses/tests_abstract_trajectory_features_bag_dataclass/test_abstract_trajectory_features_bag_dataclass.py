# coding=utf-8
import datetime
from dataclasses import dataclass
from typing import Tuple
import numpy as np
import pytest

from trajectory_container_tools import (
    AbstractTrajectoryFeaturesBag,
)
from trajectory_container_tools.dataclasses import RosStampedFeature, StdMsgsHeader
from trajectory_container_tools.temporal.timestamps import Timestamps


@dataclass
class MockTrajectoryFeaturesBag(AbstractTrajectoryFeaturesBag):
    topic_mock_1: RosStampedFeature
    topic_mock_2: RosStampedFeature


class TestAbstractTrajectoryFeaturesBag:

    @pytest.fixture(scope="function")
    def setup_mock_topic_container(
        self,
    ) -> Tuple[RosStampedFeature, RosStampedFeature]:
        topic_mock_1 = RosStampedFeature(
            feature_name="Mock topic 1",
            header=StdMsgsHeader(frame_id="topic_1", timestamps=np.arange(20) * 1e9),
        )

        topic_mock_2 = RosStampedFeature(
            feature_name="Mock topic 2",
            header=StdMsgsHeader(frame_id="topic_2", timestamps=np.arange(20) * 1e9),
        )
        return topic_mock_1, topic_mock_2

    def test_instanciation_base_case(self, setup_mock_topic_container):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container

        mf_container = MockTrajectoryFeaturesBag(
            dataset_info="Mock",
            topic_mock_1=topic_mock_1,
            topic_mock_2=topic_mock_2,
            bag_timestamps=None,
        )

        assert isinstance(mf_container.aggregated_date, datetime.datetime)
        assert mf_container.dataset_info == "Mock"
        assert mf_container._parent is None
        assert isinstance(mf_container.topic_mock_1, RosStampedFeature)
        assert isinstance(mf_container.topic_mock_2, RosStampedFeature)
        assert mf_container.topic_mock_1.feature_name == "Mock topic 1"
        assert mf_container.topic_mock_2.feature_name == "Mock topic 2"

    @pytest.mark.parametrize(
        argnames="t_bag_timestamps",
        argvalues=[True, False],
    )
    def test_string_representation(self, setup_mock_topic_container, t_bag_timestamps):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container

        if t_bag_timestamps:
            mock_bag_timestamps = Timestamps(stamps=np.arange(20) * 1e9)
        else:
            mock_bag_timestamps = None

        mf_container = MockTrajectoryFeaturesBag(
            dataset_info="Mock",
            topic_mock_1=topic_mock_1,
            topic_mock_2=topic_mock_2,
            bag_timestamps=mock_bag_timestamps,
        )

        # Minimum logic to validate run success
        print(mf_container)

    def test_case_no_bag_level_timestamps(self, setup_mock_topic_container):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container
        mf_container = MockTrajectoryFeaturesBag(
            dataset_info="Mock",
            topic_mock_1=topic_mock_1,
            topic_mock_2=topic_mock_2,
            bag_timestamps=None,
        )

        assert mf_container.bag_timestamps is None

    def test_case_bag_level_timestamps(self, setup_mock_topic_container):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container

        mock_bag_timestamps = Timestamps(stamps=np.arange(20) * 1e9)

        mf_container = MockTrajectoryFeaturesBag(
            dataset_info="Mock",
            topic_mock_1=topic_mock_1,
            topic_mock_2=topic_mock_2,
            bag_timestamps=mock_bag_timestamps,
        )

        assert isinstance(mf_container.bag_timestamps, Timestamps)

    def test_topic_key_list(self, setup_mock_topic_container):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container

        mock_bag_timestamps = Timestamps(stamps=np.arange(20) * 1e9)

        mf_container = MockTrajectoryFeaturesBag(
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

    def test_nested_member_parent_tracking(self, setup_mock_topic_container):
        topic_mock_1, topic_mock_2 = setup_mock_topic_container
        mf_container = MockTrajectoryFeaturesBag(
            dataset_info="Mock",
            topic_mock_1=topic_mock_1,
            topic_mock_2=topic_mock_2,
            bag_timestamps=None,
        )

        assert mf_container._parent is None
        for each_key in mf_container.topic_key_list:
            each_attribute = mf_container.get_dynamic_field(each_key)
            assert id(each_attribute.get_parent_container()) == id(mf_container)

            t_parent = each_attribute.header.get_parent_container()
            assert id(t_parent) == id(each_attribute)
