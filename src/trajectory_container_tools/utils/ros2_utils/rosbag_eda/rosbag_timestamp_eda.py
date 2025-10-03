# coding=utf-8

"""
Usage:

    1. execute example: $ python src/trajectory_container_tools/utils/ros2_utils/rosbag_eda/rosbag_timestamp_eda.py
    2. analyze the plots and logs at "artifact/rosbag_eda/<EXPERIMENT_NAME>/"

"""

from typing import Optional, Tuple, Union
import os
from pathlib import Path
from rosbags.typesys.store import Typestore

import trajectory_container_tools.dataclasses.core.abstract_multi_trajectory_dataclass
import trajectory_container_tools.dataclasses.ros_msgs.stamped_dataclass
from trajectory_container_tools.utils.general import dn_validate_path
from trajectory_container_tools.temporal.timestamps import to_seconds
from trajectory_container_tools.utils.ros2_utils.rosbag_eda.eda_utils.rosbag_window_crawler import (
    crawl_rosbag_window,
)
from trajectory_container_tools.utils.ros2_utils.ros2_non_native_msg import (
    register_non_native_msgs,
)
from trajectory_container_tools.utils.ros2_utils.rosbag_eda.eda_utils.general_utils import (
    compute_bag_target_window_nb,
    compute_window_start_and_stop,
    find_max_timestamp_delta_over_all_topics,
    gather_rosbag_informations,
    rosbag_log_file_name,
)
from trajectory_container_tools.utils.ros2_utils.rosbag_eda.eda_utils.plot import (
    plot_bag_timestamp_delta,
)
import trajectory_container_tools.dataclasses as tct_dataclasses


def run_rosbag_timestamp_eda(
    bag_path: Union[str, Path],
    eda_dir_path: Union[str, Path],
    features_config: dict,
    fast_forward_ns: Optional[Union[int, float]] = 0.1e9,
    window_ns: Optional[Union[int, float]] = 0.5e9,
    track_action: str = "/teleop",
    plot_ylim: Optional[float] = None,
    experiment_dir: Optional[str] = None,
    show_plot=True,
    figsize: Tuple[int, int] = (28, 10),
    save_dpi: int = 100,
    typestore: Optional[Typestore] = None,
) -> trajectory_container_tools.dataclasses.core.abstract_multi_trajectory_dataclass.AbstractMultifeatureDataclass:
    """
    Executes timestamp-based Exploratory Data Analysis (EDA) on a ROSbag file by analyzing
    specific time window chunks, generating logs, and plotting timestamp data.

    :param bag_path: Path to the ROSbag file to be analyzed.
    :param eda_dir_path: Directory where EDA artifacts and logs will be saved.
    :param features_config: Configuration dictionary containing feature extraction settings.
    :param fast_forward_ns: Time in nanoseconds to fast-forward for each data chunk.
        Defaults to 0.1e9 nanoseconds (1/10 of a second).
    :param window_ns: Duration of the time window in nanoseconds for analyzing data chunks.
        Defaults to 0.5e9 nanoseconds (half a second).
    :param track_action: Action topic in the ROSbag to monitor for chunk split. Defaults to "/teleop".
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
    typestore = register_non_native_msgs(typestore)

    bag_path_abs = Path(bag_path)

    if experiment_dir is None:
        bag_name = os.path.basename(bag_path)
        experiment_dir = bag_name

    experiment_dir_path = Path(os.path.join(eda_dir_path, experiment_dir))

    log_path_dir = os.path.join(experiment_dir_path, "logs")

    os.makedirs(log_path_dir, exist_ok=True)

    print(
        (
            f"\nBegin rosbag timestamp eda:\n\n"
            f"   bag path: {bag_path_abs}\n\n"
            f"   crawler artifact path: {experiment_dir_path}\n"
        )
    )

    if plot_ylim is None:
        plot_ylim = find_max_timestamp_delta_over_all_topics(
            bag_path_abs, features_config, typestore
        )

    bag_start_time_, bag_end_time, bag_duration_, rosbag_info_str = (
        gather_rosbag_informations(bag_path_abs)
    )

    # ==== Begin trajectory window crawling =======================================================
    num_iterations = compute_bag_target_window_nb(bag_duration_, fast_forward_ns)
    for each_idx in range(num_iterations):

        log_file_path = Path(
            os.path.join(
                log_path_dir, rosbag_log_file_name(bag_path_abs, f"window-{each_idx}")
            )
        )

        start, stop = compute_window_start_and_stop(
            bag_end_time, bag_start_time_, each_idx, fast_forward_ns, window_ns
        )

        with open(log_file_path, "w") as log_file:

            print(rosbag_info_str, file=log_file)

            try:
                tc = crawl_rosbag_window(
                    bag_path_abs,
                    log_file,
                    features_config,
                    typestore,
                    start=start,
                    stop=stop,
                )

                plot_bag_timestamp_delta(
                    bag_start_time_,
                    tc,
                    bag_path_abs,
                    experiment_dir_path,
                    chunk_end_on=track_action,
                    append_to_title=f"trajectory window size: {to_seconds(stop - start)} (s)",
                    comment=None,
                    plot_ylim=plot_ylim,
                    plot_postfix=each_idx,
                    show_plot=show_plot,
                    figsize=figsize,
                    save_dpi=save_dpi,
                )
            except ValueError as e:
                if str(e) == "[TCT error] stamps array is empty!":
                    # TS_FAST_FORWARD * each_idx > than bag time ended.
                    pass

    return tc


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
            "/odom":            tct_dataclasses.NavMsgsOdometry,
            "/tf":              tct_dataclasses.Tf2MsgsTFMessage,
            "/scan":            tct_dataclasses.Scan,
            "/teleop":          tct_dataclasses.AckermannMsgsAckermannDriveStamped,
            "/sensors/imu/raw": trajectory_container_tools.dataclasses.ros_msgs.stamped_dataclass.SensorMsgsImu,
            "/sensors/imu":     tct_dataclasses.VescMsgsVescImuStamped,
        },
        fast_forward_ns=0.1e9,  # 1/10 of a second forward
        window_ns=0.5e9,  # half a second window
        track_action="/teleop",
        show_plot=True,
        plot_ylim=1.2e8,
    )
