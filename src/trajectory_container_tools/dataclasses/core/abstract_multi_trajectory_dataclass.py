# coding=utf-8
import datetime
from dataclasses import dataclass, field, fields
from typing import List, Optional

import numpy as np

from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass_common import (
    AbstractTrajectoryDataclassCommon,
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
    :ivar aggregated_date: The datetime when the data was aggregated. This is automatically
                          set during initialization.
    :type aggregated_date: datetime.datetime
    :ivar bag_timestamps: Optional timestamps related to bags. Defaults to None.
    :type bag_timestamps: Optional[Timestamps]
    """
    dataset_info: str
    aggregated_date: datetime.datetime = field(init=False)
    bag_timestamps: Optional[Timestamps] = field(default=None, kw_only=True)

    @classmethod
    def _dataclass_internal_field(cls) -> List[str]:
        return []

    def __post_init__(self):
        self.aggregated_date = datetime.datetime.now()

    def __str__(self):
        """User representation. Handle dynamical property added at run time"""
        t_sp = " " * 0
        m_sp = " " * 3
        repr_str = f"\n{t_sp}Multifeature(\n"
        m_sp += t_sp
        for k, v in self.__dict__.items():
            if k == "dataset_info":
                repr_str += f"{m_sp}dataset_info: {v}\n"
                repr_str += f"{m_sp}aggregated_date: {self.aggregated_date}\n"
            elif k in ["aggregated_date"]:
                pass
            elif k in ["bag_timestamps"] and self.bag_timestamps is None:
                pass
            elif isinstance(v, (np.ndarray, Timestamps)):
                if isinstance(v, Timestamps):
                    range_str = (
                        f"range(nanosec) {np.min(v.stamps)} ⟶ {np.max(v.stamps)}"
                    )
                else:
                    range_str = f"range {np.min(v)} ⟶ {np.max(v)}"
                repr_str += (
                    f"{m_sp}{k}: ({extract_class_name_from_instance(v)}) "
                    f"shape {v.shape} {range_str}\n"
                )
            else:
                repr_str += f"{m_sp}{k}: {str(v)}\n"
        repr_str += f"{m_sp})"
        return repr_str

    @property
    def summary(self) -> None:
        # (NICE TO HAVE) ToDo: TCT-68 feat: deprecate AbstractMultifeatureDataclass summary property
        print(self)
        return None

    @property
    def topic_key_list(self):
        return [
            topic.name for topic in fields(self) if str(topic.name).startswith("topic_")
        ]
