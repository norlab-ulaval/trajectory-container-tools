# coding=utf-8
import os
from dataclasses import dataclass
from pathlib import Path
from typing import AnyStr, Optional, Union

import pytest
import numpy as np

from trajectory_container_tools.rosbag_to_tct import (
    aggregate_multiple_features_from_rosbag,
    check_rosbag_path_and_show_available_topics, extract_single_feature_from_rosbag,
    )
from trajectory_container_tools.trj_dataclasses.primitive_dataclass import Header

from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import (
    AckermannMsgsAckermannDriveStamped, NavMsgsOdometry,
    RosBagFeatureDataclass, Tf2MsgsTFMessage, SensorMsgsImu,
    )


@dataclass()
class RosBagConfig:
    bag_name: str
    ts_fast_forward: Optional[float]
    ts_window: Optional[float]
    bag_path: Union[Path, AnyStr]
    selected_topic: list


@pytest.fixture(scope="function")
def setup_rosbag_from_tests_dir():

    # .... Path to ROS bag in 'demo_data' directory
    # ................................................
    # For test purposes

    BAG = "2024-03-21_14-52-35-filtered"
    # BAG = "2024-03-21_14-52-35-offending-timestamps"
    rosbag_path = os.path.join(
            "demo_data",
            "rosbag_test_data",
            "rosbag-vaul-f110-grand-salon-raw-msg",
            BAG)

    # .... Setup rosbag test configuration ........................................................
    ros_bag_config = RosBagConfig(
            bag_name=BAG,
            ts_fast_forward=None,
            ts_window=None,
            bag_path=check_rosbag_path_and_show_available_topics(rosbag_path),
            selected_topic=[
                    "/teleop",
                    "/sensors/imu/raw",
                    "/odom",
                    ],
            )
    # '/ackermann_cmd',
    # '/pf/pose/odom',
    return ros_bag_config


class TestExtractROSBagFeature:

    def test_extract_single_feature_from_rosbag(self, setup_rosbag_from_tests_dir):
        container = extract_single_feature_from_rosbag(
                rosbag_path=setup_rosbag_from_tests_dir.bag_path, feature_name="/odom",
                data_container_type=NavMsgsOdometry)

        print(container)

        assert container.feature_name is "/odom"
        assert container.trajectory_len == 3120

    def test_populate_nested_trajectory_dataclass(self, setup_rosbag_from_tests_dir):
        container: Union[NavMsgsOdometry, RosBagFeatureDataclass]
        container = extract_single_feature_from_rosbag(
                rosbag_path=setup_rosbag_from_tests_dir.bag_path, feature_name="/odom",
                data_container_type=NavMsgsOdometry)

        print(container)

        assert container.pose.feature_name is None
        assert container.twist.feature_name is None
        assert container.pose.pose.feature_name is None
        assert isinstance(container.pose.pose.position_x, np.ndarray)
        assert container.pose.pose.trajectory_len == container.trajectory_len
        assert len(container.pose.pose.position_x) == container.trajectory_len

    def test_bad_argument(self, setup_rosbag_from_tests_dir):
        fn = "/aaaaaaackermann_cmddd"

        mock_value = np.arange(10)
        bad_argument = AckermannMsgsAckermannDriveStamped(
                feature_name=fn,
                header=Header(frame_id="", timestamps=mock_value),
                drive_steeringAngle=mock_value,
                drive_steeringAngleVelocity=mock_value,
                drive_speed=mock_value,
                drive_acceleration=mock_value,
                drive_jerk=mock_value,
                # timestep_index=mock_value,
                )

        with pytest.raises(AttributeError):
            # noinspection PyTypeChecker
            container = extract_single_feature_from_rosbag(
                    rosbag_path=setup_rosbag_from_tests_dir.bag_path, feature_name=fn,
                    data_container_type=bad_argument)

    def test_fail_no_existing_feature(self, setup_rosbag_from_tests_dir):
        with pytest.raises(ValueError):
            extract_single_feature_from_rosbag(rosbag_path=setup_rosbag_from_tests_dir.bag_path,
                                               feature_name="/aaaaaaackermann_cmddd",
                                               data_container_type=AckermannMsgsAckermannDriveStamped)

    def test_no_existing_feature_dimension(self, setup_rosbag_from_tests_dir):
        with pytest.raises(ValueError):
            extract_single_feature_from_rosbag(rosbag_path=setup_rosbag_from_tests_dir.bag_path,
                                               feature_name="/aaaaaaackermann_cmddd",
                                               data_container_type=NavMsgsOdometry)

    @pytest.mark.skip(reason="to implement")  # ToDo: implement test case
    def test_missing_timestep(self, setup_rosbag_from_tests_dir):
        col_label = "/ackermann_cmd"
        df_missing = setup_rosbag_from_tests_dir.drop(f"{col_label}_x_9", axis=1)

        with pytest.raises(ValueError):
            extract_single_feature_from_rosbag(rosbag_path=df_missing, feature_name=col_label,
                                               data_container_type=AckermannMsgsAckermannDriveStamped)


class TestExtractROSBagMultifeature:

    @pytest.fixture
    def setup_feature_config_new_type(self):
        feature_config: dict = {
                "/odom":            NavMsgsOdometry,
                "/sensors/imu/raw": (
                        "SensorMsgsImuMinimal",
                        "orientation_x",
                        "orientation_y",
                        "orientation_z",
                        ),
                }
        return feature_config

        # '/sensors/imu/raw': SensorMsgsImu,

    @pytest.fixture
    def setup_feature_config_known_type(self):
        feature_config: dict = {
                "/teleop":          AckermannMsgsAckermannDriveStamped,
                "/odom":            NavMsgsOdometry,
                "/sensors/imu/raw": SensorMsgsImu,
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

        assert isinstance(features_container.topic_sensors_imu_raw, RosBagFeatureDataclass)
        assert not isinstance(features_container.topic_sensors_imu_raw, SensorMsgsImu)
        assert features_container.topic_sensors_imu_raw.feature_name == '/sensors/imu/raw'
        assert features_container.topic_sensors_imu_raw.get_dimension_names() == (
                "header",
                "orientation_x",
                "orientation_y",
                "orientation_z",
                )

        assert isinstance(features_container.topic_odom, NavMsgsOdometry)
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

        assert isinstance(features_container.topic_teleop, AckermannMsgsAckermannDriveStamped)
        assert features_container.topic_teleop.feature_name == "/teleop"

        assert features_container.topic_sensors_imu_raw.feature_name == '/sensors/imu/raw'
        assert isinstance(features_container.topic_sensors_imu_raw, SensorMsgsImu)

        assert isinstance(features_container.topic_odom, RosBagFeatureDataclass)
        assert features_container.topic_odom.feature_name == "/odom"

    def test_extract_rosbag_multifeature_misspecification(
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


class TestROSBagUtilities:

    @pytest.mark.skip(reason="ToDo: implement test case")
    def test_set_timestamp(self):
        raise NotImplementedError("ToDo: implement test case ")
        set_timestamp()
