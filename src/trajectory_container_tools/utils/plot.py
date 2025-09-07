# coding=utf-8
from typing import Union

from matplotlib import pyplot as plt

from .general import extract_class_name_from_instance
from .. import AbstractMultifeatureDataclass
from ..trj_dataclasses.base_trajectory_dataclass import (
    BaseTrajectoryDataclass,
    BaseReverseAxisTrajectoryDataclass,
    )


def plot_trajectory_2d(
        trajectory_data: Union[BaseTrajectoryDataclass, BaseReverseAxisTrajectoryDataclass],
        x_axis_topic: str = "topic_odom.pose.pose.position_x",
        y_axis_topic: str = "topic_odom.pose.pose.position_y"):
    """
    Plots a 2D trajectory of position data using specified x and y axis topics.

    This function visualizes the trajectory based on the attributes of the input
    data class. The x-axis and y-axis attributes are derived from the data class
    using the provided topic strings. The plot includes the trajectory line, start
    and end points, direction arrows along the path, and labels for visualization.

    :param trajectory_data: A data container (either `BaseTrajectoryDataclass` or
        `BaseReverseAxisTrajectoryDataclass`) holding the trajectory attributes.
    :param x_axis_topic: The hierarchical string path to identify the x-axis attribute
        in `trajectory_data`. Default is "topic_odom.pose.pose.position_x".
    :param y_axis_topic: The hierarchical string path to identify the y-axis attribute
        in `trajectory_data`. Default is "topic_odom.pose.pose.position_y".
    :return: A tuple containing the matplotlib figure and axes objects with the plotted
        trajectory.
    """

    x_pos = trajectory_data.fetch_nested_attribute(x_axis_topic)
    y_pos = trajectory_data.fetch_nested_attribute(y_axis_topic)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot trajectory
    ax.plot(x_pos, y_pos, 'b-', linewidth=2, alpha=0.8, label='Trajectory')

    # Mark start and end points
    ax.scatter(x_pos[0], y_pos[0], color='green', s=150, marker='o',
               label='Start', edgecolor='black', linewidth=2, zorder=5)
    ax.scatter(x_pos[-1], y_pos[-1], color='red', s=150, marker='s',
               label='End', edgecolor='black', linewidth=2, zorder=5)

    # Add direction arrows
    skip = max(1, len(x_pos) // 100)
    for i in range(skip, len(x_pos) - skip, skip):
        dx = x_pos[i + skip // 2] - x_pos[i - skip // 2]
        dy = y_pos[i + skip // 2] - y_pos[i - skip // 2]
        ax.arrow(x_pos[i], y_pos[i], dx * 0.01, dy * 0.01,
                 head_width=0.35, head_length=0.35, fc='orange', ec='orange', alpha=0.7)

    ax.set_xlabel('X Position (m)', fontsize=12)
    ax.set_ylabel('Y Position (m)', fontsize=12)

    if isinstance(trajectory_data, AbstractMultifeatureDataclass):
        ax.set_title(f"{trajectory_data.dataset_info}", fontsize=14)
    else:
        ax.set_title(extract_class_name_from_instance(trajectory_data), fontsize=14)

    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.show()

    return fig, ax
