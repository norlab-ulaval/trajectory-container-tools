# coding=utf-8
from dataclasses import dataclass
from typing import List, Optional

import pytest
import numpy as np

from trajectory_container_tools import (
    AbstractTrajectoryUnboundedArray,
    AbstractTrajectoryFeature,
)


@dataclass()
class MockAbstractTrajectoryFeature(AbstractTrajectoryFeature):
    mock_trj_attribute: np.ndarray


@dataclass()
class MockNestedListAbstractTrajectoryUnboundedArray(AbstractTrajectoryUnboundedArray):
    mock_non_trj_array: list[bool]
    mock_trj_attribute: np.ndarray
    mock_trj_array_w_arbitrary_type: list[list[int]]
    mock_trj_feature_array: list[MockAbstractTrajectoryFeature]

    @classmethod
    def non_trajectory_field(cls) -> List[str]:
        return super().non_trajectory_field() + ["mock_non_trj_array"]


@dataclass()
class MockNoNestedListAbstractTrajectoryUnboundedArray(
    AbstractTrajectoryUnboundedArray
):
    mock_trj_attribute: np.ndarray
    mock_trj_array_w_arbitrary_type: list[int]


@pytest.fixture
def setup_mock_nested_list_subclass() -> MockNestedListAbstractTrajectoryUnboundedArray:
    return MockNestedListAbstractTrajectoryUnboundedArray(
        feature_name="mock",
        mock_non_trj_array=[True, False, True],
        mock_trj_attribute=np.arange(20),
        mock_trj_array_w_arbitrary_type=[[*range(3)]] * 20,
        mock_trj_feature_array=[
            MockAbstractTrajectoryFeature(
                feature_name="mock nested attrib 1",
                mock_trj_attribute=np.arange(10),
            ),
            MockAbstractTrajectoryFeature(
                feature_name="mock nested attrib 2",
                mock_trj_attribute=np.arange(15),
            ),
        ],
    )


class TestCaseArrayOfTrajectoryFeatureDataclasses:

    def test_instanciation(self, setup_mock_nested_list_subclass):

        t_container = setup_mock_nested_list_subclass

        assert t_container.feature_name == "mock"
        assert "feature_name" in t_container._dataclass_internal_field()
        assert (
            None not in t_container.non_trajectory_field()
            and "None" not in t_container.non_trajectory_field()
        )

        assert (
            t_container.mock_trj_feature_array[0].feature_name == "mock nested attrib 1"
        )
        assert (
            t_container.mock_trj_feature_array[1].feature_name == "mock nested attrib 2"
        )
        assert np.array_equal(
            t_container.mock_trj_feature_array[0].mock_trj_attribute, np.arange(10)
        )
        assert np.array_equal(
            t_container.mock_trj_feature_array[1].mock_trj_attribute, np.arange(15)
        )

    def test_non_trajectory_field(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass
        assert "mock_non_trj_array" in t_container.non_trajectory_field()
        assert "mock_trj_feature_array" not in t_container.non_trajectory_field()
        assert (
            "mock_trj_array_w_arbitrary_type" not in t_container.non_trajectory_field()
        )

    def test_trajectory_array_field_name(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass
        assert isinstance(t_container.trajectory_array_field_names(), list)

        # Case trajectory array field (Base case)
        assert t_container.trajectory_array_field_names() == [
            "mock_trj_array_w_arbitrary_type",
            "mock_trj_feature_array",
        ]
        assert t_container.trajectory_array_field_names(
            non_trajectory_containers_array_only=True
        ) == ["mock_trj_array_w_arbitrary_type"]
        assert t_container.trajectory_array_field_names(
            trajectory_containers_array_only=True
        ) == ["mock_trj_feature_array"]

        with pytest.raises(ValueError) as exc_info:
            t_container.trajectory_array_field_names(
                trajectory_containers_array_only=True,
                non_trajectory_containers_array_only=True,
            )
        # print(f"{exc_info=}")
        # assert exc_info.value.args == ('<The error message>',)

        # Case no trajectory array field
        t_no_array_container = MockNoNestedListAbstractTrajectoryUnboundedArray(
            mock_trj_attribute=np.arange(10),
            mock_trj_array_w_arbitrary_type=[*range(3)],
        )
        assert t_no_array_container.trajectory_array_field_names() == [
            "mock_trj_array_w_arbitrary_type"
        ]
        assert (
            t_no_array_container.trajectory_array_field_names(
                trajectory_containers_array_only=True
            )
            == []
        )

    def test_string_representation(self, setup_mock_nested_list_subclass):
        print(setup_mock_nested_list_subclass)

    def test__len__(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass
        assert len(t_container) == t_container.mock_trj_attribute.size

    def test_indexing(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass

        # .... Sanity check .......................................................................
        assert isinstance(t_container.mock_trj_array_w_arbitrary_type, list)
        assert len(t_container.mock_trj_array_w_arbitrary_type) == 20
        assert len(t_container.mock_trj_array_w_arbitrary_type[0]) == 3

        # .... Case trajectory at t=0 .............................................................
        assert t_container[0].mock_trj_attribute == 0

        assert isinstance(t_container[0].mock_trj_array_w_arbitrary_type, list)
        assert len(t_container[0].mock_trj_array_w_arbitrary_type) == 3
        assert t_container[0].mock_trj_array_w_arbitrary_type == [*range(3)]

        assert isinstance(t_container[0].mock_trj_feature_array, list)
        assert t_container[0].mock_trj_feature_array[0].mock_trj_attribute == 0
        assert t_container[0].mock_trj_feature_array[1].mock_trj_attribute == 0

        # .... Case trajectory at t=T .............................................................
        assert t_container[-1].mock_trj_attribute == 19

        assert isinstance(t_container[-1].mock_trj_array_w_arbitrary_type, list)
        assert len(t_container[-1].mock_trj_array_w_arbitrary_type) == 3
        assert t_container[-1].mock_trj_array_w_arbitrary_type == [*range(3)]

        assert isinstance(t_container[-1].mock_trj_feature_array, list)
        assert t_container[-1].mock_trj_feature_array[0].mock_trj_attribute == 9
        assert t_container[-1].mock_trj_feature_array[1].mock_trj_attribute == 14

    def test_iterator(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass
        for idx, each in enumerate(t_container):
            print(f"{idx=} {each.feature_name=}")

        for each in t_container:
            print(each)

    def test_nested_member_parent_tracking(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass

        assert t_container.get_parent_container() is None
        assert id(t_container.mock_trj_feature_array[0].get_parent_container()) == id(
            t_container
        )
        assert id(t_container.mock_trj_feature_array[1].get_parent_container()) == id(
            t_container
        )

    def test_empty(self, setup_mock_nested_list_subclass):
        t_container = setup_mock_nested_list_subclass
        assert t_container.trajectory_len == 20
        print(t_container)

        t_container_empty = t_container.empty()

        assert isinstance(t_container_empty, type(t_container))
        assert isinstance(t_container_empty.mock_non_trj_array, list)
        assert isinstance(t_container_empty.mock_trj_array_w_arbitrary_type, list)
        assert isinstance(t_container_empty.mock_trj_feature_array, list)

        assert t_container_empty.timesteps_indices.size == 0
        assert np.array_equal(
            t_container_empty.timesteps_indices, np.array([], dtype=np.int64)
        )

        assert len(t_container_empty.mock_non_trj_array) == 3
        assert len(t_container_empty.mock_trj_array_w_arbitrary_type) == 0
        assert t_container_empty.mock_trj_attribute.size == 0
        assert np.array_equal(
            t_container_empty.mock_trj_attribute, np.array([], dtype=np.int64)
        )
        assert len(t_container_empty.mock_trj_feature_array) == 2
        assert isinstance(
            t_container_empty.mock_trj_feature_array[0], MockAbstractTrajectoryFeature
        )
        assert isinstance(
            t_container_empty.mock_trj_feature_array[1], MockAbstractTrajectoryFeature
        )

        assert (
            t_container_empty.mock_trj_feature_array[0].feature_name
            == "mock nested attrib 1"
        )
        assert t_container_empty.mock_trj_feature_array[0].mock_trj_attribute.size == 0
        assert (
            t_container_empty.mock_trj_feature_array[1].feature_name
            == "mock nested attrib 2"
        )
        assert t_container_empty.mock_trj_feature_array[1].mock_trj_attribute.size == 0

        print(t_container_empty)
