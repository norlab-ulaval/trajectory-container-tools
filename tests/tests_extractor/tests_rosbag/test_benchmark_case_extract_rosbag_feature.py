# coding=utf-8
import os
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np
import pytest

from trajectory_container_tools.extractor import (
    extract_rosbag_feature,
)
from trajectory_container_tools.utils import dn_sanitize_path
from trajectory_container_tools.utils.ros2_utils.rosbag_introspection import (
    show_rosbag_summary_info,
)
from trajectory_container_tools.dataclasses import NavMsgsOdometry, RosStampedFeature


@pytest.fixture(scope="session")
def setup_rosbag_from_external_data_dir() -> Tuple[Path, Optional[int], Optional[int]]:
    # .... Path to ROS bag in 'shared_data' directory ...........................................

    # BAG = "2024-03-21_12-19-00" # small circle
    # BAG = "2024-03-21_12-23-53" # medium spiral

    # BAG = "2024-03-21_14-52-35" # ★★ 8408 timesteps
    # rosbag_start=1711047206000000000
    # rosbag_stop=1711047237203288917

    # # BAG = "2024-03-21_15-14-09" # ★★ 63063 timesteps
    # # BAG = "2024-03-21_15-26-13" # ★ 35128 timesteps
    # # BAG = "2024-03-21_15-35-28" # ★ 179236 timesteps
    # rosbag_path = os.path.join( "data", "shared_data", "rosbag-vaul-f110-grand-salon-raw-msg", BAG)

    # .... Path to ROS bag in 'tests_data' directory ...............................................

    BAG = "2024-03-21_14-52-35-filtered"
    # BAG = "2024-03-21_14-52-35-offending-timestamps"
    rosbag_start = None
    rosbag_stop = None
    rosbag_path = os.path.join(
        "data",
        "repository_data",
        "tests_data",
        "rosbag_test_data",
        "rosbag-vaul-f110-grand-salon-raw-msg",
        BAG,
    )

    return (
        dn_sanitize_path(rosbag_path),
        rosbag_start,
        rosbag_stop,
    )


def benchmark_extract_single_feature_from_rosbag(
    bag_path: Path, rosbag_start: int, rosbag_stop: int
):
    """Standalone function for benchmarking - avoids pickling issues with Joblib"""
    return extract_rosbag_feature(
        rosbag_path=bag_path,
        feature_name="/odom",
        data_container_type=NavMsgsOdometry,
        start=rosbag_start,
        stop=rosbag_stop,
    )


@pytest.mark.benchmark(
    group="EXTRACT-ROSBAG-FEATURE",
    min_time=0.05,  # default: 0.000005
    max_time=4.0,  # default: 1.0
    min_rounds=20,  # default: 5
    disable_gc=True,
    warmup=True,
)
def test_extract_rosbag_feature_benchmark(
    benchmark, setup_rosbag_from_external_data_dir
):
    t_container: Union[NavMsgsOdometry, RosStampedFeature]
    rosbag_path, rosbag_start, rosbag_stop = setup_rosbag_from_external_data_dir

    t_container = benchmark(
        benchmark_extract_single_feature_from_rosbag,
        bag_path=rosbag_path,
        rosbag_start=rosbag_start,
        rosbag_stop=rosbag_stop,
    )

    # Minimum logic to validate run success
    # print(container)
    assert isinstance(t_container.pose.pose.position.x, np.ndarray)
