# coding=utf-8
from trajectory_container_tools.dataclasses import (
    AckermannMsgsAckermannDrive,
    AckermannMsgsAckermannDriveStamped,
    StdMsgsHeader,
)


def test_AckermannMsgsAckermannDriveStamped_init(mock_ROSbag_2_trj_DC):
    md = mock_ROSbag_2_trj_DC
    dc_ = AckermannMsgsAckermannDriveStamped(
        feature_name="/teleop",
        bag_recorded_timestamps=md.bag_recorded_timestamps,
        header=StdMsgsHeader(
            frame_id=md.header.frame_id, timestamps=md.header.timestamps
        ),
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
