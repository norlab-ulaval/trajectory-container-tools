# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools.dataclasses.core.abstract_trajectory_feature_dataclass import (
    AbstractTrajectoryFeature,
)
from trajectory_container_tools.typing import NonTrajectoryField


@dataclass
class MockTrajectoryChildDFcase(AbstractTrajectoryFeature):
    aa: np.ndarray
    bb: np.ndarray
    cc: np.ndarray
    dd_metadata: NonTrajectoryField[np.ndarray] = np.array([0, 0, 0])

    def on_begin_post_init_callback(self):
        feature = self.get_dynamic_attribute("dd_metadata")
        self.set_dynamic_attribute("dd_metadata", feature + 99)

        # Create test attribute for post-init-callback logic
        self.set_dynamic_attribute("test_on_begin_post_init_callback", True)
        self.set_dynamic_attribute("test_post_init_feature_callback", False)
        self.set_dynamic_attribute("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        feature = self.get_dynamic_attribute(feature_name)
        if isinstance(feature, np.ndarray):
            feature_ini = feature[..., 0]
            self.set_dynamic_attribute(f"{feature_name}_init", feature_ini)

        self.set_dynamic_attribute("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.set_dynamic_attribute("test_on_exit_post_init_callback", True)
        return None


@dataclass
class MockTrajectoryChildRosBagCase(AbstractTrajectoryFeature):
    aa: np.ndarray
    bb: np.ndarray
    cc: np.ndarray
    dd_metadata: NonTrajectoryField[np.ndarray] = np.array([0, 0, 0])

    def on_begin_post_init_callback(self):  # self.dd_metadata += 99
        feature = self.get_dynamic_attribute("dd_metadata")
        self.set_dynamic_attribute("dd_metadata", feature + 99)

        # Create test attribute for post-init-callback logic
        self.set_dynamic_attribute("test_on_begin_post_init_callback", True)
        self.set_dynamic_attribute("test_post_init_feature_callback", False)
        self.set_dynamic_attribute("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        feature = self.get_dynamic_attribute(feature_name)
        if isinstance(feature, np.ndarray):
            feature_ini = feature[0, ...]
            self.set_dynamic_attribute(f"{feature_name}_init", feature_ini)

        self.set_dynamic_attribute("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.set_dynamic_attribute("test_on_exit_post_init_callback", True)
        return None


@dataclass
class MockTrajectoryComposedParent(AbstractTrajectoryFeature):
    child_one: MockTrajectoryChildRosBagCase
    child_two: MockTrajectoryChildRosBagCase
    aa: np.ndarray

    def on_begin_post_init_callback(self):  # self.dd_metadata += 99
        # Create test attribute for post-init-callback logic
        self.__setattr__("test_on_begin_post_init_callback", True)
        self.__setattr__("test_post_init_feature_callback", False)
        self.__setattr__("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        self.__setattr__("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.__setattr__("test_on_exit_post_init_callback", True)
        return None


@dataclass
class MockTrajectoryComposedParentNestedOnly(AbstractTrajectoryFeature):
    child_one: MockTrajectoryChildRosBagCase
    child_two: MockTrajectoryChildRosBagCase

    def on_begin_post_init_callback(self):  # self.dd_metadata += 99
        # Create test attribute for post-init-callback logic
        self.__setattr__("test_on_begin_post_init_callback", True)
        self.__setattr__("test_post_init_feature_callback", False)
        self.__setattr__("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        self.__setattr__("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.__setattr__("test_on_exit_post_init_callback", True)
        return None
