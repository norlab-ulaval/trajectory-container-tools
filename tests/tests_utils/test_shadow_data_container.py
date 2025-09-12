# coding=utf-8

import numpy as np

from trajectory_container_tools.utils.shadow_data_container import (
    instanciate_shadow_data_container,
    )
from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import (
    Pose,
    PoseWithCovariance,
    )


class TestInstanciateShadowDataContainer:

    def test_case_no_nested_container(self):
        sdc = instanciate_shadow_data_container(Pose)

        assert isinstance(sdc, dict)
        assert sdc == {
                'type':           Pose,
                # 'feature_name':   None,
                # 'timesteps_indices': None,
                'position_x':     {'data': [], 'type': np.ndarray},
                'position_y':     {'data': [], 'type': np.ndarray},
                'position_z':     {'data': [], 'type': np.ndarray},
                'orientation_x':  {'data': [], 'type': np.ndarray},
                'orientation_y':  {'data': [], 'type': np.ndarray},
                'orientation_z':  {'data': [], 'type': np.ndarray},
                'orientation_w':  {'data': [], 'type': np.ndarray},
                }

        # print(sdc)

    def test_case_nested_container(self):
        sdc = instanciate_shadow_data_container(PoseWithCovariance)

        assert isinstance(sdc, dict)
        assert sdc == {
                'type':           PoseWithCovariance,
                # 'feature_name':   None,
                # 'timesteps_indices': None,
                'pose':           {
                        'type':           Pose,
                        # 'feature_name':   None,
                        # 'timesteps_indices': None,
                        'position_x':     {'data': [], 'type': np.ndarray},
                        'position_y':     {'data': [], 'type': np.ndarray},
                        'position_z':     {'data': [], 'type': np.ndarray},
                        'orientation_x':  {'data': [], 'type': np.ndarray},
                        'orientation_y':  {'data': [], 'type': np.ndarray},
                        'orientation_z':  {'data': [], 'type': np.ndarray},
                        'orientation_w':  {'data': [], 'type': np.ndarray},
                        },
                'covariance':     {'data': [], 'type': np.ndarray},
                }

        # print(sdc)


