# coding=utf-8
from dataclasses import dataclass

import pytest

import numpy as np

from trajectory_container_tools.dataclasses import (
    Header,
    NestedRosStampedDataclass,
    RosDataclass,
    RosStampedDataclass,
)


def test_RosStampedDataclass():

    @dataclass()
    class MockSubRosStampedDataclass(RosStampedDataclass):
        mock_attribute: np.ndarray

    t_container = MockSubRosStampedDataclass(
        feature_name="mock",
        header=Header(
            frame_id="mock_frame_id",
            timestamps=np.arange(10),
        ),
        mock_attribute=np.ones(10),
    )

    assert t_container.feature_name == "mock"
    assert np.array_equal(t_container.header.timestamps.stamps, np.arange(10))
    assert np.array_equal(t_container.mock_attribute, np.ones(10))


def test_RosDataclass():

    @dataclass()
    class MockSubRosDataclass(RosDataclass):
        mock_attribute: np.ndarray

    t_container = MockSubRosDataclass(feature_name="mock", mock_attribute=np.ones(10))

    assert t_container.feature_name == "mock"
    assert np.array_equal(t_container.mock_attribute, np.ones(10))

    with pytest.raises(AttributeError) as exc_info:
        # The 'timestamps' attribute should not exist
        assert t_container.__getattribute__("header")


def test_NestedRosStampedDataclass():

    @dataclass()
    class MockSubNestedRosStampedDataclass(NestedRosStampedDataclass):
        mock_attribute: np.ndarray

    t_container = MockSubNestedRosStampedDataclass(
        header=Header(
            frame_id="mock_frame_id",
            timestamps=np.arange(10),
        ),
        mock_attribute=np.ones(10),
    )
    assert t_container.feature_name is None
    assert t_container._nested == True
    assert np.array_equal(t_container.header.timestamps.stamps, np.arange(10))
    assert np.array_equal(t_container.mock_attribute, np.ones(10))

    with pytest.raises(TypeError) as exc_info:
        # The 'feature_name' parameter should not exist
        t_container = MockSubNestedRosStampedDataclass(
            feature_name="mock",
            header=Header(
                frame_id="mock_frame_id",
                timestamps=np.arange(10),
            ),
            mock_attribute=np.ones(10),
        )
