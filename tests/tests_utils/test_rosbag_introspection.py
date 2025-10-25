# coding=utf-8
import os.path
from pathlib import Path

import pytest

from trajectory_container_tools.temporal.trajectory_timestamps_metadata import (
    TrajectoryTimestampsMetadata,
)
from trajectory_container_tools.utils.ros2_utils.rosbag_introspection import (
    gather_rosbag_informations,
    gather_rosbag_trajectory_window_informations,
    show_rosbag_summary_info,
)


def test_gather_rosbag_informations(setup_rosbag_six_topics_filtered):

    info_str, bag_time_metadata = gather_rosbag_informations(
        setup_rosbag_six_topics_filtered.bag_path
    )

    assert isinstance(info_str, str)
    print(info_str)

    assert isinstance(bag_time_metadata, TrajectoryTimestampsMetadata)
    assert bag_time_metadata.start_time == 1695601812726547969
    assert bag_time_metadata.end_time == 1695601829992486977
    assert bag_time_metadata.duration == 17265939008


def test_gather_rosbag_trajectory_window_informations(setup_rosbag_six_topics_filtered):
    rosbag_6_t = setup_rosbag_six_topics_filtered
    info_str_main = gather_rosbag_trajectory_window_informations(
        bag_path_abs=rosbag_6_t.bag_path,
        features_config=rosbag_6_t.feature_config,
        start=None,
        stop=None,
    )

    assert isinstance(info_str_main, str)
    print(info_str_main)


def test_show_rosbag_summary_info(setup_rosbag_six_topics_filtered):
    rosbag_6_t = setup_rosbag_six_topics_filtered

    sanitized_rosbag_path = show_rosbag_summary_info(rosbag_path=rosbag_6_t.bag_path)
    assert isinstance(sanitized_rosbag_path, Path)
    assert os.path.exists(sanitized_rosbag_path)
