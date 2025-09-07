# coding=utf-8
import os
from dataclasses import dataclass
from typing import AnyStr, Optional, Union

import pytest
import numpy as np

from trajectory_container_tools.rosbag_tools import (
    aggregate_multiple_features_from_rosbag,
    extract_single_feature_from_rosbag,
    )

from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import (
    AckermannMsgsAckermannDriveStamped, NavMsgsOdometry,
    RosBagFeatureDataclass, Tf2MsgsTFMessage,
    )


@dataclass()
class RosBagConfig:
    bag_name: str
    ts_fast_forward: Optional[float]
    ts_window: Optional[float]
    bag_path: AnyStr
    selected_topic: list


@pytest.fixture(scope="function")
def setup_rosbag_from_tests_dir():

    # .... Path to ROS bag in 'demo_data' directory
    # ................................................
    # For test purposes

    BAG = "2024-03-21_12-25-29"
    # BAG = "2024-03-21_15-01-04"
    rosbag_path = os.path.join(
            "demo_data",
            "rosbag_test_data",
            "rosbag-vaul-f110-grand-salon-raw-msg",
            BAG)

    # .... Construct absolute path to demo data for tests execution ...............................
    # Handle cases: pycharm-born dna run and shell-born dna run
    dn_project_path = os.getenv('DN_PROJECT_PATH')
    if os.path.exists(dn_project_path):
        rosbag_path = os.path.join(dn_project_path, rosbag_path)
    else:
        rosbag_path = os.path.realpath(os.path.join('..', rosbag_path))

    assert os.path.exists(rosbag_path)

    # .... Setup rosbag test configuration ........................................................
    ros_bag_config = RosBagConfig(
            bag_name=BAG,
            ts_fast_forward=None,
            ts_window=None,
            bag_path=rosbag_path,
            selected_topic=[
                    "/odom",
                    "/odometry/filtered",
                    "/tf",
                    "/scan",
                    "/teleop",
                    "/sensors/imu/raw",
                    ],
            )
    # '/ackermann_cmd',
    # '/pf/pose/odom',
    return ros_bag_config

@pytest.fixture(scope="function")
def setup_rosbag_from_external_data_dir():
    # .... Path to ROS bag in 'external_data' directory
    # ............................................
    # For EDA and benchmark purposes only

    # BAG = "2024-03-21_12-19-00" # small circle
    # BAG = "2024-03-21_12-23-53" # medium spiral
    # BAG = "2024-03-21_12-25-29" # empty
    BAG = "2024-03-21_14-52-35"  # ★★
    # BAG = "2024-03-21_15-01-04" # empty
    # BAG = "2024-03-21_15-03-19" # empty
    # BAG = "2024-03-21_15-14-09" # ★★
    # BAG = "2024-03-21_15-26-13" # ★
    # BAG = "2024-03-21_15-35-28" # ★
    rosbag_path = os.path.join("external_data", "rosbag-vaul-f110-grand-salon-raw-msg", BAG)

    # .... Construct absolute path to demo data for tests execution ...............................
    # Handle cases: pycharm-born dna run and shell-born dna run
    dn_project_path = os.getenv('DN_PROJECT_PATH')
    if os.path.exists(dn_project_path):
        rosbag_path = os.path.join(dn_project_path, rosbag_path)
    else:
        rosbag_path = os.path.realpath(os.path.join('..', rosbag_path))

    assert os.path.exists(rosbag_path)

    # .... Setup rosbag test configuration ........................................................
    ros_bag_config = RosBagConfig(
            bag_name=BAG,
            ts_fast_forward=None,
            ts_window=None,
            bag_path=rosbag_path,
            selected_topic=[
                    "/odom",
                    "/odometry/filtered",
                    "/tf",
                    "/scan",
                    "/teleop",
                    "/sensors/imu/raw",
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
        assert container.trajectory_len == 376

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

    @pytest.mark.parametrize(
        argnames="t_enable_multiprocessing, t_chunk_size",
        argvalues=[
            (True, 1000), (True, 250), (False, 0)
        ],
        ids=['Multiprocessing enable, chunk size 1000', 'Multiprocessing enable, chunk size 250', 'Multiprocessing disable']
    )
    def test_extract_rosbag_benchmark(self, benchmark, setup_rosbag_from_external_data_dir, t_enable_multiprocessing, t_chunk_size):
        container: Union[NavMsgsOdometry, RosBagFeatureDataclass]

        def benchmark_test():
            return extract_single_feature_from_rosbag(
                rosbag_path=setup_rosbag_from_external_data_dir.bag_path, feature_name="/odom",
                data_container_type=NavMsgsOdometry,
                enable_multiprocessing=t_enable_multiprocessing,
                chunk_size=t_chunk_size
                    )

        container = benchmark(benchmark_test)

        # Minimum logic to validate run success
        print(container)
        assert isinstance(container.pose.pose.position_x, np.ndarray)

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
                "/odometry/filtered": NavMsgsOdometry,
                "/odom":              NavMsgsOdometry,
                "/tf":                (
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
                "/odom":              NavMsgsOdometry,
                "/tf":                Tf2MsgsTFMessage,
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


class TestROSBagUtilities:

    @pytest.mark.skip(reason="ToDo: implement test case")
    def test_set_timestamp(self):
        raise NotImplementedError("ToDo: implement test case ")
        set_timestamp()
