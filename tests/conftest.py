# coding=utf-8
from dataclasses import asdict, dataclass
from typing import Dict, Union

import numpy as np
import pytest

from .rosbag_test_utils import (
    RosBagConfig,
    get_rosbag_vaul_f110_grand_salon_path,
    get_rosbag_vaul_f1tenth_nx_orin_path_filtered_short,
    get_rosbag_vaul_f1tenth_nx_orin_path_offending_timestamps,
)
from trajectory_container_tools.dataclasses.ros_msgs.non_trajectory_dataclass import (
    Tf2MsgsTFMessage,
    )
from trajectory_container_tools.dataclasses import AckermannMsgsAckermannDriveStamped, \
    NavMsgsOdometry, Scan, SensorMsgsImu, VescMsgsVescImuStamped
from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import Header

TRJ_LEN = 40


# ====Mock pandas dataframe cases==================================================================
@dataclass()
class MockDataContainer:
    name: str
    a: np.ndarray
    b: np.ndarray
    c: np.ndarray
    ts: np.ndarray
    batch: bool


@pytest.fixture(scope="function")
def mock_DF_2_trj_DC() -> MockDataContainer:
    """Mock pandas dataframe to trajectory dataclass: case even data"""
    return MockDataContainer(
        name="mock_data",
        a=np.ones((10, TRJ_LEN)),
        b=np.ones((10, TRJ_LEN)),
        c=np.ones((10, TRJ_LEN)),
        ts=np.arange(0, TRJ_LEN),
        batch=True,
    )


@pytest.fixture(scope="function")
def mock_DF_2_trj_DC_range() -> MockDataContainer:
    """Mock pandas dataframe to trajectory dataclass: case incremental data"""
    return MockDataContainer(
        name="mock_data_incremental",
        a=np.arange(10 * TRJ_LEN).reshape((TRJ_LEN, 10)).T,
        b=np.arange(10 * TRJ_LEN).reshape((TRJ_LEN, 10)).T,
        c=np.arange(10 * TRJ_LEN).reshape((TRJ_LEN, 10)).T,
        ts=np.arange(0, TRJ_LEN),
        batch=True,
    )


@pytest.fixture(scope="function")
def mock_DF_2_trj_DC_uneven_time_index() -> MockDataContainer:
    """Mock pandas dataframe to trajectory dataclass, case uneven dimensions across feature"""
    return MockDataContainer(
        name="mock_data_uneven",
        a=np.ones((10, TRJ_LEN)),
        b=np.ones((10, TRJ_LEN)),
        c=np.ones((9, 39)),
        ts=np.arange(0, TRJ_LEN),
        batch=True,
    )


# ====Mock rosbag topics cases=====================================================================
TS_START = 1000
TS_STOP = 2000


@dataclass()
class MockROSbagDataContainer:
    name: str
    a: np.ndarray
    b: np.ndarray
    c: np.ndarray
    batch: bool
    header: Header = Header(
        frame_id="map",
        timestamps=np.arange(
            TS_START, TS_STOP, (TS_STOP - TS_START) / TRJ_LEN, dtype=int
        ),
    )
    ts_idx: np.ndarray = np.arange(0, TRJ_LEN)


@pytest.fixture(scope="function")
def mock_ROSbag_2_trj_DC() -> MockROSbagDataContainer:
    """Mock rosbag to trajectory dataclass: case even data"""
    return MockROSbagDataContainer(
        name="/mocked/topic/name",
        a=np.ones((TRJ_LEN,)),
        b=np.ones((TRJ_LEN,)),
        c=np.ones((TRJ_LEN, 36)),
        batch=False,
    )


@pytest.fixture(scope="function")
def mock_ROSbag_2_trj_DC_range() -> MockROSbagDataContainer:
    """Mock rosbag to trajectory dataclass: case incremental data"""
    return MockROSbagDataContainer(
        name="/mocked/topic/name",
        a=np.arange(TRJ_LEN),
        b=np.arange(TRJ_LEN),
        c=np.arange(TRJ_LEN * 36).reshape((TRJ_LEN, 36)),
        batch=False,
    )


@pytest.fixture(scope="function")
def mock_ROSbag_2_trj_DC_longer_range() -> MockROSbagDataContainer:
    """Mock rosbag to trajectory dataclass: case incremental data"""
    return MockROSbagDataContainer(
        name="/mocked/topic/name",
        a=np.arange(TRJ_LEN + 9),
        b=np.arange(TRJ_LEN + 9),
        c=np.arange((TRJ_LEN + 9) * 36).reshape((TRJ_LEN + 9, 36)),
        batch=False,
    )


@pytest.fixture(scope="function")
def mock_ROSbag_2_trj_DC_uneven_time_index() -> MockROSbagDataContainer:
    """Mock rosbag to trajectory dataclass, case uneven dimensions across feature"""
    return MockROSbagDataContainer(
        name="/mocked/topic/name/",
        a=np.ones((TRJ_LEN,)),
        b=np.ones((TRJ_LEN,)),
        c=np.ones((TRJ_LEN - 1, 36)),
        header=Header(frame_id="map", timestamps=(np.arange(10)) * 10 + 1000),
        batch=False,
    )


@pytest.fixture(scope="function")
def mock_trajectory_dict_ordered(
    mock_ROSbag_2_trj_DC_range,
) -> Dict[str, Union[str, int, np.ndarray]]:
    ordered_trajectory_dict = asdict(mock_ROSbag_2_trj_DC_range)

    timestamps_ = []
    for each_idx in np.arange(mock_ROSbag_2_trj_DC_range.header.trajectory_len):
        timestamps_.append(mock_ROSbag_2_trj_DC_range.header.timestamps[each_idx].stamps)

    ordered_trajectory_dict["feature_name"] = "/mock_ROSbag_2_trj_DC_range"
    ordered_trajectory_dict["header"] = Header(
        frame_id=mock_ROSbag_2_trj_DC_range.header.frame_id,
        timestamps=np.array(timestamps_),
    )
    # print(ordered_trajectory_dict)

    return ordered_trajectory_dict


@pytest.fixture(scope="function")
def mock_trajectory_dict_unordered(
    mock_trajectory_dict_ordered,
) -> Dict[str, Union[str, int, np.ndarray]]:
    unordered_trajectory_dict = mock_trajectory_dict_ordered

    unordered_idx = np.arange(TRJ_LEN)
    np.random.shuffle(unordered_idx)

    for each in unordered_trajectory_dict:
        if isinstance(each, np.ndarray):
            each = each[unordered_idx]

    # print(unordered_idx)
    # print(unordered_trajectory_dict)

    return unordered_trajectory_dict


# ==== rosbag related =============================================================================


@pytest.fixture(scope="function")
def setup_rosbag_three_topics_filtered():
    bag_path, bag_name = get_rosbag_vaul_f110_grand_salon_path(offending=False)

    ros_bag_config = RosBagConfig(
        bag_name=bag_name,
        ts_fast_forward=None,
        ts_window=None,
        bag_path=bag_path,
        feature_config={
            "/odom": NavMsgsOdometry,
            "/teleop": AckermannMsgsAckermannDriveStamped,
            "/sensors/imu/raw": SensorMsgsImu,
        },
    )
    return ros_bag_config


@pytest.fixture(scope="function")
def setup_rosbag_six_topics_filtered():
    bag_path, bag_name, selected_topic = get_rosbag_vaul_f1tenth_nx_orin_path_filtered_short()

    ros_bag_config = RosBagConfig(
        bag_name=bag_name,
        ts_fast_forward=None,
        ts_window=None,
        bag_path=bag_path,
        feature_config={
            "/odom": NavMsgsOdometry,
            "/tf": Tf2MsgsTFMessage,
            "/scan": Scan,
            "/teleop": AckermannMsgsAckermannDriveStamped,
            "/sensors/imu/raw": SensorMsgsImu,
            "/sensors/imu": VescMsgsVescImuStamped,
        },
    )
    return ros_bag_config

@pytest.fixture(scope="function")
def setup_rosbag_six_topics_offending_timestamps():
    bag_path, bag_name, selected_topic = get_rosbag_vaul_f1tenth_nx_orin_path_offending_timestamps()

    ros_bag_config = RosBagConfig(
        bag_name=bag_name,
        ts_fast_forward=None,
        ts_window=None,
        bag_path=bag_path,
        feature_config={
            "/pf/pose/odom": NavMsgsOdometry,
            "/tf": Tf2MsgsTFMessage,
            "/scan": Scan,
            "/ackermann_cmd": AckermannMsgsAckermannDriveStamped,
            "/teleop": AckermannMsgsAckermannDriveStamped,
            "/sensors/imu/raw": SensorMsgsImu,
        },
    )
    return ros_bag_config
