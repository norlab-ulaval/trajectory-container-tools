# coding=utf-8
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union

from trajectory_container_tools import check_rosbag_path_and_show_available_topics


@dataclass()
class RosBagConfig:
    bag_name: str
    ts_fast_forward: Optional[float]
    ts_window: Optional[float]
    bag_path: Union[str, Path]
    feature_config: dict


def get_rosbag_vaul_f110_grand_salon_path(
    offending: bool = False,
) -> Tuple[Path, str]:
    """Path to ROS bag in 'tests_data' directory

    Note: offending timestamps are in the /teleop topic messages
    """

    if offending:
        BAG = "2024-03-21_14-52-35-offending-timestamps"
    else:
        BAG = "2024-03-21_14-52-35-filtered"

    rosbag_path = os.path.join(
        "data",
        "repository_data",
        "tests_data",
        "rosbag_test_data",
        "rosbag-vaul-f110-grand-salon-raw-msg",
        BAG,
    )

    return check_rosbag_path_and_show_available_topics(rosbag_path), BAG


def get_rosbag_vaul_f1tenth_nx_orin_path_filtered_short() -> Tuple[Path, str, list]:
    """Path to ROS bag in 'tests_data' directory"""

    BAG = "rosbag2_2023_09_24-20_30_12-filtered-short"
    SELECTED_TOPICS = [
        "/odom",
        "/tf",
        "/scan",
        "/teleop",
        "/sensors/imu/raw",
        "/sensors/imu",
    ]

    rosbag_path = os.path.join(
        "data",
        "repository_data",
        "tests_data",
        "rosbag_test_data",
        "bags_vaul-f1tenth-nx-orin",
        BAG,
    )

    return check_rosbag_path_and_show_available_topics(rosbag_path), BAG, SELECTED_TOPICS

def get_rosbag_vaul_f1tenth_nx_orin_path_offending_timestamps() -> Tuple[Path, str, list]:
    """Path to ROS bag in 'tests_data' directory"""

    BAG = "rosbag2_2023_09_25-14_20_35-offending-timestamps"
    duration = 10127987337
    SELECTED_TOPICS = [
        "/pf/pose/odom",
        "/tf",
        "/scan",
        "/ackermann_cmd",
        "/teleop",
        "/sensors/imu/raw",
    ]
    rosbag_path = os.path.join(
        "data",
        "repository_data",
        "tests_data",
        "rosbag_test_data",
        "bags_vaul-f1tenth-nx-orin",
        BAG,
    )

    return check_rosbag_path_and_show_available_topics(rosbag_path), BAG, SELECTED_TOPICS
