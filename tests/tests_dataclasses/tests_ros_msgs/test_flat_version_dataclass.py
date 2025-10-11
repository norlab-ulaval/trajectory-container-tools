# coding=utf-8
from trajectory_container_tools.dataclasses import Header
from trajectory_container_tools.dataclasses.ros_msgs.flat_version_dataclass import \
    NavMsgsOdometryFlat, SensorMsgsImuFlat


def test_NavMsgsOdometry_init_flat_version(mock_ROSbag_2_trj_DC):
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
    assert dc_._time_axis == 0


def test_SensorMsgsImuFlat_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = SensorMsgsImuFlat(
        feature_name="/sensors/imu/raw",
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
    assert dc_._time_axis == 0
