# coding=utf-8
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Optional, Union

import numpy as np

from trajectory_container_tools.dataclasses.core.abstract_trajectory_feature_dataclass import (
    AbstractTrajectoryFeature,
)
from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass_common import (
    AbstractTrajectoryCommon,
)
from trajectory_container_tools.utils import extract_class_name_from_instance


@dataclass()
class AbstractTrajectoryArray(AbstractTrajectoryCommon):
    """
    Representation of an abstract data structure for entities containing heterogonous trajectory
    data e.g., a container that contains many trajectory feature dataclass of different trajectory lenghts.
    """
    feature_name: Optional[str] = field(default=None, kw_only=True)

    @classmethod
    def _dataclass_internal_field(cls) -> List[str]:
        return super()._dataclass_internal_field() + ["feature_name",]

    @property
    def registred_trajectory_object_list(self) -> Optional[str]:
        """
        Specify the attribute name corresponding of the list of trajectory objects.

        :return: The attribute name for the NoTrajectoryDataclass lists of trajectory objects.
        """
        return None

    @classmethod
    def non_trajectory_field(cls) -> List[str]:
        attribute_name = cls.registred_trajectory_object_list
        if attribute_name is None:
            attribute_name = ""
        return super().non_trajectory_field() + [attribute_name]

    def __post_init__(self):
        # .... Pre-condition ......................................................................
        if not self.get_dimension_names():
            raise TypeError(
                f"[TCT error] AbstractTrajectoryArray is an abstract baseclass, "
                f"it must be subclassed in order to be instanciated."
            )

        # .... Base class post init logic .........................................................
        registred_list = self.registred_trajectory_object_list
        if registred_list is not None:
            registred_list = self.get_dynamic_field(registred_list)
            if registred_list is not None:
                assert isinstance(registred_list, list)
                for each in registred_list:
                    assert isinstance(each, AbstractTrajectoryFeature)

        # .... Callback logic .....................................................................
        self.on_begin_post_init_callback()

        for each_name in self.get_dimension_names():
            self.post_init_feature_callback(feature_name=each_name)

        self.on_exit_post_init_callback()

        return None

    def __str__(self):
        """User representation. Dynamically handle property added at run time"""
        out_sp = " " * 0
        in_sp = " " * 3
        nested_sp = " " * 3
        dataclass_name = extract_class_name_from_instance(self)
        repr_str = f"\n{out_sp}{dataclass_name}(\n"
        v: Union[np.ndarray, AbstractTrajectoryFeature, str, int, float]

        v = self.__dict__.get("feature_name")
        if v is not None:
            repr_str += f"{in_sp}feature_name: {v}\n"

        for k, v in self.__dict__.items():
            if k in self._dataclass_internal_field():
                pass
            elif k == self.registred_trajectory_object_list:
                indent_v = []
                for each in v:
                    for each_line in str(each).splitlines():
                        indent_v.append(f"{out_sp}{in_sp}{nested_sp*2}{each_line}")
                    indent_v[-1] = f"{indent_v[-1]},"
                indent_v = "\n".join(indent_v)
                repr_str += f"{out_sp}{in_sp}{k}: ["
                repr_str += f"{indent_v}"
                repr_str += f"\n{out_sp}{in_sp}]\n"

            elif isinstance(v, AbstractTrajectoryFeature):
                indent_v = []
                for each_line in str(v).splitlines():
                    indent_v.append(f"{out_sp}{in_sp}{nested_sp}{each_line}\n")
                indent_v = "".join(indent_v)
                repr_str += f"{out_sp}{in_sp}{k}:{indent_v}"
            else:
                repr_str += (
                    f"{out_sp}{in_sp}{k}: ({extract_class_name_from_instance(v)}) {v}\n"
                )
        repr_str += f"{out_sp})"
        return repr_str

    @property
    def lists_len(self) -> int | None:
        """
        Provides the length of the registred lists containing AbstractTrajectoryFeature objects.

        :return: The total count of items in the registered list of trajectory objects or None if
            there is no registred trajectory object list.
        """
        trj_obj_list = self.registred_trajectory_object_list
        if trj_obj_list is not None:
            registred_list = self.__getattribute__(trj_obj_list)
            return len(registred_list)
        else:
            return None

    def __len__(self) -> int:
        """
        Provides the length of the registred lists containing AbstractTrajectoryFeature objects.

        :return: The total count of items in the registered list of trajectory objects or `0` if
            there is no registred trajectory object list.
        """
        return self.lists_len or 0

    def __getitem__(self, index) -> AbstractTrajectoryFeature | None:
        trj_obj_list = self.registred_trajectory_object_list
        if trj_obj_list is not None:
            registred_list = self.__getattribute__(trj_obj_list)
            trajectory_object = deepcopy(registred_list[index])
            return trajectory_object
        else:
            return None

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self) -> AbstractTrajectoryFeature:
        if self._iter_index < len(self):
            item = self[self._iter_index]
            self._iter_index += 1
            return item
        else:
            raise StopIteration
