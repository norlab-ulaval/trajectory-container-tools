# coding=utf-8

import numpy as np

from trajectory_container_tools.trj_dataclasses.ros2_primitive_dataclass import Point, Quaternion
from trajectory_container_tools.utils.shadow_data_container import (
    instanciate_shadow_data_container,
    )
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import (
    NavMsgsOdometryFlat, Pose,
    PoseWithCovariance,
    )


class TestInstanciateShadowDataContainer:

    def test_case_leaf_container(self):
        sdc = instanciate_shadow_data_container(Point)

        assert isinstance(sdc, dict)
        assert sdc == {
                'type': Point,
                'x':    {'data': [], 'type': np.ndarray},
                'y':    {'data': [], 'type': np.ndarray},
                'z':    {'data': [], 'type': np.ndarray},
                }

        # print(sdc)

    def test_case_parent_container(self):
        sdc = instanciate_shadow_data_container(Pose)

        assert isinstance(sdc, dict)
        assert sdc == {
                'type':        Pose,
                # 'feature_name':   None,
                # 'timesteps_indices': None,
                'position':    {
                        'type': Point,
                        'x':    {'data': [], 'type': np.ndarray},
                        'y':    {'data': [], 'type': np.ndarray},
                        'z':    {'data': [], 'type': np.ndarray},
                        },
                'orientation': {
                        'type': Quaternion,
                        'x':    {'data': [], 'type': np.ndarray},
                        'y':    {'data': [], 'type': np.ndarray},
                        'z':    {'data': [], 'type': np.ndarray},
                        'w':    {'data': [], 'type': np.ndarray},
                        }
                }

        # print(sdc)
