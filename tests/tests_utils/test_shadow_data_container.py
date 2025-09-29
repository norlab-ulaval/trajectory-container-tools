# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import (
    Point,
    Quaternion,
)
from trajectory_container_tools.utils.shadow_data_container import (
    instanciate_shadow_data_container,
)
from trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass import Pose
from trajectory_container_tools.dataclasses import RosDataclass


@dataclass()
class MockListOfNestedDataclass(RosDataclass):
    list_of_point: list[Point]


class TestInstanciateShadowDataContainer:
    def test_case_leaf_container(self):
        sdc = instanciate_shadow_data_container(Point)

        assert isinstance(sdc, dict)
        assert sdc == {
            "type": Point,
            "x": {"data": [], "type": np.ndarray},
            "y": {"data": [], "type": np.ndarray},
            "z": {"data": [], "type": np.ndarray},
        }

        # print(sdc)

    def test_case_parent_container(self):
        sdc = instanciate_shadow_data_container(Pose)

        assert isinstance(sdc, dict)
        assert sdc == {
            "type": Pose,
            # 'feature_name':   None,
            # 'timesteps_indices': None,
            "position": {
                "type": Point,
                "x": {"data": [], "type": np.ndarray},
                "y": {"data": [], "type": np.ndarray},
                "z": {"data": [], "type": np.ndarray},
            },
            "orientation": {
                "type": Quaternion,
                "x": {"data": [], "type": np.ndarray},
                "y": {"data": [], "type": np.ndarray},
                "z": {"data": [], "type": np.ndarray},
                "w": {"data": [], "type": np.ndarray},
            },
        }

        # print(sdc)

    def test_case_list_of_type(self):
        sdc = instanciate_shadow_data_container(MockListOfNestedDataclass)

        print(sdc)

        assert isinstance(sdc, dict)
        assert sdc == {
            "type": MockListOfNestedDataclass,
            "list_of_point": [
                {
                    "type": Point,
                    "x": {"data": [], "type": np.ndarray},
                    "y": {"data": [], "type": np.ndarray},
                    "z": {"data": [], "type": np.ndarray},
                },
            ],
        }
