# coding=utf-8
import numpy as np
import pytest

from trajectory_container_tools.trj_dataclasses.f110_gym_trajectory_dataclass import (
    F110MotionDynamicDataclass,
)
from trajectory_container_tools.utils.containers_sanity_checks import (
    containers_timestep_alignment_sanity_check,
)


class TestContainersTimestepAlignementSanityCheck:
    @pytest.fixture
    def mock_f110_motion_dynamic_dataclass(self):
        def mock_container(
            name: str,
            trj_len: int,
            pose_x: np.ndarray,
            pose_y: np.ndarray,
            pose_theta: np.ndarray,
        ):
            t_done = np.full((trj_len,), False)
            t_done[-1] = True

            t_obs_container = F110MotionDynamicDataclass(
                feature_name=name,
                # .... actions ............................................
                steer=np.zeros((trj_len,)),
                speed=np.zeros((trj_len,)),
                # .... obs ................................................
                pose_x=pose_x,
                pose_y=pose_y,
                pose_theta=pose_theta,
                vel_x=np.zeros((trj_len,)),
                vel_y=np.zeros((trj_len,)),
                vel_ang=np.zeros((trj_len,)),
                timestamp=np.arange(trj_len) * 0.01,
                # .... next obs ...........................................
                next_pose_x=pose_x + 1,
                next_pose_y=pose_y + 1,
                next_pose_theta=pose_theta + 1,
                next_vel_x=np.zeros((trj_len,)),
                next_vel_y=np.zeros((trj_len,)),
                next_vel_ang=np.zeros((trj_len,)),
                next_timestamp=np.arange(start=1, stop=trj_len + 1) * 0.01,
                # .... other ..............................................
                done=t_done,
                reward=np.zeros((trj_len,)),
            )
            return t_obs_container

        return mock_container

    def test_both_containers_have_same_parameters(
        self, mock_f110_motion_dynamic_dataclass
    ):
        mock_container_1 = mock_f110_motion_dynamic_dataclass(
            name="mock container 1",
            trj_len=5,
            pose_x=np.array([1, 2, 3, 4, 5]),
            pose_y=np.array([1, 2, 3, 4, 5]),
            pose_theta=np.array([1, 2, 3, 4, 5]),
        )
        mock_container_2 = mock_f110_motion_dynamic_dataclass(
            name="mock container 2",
            trj_len=5,
            pose_x=np.array([1, 2, 3, 4, 5]),
            pose_y=np.array([1, 2, 3, 4, 5]),
            pose_theta=np.array([1, 2, 3, 4, 5]),
        )
        assert containers_timestep_alignment_sanity_check(
            mock_container_1, mock_container_2
        )

    def test_both_containers_have_different_trajectory_lengths(
        self, mock_f110_motion_dynamic_dataclass
    ):
        mock_container_1 = mock_f110_motion_dynamic_dataclass(
            name="mock container 1",
            trj_len=5,
            pose_x=np.array([1, 2, 3, 4, 5]),
            pose_y=np.array([1, 2, 3, 4, 5]),
            pose_theta=np.array([1, 2, 3, 4, 5]),
        )
        mock_container_2 = mock_f110_motion_dynamic_dataclass(
            name="mock container 2",
            trj_len=6,
            pose_x=np.array([1, 2, 3, 4, 5, 6]),
            pose_y=np.array([1, 2, 3, 4, 5, 6]),
            pose_theta=np.array([1, 2, 3, 4, 5, 6]),
        )
        assert not containers_timestep_alignment_sanity_check(
            mock_container_1, mock_container_2
        )

    def test_both_containers_have_different_values(
        self, mock_f110_motion_dynamic_dataclass
    ):
        mock_container_1 = mock_f110_motion_dynamic_dataclass(
            name="mock container 1",
            trj_len=5,
            pose_x=np.array([1, 2, 3, 4, 5]),
            pose_y=np.array([1, 2, 3, 4, 5]),
            pose_theta=np.array([1, 2, 3, 4, 5]),
        )
        mock_container_2 = mock_f110_motion_dynamic_dataclass(
            name="mock container 2",
            trj_len=5,
            pose_x=np.array([6, 7, 8, 9, 10]),
            pose_y=np.array([1, 2, 3, 4, 5]),
            pose_theta=np.array([1, 2, 3, 4, 5]),
        )
        assert not containers_timestep_alignment_sanity_check(
            mock_container_1, mock_container_2
        )
