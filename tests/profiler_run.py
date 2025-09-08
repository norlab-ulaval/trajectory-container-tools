# coding=utf-8
import os
from pathlib import Path
from typing import Union

from trajectory_container_tools import extract_single_feature_from_rosbag
from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import (
    NavMsgsOdometry,
    RosBagFeatureDataclass,
    )
from trajectory_container_tools.utils.optimization import detect_docker_cpu_limits


def profiler_run():
    # .... Path to ROS bag in 'external_data' directory
    # ...............................................
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

    # .... Construct absolute path to demo data for tests execution
    # ...................................
    # Handle cases: pycharm-born dna run and shell-born dna run
    dn_project_path = os.getenv('DN_PROJECT_PATH')
    if os.path.exists(dn_project_path):
        rosbag_path = os.path.join(dn_project_path, rosbag_path)
    else:
        rosbag_path = os.path.realpath(os.path.join('..', rosbag_path))

    assert os.path.exists(rosbag_path)

    detect_docker_cpu_limits()

    container: Union[NavMsgsOdometry, RosBagFeatureDataclass]

    print(f"\n[TCT] === Profiling run ====================================================")
    container = extract_single_feature_from_rosbag(rosbag_path=Path(rosbag_path),
                                                   feature_name="/odom",
                                                   data_container_type=NavMsgsOdometry)

    # Minimum logic to validate run success
    print(container)


if __name__ == '__main__':
    profiler_run()
