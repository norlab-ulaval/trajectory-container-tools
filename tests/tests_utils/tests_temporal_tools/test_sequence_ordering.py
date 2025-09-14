# coding=utf-8
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import \
    RosStampedDataclass
from trajectory_container_tools.utils.temporal_tools.sequence_ordering import \
    fix_sequence_ordering_base_on_timestamps
from trajectory_container_tools.utils.temporal_tools.timestamps import \
    timestamp_causal_ordering_sanity_check


class TestTrajectorySequenceOrderingLogic:

    def test_fix_sequence_ordering_base_on_timestamps_case_input_ordered(
            self, mock_trajectory_dict_ordered
            ):
        fixed_trajectory_dict = fix_sequence_ordering_base_on_timestamps(
                shadow_data_container=mock_trajectory_dict_ordered,
                data_container_type_=RosStampedDataclass)

        ts = fixed_trajectory_dict["header"].timestamps

        # Validate the results
        timestamp_causal_ordering_sanity_check(ts)

    def test_fix_sequence_ordering_base_on_timestamps_case_input_unordered(
            self, mock_trajectory_dict_unordered, mock_trajectory_dict_ordered
            ):
        fixed_trajectory_dict = fix_sequence_ordering_base_on_timestamps(
                shadow_data_container=mock_trajectory_dict_unordered,
                data_container_type_=RosStampedDataclass)

        ts = fixed_trajectory_dict["header"].timestamps

        # Validate the results
        timestamp_causal_ordering_sanity_check(ts)

        assert fixed_trajectory_dict == mock_trajectory_dict_ordered

        # print(fixed_trajectory_dict)
