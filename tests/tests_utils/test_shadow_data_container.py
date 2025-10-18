# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import (
    GeometryMsgsPoint,
    GeometryMsgsQuaternion,
)
from trajectory_container_tools.utils.shadow_data_container import (
    instanciate_shadow_data_container,
)
from trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass import GeometryMsgsPose
from trajectory_container_tools.dataclasses import RosDataclass


@dataclass()
class MockListOfNestedDataclass(RosDataclass):
    list_of_point: list[GeometryMsgsPoint]


class TestInstanciateShadowDataContainer:
    def test_case_leaf_container(self):
        sdc = instanciate_shadow_data_container(GeometryMsgsPoint)

        assert isinstance(sdc, dict)
        assert sdc == {
            "type": GeometryMsgsPoint,
            "x":    {"data": [], "type": np.ndarray},
            "y":    {"data": [], "type": np.ndarray},
            "z":    {"data": [], "type": np.ndarray},
        }

        # print(sdc)

    def test_case_parent_container(self):
        sdc = instanciate_shadow_data_container(GeometryMsgsPose)

        assert isinstance(sdc, dict)
        assert sdc == {
            "type":        GeometryMsgsPose,
            # 'feature_name':   None,
            # 'timesteps_indices': None,
            "position":    {
                "type": GeometryMsgsPoint,
                "x":    {"data": [], "type": np.ndarray},
                "y":    {"data": [], "type": np.ndarray},
                "z":    {"data": [], "type": np.ndarray},
            },
            "orientation": {
                "type": GeometryMsgsQuaternion,
                "x":    {"data": [], "type": np.ndarray},
                "y":    {"data": [], "type": np.ndarray},
                "z":    {"data": [], "type": np.ndarray},
                "w":    {"data": [], "type": np.ndarray},
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
                    "type": GeometryMsgsPoint,
                    "x":    {"data": [], "type": np.ndarray},
                    "y":    {"data": [], "type": np.ndarray},
                    "z":    {"data": [], "type": np.ndarray},
                },
            ],
        }
