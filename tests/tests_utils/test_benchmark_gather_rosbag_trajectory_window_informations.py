# coding=utf-8
import os
from pathlib import Path
from typing import Optional, Tuple, Union

import pytest

from tests.rosbag_test_utils import (
    get_rosbag_vaul_f1tenth_nx_orin_path_filtered_short,
    get_rosbag_vaul_f1tenth_nx_orin_path_offending_timestamps,
)
from trajectory_container_tools.utils import dn_sanitize_path
from trajectory_container_tools.dataclasses import (
    AckermannMsgsAckermannDriveStamped,
    NavMsgsOdometry,
    SensorMsgsImu,
    SensorMsgsLaserScan,
    Tf2MsgsTFMessage,
    VescMsgsVescImuStamped,
)
from trajectory_container_tools.utils.ros2_utils.rosbag_introspection import (
    gather_rosbag_trajectory_window_informations,
)


@pytest.fixture(scope="session")
def setup_rosbag_from_external_data_dir() -> Tuple[Path, Optional[int], Optional[int]]:
    rosbag_start = None
    rosbag_stop = None

    shorter_bag = False
    if shorter_bag:
        rosbag_path, bag, selected_topics = get_rosbag_vaul_f1tenth_nx_orin_path_filtered_short()
    else:
        rosbag_path, bag, selected_topics = (
            get_rosbag_vaul_f1tenth_nx_orin_path_offending_timestamps()
        )

    return (
        dn_sanitize_path(rosbag_path),
        rosbag_start,
        rosbag_stop,
    )


def benchmark_gather_rosbag_trajectory_window_informations(
    bag_path: Path, rosbag_start: int, rosbag_stop: int
):
    """Standalone function for benchmarking - avoids pickling issues with Joblib"""

    bag_name = os.path.basename(bag_path)
    if bag_name == "rosbag2_2023_09_24-20_30_12-filtered-short":
        features_config = {
            "/odom": NavMsgsOdometry,
            "/tf": Tf2MsgsTFMessage,
            "/scan": SensorMsgsLaserScan,
            "/teleop": AckermannMsgsAckermannDriveStamped,
            "/sensors/imu/raw": SensorMsgsImu,
            "/sensors/imu": VescMsgsVescImuStamped,
        }

    elif bag_name == "rosbag2_2023_09_25-14_20_35-offending-timestamps":
        features_config = {
            "/pf/pose/odom": NavMsgsOdometry,
            "/tf": Tf2MsgsTFMessage,
            "/scan": SensorMsgsLaserScan,
            "/ackermann_cmd": AckermannMsgsAckermannDriveStamped,
            "/teleop": AckermannMsgsAckermannDriveStamped,
            "/sensors/imu/raw": SensorMsgsImu,
        }
    else:
        raise ValueError(f"No features_config dictionary matching test rosbag {bag_name}")

    info_str_main = gather_rosbag_trajectory_window_informations(
        bag_path_abs=bag_path,
        features_config=features_config,
        start=rosbag_start,
        stop=rosbag_stop,
    )

    return info_str_main


@pytest.mark.benchmark(
    group="GATHER-ROSBAG-TRAJECTORY-WINDOW-INFORMATIONS",
    min_time=0.0005,  # default: 0.000005
    max_time=10.0,  # default: 1.0
    min_rounds=10,  # default: 5
    disable_gc=True,
    warmup=True,
)
def test_gather_rosbag_trajectory_window_informations_benchmark(benchmark, setup_rosbag_from_external_data_dir):
    rosbag_path, rosbag_start, rosbag_stop = setup_rosbag_from_external_data_dir

    info_str_main = benchmark(
        benchmark_gather_rosbag_trajectory_window_informations,
        bag_path=rosbag_path,
        rosbag_start=rosbag_start,
        rosbag_stop=rosbag_stop,
    )

    # Minimum logic to validate run success
    # print(info_str_main)
    assert isinstance(info_str_main, str)
