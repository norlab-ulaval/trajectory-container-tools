# coding=utf-8
from trajectory_container_tools.trj_dataclasses.primitive_dataclass import Header
from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import (
    AckermannMsgsAckermannDriveStamped, NavMsgsOdometry,
    NavMsgsOdometryFlat, Pose, PoseWithCovariance, SensorMsgsImu, Tf2MsgsTFMessage, Twist,
    TwistWithCovariance,
    )


class TestTrajectoryDataclassFromROSBagCase:

    def test_NavMsgsOdometry_init_nested_version(self, mock_ROSbag_2_trj_DC):
        md = mock_ROSbag_2_trj_DC
        dc_ = NavMsgsOdometry(
                feature_name="/pf/pose/odom",
                header=Header(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
                pose=PoseWithCovariance(
                    pose=Pose(
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
                    twist=Twist(
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

    def test_NavMsgsOdometry_init_flat_version(self, mock_ROSbag_2_trj_DC):
        md = mock_ROSbag_2_trj_DC
        dc_ = NavMsgsOdometryFlat(
                feature_name="/pf/pose/odom",
                header=Header(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
                pose_pose_position_x=md.a,
                pose_pose_position_y=md.a,
                pose_pose_position_z=md.a,
                pose_pose_orientation_x=md.a,
                pose_pose_orientation_y=md.a,
                pose_pose_orientation_z=md.a,
                pose_pose_orientation_w=md.a,
                pose_covariance=md.c,
                twist_twist_linear_x=md.a,
                twist_twist_linear_y=md.a,
                twist_twist_linear_z=md.a,
                twist_twist_angular_x=md.a,
                twist_twist_angular_y=md.a,
                twist_twist_angular_z=md.a,
                twist_covariance=md.c,
                )
        print(dc_)
        assert dc_._init_trj_axe == 0

    def test_AckermannMsgsAckermannDriveStamped_init(self, mock_ROSbag_2_trj_DC):
        md = mock_ROSbag_2_trj_DC
        dc_ = AckermannMsgsAckermannDriveStamped(
                feature_name="/ackermann_cmd",
                header=Header(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
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
                header=Header(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
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
                header=Header(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
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
