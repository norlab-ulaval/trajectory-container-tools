# coding=utf-8
from dataclasses import dataclass
from typing import List, Union

import numpy as np

from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass import AbstractTrajectoryDataclass
from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass_common import (
    AbstractTrajectoryDataclassCommon,
)
from trajectory_container_tools.utils import extract_class_name_from_instance


@dataclass()
class AbstractNoTrajectoryDataclass(AbstractTrajectoryDataclassCommon):
    """
    Representation of an abstract data structure for entities without trajectory data at top-level
    but might in nested ones e.g., a container that contains many trajectory dataclass of different
    trajectory lenghts.
    """

    feature_name: str

    @classmethod
    def _dataclass_internal_field(cls) -> List[str]:
        return [
            "feature_name",
        ]

    def __str__(self):
        """User representation. Dynamically handle property added at run time"""
        t_sp = " " * 10
        m_sp = " " * 3
        item_space = " " * 3
        dataclass_name = extract_class_name_from_instance(self)
        repr_str = f"\n{t_sp}{dataclass_name}(\n"
        v: Union[np.ndarray, AbstractTrajectoryDataclass, str, int, float]
        m_sp += t_sp

        v = self.__dict__.get("feature_name")
        if v is not None:
            repr_str += f"{m_sp}feature_name: {v}\n"

        for k, v in self.__dict__.items():
            if k in [
                "feature_name",
            ]:
                pass
            elif isinstance(v, list):
                indent_v = []
                for each in v:
                    for each_line in str(each).splitlines():
                        indent_v.append(f"{t_sp}{each_line}")
                    indent_v[-1] = f"{indent_v[-1]},"
                indent_v = "\n".join(indent_v)
                repr_str += f"{m_sp}{item_space}{k}: [" f"{indent_v}" f"\n{m_sp}]\n"

            elif isinstance(v, AbstractTrajectoryDataclass):
                indent_v = []
                for each_line in str(v).splitlines():
                    indent_v.append(f"{t_sp}{each_line}\n")
                indent_v = "".join(indent_v)
                repr_str += f"{m_sp}{item_space}{k}:{indent_v}"
            else:
                repr_str += f"{m_sp}{item_space}{k}: ({extract_class_name_from_instance(v)}) {v}\n"
        repr_str += f"{t_sp})"
        return repr_str

    def __post_init__(self):
        pass
