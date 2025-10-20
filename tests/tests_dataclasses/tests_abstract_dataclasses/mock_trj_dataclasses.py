# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools.dataclasses.core.abstract_trajectory_feature_dataclass import AbstractTrajectoryFeature


@dataclass
class MockTrajectoryChildDFcase(AbstractTrajectoryFeature):
    aa: np.ndarray
    bb: np.ndarray
    cc: np.ndarray
    dd_metadata: np.ndarray = np.array([0, 0, 0])

    @classmethod
    def non_trajectory_field(cls):
        return super().non_trajectory_field() + ["dd_metadata"]

    def on_begin_post_init_callback(self):
        feature = self.__getattribute__("dd_metadata")
        self.__setattr__("dd_metadata", feature + 99)

        # Create test attribute for post-init-callback logic
        self.__setattr__("test_on_begin_post_init_callback", True)
        self.__setattr__("test_post_init_feature_callback", False)
        self.__setattr__("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        feature = self.__getattribute__(feature_name)
        feature_ini = feature[..., 0]
        self.__setattr__(f"{feature_name}_init", feature_ini)

        self.__setattr__("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.__setattr__("test_on_exit_post_init_callback", True)
        return None


@dataclass
class MockTrajectoryChildRosBagCase(AbstractTrajectoryFeature):
    aa: np.ndarray
    bb: np.ndarray
    cc: np.ndarray
    dd_metadata: np.ndarray = np.array([0, 0, 0])

    @classmethod
    def non_trajectory_field(cls):
        return super().non_trajectory_field() + ["dd_metadata"]

    def on_begin_post_init_callback(self):  # self.dd_metadata += 99
        feature = self.__getattribute__("dd_metadata")
        self.__setattr__("dd_metadata", feature + 99)

        # Create test attribute for post-init-callback logic
        self.__setattr__("test_on_begin_post_init_callback", True)
        self.__setattr__("test_post_init_feature_callback", False)
        self.__setattr__("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        feature = self.__getattribute__(feature_name)
        feature_ini = feature[0, ...]
        self.__setattr__(f"{feature_name}_init", feature_ini)

        self.__setattr__("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.__setattr__("test_on_exit_post_init_callback", True)
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
