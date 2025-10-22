# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools.dataclasses.ros_msgs.geometry_msgs_dataclass import (
    GeometryMsgsPoint,
    GeometryMsgsQuaternion,
)
from trajectory_container_tools.temporal import Timestamps
from trajectory_container_tools.utils.shadow_data_container import (
    instanciate_shadow_data_container,
)
from trajectory_container_tools.dataclasses import GeometryMsgsPose, RosFeatureArray


@dataclass()
class MockListOfNestedFeatureArray(RosFeatureArray):
    list_of_point: list[GeometryMsgsPoint]


class TestInstanciateShadowDataContainer:
    def test_case_leaf_container(self):
        sdc = instanciate_shadow_data_container(GeometryMsgsPoint)

        assert isinstance(sdc, dict)
        assert sdc == {
            "type": GeometryMsgsPoint,
            "nested_lvl":        0,
            "bag_recorded_timestamps": {"data": [], "type": Timestamps},
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
            "nested_lvl":        0,
            "bag_recorded_timestamps": {"data": [], "type": Timestamps},
            "position":    {
                "type": GeometryMsgsPoint,
                "nested_lvl": 1,
                "bag_recorded_timestamps": {"data": [], "type": Timestamps},
                "x":    {"data": [], "type": np.ndarray},
                "y":    {"data": [], "type": np.ndarray},
                "z":    {"data": [], "type": np.ndarray},
            },
            "orientation": {
                "type": GeometryMsgsQuaternion,
                "nested_lvl": 1,
                "bag_recorded_timestamps": {"data": [], "type": Timestamps},
                "x":    {"data": [], "type": np.ndarray},
                "y":    {"data": [], "type": np.ndarray},
                "z":    {"data": [], "type": np.ndarray},
                "w":    {"data": [], "type": np.ndarray},
            },
        }

        # print(sdc)

    def test_case_list_of_type(self):
        sdc = instanciate_shadow_data_container(MockListOfNestedFeatureArray)

        print(sdc)

        assert isinstance(sdc, dict)
        assert sdc == {
            "type":          MockListOfNestedFeatureArray,
            "nested_lvl": 0,
            "bag_recorded_timestamps": {"data": [], "type": Timestamps},
            "list_of_point": [
                {
                    "type": GeometryMsgsPoint,
                    "nested_lvl": 1,
                    "bag_recorded_timestamps": {"data": [], "type": Timestamps},
                    "x":    {"data": [], "type": np.ndarray},
                    "y":    {"data": [], "type": np.ndarray},
                    "z":    {"data": [], "type": np.ndarray},
                },
            ],
        }
