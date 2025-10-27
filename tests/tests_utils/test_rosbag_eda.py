# coding=utf-8

import pytest
import os
import shutil
from pathlib import Path

from tests.testing_utils_general import is_run_on_a_teamcity_continuous_integration_server
from trajectory_container_tools.dataclasses.core.abstract_trajectory_stamped_features_bag_dataclass import (
    AbstractTrajectoryStampedFeaturesBag,
)
from trajectory_container_tools.utils.general import RosImportError, dn_sanitize_path

try:
    from rosbags.rosbag2 import Reader
except (ImportError, ModuleNotFoundError):
    raise RosImportError

from trajectory_container_tools.utils.ros2_utils.rosbag_eda.eda_utils.general_utils import (
    compute_bag_target_window_nb,
)
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


@pytest.mark.skipif(
    not is_run_on_a_teamcity_continuous_integration_server(),
    reason="Only execute on build server.",
)
@pytest.mark.slow
def test_main():

    out = os.system(
        f"python3 -m trajectory_container_tools.utils.ros2_utils.rosbag_eda.rosbag_timestamp_eda"
    )

    # Note: exit(0) <==> clean exit without any errors/problems
    assert 0 == out, f"Module invocated from command line exited with error {out}"


def test_run_rosbag_timestamp_eda_default_exp_dir(
    setup_teardown_artifact_dir, setup_rosbag_six_topics_filtered
):
    eda_dir_path = setup_teardown_artifact_dir
    run_rosbag_timestamp_eda(
        bag_path=setup_rosbag_six_topics_filtered.bag_path,
        eda_dir_path=eda_dir_path,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
        chunk_on="/teleop",
        fast_forward_ns=None,
        window_ns=500000000,
        experiment_dir=None,
        show_plot=False,
    )

    mock_exp_dir_path = os.path.join(
        eda_dir_path, setup_rosbag_six_topics_filtered.bag_name
    )
    assert os.path.exists(mock_exp_dir_path)
    assert os.path.exists(os.path.join(mock_exp_dir_path, "plots"))


def test_run_rosbag_timestamp_eda_override_exp_dir(
    setup_teardown_artifact_dir, setup_rosbag_six_topics_filtered
):
    eda_dir_path = setup_teardown_artifact_dir
    run_rosbag_timestamp_eda(
        bag_path=setup_rosbag_six_topics_filtered.bag_path,
        eda_dir_path=eda_dir_path,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
        chunk_on="/teleop",
        fast_forward_ns=None,
        window_ns=500000000,
        experiment_dir="mock_experiement_dir",
        show_plot=False,
    )

    mock_exp_dir_path = os.path.join(eda_dir_path, "mock_experiement_dir")
    assert os.path.exists(mock_exp_dir_path)
    assert os.path.exists(os.path.join(mock_exp_dir_path, "plots"))


def test_run_rosbag_timestamp_eda_full_bag(
    setup_teardown_artifact_dir, setup_rosbag_six_topics_filtered
):
    eda_dir_path = setup_teardown_artifact_dir
    tc = run_rosbag_timestamp_eda(
        bag_path=setup_rosbag_six_topics_filtered.bag_path,
        eda_dir_path=eda_dir_path,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
        chunk_on="/teleop",
        fast_forward_ns=None,
        window_ns=None,
        show_plot=False,
    )
    print(tc)
    assert isinstance(tc, AbstractTrajectoryStampedFeaturesBag)

    assert tc.topic_odom.trajectory_len == 863
    assert tc.topic_tf.transforms[0].trajectory_len == 863
    assert tc.topic_scan.trajectory_len == 688
    assert tc.topic_teleop.trajectory_len == 783
    assert tc.topic_sensors_imu_raw.trajectory_len == 858
    assert tc.topic_sensors_imu.trajectory_len == 856


def test_run_rosbag_timestamp_eda_window(
    setup_teardown_artifact_dir, setup_rosbag_six_topics_filtered
):
    eda_dir_path = setup_teardown_artifact_dir
    mock_exp_dir_path = os.path.join(
        eda_dir_path, setup_rosbag_six_topics_filtered.bag_name
    )
    mock_plot_dir_path = os.path.join(mock_exp_dir_path, "plots")
    tc = run_rosbag_timestamp_eda(
        bag_path=setup_rosbag_six_topics_filtered.bag_path,
        eda_dir_path=eda_dir_path,
        features_config=setup_rosbag_six_topics_filtered.feature_config,
        chunk_on="/teleop",
        fast_forward_ns=setup_rosbag_six_topics_filtered.ts_fast_forward,
        window_ns=setup_rosbag_six_topics_filtered.ts_window,
        show_plot=False,
    )
    print(tc)
    assert isinstance(tc, AbstractTrajectoryStampedFeaturesBag)

    assert os.path.exists(mock_plot_dir_path)

    with Reader(setup_rosbag_six_topics_filtered.bag_path) as reader:
        num_plot_files = sum(
            1 for item in Path(mock_plot_dir_path).iterdir() if item.is_file()
        )
        assert num_plot_files == compute_bag_target_window_nb(
            bag_duration=reader.duration,
            fast_forward_ns=setup_rosbag_six_topics_filtered.ts_fast_forward,
        )
