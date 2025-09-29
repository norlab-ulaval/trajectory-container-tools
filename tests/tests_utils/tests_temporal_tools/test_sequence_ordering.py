# coding=utf-8
from trajectory_container_tools.dataclasses.ros2_feature_dataclass import (
    RosStampedDataclass,
)
from trajectory_container_tools.temporal.sequence_ordering import (
    fix_sequence_ordering_base_on_timestamps,
)
from trajectory_container_tools.temporal.timestamps import (
    validate_timestamps_ordering,
)


class TestTrajectorySequenceOrderingLogic:
    def test_fix_sequence_ordering_base_on_timestamps_case_input_ordered(
        self, mock_trajectory_dict_ordered
    ):
        fixed_trajectory_dict = fix_sequence_ordering_base_on_timestamps(
            shadow_data_container=mock_trajectory_dict_ordered,
            data_container_type_=RosStampedDataclass,
        )

        ts = fixed_trajectory_dict["header"].timestamps

        # Validate the results
        validate_timestamps_ordering(ts)

    def test_fix_sequence_ordering_base_on_timestamps_case_input_unordered(
        self, mock_trajectory_dict_unordered, mock_trajectory_dict_ordered
    ):
        fixed_trajectory_dict = fix_sequence_ordering_base_on_timestamps(
            shadow_data_container=mock_trajectory_dict_unordered,
            data_container_type_=RosStampedDataclass,
        )

        ts = fixed_trajectory_dict["header"].timestamps

        # Validate the results
        validate_timestamps_ordering(ts)

        assert fixed_trajectory_dict == mock_trajectory_dict_ordered

        # print(fixed_trajectory_dict)
