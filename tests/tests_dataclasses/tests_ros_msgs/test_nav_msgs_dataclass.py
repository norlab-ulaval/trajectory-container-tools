# coding=utf-8

from trajectory_container_tools.dataclasses.ros_msgs.geometry_msgs_dataclass import (
    GeometryMsgsPoint,
    GeometryMsgsQuaternion,
    GeometryMsgsVector3,
)
from trajectory_container_tools.dataclasses import (
    GeometryMsgsPose,
    GeometryMsgsPoseWithCovariance,
    GeometryMsgsTwist,
    GeometryMsgsTwistWithCovariance,
    NavMsgsOdometry,
    StdMsgsHeader,
)


def test_NavMsgsOdometry_init_nested_version(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = NavMsgsOdometry(
        feature_name="/pf/pose/odom",
        bag_recorded_timestamps=md.bag_recorded_timestamps,
        header=StdMsgsHeader(
            frame_id=md.header.frame_id, timestamps=md.header.timestamps
        ),
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
