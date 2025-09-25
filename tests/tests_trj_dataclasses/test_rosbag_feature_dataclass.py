# coding=utf-8
import pytest

from trajectory_container_tools.rosbag_to_tct import (
    aggregate_multiple_features_from_rosbag,
)
from trajectory_container_tools.trj_dataclasses.ros2_primitive_dataclass import (
    Header,
    Point,
    Quaternion,
    Transform,
    Vector3,
)
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import (
    AckermannMsgsAckermannDrive,
    AckermannMsgsAckermannDriveStamped,
    NavMsgsOdometry,
    NavMsgsOdometryFlat,
    Pose,
    PoseWithCovariance,
    Scan,
    SensorMsgsImu,
    SensorMsgsImuFlat,
    Tf2MsgsTFMessage,
    TransformStamped,
    Twist,
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
        assert dc_._time_axis == 0

    def test_AckermannMsgsAckermannDriveStamped_init(self, mock_ROSbag_2_trj_DC):
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

    def test_Tf2MsgsTFMessage_init(self, mock_ROSbag_2_trj_DC):
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
                )
            ],
        )
        print(dc_)
        assert isinstance(dc_.transforms[0].header, Header)
        assert isinstance(dc_.transforms[1].header, Header)
        assert dc_.transforms[0].header.timestamps.stamps == pytest.approx(md.header.timestamps)
        assert id(dc_.transforms[0].header) != id(dc_.transforms[1].header)
        assert dc_.transforms[0].childFrameId == "odom"
        assert dc_.transforms[1].childFrameId == "pf_pose_odom"

    def test_Scan_init(self, mock_ROSbag_2_trj_DC):
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

    def test_SensorMsgsImu_init(self, mock_ROSbag_2_trj_DC):
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

    def test_SensorMsgsImuFlat_init(self, mock_ROSbag_2_trj_DC):
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


class TestTrajectoryDataclassFromROSBagCaseIntegration:

    def test_RosDataclass_and_RosStampedDataclass_inheriter_on_rosbag(
        self, setup_rosbag_six_topics_filtered
    ):

        container = aggregate_multiple_features_from_rosbag(
            setup_rosbag_six_topics_filtered.bag_path,
            dataset_info=setup_rosbag_six_topics_filtered.bag_name,
            features_config=setup_rosbag_six_topics_filtered.feature_config,
        )

        # Minimum logic to validate run success
        print(container)
