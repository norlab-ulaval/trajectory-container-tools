# coding=utf-8
import numpy as np
import pytest

from trajectory_container_tools.temporal import Timestamps, TimestampsInt, TimestampsFloat

try:
    from rclpy.time import Time as ROSTime
    _has_rclpy = True
except (ImportError, ModuleNotFoundError):
    _has_rclpy = False


@pytest.fixture
def setup_mock_timestamps() -> np.ndarray:
    mock_timestamps = [
        1711038330346603696,
        1711038330351773872,
        1711038330362038128,
        1711038330376558992,
        1711038330381711344,
        1711038330391960208,
        1711038330406476944,
        1711038330411627056,
        1711038330421882896,
        1711038330436485488,
    ]

    return np.array(mock_timestamps, dtype=int)


@pytest.fixture
def setup_Timestamps_object(setup_mock_timestamps) -> TimestampsInt:
    return TimestampsInt(setup_mock_timestamps)


@pytest.fixture
def setup_mock_float_timestamps() -> np.ndarray:
    mock_timestamps = [
        1.001000000,
        1.006170176,
        1.016434432,
        1.030955296,
        1.036107648,
        1.046356512,
        1.060873248,
        1.066023360,
        1.076279200,
        1.090881792,
    ]

    return np.array(mock_timestamps, dtype=np.float64)


@pytest.fixture
def setup_TimestampsFloat_object(setup_mock_float_timestamps) -> TimestampsFloat:
    return TimestampsFloat(setup_mock_float_timestamps)


@pytest.fixture
def setup_mock_ros_timestamps():
    if not _has_rclpy:
        pytest.skip("rclpy not available")

    mock_timestamps = [
        1711038330346603696,
        1711038330351773872,
        1711038330362038128,
        1711038330376558992,
        1711038330381711344,
        1711038330391960208,
        1711038330406476944,
        1711038330411627056,
        1711038330421882896,
        1711038330436485488,
    ]

    mock_timestamps = [ROSTime(nanoseconds=each) for each in mock_timestamps]

    mock_container = {
        "feature_name": "/mock_topic",
        "timestamps": np.array(mock_timestamps, dtype=int),
    }

    return mock_container
