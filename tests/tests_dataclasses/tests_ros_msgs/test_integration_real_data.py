# coding=utf-8
from trajectory_container_tools.extractor import from_rosbag


def test_RosDataclass_and_RosStampedDataclass_inheriter_on_rosbag(
    setup_rosbag_six_topics_filtered,
):

    container = from_rosbag(
        setup_rosbag_six_topics_filtered.bag_path,
        dataset_info=setup_rosbag_six_topics_filtered.bag_name,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
    )

    # Minimum logic to validate run success
    print(container)


def test_integration_feature_iterable(setup_rosbag_six_topics_filtered):

    container = from_rosbag(
        setup_rosbag_six_topics_filtered.bag_path,
        dataset_info=setup_rosbag_six_topics_filtered.bag_name,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
    )

    # print(container)

    # for idx in range(len(container.topic_odom)):
    #     assert container.topic_odom.header.timestamps.stamps[idx].size == 1
    #     print(f"idx: {idx} timestamps: {container.topic_odom.header.timestamps.stamps[idx]}")

    SELECTED_TOPICS = [
        "topic_odom",
        "topic_tf",
        "topic_scan",
        "topic_teleop",
        "topic_sensors_imu_raw",
        "topic_sensors_imu",
    ]
    for each in SELECTED_TOPICS:
        print(f"===={container.get_dynamic_field(each).feature_name}{'='*80}")
        if each != "topic_tf":
            for idx in range(len(container.get_dynamic_field(each))):
                assert (
                    container.get_dynamic_field(each).header.timestamps.stamps[idx].size
                    == 1
                )
                print(
                    f"idx: {idx} timestamps: {container.get_dynamic_field(each).header.timestamps.stamps[idx]}"
                )


def test_integration_feature_getitem(setup_rosbag_six_topics_filtered):

    container = from_rosbag(
        setup_rosbag_six_topics_filtered.bag_path,
        dataset_info=setup_rosbag_six_topics_filtered.bag_name,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
    )

    print(container)

    print("=" * 80, f"\n", container.topic_odom[0])
    print("=" * 80, f"\n", container.topic_odom.pose[0])
    print("=" * 80, f"\n", container.topic_odom.pose.pose[0])
    print("=" * 80, f"\n", container.topic_odom.pose.pose.position[0])
    print("=" * 80, f"\n", container.topic_odom.pose.pose.position.x[0])

    for idx in range(len(container.get_dynamic_field("topic_odom"))):
        # Check dimension getitem
        assert container.topic_odom[idx].pose.pose.position.x.size == 1
        assert container.topic_odom.pose[idx].pose.position.x.size == 1
        assert container.topic_odom.pose.pose[idx].position.x.size == 1
        assert container.topic_odom.pose.pose.position[idx].x.size == 1

        assert len(container.topic_odom[idx]) == 1
        assert len(container.topic_odom.pose[idx]) == 1
        assert len(container.topic_odom.pose.pose[idx]) == 1
        assert len(container.topic_odom.pose.pose.position[idx]) == 1

        # # Check nested timestamps getitem
        assert container.topic_odom.header.timestamps.stamps[idx].size == 1
        assert container.topic_odom.header.timestamps.delta_stamps[idx].size == 1
        # (CRITICAL) ToDo: on task end >> UN-mute this line ↓
        assert container.topic_odom.header.timestamps[idx].stamps.size == 1
        assert container.topic_odom.header[idx].timestamps.stamps.size == 1
        assert container.topic_odom[idx].header.timestamps.stamps.size == 1
