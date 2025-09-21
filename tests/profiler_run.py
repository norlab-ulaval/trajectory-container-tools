# coding=utf-8
import os
from pathlib import Path
from typing import Union

from trajectory_container_tools.trj_dataclasses.abstract_trajectory_dataclass import (
    AbstractMultifeatureDataclass,
)
from trajectory_container_tools.utils.optimization import detect_docker_cpu_limits
from trajectory_container_tools.rosbag_to_tct import (
    check_rosbag_path_and_show_available_topics,
)
from trajectory_container_tools.utils.ros2_non_native_msg import (
    register_ros2_non_native_msg,
)
from trajectory_container_tools.rosbag_to_tct import (
    aggregate_multiple_features_from_rosbag,
    extract_single_feature_from_rosbag,
)
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import (
    AckermannMsgsAckermannDriveStamped,
    NavMsgsOdometry,
    Scan,
    SensorMsgsImu,
    RosStampedDataclass,
)


def profiler_run():
    # .... Path to ROS bag in 'shared_data' directory ...........................................
    # For EDA and benchmark purposes only

    # BAG = "2024-03-21_12-19-00" # small circle
    # BAG = "2024-03-21_12-23-53" # medium spiral

    # BAG = "2024-03-21_14-52-35" # ★★ 8408 timesteps
    # rosbag_start=1711047206000000000
    # rosbag_stop=1711047237203288917

    BAG = "2024-03-21_14-52-35-with-scans"

    # BAG = "2024-03-21_15-14-09" # ★★ 63063 timesteps
    # BAG = "2024-03-21_15-26-13" # ★ 35128 timesteps
    # BAG = "2024-03-21_15-35-28"  # ★ 179236 timesteps
    rosbag_path = os.path.join(
        "data", "shared_data", "rosbag-vaul-f110-grand-salon-raw-msg", BAG
    )

    # .... Path to ROS bag in 'demo_data' directory ...............................................

    # BAG = "2024-03-21_14-52-35-filtered"
    # BAG = "2024-03-21_14-52-35-offending-timestamps"
    # rosbag_start = None
    # rosbag_stop = None
    # rosbag_path = os.path.join("data", "repository_data", "demo_data", "rosbag_test_data",
    #                            "rosbag-vaul-f110-grand-salon-raw-msg", BAG)

    # ..............................................................................................
    detect_docker_cpu_limits()

    # Register non-native ros message
    register_ros2_non_native_msg()

    rosbag_path = check_rosbag_path_and_show_available_topics(rosbag_path)

    print(
        f"\n[TCT] === Profiling run ===================================================="
    )
    container: Union[
        NavMsgsOdometry, RosStampedDataclass, AbstractMultifeatureDataclass
    ]

    # .... Extract Single Feature From Rosbag .....................................................
    # "/odom": NavMsgsOdometry,
    # "/teleop": AckermannMsgsAckermannDriveStamped,
    # "/sensors/imu/raw": SensorMsgsImu,
    # "/scan",
    # "/robot_description",

    # container = extract_single_feature_from_rosbag(
    #         rosbag_path=Path(rosbag_path),
    #         # feature_name="/odom",
    #         # data_container_type=NavMsgsOdometry
    #         feature_name="/teleop",
    #         data_container_type=AckermannMsgsAckermannDriveStamped,
    #         )

    # .... Aggregate Multiple Features From Rosbag ................................................
    # Basic configuration - extract odometry
    features_config_1 = {
        "/odom": NavMsgsOdometry,
        "/teleop": AckermannMsgsAckermannDriveStamped,
        "/sensors/imu/raw": SensorMsgsImu,
        "/scan": Scan,
    }
    # "/robot_description",

    container = aggregate_multiple_features_from_rosbag(
        rosbag_path,
        dataset_info=f"Robot: f110_race_car, Track: grand_salon, Run: {BAG}",
        features_config=features_config_1,
    )

    # Minimum logic to validate run success
    print(container)


if __name__ == "__main__":
    profiler_run()
