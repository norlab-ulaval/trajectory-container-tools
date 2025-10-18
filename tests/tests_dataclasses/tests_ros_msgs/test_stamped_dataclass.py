# coding=utf-8

from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import (
    StdMsgsHeader,
    GeometryMsgsPoint,
    GeometryMsgsQuaternion,
    GeometryMsgsVector3,
)
from trajectory_container_tools.dataclasses import (
    AckermannMsgsAckermannDrive,
    AckermannMsgsAckermannDriveStamped,
    NavMsgsOdometry,
    SensorMsgsLaserScan,
    SensorMsgsImu,
    VescMsgsVescImuStamped,
)
from trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass import (
    GeometryMsgsPose,
    GeometryMsgsPoseWithCovariance,
    GeometryMsgsTwist,
    GeometryMsgsTwistWithCovariance, VescMsgsVescImu,
)


def test_NavMsgsOdometry_init_nested_version(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = NavMsgsOdometry(
        feature_name="/pf/pose/odom",
        header=StdMsgsHeader(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
        pose=GeometryMsgsPoseWithCovariance(
            pose=GeometryMsgsPose(
                position=GeometryMsgsPoint(x=md.a, y=md.a, z=md.a),
                orientation=GeometryMsgsQuaternion(x=md.a, y=md.a, z=md.a, w=md.a),
            ),
            covariance=md.c,
        ),
        twist=GeometryMsgsTwistWithCovariance(
            twist=GeometryMsgsTwist(
                linear=GeometryMsgsVector3(x=md.a, y=md.a, z=md.a),
                angular=GeometryMsgsVector3(x=md.a, y=md.a, z=md.a),
            ),
            covariance=md.c,
        ),
    )
    print(dc_)
    assert dc_._time_axis == 0


def test_AckermannMsgsAckermannDriveStamped_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = AckermannMsgsAckermannDriveStamped(
        feature_name="/teleop",
        header=StdMsgsHeader(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
        drive=AckermannMsgsAckermannDrive(
            steeringAngle=md.a,
            steeringAngleVelocity=md.a,
            speed=md.a,
            acceleration=md.a,
            jerk=md.a,
        ),
    )
    print(dc_)
    assert dc_._time_axis == 0


def test_Scan_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = SensorMsgsLaserScan(
        feature_name="/scan",
        header=StdMsgsHeader(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
        angleMin=0.0,
        angleMax=0.0,
        angleIncrement=0.0,
        timeIncrement=0.0,
        scanTime=0.0,
        rangeMin=0.0,
        rangeMax=0.0,
        ranges=md.c,
        intensities=md.c,
    )
    print(dc_)
    assert dc_._time_axis == 0


def test_VescMsgsVescImuStamped_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = VescMsgsVescImuStamped(
        feature_name="/sensors/imu",
        header=StdMsgsHeader(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
        imu=VescMsgsVescImu(
                ypr=GeometryMsgsVector3(x=md.a, y=md.a, z=md.a),
                angularVelocity=GeometryMsgsVector3(x=md.a, y=md.a, z=md.a),
                linearAcceleration=GeometryMsgsVector3(x=md.a, y=md.a, z=md.a),
                compass=GeometryMsgsVector3(x=md.a, y=md.a, z=md.a),
                orientation=GeometryMsgsQuaternion(x=md.a, y=md.a, z=md.a, w=md.a),
                ),
    )
    print(dc_)
    assert dc_._time_axis == 0

def test_SensorMsgsImu_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = SensorMsgsImu(
        feature_name="/sensors/imu/raw",
        header=StdMsgsHeader(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
        orientation=GeometryMsgsQuaternion(x=md.a, y=md.a, z=md.a, w=md.a),
        orientationCovariance=md.c,
        angularVelocity=GeometryMsgsVector3(x=md.a, y=md.a, z=md.a),
        angularVelocityCovariance=md.c,
        linearAcceleration=GeometryMsgsVector3(x=md.a, y=md.a, z=md.a),
        linearAccelerationCovariance=md.c,
    )
    print(dc_)
    assert dc_._time_axis == 0
