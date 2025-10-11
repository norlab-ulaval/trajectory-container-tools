# coding=utf-8

from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import (
    Header,
    Point,
    Quaternion,
    Vector3,
)
from trajectory_container_tools.dataclasses import (
    AckermannMsgsAckermannDrive,
    AckermannMsgsAckermannDriveStamped,
    NavMsgsOdometry,
    Scan,
    SensorMsgsImu,
    VescMsgsVescImuStamped,
)
from trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass import (
    Pose,
    PoseWithCovariance,
    Twist,
    TwistWithCovariance, VescMsgsVescImu,
)


def test_NavMsgsOdometry_init_nested_version(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = NavMsgsOdometry(
        feature_name="/pf/pose/odom",
        header=Header(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
        pose=PoseWithCovariance(
            pose=Pose(
                position=Point(x=md.a, y=md.a, z=md.a),
                orientation=Quaternion(x=md.a, y=md.a, z=md.a, w=md.a),
            ),
            covariance=md.c,
        ),
        twist=TwistWithCovariance(
            twist=Twist(
                linear=Vector3(x=md.a, y=md.a, z=md.a),
                angular=Vector3(x=md.a, y=md.a, z=md.a),
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
        header=Header(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
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
    dc_ = Scan(
        feature_name="/scan",
        header=Header(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
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
        header=Header(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
        imu=VescMsgsVescImu(
                ypr=Vector3(x=md.a, y=md.a, z=md.a),
                angularVelocity=Vector3(x=md.a, y=md.a, z=md.a),
                linearAcceleration=Vector3(x=md.a, y=md.a, z=md.a),
                compass=Vector3(x=md.a, y=md.a, z=md.a),
                orientation=Quaternion(x=md.a, y=md.a, z=md.a, w=md.a),
                ),
    )
    print(dc_)
    assert dc_._time_axis == 0

def test_SensorMsgsImu_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = SensorMsgsImu(
        feature_name="/sensors/imu/raw",
        header=Header(frame_id=md.header.frame_id, timestamps=md.header.timestamps),
        orientation=Quaternion(x=md.a, y=md.a, z=md.a, w=md.a),
        orientationCovariance=md.c,
        angularVelocity=Vector3(x=md.a, y=md.a, z=md.a),
        angularVelocityCovariance=md.c,
        linearAcceleration=Vector3(x=md.a, y=md.a, z=md.a),
        linearAccelerationCovariance=md.c,
    )
    print(dc_)
    assert dc_._time_axis == 0
