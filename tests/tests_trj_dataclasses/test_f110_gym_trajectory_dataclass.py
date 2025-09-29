# coding=utf-8
import numpy as np

from trajectory_container_tools.dataclasses.f110_gym_trajectory_dataclass import (
    F110MotionDynamicDataclass,
)


class TestF110MotionDynamicDataclass:
    def test_base(self, setup_mock_trajectory_data):
        trj_len, ndim, state_obs_ndim_trj, time_obs_trj = setup_mock_trajectory_data(
            state_obs_ndim=1
        )

        t_obs_container = F110MotionDynamicDataclass(
            feature_name="F110 motion dynamic",
            # .... actions ............................................
            steer=state_obs_ndim_trj,
            speed=state_obs_ndim_trj,
            # .... obs ................................................
            pose_x=state_obs_ndim_trj,
            pose_y=state_obs_ndim_trj,
            pose_theta=state_obs_ndim_trj,
            vel_x=state_obs_ndim_trj,
            vel_y=state_obs_ndim_trj,
            vel_ang=state_obs_ndim_trj,
            timestamp=time_obs_trj * 0.01,
            # .... next obs ...........................................
            next_pose_x=state_obs_ndim_trj + 1,
            next_pose_y=state_obs_ndim_trj + 1,
            next_pose_theta=state_obs_ndim_trj + 1,
            next_vel_x=state_obs_ndim_trj,
            next_vel_y=state_obs_ndim_trj,
            next_vel_ang=state_obs_ndim_trj,
            next_timestamp=(time_obs_trj + 1) * 0.01,
            # .... other ..............................................
            done=np.zeros((trj_len,)),
            reward=np.ones((trj_len,)),
        )

        assert t_obs_container.trajectory_len == trj_len
        assert t_obs_container._time_axis == 0
