# coding=utf-8
import os
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np
import pytest

from tests.rosbag_test_utils import get_rosbag_vaul_f1tenth_nx_orin_path_filtered_short
from trajectory_container_tools.extractor import (
    from_rosbag,
)
from trajectory_container_tools.utils.ros2_utils.rosbag_introspection import \
    show_rosbag_summary_info
from trajectory_container_tools.dataclasses import (
    AckermannMsgsAckermannDriveStamped,
    NavMsgsOdometry,
    RosStampedFeature,
    SensorMsgsImu,
    SensorMsgsLaserScan,
    Tf2MsgsTFMessage,
    VescMsgsVescImuStamped,
)


@pytest.fixture(scope="function")
def setup_rosbag_from_external_data_dir() -> Tuple[Path, Optional[int], Optional[int]]:
    rosbag_start = None
    rosbag_stop = None
    rosbag_path, bag, selected_topics = get_rosbag_vaul_f1tenth_nx_orin_path_filtered_short()

    return (
            show_rosbag_summary_info(rosbag_path),
            rosbag_start,
            rosbag_stop,
    )


def benchmark_from_rosbag(
    bag_path: Path, rosbag_start: int, rosbag_stop: int
):
    """Standalone function for benchmarking - avoids pickling issues with Joblib"""
    mf_container = from_rosbag(bag_path, dataset_info=str(os.path.basename(bag_path)),
                               features_config={
                                       "/odom":            NavMsgsOdometry,
                                       "/tf":              Tf2MsgsTFMessage,
                                       "/scan":            SensorMsgsLaserScan,
                                       "/teleop":          AckermannMsgsAckermannDriveStamped,
                                       "/sensors/imu/raw": SensorMsgsImu,
                                       "/sensors/imu":     VescMsgsVescImuStamped,
                                       }, chunk_on='/teleop', start=None, stop=None, )

    for each_chunk in mf_container:
        # Minimum logic to validate chunk
        assert isinstance(each_chunk.topic_odom.pose.pose.position.x, np.ndarray)

    return mf_container


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
@pytest.mark.benchmark(
    group="FROM-ROSBAG",
    min_time=0.05, # default: 0.000005
    max_time=4.0, # default: 1.0
    min_rounds=20, # default: 5
    disable_gc=True,
    warmup=True,
)
def test_from_rosbag_benchmark(benchmark, setup_rosbag_from_external_data_dir):
    mf_container: Union[NavMsgsOdometry, RosStampedFeature]
    rosbag_path, rosbag_start, rosbag_stop = setup_rosbag_from_external_data_dir

    mf_container = benchmark(
        benchmark_from_rosbag,
        bag_path=rosbag_path,
        rosbag_start=rosbag_start,
        rosbag_stop=rosbag_stop,
    )

    # Minimum logic to validate run success
    # print(mf_container)
    assert isinstance(mf_container.topic_odom.pose.pose.position.x, np.ndarray)
