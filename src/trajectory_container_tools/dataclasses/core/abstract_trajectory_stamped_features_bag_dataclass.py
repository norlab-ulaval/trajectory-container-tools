# coding=utf-8
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

import numpy as np

from .abstract_trajectory_features_bag_dataclass import AbstractTrajectoryFeaturesBag
from .abstract_trajectory_array_dataclass import AbstractTrajectoryUnboundedArray
from trajectory_container_tools.dataclasses.ros_msgs.core_dataclass import (
    RosFeatureArray,
    RosStampedFeature,
    RosFeature,
)
from trajectory_container_tools.dataclasses.ros_msgs.core_dataclass_utils import (
    get_timestamps_slice,
)
from trajectory_container_tools.temporal import Timestamps
from ...temporal.timestamps import TimestampOutOfBoundError
from ...temporal.trajectory_timestamps_metadata import (
    TrajectoryTimestampsMetadata,
    TrajectoryTimestampsMetadataBag,
)
from trajectory_container_tools.utils.typing.tct_custom_field import (
    NonTrajectoryField,
    ContainerInternalField,
)


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
    _iter_index: ContainerInternalField[int] = field(default=0, init=False)

    def __post_init__(self):
        if self.chunk_on in self.topic_key_list:
            pass
        elif len(self.topic_key_list) == 1 and self.chunk_on not in self.topic_key_list:
            self.chunk_on = self.topic_key_list[0]
        elif self.chunk_on not in self.topic_key_list:
            raise ValueError(
                f"chunk_on={self.chunk_on} is not in "
                f"topic_key_list={self.topic_key_list}. "
                f"Please set chunk_on to a valide feature."
            )

        super().__post_init__()

    def get_chunk_on_timestamps(self) -> Timestamps:
        """
        Retrieve the timestamps from the specified chunk-on attribute.

        This method extracts timestamps based on the `chunk_on` attribute of the object.
        If the attribute includes a dynamic field "header," its associated timestamps
        are returned. Otherwise, the bag-recorded timestamps are returned.

        :return: Timestamps based on the chunk-on attribute.
        """
        chunk_on_attribute: Union[RosStampedFeature, RosFeature, RosFeatureArray] = (
            self.get_dynamic_attribute(self.chunk_on)
        )

        # Update bag start/stop to align with chunk_on attribute
        if chunk_on_attribute.has_dynamic_attribute("header"):
            return chunk_on_attribute.header.timestamps
        else:
            return chunk_on_attribute.bag_recorded_timestamps

    @property
    def chunks_total(self) -> int:
        """
        Returns the total number of chunks derived from the "chunk_on" attribute.

        This property calculates the total count of chunks based on the dynamic
        field specified by `chunk_on`.

        :return: The total number of chunks.
        """
        # return len(self.get_dynamic_attribute(self.chunk_on)) - 1
        return len(self.get_chunk_on_timestamps())

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

        # .... Set chunk reference ................................................................
        chunck_on_timestamps = self.get_chunk_on_timestamps()

        # .... Set bag level timestamps ...........................................................
        if self.bag_timestamps is not None:
            bag_timestamps_subset = _get_attribute_at_timestamps(
                chunck_on_timestamps, chunk_idx, self.bag_timestamps
            )
            mf_dataclass_at_t.__setattr__("bag_timestamps", bag_timestamps_subset)

        # .... Set topic attributes ...............................................................
        for each_topic in self.topic_key_list:
            each_attribute: Union[RosStampedFeature, RosFeatureArray] = (
                self.get_dynamic_attribute(each_topic)
            )

            if each_topic is self.chunk_on:
                each_attribute = each_attribute[chunk_idx]
            elif isinstance(each_attribute, AbstractTrajectoryUnboundedArray):
                # (☕minor) ToDo: update unit-test (ref task TCT-91)

                for each_trj_array_name in each_attribute.trajectory_array_field_names(
                    trajectory_containers_array_only=True,
                ):
                    trj_container_list_object = []
                    for each_trj_array in each_attribute.get_dynamic_attribute(
                        each_trj_array_name
                    ):
                        each_trj_array = _get_attribute_at_timestamps(
                            chunck_on_timestamps, chunk_idx, each_trj_array
                        )
                        trj_container_list_object.append(each_trj_array)
                    each_attribute.__setattr__(
                        each_trj_array_name, trj_container_list_object
                    )

                for each_trj_array_name in each_attribute.trajectory_array_field_names(
                    non_trajectory_containers_array_only=True,
                ):
                    each_trj_array = _get_attribute_at_timestamps(
                        chunck_on_timestamps, chunk_idx, each_trj_array
                    )
                    each_attribute.__setattr__(each_trj_array_name, each_trj_array)

            else:
                each_attribute = _get_attribute_at_timestamps(
                    chunck_on_timestamps, chunk_idx, each_attribute
                )

            mf_dataclass_at_t.__setattr__(each_topic, each_attribute)

        return mf_dataclass_at_t

    def __iter__(self) -> "AbstractTrajectoryStampedFeaturesBag":
        self._iter_index = 0
        return self

    # noinspection PyTypeChecker
    def __next__(self) -> "AbstractTrajectoryStampedFeaturesBag":
        if self._iter_index < self.chunks_total:
            item = self[self._iter_index]
            self._iter_index += 1
            return item
        else:
            raise StopIteration

    def get_timestamps_interval(
        self,
        start: int,
        stop: Optional[int] = None,
        startpoint: bool = True,
        endpoint: bool = True,
        resolve_out_of_bounds=True,
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
            This affect all features except the 'chunk_on' one.
        :param endpoint: A boolean indicating whether to include the 'chunk_on' feature stopping
            point in the slice.
        :param resolve_out_of_bounds: (Default True) Disable out of bound check and resolve to the
            nearest timestamps bound. (False) Raise TimestampOutOfBoundError on bound violation
            if 'startpoint' and/or 'endpoint' are False.
        :return: A data slice corresponding to the timestamps within the specified range.
        """

        mf_dataclass_at_t = deepcopy(self)

        if self.bag_timestamps is not None:
            timestamps_slice = get_timestamps_slice(
                self.bag_timestamps,
                start=start,
                stop=stop,
                startpoint=True and startpoint,
                endpoint=True and endpoint,
                resolve_out_of_bounds=resolve_out_of_bounds,
            )
            bag_timestamps_subset = mf_dataclass_at_t.bag_timestamps[timestamps_slice]
            mf_dataclass_at_t.__setattr__("bag_timestamps", bag_timestamps_subset)

        chunk_on_attribute: Union[RosStampedFeature, RosFeatureArray, RosFeature] = (
            self.get_dynamic_attribute(self.chunk_on)
        )
        chunk_on_attribute_window = chunk_on_attribute.get_timestamps_interval(
            start=start,
            stop=stop,
            startpoint=False,
            endpoint=True and endpoint,
            resolve_out_of_bounds=resolve_out_of_bounds,
        )
        mf_dataclass_at_t.__setattr__(self.chunk_on, chunk_on_attribute_window)

        chunk_stop = chunk_on_attribute_window.get_last_timestamp()

        for each_feature_name in self.topic_key_list:
            if each_feature_name == self.chunk_on:
                continue

            each_feature: Union[RosStampedFeature, RosFeatureArray, RosFeature] = (
                self.get_dynamic_attribute(each_feature_name)
            )

            each_feature = each_feature.get_timestamps_interval(
                start=start,
                stop=chunk_stop,
                startpoint=True and startpoint,
                endpoint=False,
                resolve_out_of_bounds=False or resolve_out_of_bounds,
            )

            # (NICE TO HAVE) Todo: improve ros_msgs/core_dataclass.py module 'Ros*Feature` classes
            #  'get_timestamps_interval(resolve_out_of_bounds=False)' method beaviour.
            # Note: Quick-hack to manage cases where feature trj intervall only have data before
            #   start point.
            if each_feature.get_first_timestamp() < start or each_feature.get_last_timestamp() > stop:
                each_feature = each_feature.empty()

            mf_dataclass_at_t.__setattr__(each_feature_name, each_feature)

        return mf_dataclass_at_t

    def get_trajectory_first_timestamp(self, include_bag_record: bool = True) -> int:
        """
        Retrieve the first timestamp across all features including bag record, feature record, and
        feature publish timestamps.

        :param include_bag_record: A boolean flag indicating whether to include
            the minimum timestamp from the bag file record in the computation.
        :return: The first timestamp among the evaluated trajectory sources.
        """
        all_min_timestamps = []
        if include_bag_record and self.bag_timestamps is not None:
            try:
                all_min_timestamps.append(self.bag_timestamps.min())
            except ValueError:
                pass

        for each_name in self.topic_key_list:
            if self.has_dynamic_attribute(f"{each_name}.header"):
                each_attribute = self.get_dynamic_attribute(each_name)
                try:
                    all_min_timestamps.append(each_attribute.header.timestamps.min())
                except ValueError:
                    pass

        if len(all_min_timestamps) == 0:
            raise ValueError(
                f"get_trajectory_first_timestamp({include_bag_record=}) found no trajectory timestamps."
            )

        return np.array(all_min_timestamps).min()

    def get_trajectory_last_timestamp(self, include_bag_record: bool = True) -> int:
        """
        Retrieve the latest timestamp from the trajectory data, optionally including bag records.

        :param include_bag_record: Flag indicating whether bag record timestamps
           should be included in the search.
        :return: The last timestamp among the evaluated trajectory sources.
        """
        all_max_timestamps = []
        if include_bag_record and self.bag_timestamps is not None:
            try:
                all_max_timestamps.append(self.bag_timestamps.max())
            except ValueError:
                pass

        for each_name in self.topic_key_list:
            if self.has_dynamic_attribute(f"{each_name}.header"):
                each_attribute = self.get_dynamic_attribute(each_name)
                try:
                    all_max_timestamps.append(each_attribute.header.timestamps.max())
                except ValueError:
                    pass

        if len(all_max_timestamps) == 0:
            raise ValueError(
                f"get_trajectory_last_timestamp({include_bag_record=}) found no trajectory timestamps."
            )

        return np.array(all_max_timestamps).max()

    @property
    def trajectory_published_timestamps(self) -> np.ndarray[int, np.dtype[int]]:
        """
        Returns all published timestamps for all features i.e., imply stamped feature.

        The returned numpy array is sorted and contains unique timestamps.
        Note: Those does not include the `bag_timestamps` ones.

        Usage:

        >>> print(container.trajectory_published_timestamps)
        [1711038330346603696, 1711038330351773872, 1711038330411627056, 1711038330436485488]

        :returns: A numpy array of unique timestamps.
        """
        all_features_stamps = []

        for each_topic in self.topic_key_list:
            each_attribute: Union[RosStampedFeature, RosFeatureArray] = (
                self.get_dynamic_attribute(each_topic)
            )

            if each_attribute.has_dynamic_attribute("header.timestamps"):
                all_features_stamps.append(each_attribute.header.timestamps.stamps)

            if isinstance(each_attribute, AbstractTrajectoryUnboundedArray):
                for each_trj_array_name in each_attribute.trajectory_array_field_names(
                    trajectory_containers_array_only=True
                ):
                    for each in each_attribute.get_dynamic_attribute(
                        each_trj_array_name
                    ):
                        if each.has_dynamic_attribute("header.timestamps"):
                            each: RosStampedFeature
                            all_features_stamps.append(each.header.timestamps.stamps)

        return np.unique(np.concatenate(all_features_stamps))

    @property
    def trajectory_timestamps_metadata(self) -> TrajectoryTimestampsMetadataBag:
        """
        Retrieve the first and last timestamps from all features timestamps.
        Note: Those does not include the `bag_timestamps` ones.

        Usage:

        >>> print(container.trajectory_timestamps_metadata.recorded.first)
        1711038330346603696
        >>> print(container.trajectory_timestamps_metadata.published.last)
        1711038330436485488

        :return: A tuple containing the first and the last timestamps from all features timestamps.
        """
        if self.bag_timestamps is not None:
            recorded_metadata = TrajectoryTimestampsMetadata(
                start_time=self.bag_timestamps.min(),
                end_time=self.bag_timestamps.max())
        else:
            recorded_metadata = None

        try:
            published_metadata = TrajectoryTimestampsMetadata(
                start_time=self.get_trajectory_first_timestamp(include_bag_record=False),
                end_time=self.get_trajectory_last_timestamp(include_bag_record=False), )
        except ValueError:
            published_metadata = None

        return TrajectoryTimestampsMetadataBag(
            recorded=recorded_metadata,
            published=published_metadata,
        )


def _get_attribute_at_timestamps(
    chunck_on_timestamps: Timestamps,
    chunk_idx: Union[int, slice],
    each_attribute: RosStampedFeature | Timestamps,
) -> RosStampedFeature | RosFeatureArray | Timestamps:

    startpoint = True
    endpoint = False
    if isinstance(chunk_idx, slice):
        chunck_start_stamp = chunck_on_timestamps[chunk_idx.start].stamps
        chunck_stop_stamp = chunck_on_timestamps[chunk_idx.stop].stamps
    else:
        chunck_start_stamp = chunck_on_timestamps[chunk_idx].stamps
        try:
            chunck_stop_stamp = chunck_on_timestamps[chunk_idx + 1].stamps
        except IndexError:
            chunck_stop_stamp = chunck_on_timestamps[chunk_idx].stamps
            endpoint = True

    if isinstance(each_attribute, Timestamps):
        timestamps_slice = get_timestamps_slice(
            each_attribute,
            start=chunck_start_stamp,
            stop=chunck_stop_stamp,
            startpoint=startpoint,
            endpoint=endpoint,
            resolve_out_of_bounds=True,
        )
        each_attribute = each_attribute[timestamps_slice]
    else:
        each_attribute = each_attribute.get_timestamps_interval(
            start=chunck_start_stamp,
            stop=chunck_stop_stamp,
            startpoint=startpoint,
            endpoint=endpoint,
            resolve_out_of_bounds=True,
        )
    return each_attribute
