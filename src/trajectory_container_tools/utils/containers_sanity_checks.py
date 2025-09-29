# coding=utf-8
from typing import Optional, Tuple

import numpy as np

from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass import AbstractTrajectoryDataclass


def containers_timestep_alignment_sanity_check(
    container_a: AbstractTrajectoryDataclass,
    container_b: AbstractTrajectoryDataclass,
    check_attribute: Optional[Tuple[str, ...]] = (
        "pose_x",
        "pose_y",
        "pose_theta",
        "timestamp",
        "next_pose_x",
        "next_pose_y",
        "next_pose_theta",
        "next_timestamp",
    ),
) -> bool:
    """
    Check if two containers are temporaly aligned for a given attributes. Usefull for validating
    that a modified container copy kept the integrity of selected attribute values.

    :param container_a: The first container of abstract feature dataclass.
    :param container_b: The second container of abstract feature dataclass.
    :param check_attribute: The attributes to check for alignment. Default is ("pose_x",
    "pose_y", "pose_theta").

    :return: True if the timesteps_indices for the specified attributes are aligned between the two
    containers, False otherwise.
    """
    assert isinstance(container_a, AbstractTrajectoryDataclass)
    assert isinstance(container_b, AbstractTrajectoryDataclass)
    try:
        assert container_a.trajectory_len == container_b.trajectory_len
        for each_attr in check_attribute:
            for each_idx in np.arange(container_a.trajectory_len):
                assert (
                    container_a.__getattribute__(each_attr)[each_idx]
                    == container_b.__getattribute__(each_attr)[each_idx]
                )

        return True
    except AssertionError:
        return False
