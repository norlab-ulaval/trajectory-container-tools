# coding=utf-8
import os
from pathlib import Path
from typing import Union

import numpy as np
import pytest

from trajectory_container_tools import extract_single_feature_from_rosbag
from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import (
    NavMsgsOdometry,
    RosBagFeatureDataclass,
    )


@pytest.fixture(scope="function")
def setup_rosbag_from_external_data_dir() -> Path:
    # .... Path to ROS bag in 'external_data' directory ...........................................

    # BAG = "2024-03-21_12-19-00" # small circle
    # BAG = "2024-03-21_12-23-53" # medium spiral

    # BAG = "2024-03-21_14-52-35" # ★★ 8408 timesteps
    # rosbag_start=1711047206000000000
    # rosbag_stop=1711047237203288917

    # # BAG = "2024-03-21_15-14-09" # ★★ 63063 timesteps
    # # BAG = "2024-03-21_15-26-13" # ★ 35128 timesteps
    # # BAG = "2024-03-21_15-35-28" # ★ 179236 timesteps
    # rosbag_path = os.path.join( "external_data", "rosbag-vaul-f110-grand-salon-raw-msg", BAG)

    # .... Path to ROS bag in 'demo_data' directory
    # ................................................

    BAG = "2024-03-21_14-52-35-filtered"
    # BAG = "2024-03-21_14-52-35-offending-timestamps"
    rosbag_start = None
    rosbag_stop = None
    rosbag_path = os.path.join("demo_data", "rosbag_test_data",
                               "rosbag-vaul-f110-grand-salon-raw-msg", BAG)

    # .... Construct absolute path to demo data for tests execution ...............................
    # Handle cases: pycharm-born dna run and shell-born dna run
    dn_project_path = os.getenv('DN_PROJECT_PATH')
    if os.path.exists(dn_project_path):
        rosbag_path = os.path.join(dn_project_path, rosbag_path)
    else:
        rosbag_path = os.path.realpath(os.path.join('..', rosbag_path))

    assert os.path.exists(rosbag_path)

    return Path(rosbag_path), rosbag_start, rosbag_stop


def benchmark_extract_single_feature_from_rosbag(bag_path: Path, rosbag_start: int,
                                                 rosbag_stop: int):
    """Standalone function for benchmarking - avoids pickling issues with Joblib"""
    return extract_single_feature_from_rosbag(rosbag_path=bag_path, feature_name="/odom",
                                              data_container_type=NavMsgsOdometry,
                                              start=rosbag_start,
                                              stop=rosbag_stop
                                              )


# @pytest.mark.parametrize(
#         argnames="t_enable_multiprocessing, t_n_jobs, t_chunk_size",
#         argvalues=[
#                 (True, 8, 50000),
#                 (True, 4, 50000),
#                 (True, 8, 20000),
#                 (True, 4, 20000),
#                 (False, 0, 0)
#                 ],
#         ids=[
#                 'Multiprocessing enabled, n_jobs 8, chunk size 50000',
#                 'Multiprocessing enabled, n_jobs 4, chunk size 50000',
#                 'Multiprocessing enabled, n_jobs 8, chunk size 20000',
#                 'Multiprocessing enabled, n_jobs 4, chunk size 20000',
#                 'Multiprocessing disabled']
#         )
def test_extract_rosbag_benchmark(benchmark, setup_rosbag_from_external_data_dir):
    container: Union[NavMsgsOdometry, RosBagFeatureDataclass]
    rosbag_path, rosbag_start, rosbag_stop = setup_rosbag_from_external_data_dir

    container = benchmark(benchmark_extract_single_feature_from_rosbag,
                          bag_path=rosbag_path,
                          rosbag_start=rosbag_start,
                          rosbag_stop=rosbag_stop,
                          )

    # Minimum logic to validate run success
    print(container)
    assert isinstance(container.pose.pose.position_x, np.ndarray)
