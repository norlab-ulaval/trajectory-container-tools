# coding=utf-8
import os
from typing import Union

from trajectory_container_tools import AbstractTrajectoryFeaturesBag
from trajectory_container_tools.utils.optimization import detect_docker_cpu_limits
from trajectory_container_tools.utils.ros2_utils.rosbag_introspection import \
    show_rosbag_summary_info
from trajectory_container_tools.extractor.rosbag_to_tct import (
    from_rosbag,
    )
from trajectory_container_tools.dataclasses import AckermannMsgsAckermannDriveStamped, \
    NavMsgsOdometry, RosStampedFeature, SensorMsgsLaserScan, SensorMsgsImu


def profiler_run(): # pragma: no cover
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

    # .... Path to ROS bag in 'tests_data' directory ...............................................

    # BAG = "2024-03-21_14-52-35-filtered"
    # BAG = "2024-03-21_14-52-35-offending-timestamps"
    # rosbag_start = None
    # rosbag_stop = None
    # rosbag_path = os.path.join("data", "repository_data", "tests_data", "rosbag_test_data",
    #                            "rosbag-vaul-f110-grand-salon-raw-msg", BAG)

    # ..............................................................................................
    detect_docker_cpu_limits()

    rosbag_path = show_rosbag_summary_info(rosbag_path)

    print(
        f"\n[TCT] === Profiling run ===================================================="
    )
    container: Union[
        NavMsgsOdometry, RosStampedFeature, AbstractTrajectoryFeaturesBag
    ]

    # .... Extract Single Feature From Rosbag .....................................................
    # "/odom": NavMsgsOdometry,
    # "/teleop": AckermannMsgsAckermannDriveStamped,
    # "/sensors/imu/raw": SensorMsgsImu,
    # "/scan",
    # "/robot_description",

    # container = extract_rosbag_feature(
    #         rosbag_path=Path(rosbag_path),
    #         # feature_name="/odom",
    #         # data_container_type=NavMsgsOdometry
    #         feature_name="/teleop",
    #         data_container_type=AckermannMsgsAckermannDriveStamped,
    #         )

    # .... Aggregate Multiple Features From Rosbag ................................................
    # Basic configuration - extract odometry
    features_config_1 = {
        "/odom":            NavMsgsOdometry,
        "/teleop":          AckermannMsgsAckermannDriveStamped,
        "/sensors/imu/raw": SensorMsgsImu,
        "/scan":            SensorMsgsLaserScan,
    }
    # "/robot_description",

    container = from_rosbag(rosbag_path,
                            dataset_info=f"Robot: f110_race_car, Track: grand_salon, Run: {BAG}",
                            features_config=features_config_1)

    # Minimum logic to validate run success
    print(container)


if __name__ == "__main__":
    profiler_run()
