# coding=utf-8
import pytest

from trajectory_container_tools.dataclasses.core import AbstractMultifeatureStampedDataclass
from trajectory_container_tools.extractor import from_rosbag


class TestIntegrationMultifeatureTrajectoryDataclass:
    """
    This class contains test methods to validate the interaction between the ROS trajectory
    dataclasses and ROS bag files. The focus is on verifying correct data handling, feature
    accessibility, and iterable structure usage. Each test method performs specific checks to
    confirm the integrity and expected behavior of the implemented functionalities.

    Note: The following tests leverage the `from_rosbag` function but aim only at assessing the
    its output e.g., `mf_container[idx]`
    """

    def test_RosDataclass_and_RosStampedDataclass_inheriter_on_rosbag(
        self,
        setup_rosbag_six_topics_filtered,
    ):

        mf_container = from_rosbag(
            setup_rosbag_six_topics_filtered.bag_path,
            dataset_info=setup_rosbag_six_topics_filtered.bag_name,
            features_config=setup_rosbag_six_topics_filtered.feature_config,
        )

        # Minimum logic to validate run success
        print(mf_container)

        assert isinstance(mf_container, AbstractMultifeatureStampedDataclass)

    def test_integration_chunk_getitem_three_topics(
        self, setup_rosbag_three_topics_filtered
    ):

        mf_container = from_rosbag(
            setup_rosbag_three_topics_filtered.bag_path,
            dataset_info=setup_rosbag_three_topics_filtered.bag_name,
            features_config=setup_rosbag_three_topics_filtered.feature_config,
            chunk_on="/teleop",
        )

        print("==== FULL VIEW", "=" * 80, "\n", mf_container, "\n")

        print("==== Indexed VIEW", "=" * 77, "\n")
        debuging = False
        for idx in range(mf_container.chunks_total):
            print("\n... idx: ", idx, "." * 80)
            if debuging:
                print(mf_container[idx].topic_odom.header.timestamps.stamps)
                print(mf_container[idx].topic_sensors_imu_raw.header.timestamps.stamps)
                print(mf_container[idx].topic_teleop.header.timestamps.stamps)
            print(mf_container[idx])

    def test_integration_chunk_getitem_six_topics(
        self, setup_rosbag_six_topics_filtered
    ):

        mf_container = from_rosbag(
            setup_rosbag_six_topics_filtered.bag_path,
            dataset_info=setup_rosbag_six_topics_filtered.bag_name,
            features_config=setup_rosbag_six_topics_filtered.feature_config,
            chunk_on="/teleop",
        )

        print(
            f"\n==== FULL VIEW {'=' * 80}\n",
            mf_container,
            f"\n==== Indexed VIEW {'=' * 77}\n",
        )
        for idx in range(mf_container.chunks_total):
            print("\n... idx: ", idx, "." * 80)
            print(mf_container[idx])

    def test_integration_chunk_iterable_three_topics(
        self, setup_rosbag_three_topics_filtered
    ):

        mf_container = from_rosbag(
            setup_rosbag_three_topics_filtered.bag_path,
            dataset_info=setup_rosbag_three_topics_filtered.bag_name,
            features_config=setup_rosbag_three_topics_filtered.feature_config,
            chunk_on="/teleop",
        )

        for each in mf_container:
            print(each)

    def test_integration_chunk_iterable_six_topics(
        self, setup_rosbag_six_topics_filtered
    ):

        mf_container = from_rosbag(
            setup_rosbag_six_topics_filtered.bag_path,
            dataset_info=setup_rosbag_six_topics_filtered.bag_name,
            features_config=setup_rosbag_six_topics_filtered.feature_config,
            chunk_on="/teleop",
        )

        for each in mf_container:
            print(each)
