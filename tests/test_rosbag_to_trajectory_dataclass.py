# coding=utf-8
from dataclasses import asdict
from typing import Dict, Type, Union

import pytest
import numpy as np

from trajectory_container_tools.rosbag_tools import (
    aggregate_multiple_features_from_rosbag,
    extract_single_feature_from_rosbag,
    _fix_sequence_ordering_base_on_timestamps,
)

from trajectory_container_tools.dataclasses.rosbag_feature_dataclass import (
    AckermannMsgsAckermannDriveStamped, NavMsgsOdometry,
    RosBagFeatureDataclass, SensorMsgsImu, Tf2MsgsTFMessage,
    )

from trajectory_container_tools.utils.data_sanity_checks import timestamp_sanity_check


class TestExtractROSBagFeature:
    def test_extract_single_feature_from_rosbag(self, setup_rosbag_from_tests_dir):
        container = extract_single_feature_from_rosbag(
            rosbag_path=setup_rosbag_from_tests_dir.bag_path,
            feature_name="/odom",
            data_container_type=NavMsgsOdometry,
        )

        print(container)

        assert container.feature_name is "/odom"
        assert container.trajectory_len == 376

    def test_bad_argument(self, setup_rosbag_from_tests_dir):
        fn = "/aaaaaaackermann_cmddd"

        mock_value = np.arange(10)
        bad_argument = AckermannMsgsAckermannDriveStamped(
            feature_name=fn,
            header_FrameId="",
            drive_steeringAngle=mock_value,
            drive_steeringAngleVelocity=mock_value,
            drive_speed=mock_value,
            drive_acceleration=mock_value,
            drive_jerk=mock_value,
            timestamps=mock_value,
            timestep_index=mock_value,
        )

        with pytest.raises(AttributeError):
            # noinspection PyTypeChecker
            container = extract_single_feature_from_rosbag(
                rosbag_path=setup_rosbag_from_tests_dir.bag_path,
                feature_name=fn,
                data_container_type=bad_argument,
            )

    def test_fail_no_existing_feature(self, setup_rosbag_from_tests_dir):
        with pytest.raises(ValueError):
            extract_single_feature_from_rosbag(
                rosbag_path=setup_rosbag_from_tests_dir.bag_path,
                feature_name="/aaaaaaackermann_cmddd",
                data_container_type=AckermannMsgsAckermannDriveStamped,
            )

    def test_no_existing_feature_dimension(self, setup_rosbag_from_tests_dir):
        with pytest.raises(ValueError):
            extract_single_feature_from_rosbag(
                rosbag_path=setup_rosbag_from_tests_dir.bag_path,
                feature_name="/aaaaaaackermann_cmddd",
                data_container_type=NavMsgsOdometry,
            )

    @pytest.mark.skip(reason="to implement")  # ToDo: implement test case
    def test_missing_timestep(self, setup_rosbag_from_tests_dir):
        col_label = "/ackermann_cmd"
        df_missing = setup_rosbag_from_tests_dir.drop(f"{col_label}_x_9", axis=1)

        with pytest.raises(ValueError):
            extract_single_feature_from_rosbag(
                rosbag_path=df_missing,
                feature_name=col_label,
                data_container_type=AckermannMsgsAckermannDriveStamped,
            )


class TestExtractROSBagMultifeature:
    @pytest.fixture
    def setup_feature_config_new_type(self):
        feature_config: dict = {
            "/odometry/filtered": NavMsgsOdometry,
            "/odom": NavMsgsOdometry,
            "/tf": (
                "Tf2MsgsTFMessage",
                "transform_translation_x",
                "transform_translation_y",
                "transform_translation_z",
            ),
        }
        return feature_config

        # '/sensors/imu/raw': SensorMsgsImu,

    @pytest.fixture
    def setup_feature_config_known_type(self):
        feature_config: dict = {
            "/odometry/filtered": NavMsgsOdometry,
            "/odom": NavMsgsOdometry,
            "/tf": Tf2MsgsTFMessage,
        }
        return feature_config

        # '/sensors/imu/raw': SensorMsgsImu,

    def test_aggregate_multiple_features_from_rosbag_with_new_type(
        self, setup_rosbag_from_tests_dir, setup_feature_config_new_type
    ):
        features_container = aggregate_multiple_features_from_rosbag(
            rosbag_path=setup_rosbag_from_tests_dir.bag_path,
            dataset_info=None,
            features_config=setup_feature_config_new_type,
        )

        print(features_container)

        assert isinstance(features_container.topic_tf, RosBagFeatureDataclass)
        assert features_container.topic_tf.feature_name == "/tf"
        assert features_container.topic_tf.get_dimension_names() == (
            "header_FrameId",
            "timestamps",
            "transform_translation_x",
            "transform_translation_y",
            "transform_translation_z",
        )

        assert isinstance(features_container.topic_odometry_filtered, NavMsgsOdometry)
        assert features_container.topic_odometry_filtered.feature_name == "/odometry/filtered"
        # assert isinstance(features_container.topic_sensors_imu_raw, SensorMsgsImu)
        # assert features_container.topic_sensors_imu_raw.feature_name == '/sensors/imu/raw'

        assert isinstance(features_container.topic_odom, RosBagFeatureDataclass)
        assert features_container.topic_odom.feature_name == "/odom"

    def test_aggregate_multiple_features_from_rosbag_with_known_type(
        self, setup_rosbag_from_tests_dir, setup_feature_config_known_type
    ):
        features_container = aggregate_multiple_features_from_rosbag(
            rosbag_path=setup_rosbag_from_tests_dir.bag_path,
            dataset_info=None,
            features_config=setup_feature_config_known_type,
        )

        print(features_container)

        assert isinstance(features_container.topic_tf, RosBagFeatureDataclass)
        assert features_container.topic_tf.feature_name == "/tf"
        assert features_container.topic_tf.get_dimension_names() == (
            "header_FrameId",
            "timestamps",
            "childFrameId",
            "transform_translation_x",
            "transform_translation_y",
            "transform_translation_z",
            "transform_rotation_x",
            "transform_rotation_y",
            "transform_rotation_z",
            "transform_rotation_w",
        )

        assert isinstance(features_container.topic_odometry_filtered, NavMsgsOdometry)
        assert features_container.topic_odometry_filtered.feature_name == "/odometry/filtered"
        # assert isinstance(features_container.topic_sensors_imu_raw, SensorMsgsImu)
        # assert features_container.topic_sensors_imu_raw.feature_name == '/sensors/imu/raw'

        assert isinstance(features_container.topic_odom, RosBagFeatureDataclass)
        assert features_container.topic_odom.feature_name == "/odom"

    def test_extract_dataframe_multifeature_misspecification(
        self, setup_rosbag_from_tests_dir, setup_feature_config_known_type
    ):
        setup_feature_config_known_type_bad = setup_feature_config_known_type.copy()
        setup_feature_config_known_type_bad["/pf/pose/odom"] = (
            "AckermannMsgsAckermannDriveStamped",
        )

        with pytest.raises(KeyError):
            feats = aggregate_multiple_features_from_rosbag(
                rosbag_path=setup_rosbag_from_tests_dir.bag_path,
                dataset_info="",
                features_config=setup_feature_config_known_type_bad,
            )

            print(feats)


class TestTrajectorySequenceOrderingLogic:
    def test_fix_sequence_ordering_base_on_timestamps_case_input_ordered(
        self, mock_trajectory_dict_ordered
    ):
        fixed_trajectory_dict = _fix_sequence_ordering_base_on_timestamps(
            trajectory_dict=mock_trajectory_dict_ordered,
            data_container_type_=RosBagFeatureDataclass,
        )

        timestamp_sanity_check(fixed_trajectory_dict)

    def test_fix_sequence_ordering_base_on_timestamps_case_input_unordered(
        self, mock_trajectory_dict_unordered, mock_trajectory_dict_ordered
    ):
        fixed_trajectory_dict = _fix_sequence_ordering_base_on_timestamps(
            trajectory_dict=mock_trajectory_dict_unordered,
            data_container_type_=RosBagFeatureDataclass,
        )

        timestamp_sanity_check(fixed_trajectory_dict)

        assert fixed_trajectory_dict == mock_trajectory_dict_ordered

        print(fixed_trajectory_dict)
