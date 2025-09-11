# coding=utf-8

import pytest
import numpy as np

from trajectory_container_tools.utils.data_sanity_checks import (
    fix_sequence_ordering_base_on_timestamps, timestamp_causal_ordering_sanity_check,
    )
from trajectory_container_tools.utils.shadow_data_container import (
    instanciate_shadow_data_container,
    )
from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import (
    Pose,
    PoseWithCovariance, NavMsgsOdometry, RosBagFeatureDataclass,
    )


class TestInstanciateShadowDataContainer:

    def test_case_no_nested_container(self):
        sdc = instanciate_shadow_data_container(Pose)

        assert isinstance(sdc, dict)
        assert sdc == {
                'type':           Pose,
                # 'feature_name':   None,
                # 'timesteps': None,
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
                # 'timesteps': None,
                'pose':           {
                        'type':           Pose,
                        # 'feature_name':   None,
                        # 'timesteps': None,
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


class TestTrajectorySequenceOrderingLogic:

    def test_fix_sequence_ordering_base_on_timestamps_case_input_ordered(
            self, mock_trajectory_dict_ordered
            ):
        fixed_trajectory_dict = fix_sequence_ordering_base_on_timestamps(
                shadow_data_container=mock_trajectory_dict_ordered,
                data_container_type_=RosBagFeatureDataclass)

        timestamp_causal_ordering_sanity_check(fixed_trajectory_dict)

    def test_fix_sequence_ordering_base_on_timestamps_case_input_unordered(
            self, mock_trajectory_dict_unordered, mock_trajectory_dict_ordered
            ):
        fixed_trajectory_dict = fix_sequence_ordering_base_on_timestamps(
                shadow_data_container=mock_trajectory_dict_unordered,
                data_container_type_=RosBagFeatureDataclass)

        timestamp_causal_ordering_sanity_check(fixed_trajectory_dict)

        assert fixed_trajectory_dict == mock_trajectory_dict_ordered

        # print(fixed_trajectory_dict)
