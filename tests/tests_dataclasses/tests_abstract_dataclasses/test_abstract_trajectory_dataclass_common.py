# coding=utf-8

import pytest

from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass_common import \
    AbstractTrajectoryCommon
import numpy as np

class MockNestedTrajectory(AbstractTrajectoryCommon):
    mock_attr: np.ndarray

    def __post_init__(self):
        pass

class MockTrajectory(AbstractTrajectoryCommon):
    mock_nested_attr: MockNestedTrajectory
    mock_attr: np.ndarray

    def __post_init__(self):
        pass


class TestAbstractTrajectoryCommon:
    pass
