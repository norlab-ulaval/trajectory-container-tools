# coding=utf-8
import numpy as np
import pytest
from rclpy.time import Time as ROSTime

from trajectory_container_tools.temporal import Timestamps


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
def setup_Timestamps_object(setup_mock_timestamps) -> Timestamps:
    return Timestamps(setup_mock_timestamps)


@pytest.fixture
def setup_mock_ros_timestamps():
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
