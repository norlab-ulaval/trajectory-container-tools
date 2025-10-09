# coding=utf-8
import datetime
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
from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass import AbstractTrajectoryDataclass
from trajectory_container_tools.dataclasses.core.abstract_no_trajectory_dataclass import AbstractNoTrajectoryDataclass
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
        self._aggregated_date = datetime.datetime.now()

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
                if isinstance(v, Timestamps):
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
            elif isinstance(v, (AbstractTrajectoryDataclass, AbstractNoTrajectoryDataclass)):
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

    @classmethod
    def _dataclass_internal_field(cls) -> List[str]:
        return super()._dataclass_internal_field() + ["_iter_index"]

    @property
    def chunks_total(self) -> int:
        return len(self.fetch_nested_attribute(self.chunk_on))

    def __len__(self) -> int:
        return self.chunks_total

    def _metadata_field_str(
        self, m_space: str, repr_str: str, key: str, value: Any
    ) -> str:
        repr_str = super()._metadata_field_str(m_space, repr_str, key, value)
        repr_str += f"{m_space}chunks_total: {self.chunks_total}\n"
        return repr_str

    def __getitem__(self, chunk_idx):
        mf_dataclass_at_t = deepcopy(self)

        chunk_on_topic = self.fetch_nested_attribute(self.chunk_on)
        if isinstance(chunk_idx, slice):
            chunck_on_timestamp = chunk_on_topic.header.timestamps[
                chunk_idx.stop - 1
            ].stamps
        else:
            chunck_on_timestamp = chunk_on_topic.header.timestamps[chunk_idx].stamps

        for each_topic in self.topic_key_list:
            each_attribute: Union[
                RosStampedDataclass, NestedRosStampedDataclass, RosDataclass
            ] = self.fetch_nested_attribute(each_topic)

            if each_topic is self.chunk_on:
                each_attribute = each_attribute[chunk_idx]
            elif isinstance(each_attribute, RosDataclass):
                raise NotImplementedError(
                    "ToDo: implement support for non-trajectry dataclass (Ref task TCT-64)"
                )
            else:
                if isinstance(chunk_idx, slice):
                    if chunk_idx.start == 0:
                        each_start = each_attribute.header.timestamps[0].stamps
                        startpoint = True
                    else:
                        each_start = chunk_on_topic.header.timestamps[
                            chunk_idx.start - 1
                        ].stamps
                        startpoint = True

                else:
                    if chunk_idx == 0:
                        each_start = each_attribute.header.timestamps[0].stamps
                        startpoint = True
                    else:
                        each_start = chunk_on_topic.header.timestamps[
                            chunk_idx - 1
                        ].stamps
                        startpoint = True

                endpoint = False
                each_attribute = each_attribute.get_timestamps(
                    start=each_start,
                    stop=chunck_on_timestamp,
                    startpoint=startpoint,
                    endpoint=endpoint,
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
