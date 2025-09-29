# coding=utf-8
import pytest

from trajectory_container_tools.extractor.rosbag_to_tct import (
    from_rosbag,
)
from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import (
    Header,
    Point,
    Quaternion,
    Transform,
    Vector3,
)
from trajectory_container_tools.dataclasses.ros_msgs.non_trajectory_dataclass import (
    Tf2MsgsTFMessage,
    )
from trajectory_container_tools.dataclasses import AckermannMsgsAckermannDrive, \
    AckermannMsgsAckermannDriveStamped, NavMsgsOdometry, Scan, SensorMsgsImu
from trajectory_container_tools.dataclasses.ros_msgs.flat_version_dataclass import \
    NavMsgsOdometryFlat, SensorMsgsImuFlat
from trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass import Pose, \
    PoseWithCovariance, TransformStamped, Twist, TwistWithCovariance


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

        container = from_rosbag(
            setup_rosbag_six_topics_filtered.bag_path,
            dataset_info=setup_rosbag_six_topics_filtered.bag_name,
            features_config=setup_rosbag_six_topics_filtered.feature_config,
        )

        # Minimum logic to validate run success
        print(container)

    def test_integration_feature_iterable(self, setup_rosbag_six_topics_filtered):

        container = from_rosbag(
            setup_rosbag_six_topics_filtered.bag_path,
            dataset_info=setup_rosbag_six_topics_filtered.bag_name,
            features_config=setup_rosbag_six_topics_filtered.feature_config,
        )

        # print(container)

        # for idx in range(len(container.topic_odom)):
        #     assert container.topic_odom.header.timestamps.stamps[idx].size == 1
        #     print(f"idx: {idx} timestamps: {container.topic_odom.header.timestamps.stamps[idx]}")

        SELECTED_TOPICS = [
            "topic_odom",
            "topic_tf",
            "topic_scan",
            "topic_teleop",
            "topic_sensors_imu_raw",
            "topic_sensors_imu",
        ]
        for each in SELECTED_TOPICS:
            print(f"===={container.get_dynamic_field(each).feature_name}{'='*80}")
            if each != "topic_tf":
                for idx in range(len(container.get_dynamic_field(each))):
                    assert (
                        container.get_dynamic_field(each)
                        .header.timestamps.stamps[idx]
                        .size
                        == 1
                    )
                    print(
                        f"idx: {idx} timestamps: {container.get_dynamic_field(each).header.timestamps.stamps[idx]}"
                    )

    def test_integration_feature_getitem(self, setup_rosbag_six_topics_filtered):

        container = from_rosbag(
            setup_rosbag_six_topics_filtered.bag_path,
            dataset_info=setup_rosbag_six_topics_filtered.bag_name,
            features_config=setup_rosbag_six_topics_filtered.feature_config,
        )

        print(container)

        print("="*80, f"\n", container.topic_odom[0])
        print("="*80, f"\n", container.topic_odom.pose[0])
        print("="*80, f"\n", container.topic_odom.pose.pose[0])
        print("="*80, f"\n", container.topic_odom.pose.pose.position[0])
        print("="*80, f"\n", container.topic_odom.pose.pose.position.x[0])

        for idx in range(len(container.get_dynamic_field("topic_odom"))):
            # Check dimension getitem
            assert container.topic_odom[idx].pose.pose.position.x.size == 1
            assert container.topic_odom.pose[idx].pose.position.x.size == 1
            assert container.topic_odom.pose.pose[idx].position.x.size == 1
            assert container.topic_odom.pose.pose.position[idx].x.size == 1

            assert len(container.topic_odom[idx]) == 1
            assert len(container.topic_odom.pose[idx]) == 1
            assert len(container.topic_odom.pose.pose[idx]) == 1
            assert len(container.topic_odom.pose.pose.position[idx]) == 1

            # # Check nested timestamps getitem
            assert container.topic_odom.header.timestamps.stamps[idx].size == 1
            assert container.topic_odom.header.timestamps.delta_stamps[idx].size == 1
            # (CRITICAL) ToDo: on task end >> UN-mute this line ↓
            assert container.topic_odom.header.timestamps[idx].stamps.size == 1
            assert container.topic_odom.header[idx].timestamps.stamps.size == 1
            assert container.topic_odom[idx].header.timestamps.stamps.size == 1
