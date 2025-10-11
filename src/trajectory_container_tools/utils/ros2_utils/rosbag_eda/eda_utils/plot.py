# coding=utf-8
import os
import pathlib
from typing import Optional, Tuple, Union

from matplotlib import pyplot as plt

import trajectory_container_tools as tct
import trajectory_container_tools.temporal.timestamps

from ...ros2_general import convert_rosbag_topic_key_to_tct_mf_topic_key
from .plot_management import plot_manager


def plot_bag_timestamp_delta(
    bag_start_time: int,
    tct_container: tct.typing.MultifeatureTrajectoryDataclass,
    bag_path_abs: pathlib.Path,
    experiment_dir_path: pathlib.Path,
    chunk_end_on: Optional[str] = "/teleop",
    append_to_title: Optional[str] = None,
    comment: Optional[str] = None,
    plot_ylim: float = 1e8,
    plot_postfix: Optional[Union[str, int]] = None,
    show_plot: bool = True,
    headless: bool = False,
    figsize: Tuple[int, int] = (28, 10),
    save_dpi: int = 100,
) -> None:
    """
    Generates and saves a plot illustrating the delta between consecutive message
    timestamps from a ROS bag, with options for customization and display.

    :param bag_start_time: The start time of the bag in nanoseconds.
    :param tct_container: Container holding topic information and data.
    :param bag_path_abs: Absolute path to the ROS bag file.
    :param experiment_dir_path: Path to the directory where results are saved.
    :param headless: If True, disables interactive plotting and saves the plot using a non-GUI backend.
    :param show_plot: Determines whether the plot should be displayed interactively.
    :param plot_ylim: Y-axis limit for the plot, if specified.
    :param plot_postfix: Optional string or integer to append to the plot filename to differentiate it.
    :param chunk_end_on: The topic name trigger to add visual markers at timestamps.
    :param comment: An optional text comment displayed on the plot.
    :param append_to_title: Additional text appended to the plot title.
    :param figsize: The target figure size. Default to (28, 10)
    :param save_dpi: Dpi of the saved figures. Default to matplotlib default i.e., dpi=100
    :return: None
    """
    LINEWIDTH = 1.5

    with plot_manager(show_plot, headless):

        fig = plt.figure(
            num=None, figsize=figsize, dpi=None, facecolor=None, edgecolor=None
        )
        if append_to_title:
            append_to_title = f"{append_to_title}, "
        plt.title(
            r"Topic messages timestamps delta"
            + f" ({append_to_title}bag: {os.path.basename(bag_path_abs)})"
        )

        chunk_end_on = convert_rosbag_topic_key_to_tct_mf_topic_key(chunk_end_on)

        # ... Topics plots ........................................................................
        for each_topic_name in [*tct_container.topic_key_list, "bag_timestamps"]:
            each_topic: Union[
                tct.dataclasses.RosDataclass, tct.dataclasses.RosStampedDataclass
            ] = tct_container.get_dynamic_field(each_topic_name)

            if isinstance(each_topic, tct.dataclasses.RosStampedDataclass):

                topic_ts_stamps = each_topic.header.timestamps.stamps[1:]
                topic_ts_delta = each_topic.header.timestamps.delta_stamps[1:]

                if topic_ts_delta is not None and len(topic_ts_delta) > 0:
                    y = topic_ts_delta
                    x = topic_ts_stamps - bag_start_time
                    x_in_second = trajectory_container_tools.temporal.timestamps.to_seconds(x)

                    if "ackermann" in each_topic_name:
                        _l = "-"
                        _m = ">"
                    elif "teleop" in each_topic_name:
                        _l = "--"
                        _m = ">"
                    elif "scan" in each_topic_name:
                        _l = ":"
                        _m = "."
                    elif "imu" in each_topic_name:
                        _l = "-."
                        _m = "."
                    elif "pf_pose_odom" in each_topic_name:
                        _l = "-"
                        _m = "*"
                    elif "odom" in each_topic_name:
                        _l = ":"
                        _m = "*"
                    else:
                        _l = "-"
                        _m = "."

                    if chunk_end_on in each_topic_name:
                        plt.vlines(
                            x=x_in_second,
                            ymin=0,
                            ymax=plot_ylim,
                            colors="Gray",
                            alpha=0.8,
                            linewidth=0.5,
                        )

                    plt.plot(
                        x_in_second,
                        y,
                        alpha=0.6,
                        label=f"{each_topic_name}",
                        linewidth=LINEWIDTH,
                        linestyle=_l,
                        marker=_m,
                    )

            if isinstance(each_topic, tct.temporal.Timestamps):
                topic_ts_stamps = each_topic.stamps[1:]
                topic_ts_delta = each_topic.delta_stamps[1:]
                if topic_ts_delta is not None and len(topic_ts_delta) > 0:
                    x = topic_ts_stamps - bag_start_time
                    x_in_second = trajectory_container_tools.temporal.timestamps.to_seconds(x)

                    plt.vlines(
                        x=x_in_second,
                        ymin=0,
                        ymax=plot_ylim,
                        colors="Gray",
                        alpha=0.05,
                        linewidth=0.8,
                        linestyles="--",
                    )

        # ....Plot general config..................................................................
        plt.legend()
        plt.ylabel(r"Timestamp $\Delta$ (ns)")
        plt.xlabel("Timestamp (s)")

        comment_ = (
            f"Vertical solide lines: Chunk ending on {chunk_end_on}\n"
            f"Vertical dashed lines: Bag timestamp references"
        )
        if comment:
            comment_ = comment_.join(f"\n{comment}")
        fig.text(
            0.035,
            0.94,
            comment_,
            bbox=dict(edgecolor="lightgray", facecolor="white", alpha=0.9),
            verticalalignment="top",
        )

        footer_comment_v = 0.024
        fig.text(0.018, footer_comment_v, "1e9 (ns) = 1 (s)")

        fig.text(
            0.99,
            footer_comment_v,
            f"+ bag start time {trajectory_container_tools.temporal.timestamps.to_seconds(bag_start_time)} (s)",
            horizontalalignment="right",
        )

        if plot_ylim:
            plt.ylim(0, plot_ylim)
        plt.tight_layout(pad=2)
        if plot_postfix is not None:
            plot_postfix = f"-window-{plot_postfix}"
        else:
            plot_postfix = ""

        os.makedirs(os.path.join(experiment_dir_path, "plots"), exist_ok=True)
        plt.savefig(
            os.path.join(
                experiment_dir_path,
                f"plots",
                f"{os.path.basename(bag_path_abs)}{plot_postfix}.png",
            ),
            dpi=save_dpi,
        )

        return None
