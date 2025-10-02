# coding=utf-8
import os
import shutil

import pytest

import trajectory_container_tools as tct
from trajectory_container_tools.utils.ros2_utils.rosbag_eda.rosbag_timestamp_eda import (
    run_rosbag_timestamp_eda,
)


@pytest.fixture(scope="module")
def setup_teardown_artifact_dir():
    eda_dir_path = f"tests/artifact"
    test_dir = f"tests_rosbag_timestamp_eda_run{os.environ.get('PYTEST_XDIST_WORKER')}"

    yield os.path.join(eda_dir_path, test_dir)

    original_dir = os.getcwd()
    os.chdir(eda_dir_path)
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.chdir(original_dir)


def test_run_rosbag_timestamp_eda_default_exp_dir(
    setup_teardown_artifact_dir, setup_rosbag_six_topics_filtered
):
    eda_dir_path = setup_teardown_artifact_dir
    run_rosbag_timestamp_eda(
        bag_path=setup_rosbag_six_topics_filtered.bag_path,
        eda_dir_path=eda_dir_path,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
        fast_forward_ns=None,
        window_ns=500000000,
        experiment_dir=None,
        show_plot=False,
    )

    mock_exp_dir_path = os.path.join(
        eda_dir_path, setup_rosbag_six_topics_filtered.bag_name
    )
    assert os.path.exists(mock_exp_dir_path)
    assert os.path.exists(os.path.join(mock_exp_dir_path, "logs"))
    assert os.path.exists(os.path.join(mock_exp_dir_path, "plots"))


def test_run_rosbag_timestamp_eda_override_exp_dir(
    setup_teardown_artifact_dir, setup_rosbag_six_topics_filtered
):
    eda_dir_path = setup_teardown_artifact_dir
    run_rosbag_timestamp_eda(
        bag_path=setup_rosbag_six_topics_filtered.bag_path,
        eda_dir_path=eda_dir_path,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
        fast_forward_ns=None,
        window_ns=500000000,
        experiment_dir="mock_experiement_dir",
        show_plot=False,
    )

    mock_exp_dir_path = os.path.join(eda_dir_path, "mock_experiement_dir")
    assert os.path.exists(mock_exp_dir_path)
    assert os.path.exists(os.path.join(mock_exp_dir_path, "logs"))
    assert os.path.exists(os.path.join(mock_exp_dir_path, "plots"))


def test_run_rosbag_timestamp_eda_full_bag(
    setup_teardown_artifact_dir, setup_rosbag_six_topics_filtered
):
    eda_dir_path = setup_teardown_artifact_dir
    tc = run_rosbag_timestamp_eda(
        bag_path=setup_rosbag_six_topics_filtered.bag_path,
        eda_dir_path=eda_dir_path,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
        fast_forward_ns=None,
        window_ns=None,
        show_plot=False,
    )
    print(tc)
    assert isinstance(tc, tct.AbstractMultifeatureDataclass)

    assert tc.topic_odom.trajectory_len == 864
    assert tc.topic_tf.transforms[0].trajectory_len == 866
    assert tc.topic_scan.trajectory_len == 691
    assert tc.topic_teleop.trajectory_len == 783
    assert tc.topic_sensors_imu_raw.trajectory_len == 859
    assert tc.topic_sensors_imu.trajectory_len == 857


def test_run_rosbag_timestamp_eda_window(
    setup_teardown_artifact_dir, setup_rosbag_six_topics_filtered
):
    eda_dir_path = setup_teardown_artifact_dir
    tc = run_rosbag_timestamp_eda(
        bag_path=setup_rosbag_six_topics_filtered.bag_path,
        eda_dir_path=eda_dir_path,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
        fast_forward_ns=setup_rosbag_six_topics_filtered.ts_fast_forward,
        window_ns=setup_rosbag_six_topics_filtered.ts_window,
        show_plot=False,
    )
    print(tc)
    assert isinstance(tc, tct.AbstractMultifeatureDataclass)

    assert tc.topic_odom.trajectory_len == 364
    assert tc.topic_tf.transforms[0].trajectory_len == 364
    assert tc.topic_scan.trajectory_len == 290
    assert tc.topic_teleop.trajectory_len == 307
    assert tc.topic_sensors_imu_raw.trajectory_len == 364
    assert tc.topic_sensors_imu.trajectory_len == 364
