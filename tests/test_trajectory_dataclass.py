# coding=utf-8
import numpy as np
import pytest

from trajectory_container_tools.trj_dataclasses.math_gymnasium_trajectory_dataclass import (
    MathEnvTrajectoryDataclass, StateAxDataclass, TimeAxDataclass,
    )
from trajectory_container_tools.trj_dataclasses.f110_gym_trajectory_dataclass import \
    F110MotionDynamicDataclass
from trajectory_container_tools.trj_dataclasses.panda_dataframe_feature_dataclass import (
    CmdStandard, StatePose2D, Velocity,
    )
from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import (
    AckermannMsgsAckermannDriveStamped, NavMsgsOdometry, SensorMsgsImu, Tf2MsgsTFMessage,
    Pose, PoseWithCovariance, Twist, TwistWithCovariance
    )


# ====Pandas dataframe cases=======================================================================
class TestTrajectoryDataclassFromDataframeCase:

    def test_init_empty_data_properties(self, mock_DF_2_trj_DC):
        md = mock_DF_2_trj_DC
        with pytest.raises(TypeError):
            dc_ = StatePose2D(feature_name=md.name)

    def test_StatePose2D_init(self, mock_DF_2_trj_DC):
        md = mock_DF_2_trj_DC
        dc_ = StatePose2D(feature_name=md.name, x=md.a, y=md.b, yaw=md.c, timestep_index=md.ts)
        print(dc_)
        assert dc_._init_trj_axe == -1

    def test_CmdStandard_init(self, mock_DF_2_trj_DC):
        md = mock_DF_2_trj_DC
        dc_ = CmdStandard(
                feature_name=md.name, linear_vel=md.a, angular_vel=md.b, timestep_index=md.ts
                )
        print(dc_)
        assert dc_._init_trj_axe == -1

    def test_Velocity_init(self, mock_DF_2_trj_DC):
        md = mock_DF_2_trj_DC
        dc_ = Velocity(
                feature_name=md.name, linear_vel=md.a, angular_vel=md.b, timestep_index=md.ts
                )
        print(dc_)
        assert dc_._init_trj_axe == -1


# ====Rosbag topics cases==========================================================================
class TestTrajectoryDataclassFromROSBagCase:

    def test_NavMsgsOdometry_init(self, mock_ROSbag_2_trj_DC):
        md = mock_ROSbag_2_trj_DC
        dc_ = NavMsgsOdometry(
                feature_name="/pf/pose/odom",
                header_FrameId=md.header_FrameId,
                timestamps=md.timestamps,
                timestep_index=md.ts_idx,
                pose=PoseWithCovariance(
                    feature_name="Netsed PoseWithCovariance",
                    pose=Pose(
                        feature_name="Netsed Pose",
                        position_x=md.a,
                        position_y=md.a,
                        position_z=md.a,
                        orientation_x=md.a,
                        orientation_y=md.a,
                        orientation_z=md.a,
                        orientation_w=md.a,
                    ),
                    covariance=md.c,
                ),
                twist=TwistWithCovariance(
                    feature_name="Netsed TwistWithCovariance",
                    twist=Twist(
                        feature_name="Netsed Twist",
                        linear_x=md.a,
                        linear_y=md.a,
                        linear_z=md.a,
                        angular_x=md.a,
                        angular_y=md.a,
                        angular_z=md.a,
                    ),
                    covariance=md.c,
                    )
                )
        print(dc_)
        assert dc_._init_trj_axe == 0

    def test_AckermannMsgsAckermannDriveStamped_init(self, mock_ROSbag_2_trj_DC):
        md = mock_ROSbag_2_trj_DC
        dc_ = AckermannMsgsAckermannDriveStamped(
                feature_name="/ackermann_cmd",
                header_FrameId=md.header_FrameId,
                timestamps=md.timestamps,
                timestep_index=md.ts_idx,
                drive_steeringAngle=md.a,
                drive_steeringAngleVelocity=md.a,
                drive_speed=md.a,
                drive_acceleration=md.a,
                drive_jerk=md.a,
                )
        print(dc_)
        assert dc_._init_trj_axe == 0

    def test_Tf2MsgsTFMessage_init(self, mock_ROSbag_2_trj_DC):
        md = mock_ROSbag_2_trj_DC
        dc_ = Tf2MsgsTFMessage(
                feature_name="/ackermann_cmd",
                header_FrameId=md.header_FrameId,
                timestamps=md.timestamps,
                timestep_index=md.ts_idx,
                childFrameId="odom",
                transform_translation_x=md.a,
                transform_translation_y=md.a,
                transform_translation_z=md.a,
                transform_rotation_x=md.a,
                transform_rotation_y=md.a,
                transform_rotation_z=md.a,
                transform_rotation_w=md.a,
                )
        print(dc_)
        assert dc_._init_trj_axe == 0

    def test_SensorMsgsImu_init(self, mock_ROSbag_2_trj_DC):
        md = mock_ROSbag_2_trj_DC
        dc_ = SensorMsgsImu(
                feature_name="/ackermann_cmd",
                header_FrameId=md.header_FrameId,
                timestamps=md.timestamps,
                timestep_index=md.ts_idx,
                orientation_x=md.a,
                orientation_y=md.a,
                orientation_z=md.a,
                orientation_w=md.a,
                orientationCovariance=md.c,
                angularVelocity_x=md.a,
                angularVelocity_y=md.a,
                angularVelocity_z=md.a,
                angularVelocityCovariance=md.c,
                linearAcceleration_x=md.a,
                linearAcceleration_y=md.a,
                linearAcceleration_z=md.a,
                linearAccelerationCovariance=md.c,
                )
        print(dc_)
        assert dc_._init_trj_axe == 0


# ====Gym cases====================================================================================
@pytest.fixture
def setup_data():
    def generate_trajectory_data(state_obs_ndim):
        trj_len = 9
        state_obs_ndim_trj = np.ones(trj_len * state_obs_ndim).reshape(trj_len, state_obs_ndim)
        if state_obs_ndim == 1:
            state_obs_ndim_trj = state_obs_ndim_trj.squeeze()
        time_obs_trj = np.arange(trj_len)
        return trj_len, state_obs_ndim, state_obs_ndim_trj, time_obs_trj

    return generate_trajectory_data


class TestF110MotionDynamicDataclass:

    def test_base(self, setup_data):
        trj_len, ndim, state_obs_ndim_trj, time_obs_trj = setup_data(state_obs_ndim=1)

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
        assert t_obs_container._init_trj_axe == 0


class TestMathEnvTrajectoryDataclass:

    def test_member_dataclass_StateAxesDataclass(self, setup_data):
        trj_len, ndim, state_obs_ndim_trj, time_obs_trj = setup_data(state_obs_ndim=3)

        t_state_axes_container = StateAxDataclass(
                poses=state_obs_ndim_trj,
                vels=state_obs_ndim_trj,
                obs=state_obs_ndim_trj,
                )

        assert t_state_axes_container.trajectory_len == trj_len
        assert t_state_axes_container._init_trj_axe == 0

    def test_member_dataclass_TimeAxisDataclass(self, setup_data):
        trj_len, ndim, state_obs_ndim_trj, time_obs_trj = setup_data(state_obs_ndim=3)

        t_time_axis_container = TimeAxDataclass(
                wall=time_obs_trj,
                delta=time_obs_trj,
                obs=time_obs_trj,
                )

        assert t_time_axis_container.trajectory_len == trj_len
        assert t_time_axis_container._init_trj_axe == 0

    def test_parent_dataclass(self, setup_data):
        trj_len, ndim, state_obs_ndim_trj, time_obs_trj = setup_data(state_obs_ndim=3)

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
        assert t_trajectory_container._init_trj_axe == 0
