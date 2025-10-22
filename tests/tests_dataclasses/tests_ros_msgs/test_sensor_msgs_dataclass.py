# coding=utf-8
from trajectory_container_tools.dataclasses import (
    GeometryMsgsQuaternion,
    GeometryMsgsVector3,
    SensorMsgsImu,
    SensorMsgsLaserScan,
    StdMsgsHeader,
)


def test_SensorMsgsLaserScan_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = SensorMsgsLaserScan(
        feature_name="/scan",
        bag_recorded_timestamps=md.bag_recorded_timestamps,
        header=StdMsgsHeader(
            frame_id=md.header.frame_id, timestamps=md.header.timestamps
        ),
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


def test_SensorMsgsImu_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = SensorMsgsImu(
        feature_name="/sensors/imu/raw",
        bag_recorded_timestamps=md.bag_recorded_timestamps,
        header=StdMsgsHeader(
            frame_id=md.header.frame_id, timestamps=md.header.timestamps
        ),
        orientation=GeometryMsgsQuaternion(x=md.a, y=md.a, z=md.a, w=md.a),
        orientationCovariance=md.c,
        angularVelocity=GeometryMsgsVector3(x=md.a, y=md.a, z=md.a),
        angularVelocityCovariance=md.c,
        linearAcceleration=GeometryMsgsVector3(x=md.a, y=md.a, z=md.a),
        linearAccelerationCovariance=md.c,
    )
    print(dc_)
    assert dc_._time_axis == 0
