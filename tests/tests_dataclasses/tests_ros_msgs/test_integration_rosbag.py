# coding=utf-8

from trajectory_container_tools.extractor import from_rosbag


class TestIntegrationTrajectoryDataclass:
    """
    This class contains test methods to validate the interaction between the ROS trajectory
    dataclasses and ROS bag files. The focus is on verifying correct data handling, feature
    accessibility, and iterable structure usage. Each test method performs specific checks to
    confirm the integrity and expected behavior of the implemented functionalities.

    Note: The following tests leverage the `from_rosbag` function but aim only at assessing the
    its output e.g., `mf_container.topic_odom`
    """

    def test_RosDataclass_and_RosStampedDataclass_inheriter_on_rosbag(
        self,
        setup_rosbag_six_topics_filtered,
    ):

        mf_container = from_rosbag(setup_rosbag_six_topics_filtered.bag_path,
                                   dataset_info=setup_rosbag_six_topics_filtered.bag_name,
                                   features_config=setup_rosbag_six_topics_filtered.feature_config)

        # Minimum logic to validate run success
        print(mf_container)

    def test_integration_feature_iterable(self, setup_rosbag_six_topics_filtered):

        mf_container = from_rosbag(setup_rosbag_six_topics_filtered.bag_path,
                                   dataset_info=setup_rosbag_six_topics_filtered.bag_name,
                                   features_config=setup_rosbag_six_topics_filtered.feature_config)

        SELECTED_TOPICS = [
            "topic_odom",
            "topic_tf",
            "topic_scan",
            "topic_teleop",
            "topic_sensors_imu_raw",
            "topic_sensors_imu",
        ]
        for each in SELECTED_TOPICS:
            print(f"===={mf_container.get_dynamic_field(each).feature_name}{'='*80}")
            if each != "topic_tf":
                for idx in range(len(mf_container.get_dynamic_field(each))):
                    assert (
                        mf_container.get_dynamic_field(each)
                        .header.timestamps.stamps[idx]
                        .size
                        == 1
                    )
                    print(
                        f"idx: {idx} timestamps: {mf_container.get_dynamic_field(each).header.timestamps.stamps[idx]}"
                    )

    def test_integration_feature_getitem(self, setup_rosbag_six_topics_filtered):

        mf_container = from_rosbag(setup_rosbag_six_topics_filtered.bag_path,
                                   dataset_info=setup_rosbag_six_topics_filtered.bag_name,
                                   features_config=setup_rosbag_six_topics_filtered.feature_config)

        print(mf_container)

        print("=" * 80, f"\n", mf_container.topic_odom[0])
        print("=" * 80, f"\n", mf_container.topic_odom.pose[0])
        print("=" * 80, f"\n", mf_container.topic_odom.pose.pose[0])
        print("=" * 80, f"\n", mf_container.topic_odom.pose.pose.position[0])
        print("=" * 80, f"\n", mf_container.topic_odom.pose.pose.position.x[0])

        for idx in range(len(mf_container.get_dynamic_field("topic_odom"))):
            # Check dimension getitem
            assert mf_container.topic_odom[idx].pose.pose.position.x.size == 1
            assert mf_container.topic_odom.pose[idx].pose.position.x.size == 1
            assert mf_container.topic_odom.pose.pose[idx].position.x.size == 1
            assert mf_container.topic_odom.pose.pose.position[idx].x.size == 1

            assert len(mf_container.topic_odom[idx]) == 1
            assert len(mf_container.topic_odom.pose[idx]) == 1
            assert len(mf_container.topic_odom.pose.pose[idx]) == 1
            assert len(mf_container.topic_odom.pose.pose.position[idx]) == 1

            # # Check nested timestamps getitem
            assert mf_container.topic_odom.header.timestamps.stamps[idx].size == 1
            assert mf_container.topic_odom.header.timestamps.delta_stamps[idx].size == 1
            # (CRITICAL) ToDo: on task end >> UN-mute this line ↓
            assert mf_container.topic_odom.header.timestamps[idx].stamps.size == 1
            assert mf_container.topic_odom.header[idx].timestamps.stamps.size == 1
            assert mf_container.topic_odom[idx].header.timestamps.stamps.size == 1


