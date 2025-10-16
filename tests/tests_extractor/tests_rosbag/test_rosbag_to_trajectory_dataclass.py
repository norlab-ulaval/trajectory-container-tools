# coding=utf-8
from typing import Union

import pytest
import numpy as np

from tests.rosbag_test_utils import get_rosbag_vaul_f110_grand_salon_path
from trajectory_container_tools.extractor.rosbag_to_tct import (
    from_rosbag,
    extract_rosbag_feature,
)
from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import Header

from trajectory_container_tools.dataclasses.ros_msgs.non_trajectory_dataclass import (
    Tf2MsgsTFMessage,
)
from trajectory_container_tools.dataclasses import (
    AckermannMsgsAckermannDrive,
    AckermannMsgsAckermannDriveStamped,
    NavMsgsOdometry,
    RosStampedDataclass,
    Scan,
    SensorMsgsImu,
    VescMsgsVescImuStamped,
)
from trajectory_container_tools.temporal.timestamps import (
    TimestampCausalOrderingError,
)


class TestExtractROSBagFeature:
    def test_extract_single_feature_from_rosbag(
        self, setup_rosbag_three_topics_filtered
    ):
        container = extract_rosbag_feature(
            rosbag_path=setup_rosbag_three_topics_filtered.bag_path,
            feature_name="/odom",
            data_container_type=NavMsgsOdometry,
        )

        print(container)

        assert container.feature_name is "/odom"
        assert container.trajectory_len == 3120

    def test_populate_nested_trajectory_dataclass(
        self, setup_rosbag_three_topics_filtered
    ):
        container: Union[NavMsgsOdometry, RosStampedDataclass]
        container = extract_rosbag_feature(
            rosbag_path=setup_rosbag_three_topics_filtered.bag_path,
            feature_name="/odom",
            data_container_type=NavMsgsOdometry,
        )

        print(container)

        assert container.pose.feature_name is None
        assert container.twist.feature_name is None
        assert container.pose.pose.feature_name is None
        assert isinstance(container.pose.pose.position.x, np.ndarray)
        assert container.pose.pose.trajectory_len == container.trajectory_len
        assert len(container.pose.pose.position.x) == container.trajectory_len

    def test_bad_argument(self, setup_rosbag_three_topics_filtered):
        fn = "/aaaaaaackermann_cmddd"

        mock_value = np.arange(10)
        bad_argument = AckermannMsgsAckermannDriveStamped(
            feature_name=fn,
            header=Header(frame_id="", timestamps=mock_value),
            drive=AckermannMsgsAckermannDrive(
                steeringAngle=mock_value,
                steeringAngleVelocity=mock_value,
                speed=mock_value,
                acceleration=mock_value,
                jerk=mock_value,
            ),
            # timesteps_indices=mock_value,
        )

        with pytest.raises(AttributeError):
            # noinspection PyTypeChecker
            container = extract_rosbag_feature(
                rosbag_path=setup_rosbag_three_topics_filtered.bag_path,
                feature_name=fn,
                data_container_type=bad_argument,
            )

    def test_fail_no_existing_feature(self, setup_rosbag_three_topics_filtered):
        with pytest.raises(ValueError):
            extract_rosbag_feature(
                rosbag_path=setup_rosbag_three_topics_filtered.bag_path,
                feature_name="/aaaaaaackermann_cmddd",
                data_container_type=AckermannMsgsAckermannDriveStamped,
            )

    def test_no_existing_feature_dimension(self, setup_rosbag_three_topics_filtered):
        with pytest.raises(ValueError):
            extract_rosbag_feature(
                rosbag_path=setup_rosbag_three_topics_filtered.bag_path,
                feature_name="/aaaaaaackermann_cmddd",
                data_container_type=NavMsgsOdometry,
            )

    def test_catch_timestamps_sanity_check_error(self):
        # 2024-03-21_14-52-35-offending-timestamps
        bag_path, bag_name = get_rosbag_vaul_f110_grand_salon_path(offending=True)

        with pytest.raises(TimestampCausalOrderingError) as exc_info:
            extract_rosbag_feature(
                rosbag_path=bag_path,
                feature_name="/teleop",
                data_container_type=AckermannMsgsAckermannDriveStamped,
            )
        print(f"{exc_info=}")
        error_msg = (
            "Detected timestamps causal ordering violation in rosbag /teleop topic "
            "message!\n\n"
            "Timestamp causal ordering violations:\n"
            "    Number of offending timestamps 15/3409"
        )
        assert error_msg in exc_info.value.args[0]


class TestExtractROSBagMultifeature:
    @pytest.fixture
    def setup_feature_config_custom_type(self):
        feature_config: dict = {
            "/odom": NavMsgsOdometry,
            "/sensors/imu/raw": (
                "SensorMsgsImuMinimal",
                "orientation_x",
                "orientation_y",
                "orientation_z",
            ),
        }
        return feature_config

    @pytest.fixture
    def setup_feature_config_known_type(self):
        feature_config: dict = {
            "/teleop": AckermannMsgsAckermannDriveStamped,
            "/odom": NavMsgsOdometry,
            "/sensors/imu/raw": SensorMsgsImu,
        }
        return feature_config

        # '/sensors/imu/raw': SensorMsgsImu,

    def test_features_config_misspecification(
        self, setup_rosbag_three_topics_filtered, setup_feature_config_known_type
    ):
        setup_feature_config_known_type_bad = setup_feature_config_known_type.copy()
        setup_feature_config_known_type_bad["/pf/pose/odom"] = (
            "AckermannMsgsAckermannDriveStamped",
        )

        with pytest.raises(KeyError):
            feats = from_rosbag(rosbag_path=setup_rosbag_three_topics_filtered.bag_path,
                                dataset_info="",
                                features_config=setup_feature_config_known_type_bad)

            print(feats)

    def test_with_custom_type(
        self, setup_rosbag_three_topics_filtered, setup_feature_config_custom_type
    ):
        mf_container = from_rosbag(rosbag_path=setup_rosbag_three_topics_filtered.bag_path,
                                   dataset_info=None,
                                   features_config=setup_feature_config_custom_type,
                                   chunk_on='/odom')

        print(mf_container)

        assert isinstance(mf_container.topic_sensors_imu_raw, RosStampedDataclass)
        assert not isinstance(mf_container.topic_sensors_imu_raw, SensorMsgsImu)
        assert (
                mf_container.topic_sensors_imu_raw.feature_name == "/sensors/imu/raw"
        )
        assert mf_container.topic_sensors_imu_raw.get_dimension_names() == (
            "header",
            "orientation_x",
            "orientation_y",
            "orientation_z",
        )

        assert isinstance(mf_container.topic_odom, NavMsgsOdometry)
        assert mf_container.topic_odom.feature_name == "/odom"

    def test_with_known_type_three_topics(
        self, setup_rosbag_three_topics_filtered, setup_feature_config_known_type
    ):
        mf_container = from_rosbag(rosbag_path=setup_rosbag_three_topics_filtered.bag_path,
                                   dataset_info=None,
                                   features_config=setup_feature_config_known_type)

        print(mf_container)

        assert isinstance(
            mf_container.topic_teleop, AckermannMsgsAckermannDriveStamped
        )
        assert mf_container.topic_teleop.feature_name == "/teleop"

        assert (
                mf_container.topic_sensors_imu_raw.feature_name == "/sensors/imu/raw"
        )
        assert isinstance(mf_container.topic_sensors_imu_raw, SensorMsgsImu)

        assert isinstance(mf_container.topic_odom, RosStampedDataclass)
        assert mf_container.topic_odom.feature_name == "/odom"

    def test_with_known_type_six_topics(self, setup_rosbag_six_topics_filtered):
        """
        Test on a wider selection of topics including some with special case handling e.g., /tf
        
          - '/odom': NavMsgsOdometry,
          - '/tf': Tf2MsgsTFMessage,
          - '/scan': Scan,
          - '/teleop': AckermannMsgsAckermannDriveStamped,
          - '/sensors/imu/raw': SensorMsgsImu,
          - '/sensors/imu': VescMsgsVescImuStamped,
        
        """""

        mf_container = from_rosbag(setup_rosbag_six_topics_filtered.bag_path,
                                   dataset_info=setup_rosbag_six_topics_filtered.bag_name,
                                   features_config={
                                           "/odom":            NavMsgsOdometry,
                                           "/tf":              Tf2MsgsTFMessage,
                                           "/scan":            Scan,
                                           "/teleop":          AckermannMsgsAckermannDriveStamped,
                                           "/sensors/imu/raw": SensorMsgsImu,
                                           "/sensors/imu":     VescMsgsVescImuStamped,
                                           }, start=None, stop=None)

        # Minimum logic to validate run success
        print(mf_container)
