# coding=utf-8
from trajectory_container_tools.dataclasses import (
    GeometryMsgsQuaternion,
    GeometryMsgsVector3,
    StdMsgsHeader,
    VescMsgsVescImu,
    VescMsgsVescImuStamped,
)


def test_VescMsgsVescImuStamped_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = VescMsgsVescImuStamped(
        feature_name="/sensors/imu",
        bag_recorded_timestamps=md.bag_recorded_timestamps,
        header=StdMsgsHeader(
            frame_id=md.header.frame_id, timestamps=md.header.timestamps
        ),
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
