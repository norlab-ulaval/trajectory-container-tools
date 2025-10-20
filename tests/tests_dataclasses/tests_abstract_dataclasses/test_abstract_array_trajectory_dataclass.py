# coding=utf-8
from dataclasses import dataclass
from typing import Optional

import pytest
import numpy as np

from trajectory_container_tools import (
    AbstractTrajectoryArray,
    AbstractTrajectoryFeature,
)


@dataclass()
class MockNoNestedListAbstractTrajectoryArray(AbstractTrajectoryArray):
    mock_no_trj_attribute: np.ndarray


@dataclass()
class MockAbstractTrajectoryFeature(AbstractTrajectoryFeature):
    mock_attribute: np.ndarray


@dataclass()
class MockNestedListAbstractTrajectoryArray(AbstractTrajectoryArray):
    mock_list_attribute: list[MockAbstractTrajectoryFeature]

    @property
    def registred_trajectory_object_list(self) -> Optional[str]:
        return "mock_list_attribute"


@pytest.fixture
def setup_mock_no_nested_list_subclass() -> MockNoNestedListAbstractTrajectoryArray:
    return MockNoNestedListAbstractTrajectoryArray(
        feature_name="mock", mock_no_trj_attribute=np.ones(10)
    )


@pytest.fixture
def setup_mock_nested_list_subclass() -> MockNestedListAbstractTrajectoryArray:
    return MockNestedListAbstractTrajectoryArray(
        feature_name="mock",
        mock_list_attribute=[
            MockAbstractTrajectoryFeature(
                feature_name="mock nested attrib 1", mock_attribute=np.arange(10)
            ),
            MockAbstractTrajectoryFeature(
                feature_name="mock nested attrib 2", mock_attribute=np.arange(15)
            ),
        ],
    )


class TestCaseNoNestedListSubclass:

    def test_instanciation(self, setup_mock_no_nested_list_subclass):
        t_container = setup_mock_no_nested_list_subclass

        assert t_container.feature_name == "mock"
        assert "feature_name" in t_container._dataclass_internal_field()
        assert t_container.registred_trajectory_object_list is None
        assert (
            None not in t_container.non_trajectory_field()
            and "None" not in t_container.non_trajectory_field()
        )

        assert np.array_equal(t_container.mock_no_trj_attribute, np.ones(10))

    def test_string_representation(self, setup_mock_no_nested_list_subclass):
        print(setup_mock_no_nested_list_subclass)

    def test_lists_len(self, setup_mock_no_nested_list_subclass):
        t_container = setup_mock_no_nested_list_subclass
        assert t_container.lists_len is None

    def test__len__(self, setup_mock_no_nested_list_subclass):
        t_container = setup_mock_no_nested_list_subclass
        assert len(t_container) == 0

    def test_indexing(self, setup_mock_no_nested_list_subclass):
        t_container = setup_mock_no_nested_list_subclass
        assert t_container[0] is None

    def test_iterator(self, setup_mock_no_nested_list_subclass):
        t_container = setup_mock_no_nested_list_subclass
        assert len([*t_container]) == 0


class TestCaseNestedListSubclass:

    def test_instanciation(self, setup_mock_nested_list_subclass):

        t_container = setup_mock_nested_list_subclass

        assert t_container.feature_name == "mock"
        assert "feature_name" in t_container._dataclass_internal_field()
        assert t_container.registred_trajectory_object_list == "mock_list_attribute"
        assert (
            None not in t_container.non_trajectory_field()
            and "None" not in t_container.non_trajectory_field()
        )

        assert t_container.mock_list_attribute[0].feature_name == "mock nested attrib 1"
        assert t_container.mock_list_attribute[1].feature_name == "mock nested attrib 2"
        assert np.array_equal(
            t_container.mock_list_attribute[0].mock_attribute, np.arange(10)
        )
        assert np.array_equal(
            t_container.mock_list_attribute[1].mock_attribute, np.arange(15)
        )

    def test_string_representation(self, setup_mock_nested_list_subclass):
        print(setup_mock_nested_list_subclass)

    def test_lists_len(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass
        assert t_container.lists_len == 2

    def test__len__(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass
        assert len(t_container) == 2

    def test_indexing(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass
        assert t_container[0].feature_name == "mock nested attrib 1"
        assert t_container[1].feature_name == "mock nested attrib 2"

    def test_iterator(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass
        for idx, each in enumerate(t_container):
            print(f"{idx=} {each.feature_name=}")

        for each in t_container:
            print(each)
