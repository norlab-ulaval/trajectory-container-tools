# coding=utf-8
import pytest

from trajectory_container_tools.dataclasses import Header, Tf2MsgsTFMessage
from trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass import TransformStamped
from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import Quaternion, \
    Transform, Vector3


def test_Tf2MsgsTFMessage_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = Tf2MsgsTFMessage(
        feature_name="/tf",
        transforms=[
            TransformStamped(
                header=Header(
                    frame_id=md.header.frame_id, timestamps=md.header.timestamps
                ),
                childFrameId="odom",
                transform=Transform(
                    translation=Vector3(x=md.a, y=md.a, z=md.a),
                    rotation=Quaternion(x=md.a, y=md.a, z=md.a, w=md.a),
                ),
            ),
            TransformStamped(
                header=Header(
                    frame_id=md.header.frame_id, timestamps=md.header.timestamps
                ),
                childFrameId="pf_pose_odom",
                transform=Transform(
                    translation=Vector3(x=md.a, y=md.a, z=md.a),
                    rotation=Quaternion(x=md.a, y=md.a, z=md.a, w=md.a),
                ),
            ),
        ],
    )
    print(dc_)
    assert isinstance(dc_.transforms[0].header, Header)
    assert isinstance(dc_.transforms[1].header, Header)
    assert dc_.transforms[0].header.timestamps.stamps == pytest.approx(
        md.header.timestamps.stamps
    )
    assert id(dc_.transforms[0].header) != id(dc_.transforms[1].header)
    assert dc_.transforms[0].childFrameId == "odom"
    assert dc_.transforms[1].childFrameId == "pf_pose_odom"
