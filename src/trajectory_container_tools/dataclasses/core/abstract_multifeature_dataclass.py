# coding=utf-8
import datetime
import time
from copy import deepcopy

from deprecated import deprecated
from dataclasses import dataclass, field, fields
from typing import Any, List, Optional, Union

import numpy as np

from ..ros_msgs.core_dataclass import (
    NestedRosStampedDataclass,
    RosDataclass,
    RosStampedDataclass,
)
from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass_common import (
    AbstractTrajectoryDataclassCommon,
)
from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
)
from trajectory_container_tools.dataclasses.core.abstract_no_trajectory_dataclass import (
    AbstractNoTrajectoryDataclass,
)
from trajectory_container_tools.temporal import Timestamps
from trajectory_container_tools.utils import extract_class_name_from_instance


@dataclass
class AbstractMultifeatureDataclass(AbstractTrajectoryDataclassCommon):
    """
    Abstract base class representing a multifeature dataclass with dataset information,
    timestamp handling, and dynamic runtime properties.

    This class is designed to provide a structure for managing multifeature datasets,
    including a record of when the data was last aggregated and optional timestamps for
    bags. It also includes helper methods for user-friendly representations and topic
    key management.

    :ivar dataset_info: Information about the dataset.
    :type dataset_info: str
    :ivar bag_timestamps: Optional timestamps related to bags. Defaults to None.
    :type bag_timestamps: Optional[Timestamps]
    """

    dataset_info: str
    bag_timestamps: Optional[Timestamps] = field(default=None, kw_only=True)
    _aggregated_date: datetime.datetime = field(init=False)

    @classmethod
    def _dataclass_internal_field(cls) -> List[str]:
        return super()._dataclass_internal_field() + ["_aggregated_date"]

    def __post_init__(self):
        # .... Pre-condition ......................................................................
        if not self.get_dimension_names():
            raise TypeError(
                f"[TCT error] {self.__class__.__name__} is an abstract baseclass, "
                f"it must be subclassed in order to be instanciated."
            )

        # .... Base class post init logic .........................................................
        self._aggregated_date = datetime.datetime.now()

        # .... Callback logic .....................................................................
        self.on_begin_post_init_callback()

        for each_name in self.get_dimension_names():
            self.post_init_feature_callback(feature_name=each_name)

        self.on_exit_post_init_callback()

        return None

    @property
    def aggregated_date(self):
        return self._aggregated_date

    def _metadata_field_str(
        self, m_space: str, repr_str: str, key: str, value: Any
    ) -> str:
        repr_str += f"{m_space}dataset_info: {value}\n"
        repr_str += f"{m_space}aggregated_date: {self._aggregated_date}\n"
        return repr_str

    def __str__(self):
        """User representation. Handle dynamical property added at run time"""
        out_sp = " " * 0
        in_sp = " " * 3
        nested_sp = " " * 3
        repr_str = f"\n{out_sp}Multifeature(\n"
        for k, v in self.__dict__.items():
            if k in self._dataclass_internal_field():
                pass
            elif k == "dataset_info":
                repr_str = self._metadata_field_str(in_sp, repr_str, k, v)
            elif k in ["bag_timestamps"] and self.bag_timestamps is None:
                pass
            elif isinstance(v, (np.ndarray, Timestamps)):
                if k == "bag_timestamps" and isinstance(v, Timestamps):
                    indent_v = []
                    for each_line in str(v).splitlines():
                        indent_v.append(f"{out_sp}{in_sp}{nested_sp} {each_line}\n")
                    indent_v = "".join(indent_v)
                    repr_str += f"{out_sp}{in_sp}{k}:{indent_v}"
                else:
                    range_str = f"range {np.min(v)} ←→ {np.max(v)}"
                    repr_str += (
                        f"{out_sp}{in_sp}{k}: ({extract_class_name_from_instance(v)}) "
                        f"shape {v.shape} {range_str}\n"
                    )
            elif isinstance(
                v, (AbstractTrajectoryDataclass, AbstractNoTrajectoryDataclass)
            ):
                indent_v = []
                for each_line in str(v).splitlines():
                    indent_v.append(f"{out_sp}{in_sp}{nested_sp}{each_line}\n")
                indent_v = "".join(indent_v)
                repr_str += f"{out_sp}{in_sp}{k}:{indent_v}"
            else:
                repr_str += f"{out_sp}{in_sp}{k}: {str(v)}\n"
        repr_str += f"{out_sp})"
        return repr_str

    @property
    def topic_key_list(self):
        return [
            topic.name for topic in fields(self) if str(topic.name).startswith("topic_")
        ]

    @property
    @deprecated(
        reason="Directly print the MultifeatureTrajectoryDataclass object instead."
    )
    def summary(self) -> None:
        # inprogress: TCT-68 feat: deprecate AbstractMultifeatureDataclass summary property
        print(self)
        return None


@dataclass()
class AbstractMultifeatureStampedDataclass(AbstractMultifeatureDataclass):
    """
    AbstractMultifeatureStampedDataclass extends the functionality of AbstractMultifeatureDataclass
    to handle chunk-based operations and iteration for specific attributes.

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
    def _dataclass_internal_field(cls) -> List[str]:
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

    def __getitem__(self, chunk_idx: Union[int, slice]):
        mf_dataclass_at_t = deepcopy(self)

        chunk_on_attribute = self.get_dynamic_field(self.chunk_on)
        if isinstance(chunk_idx, slice):
            chunck_on_timestamp = chunk_on_attribute.header.timestamps[
                chunk_idx.stop - 1
            ].stamps
        else:
            chunck_on_timestamp = chunk_on_attribute.header.timestamps[chunk_idx].stamps

        each_attribute: Union[
            RosStampedDataclass, NestedRosStampedDataclass, RosDataclass
        ]
        for each_topic in self.topic_key_list:
            each_attribute = self.get_dynamic_field(each_topic)

            if each_topic is self.chunk_on:
                each_attribute = each_attribute[chunk_idx]
            elif isinstance(each_attribute, AbstractNoTrajectoryDataclass):
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

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
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
    ):
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
        # ToDo: update doc (ref task TCT-71)
        mf_dataclass_at_t = deepcopy(self)

        for each_topic in self.topic_key_list:
            each_attribute: Union[
                RosStampedDataclass, NestedRosStampedDataclass, RosDataclass
            ] = self.get_dynamic_field(each_topic)

            if isinstance(each_attribute, AbstractNoTrajectoryDataclass):
                registred_trj_object_list_name = (
                    each_attribute.registred_trajectory_object_list
                )
                if registred_trj_object_list_name is not None:
                    trj_container_list_object = []
                    for idx, each in enumerate(each_attribute):
                        each: Union[RosStampedDataclass, NestedRosStampedDataclass] = (
                            each.get_timestamps(
                                start=start,
                                stop=stop,
                                startpoint=startpoint,
                                endpoint=endpoint,
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
                )

            mf_dataclass_at_t.__setattr__(each_topic, each_attribute)

        return mf_dataclass_at_t


def _get_attribute_timestamps(
    chunck_on_timestamp: int,
    chunk_idx: Union[int, slice],
    chunk_on_topic: RosStampedDataclass,
    each_attribute: RosStampedDataclass | NestedRosStampedDataclass,
) -> RosStampedDataclass | NestedRosStampedDataclass | RosDataclass:
    if isinstance(chunk_idx, slice):
        chunk_idx = chunk_idx.start

    if chunk_idx == 0:
        each_start_timestamp = each_attribute.header.timestamps[0].stamps
        startpoint = True
    else:
        # Fetch the previous `chunck_on_timestamp` value
        each_start_timestamp = chunk_on_topic.header.timestamps[chunk_idx - 1].stamps
        startpoint = True

    endpoint = False
    each_attribute = each_attribute.get_timestamps(
        start=each_start_timestamp,
        stop=chunck_on_timestamp,
        startpoint=startpoint,
        endpoint=endpoint,
    )
    return each_attribute
