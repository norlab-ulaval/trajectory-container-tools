# coding=utf-8
from copy import deepcopy
from dataclasses import dataclass
from typing import Tuple, Union

import numpy as np
import pytest

from trajectory_container_tools.dataclasses import Header, RosStampedDataclass
from trajectory_container_tools.dataclasses.core.abstract_multifeature_dataclass import (
    AbstractMultifeatureStampedDataclass,
)
from trajectory_container_tools.temporal import Timestamps


# ==== Mock dataclasses ===========================================================================
@dataclass
class MockRosStampedDataclass(RosStampedDataclass):
    mock_feature: np.ndarray


@dataclass
class MockMultifeatureStampedDataclass(AbstractMultifeatureStampedDataclass):
    topic_mock_observation: MockRosStampedDataclass
    topic_mock_action: MockRosStampedDataclass


@dataclass
class MockTopicsTimestamps:
    t_obs_timestamps: Union[np.ndarray, list]
    t_act_timestamps: Union[np.ndarray, list]

    def __post_init__(self):
        self.t_obs_timestamps = (
            np.array(self.t_obs_timestamps, dtype=int) * 100000000 + 1000000000000000000
        )
        self.t_act_timestamps = (
            np.array(self.t_act_timestamps, dtype=int) * 100000000 + 1000000000000000000
        )

    @property
    def t_trajectorie_stamps(self) -> np.ndarray:
        all_stamps = np.concatenate((self.t_obs_timestamps, self.t_act_timestamps))
        return np.unique(all_stamps)

    def __len__(self):
        return self.t_trajectorie_stamps.size

# ==== Mock timestamps cases ======================================================================


def setup_mock_timestamps_case_alternate() -> MockTopicsTimestamps:
    return MockTopicsTimestamps(
        t_obs_timestamps=[
            1,
            3,
            5,
            7,
            9,
            11,
        ],
        t_act_timestamps=[
            2,
            4,
            6,
            8,
            10,
            12,
        ],
    )


def setup_mock_timestamps_case_more_obs() -> MockTopicsTimestamps:
    return MockTopicsTimestamps(
        t_obs_timestamps=[
            1,
            2,
            4,
            5,
            7,
            8,
            9,
            10,
        ],
        t_act_timestamps=[
            3,
            6,
            11,
        ],
    )


def setup_mock_timestamps_case_more_act() -> MockTopicsTimestamps:
    return MockTopicsTimestamps(
        t_obs_timestamps=[
            1,
            3,
            7,
        ],
        t_act_timestamps=[
            2,
            4,
            5,
            6,
        ],
    )


def setup_mock_timestamps_case_act_and_obs_shared_stamps() -> MockTopicsTimestamps:
    return MockTopicsTimestamps(
        t_obs_timestamps=[
            1,
            2,
            3,
            4,
        ],
        t_act_timestamps=[
            3,
            5,
        ],
    )


def setup_mock_timestamps_case_last_stamp_on_obs() -> MockTopicsTimestamps:
    """
    Should raise IndexError on `print(mf_container[1])`
    """
    return MockTopicsTimestamps(
        t_obs_timestamps=[
            1,
            2,
            4,
            5,
        ],
        t_act_timestamps=[
            3,
        ],
    )


def setup_mock_timestamps_case_mixing() -> MockTopicsTimestamps:
    return MockTopicsTimestamps(
        t_obs_timestamps=[
            1,
            3,
            5,
            7,
            8,
            10,
            12,
            13,
            15,
            16,
            18,
        ],
        t_act_timestamps=[
            2,
            5,
            8,
            11,
            14,
            17,
            20,
        ],
    )


# ==== Test setup/teardown ========================================================================
@pytest.fixture(scope="function")
def setup_mock_mf_container():

    def setup_fct(timestamp_case) -> MockMultifeatureStampedDataclass:
        topic_mock_obs = MockRosStampedDataclass(
            feature_name="Mock observation topic",
            header=Header(
                frame_id="topic_obs",
                timestamps=Timestamps(timestamp_case.t_obs_timestamps),
            ),
            mock_feature=np.arange(timestamp_case.t_obs_timestamps.size),
        )

        topic_mock_act = MockRosStampedDataclass(
            feature_name="Mock action topic",
            header=Header(
                frame_id="topic_act",
                timestamps=Timestamps(timestamp_case.t_act_timestamps),
            ),
            mock_feature=np.arange(timestamp_case.t_act_timestamps.size),
        )

        mf_container = MockMultifeatureStampedDataclass(
            dataset_info="Mock",
            topic_mock_observation=topic_mock_obs,
            topic_mock_action=topic_mock_act,
            bag_timestamps=None,
            chunk_on="topic_mock_action",
        )
        return deepcopy(mf_container)

    return setup_fct
