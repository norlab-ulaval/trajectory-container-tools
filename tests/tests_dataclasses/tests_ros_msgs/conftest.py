# coding=utf-8

import pytest
import numpy as np

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

