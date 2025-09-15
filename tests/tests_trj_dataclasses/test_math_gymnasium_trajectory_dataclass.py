# coding=utf-8

from trajectory_container_tools.trj_dataclasses.math_gymnasium_trajectory_dataclass import (
    MathEnvTrajectoryDataclass, StateAxDataclass, TimeAxDataclass,
    )


class TestMathEnvTrajectoryDataclass:

    def test_member_dataclass_StateAxesDataclass(self, setup_mock_trajectory_data):
        trj_len, ndim, state_obs_ndim_trj, time_obs_trj = setup_mock_trajectory_data(
            state_obs_ndim=3)

        t_state_axes_container = StateAxDataclass(
                poses=state_obs_ndim_trj,
                vels=state_obs_ndim_trj,
                obs=state_obs_ndim_trj,
                )

        assert t_state_axes_container.trajectory_len == trj_len
        assert t_state_axes_container._time_axis == 0

    def test_member_dataclass_TimeAxisDataclass(self, setup_mock_trajectory_data):
        trj_len, ndim, state_obs_ndim_trj, time_obs_trj = setup_mock_trajectory_data(
            state_obs_ndim=3)

        t_time_axis_container = TimeAxDataclass(
                wall=time_obs_trj,
                delta=time_obs_trj,
                obs=time_obs_trj,
                )

        assert t_time_axis_container.trajectory_len == trj_len
        assert t_time_axis_container._time_axis == 0

    def test_parent_dataclass(self, setup_mock_trajectory_data):
        trj_len, ndim, state_obs_ndim_trj, time_obs_trj = setup_mock_trajectory_data(
            state_obs_ndim=3)

        t_trajectory_container = MathEnvTrajectoryDataclass(
                feature_name="Parent",
                state_axes=StateAxDataclass(
                        poses=state_obs_ndim_trj,
                        vels=state_obs_ndim_trj,
                        obs=state_obs_ndim_trj,
                        ),
                time_axis=TimeAxDataclass(
                        wall=time_obs_trj,
                        delta=time_obs_trj,
                        obs=time_obs_trj,
                        ),
                )

        assert t_trajectory_container.trajectory_len == trj_len
        assert t_trajectory_container._time_axis == 0
