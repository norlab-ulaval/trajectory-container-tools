# coding=utf-8
import typing
from dataclasses import dataclass
from typing import Union

import pytest

from trajectory_container_tools.dataclasses.core.abstract_trajectory_features_bag_dataclass import (
    AbstractTrajectoryFeaturesBag,
)
from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass_common import (
    AbstractTrajectoryCommon,
)
from trajectory_container_tools.utils.typing.tct_custom_field import (
    NonTrajectoryField,
    ContainerInternalField,
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
    mock_non_trj_array: NonTrajectoryField[np.ndarray]
    mock_internal: ContainerInternalField[list[int]]

    def __post_init__(self):
        # .... Pre-condition ......................................................................
        if not self.get_cls_public_field_names():
            raise TypeError(
                f"[TCT error] {self.__class__.__name__} is an abstract baseclass, "
                f"it must be subclassed in order to be instanciated."
            )

        # .... Base class initialization logic ....................................................
        # Note: skip self.set_parent_container_reference_tracking() for testing

        # .... Callback and attribute customization logic .........................................
        self.on_begin_post_init_callback()

        for each_name in self.get_cls_public_field_names(include_non_init_dim=True):
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
    mock_trj_array_w_arbitrary_type: list[list[int]]
    mock_attr: np.ndarray
    mock_non_trj_array = NonTrajectoryField[np.ndarray]
    mock_internal: ContainerInternalField[list[int]]


@dataclass()
class MockAbstractTrajectoryFeaturesBag(AbstractTrajectoryFeaturesBag):
    topic_mock_feature: MockTrajectory


@pytest.fixture(scope="function")
def setup_two_lvl_trajectory_dataclass() -> MockTrajectory:
    return MockTrajectory(
        mock_nested_attr=MockNestedTrajectory(np.arange(10)),
        mock_attr=np.arange(10),
        mock_non_trj_array=np.ones((3,)),
        mock_internal=[1, 2, 3],
    )


@pytest.fixture(scope="function")
def setup_two_lvl_trajectory_array_dataclass() -> MockTrajectory:
    return MockTrajectoryArray(
        mock_trj_array_w_arbitrary_type=[[*range(99)]] * 10,
        mock_nested_attr=[
            MockNestedTrajectory(np.arange(10)),
            MockNestedTrajectory(np.arange(10) + 10),
        ],
        mock_attr=np.arange(10),
        mock_non_trj_array=np.ones((3,)),
        mock_internal=[1, 2, 3],
    )


@pytest.fixture(scope="function")
def setup_three_lvl_trajectory_dataclass() -> MockTrajectory:
    return MockTrajectory(
        mock_nested_attr=MockTrajectory(
            mock_nested_attr=MockNestedTrajectory(np.arange(10)),
            mock_attr=np.arange(10),
            mock_non_trj_array=np.ones((3,)),
            mock_internal=[1, 2, 3],
        ),
        mock_attr=np.arange(10),
        mock_non_trj_array=np.ones((3,)),
        mock_internal=[1, 2, 3],
    )


class TestAbstractTrajectoryCommon:

    def test_instanciation_with_special_type_field(
        self, setup_three_lvl_trajectory_dataclass
    ):
        t_container = setup_three_lvl_trajectory_dataclass

        # .... Test field typed with NonTrajectoryField[Any] ......................................
        assert (
            typing.get_origin(typing.get_type_hints(MockTrajectory)['mock_non_trj_array']) is NonTrajectoryField
        )
        assert isinstance(t_container.mock_non_trj_array, np.ndarray)

        # .... Test field typed with ContainerInternalField[Any] ..................................
        assert typing.get_origin(typing.get_type_hints(MockTrajectory)['mock_internal']) is ContainerInternalField
        assert isinstance(t_container.mock_internal, list)

        # .... Test field typed with Union ........................................................
        assert typing.get_origin(typing.get_type_hints(MockTrajectory)['mock_nested_attr']) is Union
        assert isinstance(t_container.mock_nested_attr, MockTrajectory)

        # .... Test other fields ..................................................................
        assert isinstance(t_container, MockTrajectory)
        assert isinstance(t_container.mock_attr, np.ndarray)

        assert isinstance(
            t_container.mock_nested_attr.mock_nested_attr, MockNestedTrajectory
        )
        assert isinstance(t_container.mock_nested_attr.mock_attr, np.ndarray)
        assert isinstance(t_container.mock_nested_attr.mock_non_trj_array, np.ndarray)
        assert isinstance(t_container.mock_nested_attr.mock_internal, list)

        assert isinstance(
            t_container.mock_nested_attr.mock_nested_attr.mock_attr_nested_attr,
            np.ndarray,
        )

    def test_non_trajectory_field(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass
        assert t_container.non_trajectory_field() == [
            "mock_non_trj_array",
        ]
        assert t_container.mock_nested_attr.non_trajectory_field() == [
            "mock_non_trj_array",
        ]
        assert np.array_equal(t_container.mock_non_trj_array, np.ones((3,)))
        assert np.array_equal(
            t_container.mock_nested_attr.mock_non_trj_array, np.ones((3,))
        )

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
            dataset_info="Mock feature bag",
            topic_mock_feature=setup_three_lvl_trajectory_dataclass,
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

    def test_get_dynamic_attribute(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass
        assert np.array_equal(
            t_container.get_dynamic_attribute("mock_attr"), t_container.mock_attr
        )
        assert np.array_equal(
            t_container.get_dynamic_attribute("mock_nested_attr.mock_attr"),
            t_container.mock_nested_attr.mock_attr,
        )
        assert np.array_equal(
            t_container.get_dynamic_attribute(
                "mock_nested_attr.mock_nested_attr.mock_attr_nested_attr"
            ),
            t_container.mock_nested_attr.mock_nested_attr.mock_attr_nested_attr,
        )

    def test_has_dynamic_attribute(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass

        assert t_container.has_dynamic_attribute("mock_attr") == True
        assert t_container.has_dynamic_attribute("mock_nested_attr.mock_attr") == True
        assert (
            t_container.has_dynamic_attribute(
                "mock_nested_attr.mock_nested_attr.mock_attr_nested_attr"
            )
            == True
        )

        assert t_container.has_dynamic_attribute("mock_attr999") == False
        assert (
            t_container.has_dynamic_attribute("mock_nested_attr.mock_attr999") == False
        )
        assert (
            t_container.has_dynamic_attribute(
                "mock_nested_attr.mock_nested_attr.mock_attr_nested_attr999"
            )
            == False
        )

    def test_set_dynamic_attribute(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass

        t_expected = np.ones((10,))
        t_container.set_dynamic_attribute("mock_attr", t_expected)
        t_container.set_dynamic_attribute("mock_nested_attr.mock_attr", t_expected)
        t_container.set_dynamic_attribute(
            "mock_nested_attr.mock_nested_attr.mock_attr_nested_attr", t_expected
        )

        assert np.array_equal(
            t_container.get_dynamic_attribute("mock_attr"), t_expected
        )
        assert np.array_equal(
            t_container.get_dynamic_attribute("mock_nested_attr.mock_attr"),
            t_expected,
        )
        assert np.array_equal(
            t_container.get_dynamic_attribute(
                "mock_nested_attr.mock_nested_attr.mock_attr_nested_attr"
            ),
            t_expected,
        )

    def test_get_cls_public_field_type(
        self,
        setup_two_lvl_trajectory_dataclass,
        setup_two_lvl_trajectory_array_dataclass,
    ):

        # .... Case nested feature trajectory dataclass ...........................................
        t_container = setup_two_lvl_trajectory_dataclass

        dimension_type, is_list_of_type = t_container.get_cls_public_field_type(
            "mock_attr"
        )
        assert issubclass(dimension_type, np.ndarray)
        assert is_list_of_type == False

        dimension_type, is_list_of_type = t_container.get_cls_public_field_type(
            "mock_nested_attr"
        )
        assert issubclass(dimension_type, MockNestedTrajectory)
        assert is_list_of_type == False

        # .... Case nested array features trajectory dataclass ....................................
        t_container_array = setup_two_lvl_trajectory_array_dataclass

        dimension_type, is_list_of_type = t_container_array.get_cls_public_field_type(
            "mock_attr"
        )
        assert issubclass(dimension_type, np.ndarray)
        assert is_list_of_type == False

        dimension_type, is_list_of_type = t_container_array.get_cls_public_field_type(
            "mock_nested_attr"
        )
        assert issubclass(dimension_type, MockNestedTrajectory)
        assert is_list_of_type == True

        dimension_type, is_list_of_type = t_container_array.get_cls_public_field_type(
            "mock_trj_array_w_arbitrary_type"
        )
        assert issubclass(dimension_type, list)
        assert is_list_of_type == True

    def test_get_cls_public_field_names(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass
        assert t_container.get_cls_public_field_names() == (
            "mock_nested_attr",
            "mock_attr",
            "mock_non_trj_array",
        )
        assert "_parent" not in t_container.get_cls_public_field_names()
        assert "mock_internal" not in t_container.get_cls_public_field_names()

    def test_get_public_attribute_names(self, setup_three_lvl_trajectory_dataclass):
        t_container = setup_three_lvl_trajectory_dataclass
        assert t_container.get_public_attribute_names() == (
            "mock_nested_attr",
            "mock_attr",
            "mock_non_trj_array",
            "test_on_begin_post_init_callback",
            "test_post_init_feature_callback",
            "test_on_exit_post_init_callback",
            "mock_attr_init",
        )
        assert "_parent" not in t_container.get_public_attribute_names()
        assert "mock_internal" not in t_container.get_public_attribute_names()
