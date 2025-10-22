# coding=utf-8
from dataclasses import dataclass
from typing import Union

import pytest

from trajectory_container_tools.dataclasses.core.abstract_trajectory_features_bag_dataclass import (
    AbstractTrajectoryFeaturesBag,
)
from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass_common import (
    AbstractTrajectoryCommon,
)
import numpy as np


@dataclass
class MockNestedTrajectory(AbstractTrajectoryCommon):
    mock_attr_nested_attr: np.ndarray

    def __post_init__(self):
        pass


@dataclass
class MockTrajectory(AbstractTrajectoryCommon):
    mock_nested_attr: Union[MockNestedTrajectory, "MockTrajectory"]
    mock_attr: np.ndarray

    def __post_init__(self):
        # .... Pre-condition ......................................................................
        if not self.get_dimension_names():
            raise TypeError(
                f"[TCT error] {self.__class__.__name__} is an abstract baseclass, "
                f"it must be subclassed in order to be instanciated."
            )

        # .... Base class initialization logic ....................................................
        # Note: skip self.set_parent_container_reference_tracking() for testing

        # .... Callback and attribute customization logic .........................................
        self.on_begin_post_init_callback()

        for each_name in self.get_dimension_names():
            self.post_init_feature_callback(feature_name=each_name)

        self.on_exit_post_init_callback()
        return None

    def on_begin_post_init_callback(self):
        # Create test attribute for post-init-callback logic
        self.__setattr__("test_on_begin_post_init_callback", True)
        self.__setattr__("test_post_init_feature_callback", False)
        self.__setattr__("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        if feature_name == "mock_attr":
            feature = self.__getattribute__(feature_name)
            feature_ini = feature[-1]
            self.__setattr__(f"mock_attr_init", feature_ini)

        self.__setattr__("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.__setattr__("test_on_exit_post_init_callback", True)
        return None


@dataclass
class MockTrajectoryArray(MockTrajectory):
    mock_nested_attr: list[MockNestedTrajectory]
    mock_attr: np.ndarray


@dataclass()
class MockAbstractTrajectoryFeaturesBag(AbstractTrajectoryFeaturesBag):
    topic_mock_feature: MockTrajectory


@pytest.fixture(scope="function")
def setup_two_lvl_trajectory_dataclass() -> MockTrajectory:
    return MockTrajectory(
        mock_nested_attr=MockNestedTrajectory(np.arange(10)), mock_attr=np.arange(10)
    )


@pytest.fixture(scope="function")
def setup_two_lvl_trajectory_array_dataclass() -> MockTrajectory:
    return MockTrajectoryArray(
        mock_nested_attr=[
            MockNestedTrajectory(np.arange(10)),
            MockNestedTrajectory(np.arange(10) + 10),
        ],
        mock_attr=np.arange(10),
    )


@pytest.fixture(scope="function")
def setup_three_lvl_trajectory_dataclass() -> MockTrajectory:
    return MockTrajectory(
        mock_nested_attr=MockTrajectory(
            mock_nested_attr=MockNestedTrajectory(np.arange(10)),
            mock_attr=np.arange(10),
        ),
        mock_attr=np.arange(10),
    )


class TestAbstractTrajectoryCommon:

    def test_set_parent_container_reference_tracking_case_base(
        self, setup_three_lvl_trajectory_dataclass
    ):
        t_container = setup_three_lvl_trajectory_dataclass

        t_container.set_parent_container_reference_tracking()
        t_container.mock_nested_attr.set_parent_container_reference_tracking()

        assert t_container.get_parent_container() is None
        assert t_container.mock_nested_attr.get_parent_container() is not None
        assert id(t_container.mock_nested_attr.get_parent_container()) == id(
            t_container
        )
        assert id(
            t_container.mock_nested_attr.mock_nested_attr.get_parent_container()
        ) == id(t_container.mock_nested_attr)

    def test_set_parent_container_reference_tracking_case_array(
        self, setup_two_lvl_trajectory_array_dataclass
    ):
        t_container_array = setup_two_lvl_trajectory_array_dataclass

        t_container_array.set_parent_container_reference_tracking()

        assert t_container_array.get_parent_container() is None
        assert id(t_container_array.mock_nested_attr[0].get_parent_container()) == id(
            t_container_array
        )
        assert id(t_container_array.mock_nested_attr[1].get_parent_container()) == id(
            t_container_array
        )

    def test_get_parent_container_case_base(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass

        t_container.set_parent_container_reference_tracking()
        t_container.mock_nested_attr.set_parent_container_reference_tracking()

        assert t_container.get_parent_container() is None
        assert id(t_container.mock_nested_attr.get_parent_container()) == id(
            t_container
        )
        assert id(
            t_container.mock_nested_attr.mock_nested_attr.get_parent_container()
        ) == id(t_container.mock_nested_attr)

    def test_get_parent_container_case_array(
        self, setup_two_lvl_trajectory_array_dataclass
    ):
        t_container_array = setup_two_lvl_trajectory_array_dataclass

        t_container_array.set_parent_container_reference_tracking()

        assert t_container_array.get_parent_container() is None
        assert id(t_container_array.mock_nested_attr[0].get_parent_container()) == id(
            t_container_array
        )
        assert id(t_container_array.mock_nested_attr[1].get_parent_container()) == id(
            t_container_array
        )

    def test_get_container_root_case_base(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass

        t_container.set_parent_container_reference_tracking()
        t_container.mock_nested_attr.set_parent_container_reference_tracking()

        assert id(t_container.get_container_root()) == id(t_container)
        assert id(
            t_container.mock_nested_attr.mock_nested_attr.get_container_root()
        ) == id(t_container)

    def test_get_container_root_case_feature_bag(
        self, setup_three_lvl_trajectory_dataclass
    ):

        t_feature_bag = MockAbstractTrajectoryFeaturesBag(
            dataset_info="Mock feature bag", topic_mock_feature=setup_three_lvl_trajectory_dataclass
        )

        t_feature_bag.set_parent_container_reference_tracking()
        t_feature_bag.topic_mock_feature.set_parent_container_reference_tracking()
        t_feature_bag.topic_mock_feature.mock_nested_attr.set_parent_container_reference_tracking()

        assert id(t_feature_bag.get_container_root(include_feature_bag=True)) == id(
            t_feature_bag
        )
        assert id(
            t_feature_bag.topic_mock_feature.mock_nested_attr.get_container_root(
                include_feature_bag=False
            )
        ) == id(t_feature_bag.topic_mock_feature)
        assert id(
            t_feature_bag.topic_mock_feature.mock_nested_attr.get_container_root(
                include_feature_bag=True
            )
        ) == id(t_feature_bag)

    def test_get_container_root_case_array(
        self, setup_two_lvl_trajectory_array_dataclass
    ):
        t_container_array = setup_two_lvl_trajectory_array_dataclass

        t_container_array.set_parent_container_reference_tracking()

        assert id(t_container_array.get_container_root()) == id(t_container_array)
        assert id(t_container_array.mock_nested_attr[0].get_container_root()) == id(
            t_container_array
        )
        assert id(t_container_array.mock_nested_attr[1].get_container_root()) == id(
            t_container_array
        )

    def test_is_nested(self, setup_two_lvl_trajectory_dataclass):
        t_container = setup_two_lvl_trajectory_dataclass

        t_container.set_parent_container_reference_tracking()

        assert t_container.is_nested() == False
        assert t_container.mock_nested_attr.is_nested() == True

    def test_post_init_callback_logic(self, setup_two_lvl_trajectory_dataclass):
        t_container = setup_two_lvl_trajectory_dataclass

        # Check each post-init-callback overriden method was hit
        assert t_container.__getattribute__("test_on_begin_post_init_callback") == True
        assert t_container.__getattribute__("test_post_init_feature_callback") == True
        assert t_container.__getattribute__("test_on_exit_post_init_callback") == True
        assert (
            t_container.__getattribute__("mock_attr_init") == t_container.mock_attr[-1]
        )

    def test_get_dynamic_field(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass
        assert np.array_equal(
            t_container.get_dynamic_field("mock_attr"), t_container.mock_attr
        )
        assert np.array_equal(
            t_container.get_dynamic_field("mock_nested_attr.mock_attr"),
            t_container.mock_nested_attr.mock_attr,
        )
        assert np.array_equal(
            t_container.get_dynamic_field(
                "mock_nested_attr.mock_nested_attr.mock_attr_nested_attr"
            ),
            t_container.mock_nested_attr.mock_nested_attr.mock_attr_nested_attr,
        )

    def test_set_dynamic_field(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass

        t_expected = np.ones((10,))
        t_container.set_dynamic_field("mock_attr", t_expected)
        t_container.set_dynamic_field("mock_nested_attr.mock_attr", t_expected)
        t_container.set_dynamic_field(
            "mock_nested_attr.mock_nested_attr.mock_attr_nested_attr", t_expected
        )

        assert np.array_equal(t_container.get_dynamic_field("mock_attr"), t_expected)
        assert np.array_equal(
            t_container.get_dynamic_field("mock_nested_attr.mock_attr"),
            t_expected,
        )
        assert np.array_equal(
            t_container.get_dynamic_field(
                "mock_nested_attr.mock_nested_attr.mock_attr_nested_attr"
            ),
            t_expected,
        )

    def test_get_dimension_type(
        self,
        setup_two_lvl_trajectory_dataclass,
        setup_two_lvl_trajectory_array_dataclass,
    ):

        # .... Case nested feature trajectory dataclass ...........................................
        t_container = setup_two_lvl_trajectory_dataclass

        dimension_type, is_list_of_type = t_container.get_dimension_type("mock_attr")
        assert issubclass(dimension_type, np.ndarray)
        assert is_list_of_type == False

        dimension_type, is_list_of_type = t_container.get_dimension_type(
            "mock_nested_attr"
        )
        assert issubclass(dimension_type, MockNestedTrajectory)
        assert is_list_of_type == False

        # .... Case nested array features trajectory dataclass ....................................
        t_container_array = setup_two_lvl_trajectory_array_dataclass

        dimension_type, is_list_of_type = t_container_array.get_dimension_type(
            "mock_attr"
        )
        assert issubclass(dimension_type, np.ndarray)
        assert is_list_of_type == False

        dimension_type, is_list_of_type = t_container_array.get_dimension_type(
            "mock_nested_attr"
        )
        assert issubclass(dimension_type, MockNestedTrajectory)
        assert is_list_of_type == True

    def test_get_dimension_names(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass
        assert t_container.get_dimension_names() == ("mock_nested_attr", "mock_attr")
        assert "_parent" not in t_container.get_dimension_names()
