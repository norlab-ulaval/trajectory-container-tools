# coding=utf-8
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

import numpy as np

from .abstract_trajectory_features_bag_dataclass import AbstractTrajectoryFeaturesBag
from .abstract_array_trajectory_dataclass import AbstractTrajectoryArray
from trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass import (
    NestedRosStampedFeature,
)
from trajectory_container_tools.dataclasses.ros_msgs.stamped_dataclass import (
    RosStampedFeature,
)
from trajectory_container_tools.dataclasses.ros_msgs.non_trajectory_dataclass import (
    RosFeaturesArray,
)
from trajectory_container_tools.dataclasses.ros_msgs.core_dataclass_utils import (
    get_timestamps_slice,
)
from trajectory_container_tools.temporal import Timestamps
from ...temporal.trajectory_timestamps_metadata import TrajectoryTimestampsMetadata


@dataclass()
class AbstractTrajectoryStampedFeaturesBag(AbstractTrajectoryFeaturesBag):
    """
    AbstractTrajectoryStampedFeaturesBag extends the functionality of
    AbstractTrajectoryFeaturesBag to handle chunk-based operations and iteration for
    stamped features.

    This dataclass serves the purpose of managing and processing operations for multi-feature data
    structured in chunks, such as splitting, accessing, and iterating over these chunks based on
    a specific attribute. Specifically, it allows slicing data based on timestamp, ensuring
    structured handling of nested and complex data. It defines methods to calculate the number of
    chunks, index elements, and iterate through the data at finer levels of granularity. This is
    useful in scenarios requiring consistent and efficient handling of timestamp-aligned data
    features across topics.

    :ivar dataset_info: Information about the dataset.
    :type dataset_info: str
    :ivar bag_timestamps: Optional timestamps related to bags. Defaults to None.
    :type bag_timestamps: Optional[Timestamps]
    :ivar chunk_on: Name of the attribute used to split the data into chunks.
    :type chunk_on: str
    """

    chunk_on: str = field(default="topic_teleop", kw_only=True)
    _iter_index: int = field(default=0, init=False)

    def __post_init__(self):
        chunk_on_is_default = self.chunk_on == "topic_teleop"
        if (
            len(self.topic_key_list) == 1
            and self.chunk_on not in self.topic_key_list
            and chunk_on_is_default
        ):
            self.chunk_on = self.topic_key_list[0]
        elif self.chunk_on not in self.topic_key_list:
            raise ValueError(
                f"chunk_on={self.chunk_on} is not in "
                f"topic_key_list={self.topic_key_list}. "
                f"Please set chunk_on to a valide feature."
            )

        super().__post_init__()

    @classmethod
    def _dataclass_internal_field(cls) -> list[str]:
        return super()._dataclass_internal_field() + ["_iter_index"]

    @property
    def chunks_total(self) -> int:
        return len(self.get_dynamic_field(self.chunk_on))

    def __len__(self) -> int:
        return self.chunks_total

    def _metadata_field_str(
        self, m_space: str, repr_str: str, key: str, value: Any
    ) -> str:
        repr_str = super()._metadata_field_str(m_space, repr_str, key, value)
        repr_str += f"{m_space}chunks_total: {self.chunks_total}\n"
        return repr_str

    def __getitem__(
        self, chunk_idx: Union[int, slice]
    ) -> "AbstractTrajectoryStampedFeaturesBag":

        mf_dataclass_at_t = deepcopy(self)

        chunk_on_attribute = self.get_dynamic_field(self.chunk_on)
        if isinstance(chunk_idx, slice):
            chunck_on_timestamp = chunk_on_attribute.header.timestamps[
                chunk_idx.stop - 1
            ].stamps
        else:
            chunck_on_timestamp = chunk_on_attribute.header.timestamps[chunk_idx].stamps

        if self.bag_timestamps is not None:
            bag_timestamps_subset = _get_attribute_timestamps(
                chunck_on_timestamp, chunk_idx, chunk_on_attribute, self.bag_timestamps
            )
            mf_dataclass_at_t.__setattr__("bag_timestamps", bag_timestamps_subset)

        each_attribute: Union[
            RosStampedFeature, NestedRosStampedFeature, RosFeaturesArray
        ]
        for each_topic in self.topic_key_list:
            each_attribute = self.get_dynamic_field(each_topic)

            if each_topic is self.chunk_on:
                each_attribute = each_attribute[chunk_idx]
            elif isinstance(each_attribute, AbstractTrajectoryArray):
                registred_trj_object_list_name = (
                    each_attribute.registred_trajectory_object_list
                )
                if registred_trj_object_list_name is not None:
                    trj_container_list_object = []
                    for idx, each in enumerate(each_attribute):
                        each = _get_attribute_timestamps(
                            chunck_on_timestamp, chunk_idx, chunk_on_attribute, each
                        )
                        trj_container_list_object.append(each)
                    each_attribute.__setattr__(
                        registred_trj_object_list_name, trj_container_list_object
                    )
                else:
                    # Note: set attribute as is
                    pass
            else:
                each_attribute = _get_attribute_timestamps(
                    chunck_on_timestamp, chunk_idx, chunk_on_attribute, each_attribute
                )

            mf_dataclass_at_t.__setattr__(each_topic, each_attribute)

        return mf_dataclass_at_t

    def __iter__(self) -> "AbstractTrajectoryStampedFeaturesBag":
        self._iter_index = 0
        return self

    def __next__(self) -> "AbstractTrajectoryStampedFeaturesBag":
        if self._iter_index < self.chunks_total:
            item = self[self._iter_index]
            self._iter_index += 1
            return item
        else:
            raise StopIteration

    def get_timestamps(
        self,
        start: int,
        stop: Optional[int] = None,
        startpoint: bool = True,
        endpoint: bool = False,
    ) -> "AbstractTrajectoryStampedFeaturesBag":
        """
        Retrieve a trajectory interval within a specified timestamps range.

        This function allows extracting trajectory associated data from a given timestamps range
        defined by the start, stop, and optional parameters controlling the inclusion of the range
        startpoint and endpoint.

        :param start: The starting timestamp value of the slice.
        :param stop: The optional stopping timestamp value of the slice. If not specified,
            the slice will retrive a trajectory of length 1.
        :param startpoint: A boolean indicating whether to include the starting point in the slice.
        :param endpoint: A boolean indicating whether to include the stopping point in the slice.
        :return: A data slice corresponding to the timestamps within the specified range.
        """
        mf_dataclass_at_t = deepcopy(self)

        if self.bag_timestamps is not None:
            timestamps_slice = get_timestamps_slice(
                self.bag_timestamps,
                start=start,
                stop=stop,
                startpoint=startpoint,
                endpoint=endpoint,
                resolve_out_of_bounds=True,
            )
            bag_timestamps_subset = mf_dataclass_at_t.bag_timestamps[timestamps_slice]
            mf_dataclass_at_t.__setattr__("bag_timestamps", bag_timestamps_subset)

        for each_topic in self.topic_key_list:
            each_attribute: Union[
                RosStampedFeature, NestedRosStampedFeature, RosFeaturesArray
            ] = self.get_dynamic_field(each_topic)

            if isinstance(each_attribute, AbstractTrajectoryArray):
                registred_trj_object_list_name = (
                    each_attribute.registred_trajectory_object_list
                )
                if registred_trj_object_list_name is not None:
                    trj_container_list_object = []
                    for idx, each in enumerate(each_attribute):
                        each: Union[RosStampedFeature, NestedRosStampedFeature] = (
                            each.get_timestamps(
                                start=start,
                                stop=stop,
                                startpoint=startpoint,
                                endpoint=endpoint,
                                resolve_out_of_bounds=True,
                            )
                        )
                        trj_container_list_object.append(each)
                    each_attribute.__setattr__(
                        registred_trj_object_list_name, trj_container_list_object
                    )
                else:
                    # Note: set attribute as is
                    pass
            else:
                each_attribute = each_attribute.get_timestamps(
                    start=start,
                    stop=stop,
                    startpoint=startpoint,
                    endpoint=endpoint,
                    resolve_out_of_bounds=True,
                )

            mf_dataclass_at_t.__setattr__(each_topic, each_attribute)

        return mf_dataclass_at_t

    @property
    def trajectory_timestamps(self) -> np.ndarray[int, np.dtype[int]]:
        """
        Returns all timestamps for all features. The returned numpy array is sorted and contains unique timestamps.
        Note: Those does not include the `bag_timestamps` ones.

        Usage:

        >>> print(container.trajectory_timestamps)
        [1711038330346603696, 1711038330351773872, 1711038330411627056, 1711038330436485488]

        :returns: A numpy array of unique timestamps.
        """
        all_features_stamps = []

        for each_topic in self.topic_key_list:
            each_attribute: Union[
                RosStampedFeature, NestedRosStampedFeature, RosFeaturesArray
            ] = self.get_dynamic_field(each_topic)

            if isinstance(each_attribute, AbstractTrajectoryArray):
                registred_trj_object_list_name = (
                    each_attribute.registred_trajectory_object_list
                )
                if registred_trj_object_list_name is not None:
                    for idx, each in enumerate(each_attribute):
                        each: Union[RosStampedFeature, NestedRosStampedFeature]
                        all_features_stamps.append(each.header.timestamps.stamps)
            else:
                all_features_stamps.append(each_attribute.header.timestamps.stamps)

        return np.unique(np.concatenate(all_features_stamps))

    @property
    def trajectory_timestamps_limits(self) -> TrajectoryTimestampsMetadata:
        """
        Retrieve the first and last timestamps from all features timestamps.
        Note: Those does not include the `bag_timestamps` ones.

        Usage:

        >>> print(container.trajectory_timestamps_limits)
        TrajectoryTimestampsMetadata(first=1711038330346603696, last=1711038330436485488)
        >>> print(container.trajectory_timestamps_limits.first)
        1711038330346603696
        >>> print(container.trajectory_timestamps_limits.last)
        1711038330436485488

        :return: A tuple containing the first and the last timestamps from all features timestamps.
        """

        return TrajectoryTimestampsMetadata(
            start_time=self.trajectory_timestamps[0],
            end_time=self.trajectory_timestamps[-1],
        )


def _get_attribute_timestamps(
    chunck_on_timestamp: int,
    chunk_idx: Union[int, slice],
    chunk_on_topic: RosStampedFeature,
    each_attribute: RosStampedFeature | NestedRosStampedFeature | Timestamps,
) -> RosStampedFeature | NestedRosStampedFeature | RosFeaturesArray | Timestamps:
    if isinstance(chunk_idx, slice):
        chunk_idx = chunk_idx.start

    if chunk_idx == 0:
        if not isinstance(each_attribute, Timestamps):
            each_start_timestamp = each_attribute.header.timestamps[0].stamps
        else:
            each_start_timestamp = each_attribute[0].stamps

        startpoint = True
    else:
        # Fetch the previous `chunck_on_timestamp` value
        each_start_timestamp = chunk_on_topic.header.timestamps[chunk_idx - 1].stamps
        startpoint = True

    endpoint = False
    if not isinstance(each_attribute, Timestamps):
        each_attribute = each_attribute.get_timestamps(
            start=each_start_timestamp,
            stop=chunck_on_timestamp,
            startpoint=startpoint,
            endpoint=endpoint,
            resolve_out_of_bounds=True,
        )
    else:
        timestamps_slice = get_timestamps_slice(
            each_attribute,
            start=each_start_timestamp,
            stop=chunck_on_timestamp,
            startpoint=startpoint,
            endpoint=endpoint,
            resolve_out_of_bounds=True,
        )
        each_attribute = each_attribute[timestamps_slice]
    return each_attribute
