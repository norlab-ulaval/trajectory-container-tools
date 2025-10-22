# coding=utf-8
from dataclasses import dataclass

import pytest

from trajectory_container_tools import (
    BaseTrajectoryFeatureArray,
    BaseTrajectoryFeature,
)
from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import NestedBaseTrajectory
import numpy as np


def test_BaseTrajectoryFeature():

    @dataclass()
    class MockBaseTrajectoryFeature(BaseTrajectoryFeature):
        timestamps: np.ndarray
        mock_attribute: np.ndarray

    t_container = MockBaseTrajectoryFeature(
        feature_name="mock", timestamps=np.arange(10), mock_attribute=np.ones(10)
    )

    assert t_container.feature_name == "mock"
    assert t_container.is_nested() == False
    assert np.array_equal(t_container.timestamps, np.arange(10))
    assert np.array_equal(t_container.mock_attribute, np.ones(10))


@pytest.mark.deprecated("Dataclass NestedBaseTrajectory is marked as deprecated (ref task TCT-87)")
def test_NestedBaseTrajectory():

    @dataclass()
    class MockNestedBaseTrajectory(NestedBaseTrajectory):
        timestamps: np.ndarray
        mock_attribute: np.ndarray

    @dataclass()
    class MockBaseTrajectoryDataclass(BaseTrajectoryFeature):
        timestamps: np.ndarray
        mock_attribute: np.ndarray
        nested_container: MockNestedBaseTrajectory

    t_container = MockBaseTrajectoryDataclass(
        timestamps=np.arange(10),
        mock_attribute=np.ones(10),
        nested_container=MockNestedBaseTrajectory(
            timestamps=np.arange(10),
            mock_attribute=np.ones(10),
        ),
    )

    assert t_container.feature_name is None
    assert t_container.is_nested() == False
    assert t_container.nested_container.is_nested() == True
    assert np.array_equal(t_container.timestamps, np.arange(10))
    assert np.array_equal(t_container.mock_attribute, np.ones(10))


def test_BaseTrajectoryArray():

    @dataclass()
    class MockBaseTrajectoryFeatureArray(BaseTrajectoryFeatureArray):
        mock_attribute: np.ndarray

    t_container = MockBaseTrajectoryFeatureArray(
        feature_name="mock", mock_attribute=np.ones(10)
    )

    assert t_container.feature_name == "mock"
    assert t_container.is_nested() == False
    assert np.array_equal(t_container.mock_attribute, np.ones(10))

    with pytest.raises(AttributeError) as exc_info:
        # The 'timestamps' attribute should not exist
        assert t_container.__getattribute__("timestamps")
