# coding=utf-8
from dataclasses import dataclass

import pytest

from trajectory_container_tools import (
    BaseNoTrajectoryDataclass,
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass
)
import numpy as np


def test_BaseTrajectoryDataclass():

    @dataclass()
    class MockSubBaseTrajectoryDataclass(BaseTrajectoryDataclass):
        timestamps: np.ndarray
        mock_attribute: np.ndarray

    t_container = MockSubBaseTrajectoryDataclass(
        feature_name="mock", timestamps=np.arange(10), mock_attribute=np.ones(10)
    )

    assert t_container.feature_name == "mock"
    assert np.array_equal(t_container.timestamps, np.arange(10))
    assert np.array_equal(t_container.mock_attribute, np.ones(10))

def test_NestedBaseTrajectoryDataclass():

    @dataclass()
    class MockSubNestedBaseTrajectoryDataclass(NestedBaseTrajectoryDataclass):
        timestamps: np.ndarray
        mock_attribute: np.ndarray

    t_container = MockSubNestedBaseTrajectoryDataclass(
        timestamps=np.arange(10), mock_attribute=np.ones(10)
    )
    assert t_container.feature_name is None
    assert t_container._nested == True
    assert np.array_equal(t_container.timestamps, np.arange(10))
    assert np.array_equal(t_container.mock_attribute, np.ones(10))

    with pytest.raises(TypeError) as exc_info:
        # The 'feature_name' parameter should not exist
        t_container = MockSubNestedBaseTrajectoryDataclass(
            feature_name="mock", timestamps=np.arange(10), mock_attribute=np.ones(10)
        )

def test_BaseNoTrajectoryDataclass():

    @dataclass()
    class MockSubBaseNoTrajectoryDataclass(BaseNoTrajectoryDataclass):
        mock_attribute: np.ndarray

    t_container = MockSubBaseNoTrajectoryDataclass(
        feature_name="mock", mock_attribute=np.ones(10)
    )

    assert t_container.feature_name == "mock"
    assert np.array_equal(t_container.mock_attribute, np.ones(10))

    with pytest.raises(AttributeError) as exc_info:
        # The 'timestamps' attribute should not exist
        assert t_container.__getattribute__('timestamps')
