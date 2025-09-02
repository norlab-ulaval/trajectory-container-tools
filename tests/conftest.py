# coding=utf-8
from dataclasses import asdict, dataclass
from typing import AnyStr, Dict, Optional, Union
import os

import numpy as np
import pytest

from rclpy.time import Time as RosTime

TRJ_LEN = 40


# ====Mock pandas dataframe cases==================================================================
@dataclass()
class MockDataContainer:
    name: str
    a: np.ndarray
    b: np.ndarray
    c: np.ndarray
    ts: np.ndarray


@pytest.fixture(scope="function")
def mock_DF_2_trj_DC() -> MockDataContainer:
    """Mock pandas dataframe to trajectory dataclass: case even data"""
    return MockDataContainer(
        name="mock_data",
        a=np.ones((10, TRJ_LEN)),
        b=np.ones((10, TRJ_LEN)),
        c=np.ones((10, TRJ_LEN)),
        ts=np.arange(0, TRJ_LEN),
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
    header_FrameId: str = "map"
    timestamps: np.ndarray = np.arange(
        TS_START, TS_STOP, (TS_STOP - TS_START) / TRJ_LEN, dtype=int
    )
    ts_idx: np.ndarray = np.arange(0, TRJ_LEN)
    trj_axe: int = 0


@pytest.fixture(scope="function")
def mock_ROSbag_2_trj_DC() -> MockROSbagDataContainer:
    """Mock rosbag to trajectory dataclass: case even data"""
    return MockROSbagDataContainer(
        name="/mocked/topic/name",
        a=np.ones((TRJ_LEN,)),
        b=np.ones((TRJ_LEN,)),
        c=np.ones((TRJ_LEN, 36)),
    )


@pytest.fixture(scope="function")
def mock_ROSbag_2_trj_DC_range() -> MockROSbagDataContainer:
    """Mock rosbag to trajectory dataclass: case incremental data"""
    return MockROSbagDataContainer(
        name="/mocked/topic/name",
        a=np.arange(TRJ_LEN),
        b=np.arange(TRJ_LEN),
        c=np.arange(TRJ_LEN * 36).reshape((TRJ_LEN, 36)),
    )


@pytest.fixture(scope="function")
def mock_ROSbag_2_trj_DC_longer_range() -> MockROSbagDataContainer:
    """Mock rosbag to trajectory dataclass: case incremental data"""
    return MockROSbagDataContainer(
        name="/mocked/topic/name",
        a=np.arange(TRJ_LEN + 9),
        b=np.arange(TRJ_LEN + 9),
        c=np.arange((TRJ_LEN + 9) * 36).reshape((TRJ_LEN + 9, 36)),
    )


@pytest.fixture(scope="function")
def mock_ROSbag_2_trj_DC_uneven_time_index() -> MockROSbagDataContainer:
    """Mock rosbag to trajectory dataclass, case uneven dimensions across feature"""
    return MockROSbagDataContainer(
        name="/mocked/topic/name/",
        a=np.ones((TRJ_LEN,)),
        b=np.ones((TRJ_LEN,)),
        c=np.ones((TRJ_LEN - 1, 36)),
        timestamps=(np.arange(10)) * 10 + 1000,
    )


@pytest.fixture(scope="function")
def mock_trajectory_dict_ordered(
    mock_ROSbag_2_trj_DC_range,
) -> Dict[str, Union[str, int, np.ndarray]]:
    ordered_trajectory_dict = asdict(mock_ROSbag_2_trj_DC_range)

    timestamps_ = []
    for each_idx in np.arange(len(ordered_trajectory_dict["timestamps"])):
        timestamps_.append(RosTime(seconds=ordered_trajectory_dict["timestamps"][each_idx]))

    ordered_trajectory_dict["timestamps"] = np.array(timestamps_)
    print(ordered_trajectory_dict)

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
    print(unordered_trajectory_dict)

    return unordered_trajectory_dict


# ::: rosbag related ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


@dataclass()
class RosBagConfig:
    bag_name: str
    ts_fast_forward: Optional[float]
    ts_window: Optional[float]
    bag_path: AnyStr
    selected_topic: list


@pytest.fixture(scope="function")
def setup_rosbag_from_src_data_dir():
    """Rosbag stored in the data directory.
    Note: don't use in test that are going to run on CI as 'external_data/*' dir is in the
    gitignore (!)
    """
    raise UserWarning("For local tests only.")  # Mute this line for use
    BAG = "rosbag2_2023_09_25-14_27_58"
    ros_bag_config = RosBagConfig(
            bag_name=BAG,
            ts_fast_forward=10.15e9,
            ts_window=10e8,
            bag_path=os.path.realpath(
                os.path.join("../external_data/bags_vaul-f1tenth-nx-orin", BAG)),
            selected_topic=[
                    "/pf/pose/odom",
                    "/tf",
                    "/scan",
                    "/ackermann_cmd",
                    "/teleop",
                    "/sensors/imu/raw",
                    ],
            )

    return ros_bag_config


@pytest.fixture(scope="function")
def setup_rosbag_for_eda_from_tests_dir():
    """(!) This rosbag is in the gitignore for the moment as it this ~20mg and only a fraction is
    used in tests. Test using this fixture are muted in ci for the moment.
    """
    # raise UserWarning("Don't use this fixture in CI tests for now") # Mute this line for use
    BAG = "rosbag2_2023_09_25-14_20_35"
    ros_bag_config = RosBagConfig(
            bag_name=BAG,
            ts_fast_forward=17e9,
            ts_window=2e8,
            bag_path=os.path.realpath(
                    os.path.join("../tests/rosbag_test_data/vaul-f1tenth-nx-orin", BAG)
                    ),
            selected_topic=[
                    "/pf/pose/odom",
                    "/tf",
                    "/scan",
                    "/ackermann_cmd",
                    "/teleop",
                    "/sensors/imu/raw",
                    ],
            )
    return ros_bag_config


@pytest.fixture(scope="function")
def setup_rosbag_from_tests_dir():
    BAG = "2024-03-21_12-25-29"
    # BAG = "2024-03-21_15-01-04"
    ros_bag_config = RosBagConfig(
            bag_name=BAG,
            ts_fast_forward=None,
            ts_window=None,
            bag_path=os.path.realpath(
                    os.path.join("../tests/rosbag_test_data/rosbag-vaul-f110-grand-salon-raw-msg",
                                 BAG)
                    ),
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
