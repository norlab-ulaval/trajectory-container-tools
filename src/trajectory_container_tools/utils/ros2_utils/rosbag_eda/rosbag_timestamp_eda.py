# coding=utf-8

"""
Usage:

    1. execute example: $ python src/trajectory_container_tools/utils/ros2_utils/rosbag_eda/rosbag_timestamp_eda.py
    2. analyze the plots and logs at "artifact/rosbag_eda/<EXPERIMENT_NAME>/"

"""

from typing import Optional, Tuple, Union
import os
from pathlib import Path

import trajectory_container_tools as tct
import trajectory_container_tools.dataclasses.ros_msgs.stamped_dataclass
from trajectory_container_tools.utils.general import dn_validate_path
from trajectory_container_tools.temporal.timestamps import to_seconds
from trajectory_container_tools.utils.ros2_utils.ros2_non_native_msg import (
    register_non_native_msgs,
)
from trajectory_container_tools.dataclasses.core import AbstractTrajectoryStampedFeaturesBag
from trajectory_container_tools.utils.ros2_utils.rosbag_eda.eda_utils.general_utils import (
    compute_bag_target_window_nb,
    compute_window_start_and_stop,
    find_max_timestamp_delta_over_all_topics,
    gather_rosbag_informations,
    gather_rosbag_trajectory_window_informations,
    rosbag_log_file_name,
)
from trajectory_container_tools.utils.ros2_utils.rosbag_eda.eda_utils.plot import (
    plot_bag_timestamp_delta,
)
import trajectory_container_tools.dataclasses as tct_dataclasses
from trajectory_container_tools.utils.general import RosImportError

try:
    from rosbags.typesys.store import Typestore
except (ImportError, ModuleNotFoundError):
    raise RosImportError


def run_rosbag_timestamp_eda(
    bag_path: Union[str, Path],
    eda_dir_path: Union[str, Path],
    features_config: dict,
    chunk_on: str,
    fast_forward_ns: Optional[Union[int, float]] = 0.1e9,
    window_ns: Optional[Union[int, float]] = 0.5e9,
    plot_ylim: Optional[float] = None,
    experiment_dir: Optional[str] = None,
    show_plot=True,
    figsize: Tuple[int, int] = (28, 10),
    save_dpi: int = 100,
    typestore: Optional[Typestore] = None,
) -> AbstractTrajectoryStampedFeaturesBag:
    """
    Executes timestamp-based Exploratory Data Analysis (EDA) on a ROSbag file by analyzing
    specific time window chunks, generating logs, and plotting timestamp data.

    :param bag_path: Path to the ROSbag file to be analyzed.
    :param eda_dir_path: Directory where EDA artifacts and logs will be saved.
    :param features_config: Configuration dictionary containing feature extraction settings.
    :param chunk_on: Topic in the ROSbag to monitor for chunk split e.g., '/teleop'.
    :param fast_forward_ns: Time in nanoseconds to fast-forward for each data chunk.
        Defaults to 0.1e9 nanoseconds (1/10 of a second).
    :param window_ns: Duration of the time window in nanoseconds for analyzing data chunks.
        Defaults to 0.5e9 nanoseconds (half a second).
    :param plot_ylim: Optional vertical limits for the plots. Defaults to None.
    :param experiment_dir: Directory to group all outputs for the analysis. If None, the
        bag name will be used. Defaults to None.
    :param show_plot: Determines whether the plot should be displayed interactively.
    :param figsize: The target figure size. Default to (28, 10)
    :param save_dpi: Dpi of the saved figures. Default to matplotlib default i.e., dpi=100
    :param typestore: Optional. The typestore instance to register the non-native
        messages. If not provided, a default typestore will be initialized.
    :return: None
    """
    # .... Setup path .............................................................................
    bag_path_abs = Path(bag_path)

    if experiment_dir is None:
        bag_name = os.path.basename(bag_path)
        experiment_dir = bag_name

    experiment_dir_path = Path(os.path.join(eda_dir_path, experiment_dir))
    log_file_path = Path(
        os.path.join(experiment_dir_path, rosbag_log_file_name(bag_path_abs))
    )
    os.makedirs(experiment_dir_path, exist_ok=True)

    print(
        (
            f"\nBegin rosbag timestamp eda:\n\n"
            f"   bag path: {bag_path_abs}\n\n"
            f"   crawler artifact path: {experiment_dir_path}\n"
        )
    )

    # .... Setup general ..........................................................................
    typestore = register_non_native_msgs(typestore)

    rosbag_info_str, bag_timestamps_meta = gather_rosbag_informations(bag_path_abs)
    print(rosbag_info_str)

    mf_container = tct.extractor.from_rosbag(
        rosbag_path=bag_path_abs,
        dataset_info=None,
        features_config=features_config,
        chunk_on=chunk_on,
        start=bag_timestamps_meta.start_time,
        stop=bag_timestamps_meta.end_time,
        typestore=typestore,
    )

    # .... Collect rosbag information .............................................................
    with open(log_file_path, "w") as log_file:

        print(rosbag_info_str, file=log_file)

        window_info = gather_rosbag_trajectory_window_informations(
            bag_path_abs,
            features_config,
            bag_timestamps_meta.start_time,
            bag_timestamps_meta.end_time,
        )
        print(window_info)
        print(window_info, file=log_file)

        MSG = "Multi-feature trajectory container"
        print(f"\n...{MSG:.<80}\n", file=log_file)

        print(mf_container, file=log_file)

        MSG = "Topic trajectory window timestamps logs"
        window_info_final = f"\n===={MSG:=<80}\n"

        for each_topic_name in mf_container.topic_key_list:
            each_topic: tct.dataclasses.RosStampedFeature = (
                mf_container.get_dynamic_field(each_topic_name)
            )
            window_info_final += f"\nTopic log: {each_topic.feature_name}\n"

            if "header" in each_topic.get_dimension_names():
                timestamps_ = each_topic.header.timestamps
                delta_stamps = timestamps_.delta_stamps[1:]
                if len(timestamps_) > 0:
                    window_info_final += (
                        f"  trajectory len: {len(timestamps_)}\n"
                        f"  timestamp delta:\n"
                        f"       max: {delta_stamps.max()}\n"
                        f"      mean: {delta_stamps.mean():.2f}\n"
                        f"       min: {delta_stamps.min()}\n"
                        f"    values:\n    {delta_stamps}\n"
                    )
        print(window_info_final, file=log_file)

        MSG = "Finish reading rosbag trajectory"
        print(f"\n===={MSG:=<80}\n", file=log_file)

    # .... Setup plot .............................................................................
    if plot_ylim is None:
        plot_ylim = find_max_timestamp_delta_over_all_topics(
            bag_path_abs, features_config, typestore
        )

    # .... Begin trajectory window crawling .......................................................
    num_iterations = compute_bag_target_window_nb(
        bag_timestamps_meta.duration, fast_forward_ns
    )
    for each_idx in range(num_iterations):

        window_start, window_stop = compute_window_start_and_stop(
            bag_timestamps_meta.start_time,
            bag_timestamps_meta.end_time,
            each_idx,
            fast_forward_ns,
            window_ns,
        )

        plot_bag_timestamp_delta(
            bag_timestamps_meta.start_time,
            mf_container.get_timestamps(
                start=window_start, stop=window_stop, startpoint=True, endpoint=True
            ),
            bag_path_abs,
            experiment_dir_path,
            chunk_on=chunk_on,
            append_to_title=f"trajectory window size: {to_seconds(window_stop - window_start)} (s)",
            comment=None,
            plot_ylim=plot_ylim,
            plot_postfix=each_idx,
            show_plot=show_plot,
            figsize=figsize,
            save_dpi=save_dpi,
        )

    return mf_container


if __name__ == "__main__":
    """
    Rosbag timestamp Exploratory Data Analysis example
    """

    bag_name_ = "rosbag2_2023_09_24-20_30_12-filtered-short"
    bag_path_ = dn_validate_path(
        os.path.join(
            "data/repository_data/tests_data/rosbag_test_data",
            "bags_vaul-f1tenth-nx-orin",
            bag_name_,
        )
    )

    run_rosbag_timestamp_eda(
        bag_path_,
        eda_dir_path=dn_validate_path("artifact/rosbag_eda"),
        features_config={
            "/odom": tct_dataclasses.NavMsgsOdometry,
            "/tf": tct_dataclasses.Tf2MsgsTFMessage,
            "/scan": tct_dataclasses.SensorMsgsLaserScan,
            "/teleop": tct_dataclasses.AckermannMsgsAckermannDriveStamped,
            "/sensors/imu/raw": trajectory_container_tools.dataclasses.ros_msgs.stamped_dataclass.SensorMsgsImu,
            "/sensors/imu": tct_dataclasses.VescMsgsVescImuStamped,
        },
        chunk_on="/teleop",
        fast_forward_ns=0.1e9,
        window_ns=0.5e9,
        plot_ylim=1.2e8,
        show_plot=True,
    )
