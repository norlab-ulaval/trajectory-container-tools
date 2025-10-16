# coding=utf-8
import datetime

from deprecated import deprecated
from dataclasses import dataclass, field, fields
from typing import Any, List, Optional

import numpy as np

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


