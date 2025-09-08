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
    # .... Path to ROS bag in 'external_data' directory
    # ............................................
    # For EDA and benchmark purposes only

    # BAG = "2024-03-21_12-19-00" # small circle
    # BAG = "2024-03-21_12-23-53" # medium spiral
    # BAG = "2024-03-21_12-25-29" # empty
    # BAG = "2024-03-21_14-52-35"  # ★★ 8408 timestpes
    # BAG = "2024-03-21_15-01-04" # empty
    # BAG = "2024-03-21_15-03-19" # empty
    # BAG = "2024-03-21_15-14-09"  # ★★ 63063 timesteps
    # BAG = "2024-03-21_15-26-13" # ★ 35128 timesteps
    BAG = "2024-03-21_15-35-28" # ★ 179236 timesteps
    rosbag_path = os.path.join("external_data", "rosbag-vaul-f110-grand-salon-raw-msg", BAG)

    # .... Construct absolute path to demo data for tests execution ...............................
    # Handle cases: pycharm-born dna run and shell-born dna run
    dn_project_path = os.getenv('DN_PROJECT_PATH')
    if os.path.exists(dn_project_path):
        rosbag_path = os.path.join(dn_project_path, rosbag_path)
    else:
        rosbag_path = os.path.realpath(os.path.join('..', rosbag_path))

    assert os.path.exists(rosbag_path)

    return Path(rosbag_path)


def benchmark_extract_single_feature_from_rosbag(bag_path: Path, t_enable_multiprocessing: bool,
                                                 t_n_jobs: int, t_chunk_size: int):
    """Standalone function for benchmarking - avoids pickling issues with Joblib"""
    return extract_single_feature_from_rosbag(
            rosbag_path=bag_path,
            feature_name="/odom",
            data_container_type=NavMsgsOdometry,
            enable_multiprocessing=t_enable_multiprocessing,
            n_jobs=t_n_jobs,
            chunk_size=t_chunk_size,
            )


@pytest.mark.parametrize(
        argnames="t_enable_multiprocessing, t_n_jobs, t_chunk_size",
        argvalues=[
                (True, 8, 50000),
                (True, 4, 50000),
                (True, 8, 20000),
                (True, 4, 20000),
                (False, 0, 0)
                ],
        ids=[
                'Multiprocessing enabled, n_jobs 8, chunk size 50000',
                'Multiprocessing enabled, n_jobs 4, chunk size 50000',
                'Multiprocessing enabled, n_jobs 8, chunk size 20000',
                'Multiprocessing enabled, n_jobs 4, chunk size 20000',
                'Multiprocessing disabled']
        )
def test_extract_rosbag_benchmark(benchmark, setup_rosbag_from_external_data_dir,
                                  t_enable_multiprocessing, t_n_jobs, t_chunk_size):
    container: Union[NavMsgsOdometry, RosBagFeatureDataclass]

    container = benchmark(benchmark_extract_single_feature_from_rosbag,
                          bag_path=setup_rosbag_from_external_data_dir,
                          t_enable_multiprocessing=t_enable_multiprocessing,
                          t_n_jobs=t_n_jobs,
                          t_chunk_size=t_chunk_size)

    # Minimum logic to validate run success
    print(container)
    assert isinstance(container.pose.pose.position_x, np.ndarray)
