# coding=utf-8

import pytest
import numpy as np


@pytest.fixture
def setup_simple_stamps() -> np.ndarray:
    return np.arange(start=10, stop=110, step=10, dtype=int)

@pytest.fixture
def setup_mock_timestamps() -> np.ndarray:
    mock_timestamps = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
    ]

    return np.array(mock_timestamps, dtype=int) * 100000000 + 1000000000000000000


@pytest.fixture
def setup_real_timestamps() -> np.ndarray:
    real_timestamps = [
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

    return np.array(real_timestamps, dtype=int)
