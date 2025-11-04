# coding=utf-8
from dataclasses import dataclass
import numpy as np

from trajectory_container_tools.dataclasses.core.abstract_trajectory_feature_dataclass import (
    AbstractTrajectoryFeature,
    _repr_ndarray_and_timestamps_obj,
    _repr_nested_AbstractTrajectoryFeature_obj,
)

from trajectory_container_tools.temporal import Timestamps
from trajectory_container_tools.utils import extract_class_name_from_instance


@dataclass()
class AbstractTrajectoryUnboundedArray(AbstractTrajectoryFeature):
    """
    Representation of an abstract data structure for entities containing heterogonous trajectory
    data e.g., a container that contains an array of many trajectory feature dataclass of different
    trajectory lenghts.
    """

    def trajectory_array_field_names(
        self,
        trajectory_containers_array_only: bool = False,
        non_trajectory_containers_array_only: bool = False,
    ) -> list[str]:
        """
        Get attribute name corresponding of the list of trajectory objects.

        :param trajectory_containers_array_only: (Optional) Return only arrays containing TrajectoryContainer dataclasses.
        :param non_trajectory_containers_array_only: (Optional) Return only arrays not containing TrajectoryContainer dataclasses.
        :return: The attribute names for the AbstractTrajectoryUnboundedArray lists of nested trajectory objects.
        :raises ValueError: If both paramters are set to True
        """

        trj_array_w_arbitrary_type_field_names = []
        trj_array_w_trj_containers_type_field_names = []

        for each in self.get_public_attribute_names():
            if each in self.non_trajectory_field():
                continue

            dimension_type, is_list_of_type = self.get_cls_public_field_type(each)
            if is_list_of_type and issubclass(
                dimension_type, AbstractTrajectoryFeature
            ):
                trj_array_w_trj_containers_type_field_names.append(each)
            elif is_list_of_type:
                trj_array_w_arbitrary_type_field_names.append(each)

        if (
            trajectory_containers_array_only is True
            and non_trajectory_containers_array_only is True
        ):
            raise ValueError(
                "Parameters 'trajectory_containers_array_only' and 'non_trajectory_containers_array_only' are both set to True. This would return an empty list!"
            )
        elif trajectory_containers_array_only:
            return trj_array_w_trj_containers_type_field_names
        elif non_trajectory_containers_array_only:
            return trj_array_w_arbitrary_type_field_names
        else:
            return (
                trj_array_w_arbitrary_type_field_names
                + trj_array_w_trj_containers_type_field_names
            )

    def __getitem__(self, index) -> "AbstractTrajectoryUnboundedArray":
        trj_feature_array_at_t = super().__getitem__(index)

        for each_array_name in self.trajectory_array_field_names(
            trajectory_containers_array_only=True
        ):
            updated_list = []

            each_trj_array = trj_feature_array_at_t.__getattribute__(each_array_name)
            for each_member in each_trj_array:
                try:
                    each_member = each_member[index]
                except IndexError:
                    each_member = each_member.empty()

                updated_list.append(each_member)

            trj_feature_array_at_t.__setattr__(each_array_name, updated_list)

        for each_array_name in self.trajectory_array_field_names(
            non_trajectory_containers_array_only=True
        ):
            if self.is_trajectory_sequence(each_array_name):
                each_trj_array = trj_feature_array_at_t.__getattribute__(each_array_name)
                trj_feature_array_at_t.__setattr__(each_array_name, each_trj_array[index])

        return trj_feature_array_at_t

    def empty(self) -> "AbstractTrajectoryUnboundedArray":
        empty_trj_feature = super().empty()

        updated_list = []
        for each_array_name in self.trajectory_array_field_names(
            trajectory_containers_array_only=True
        ):
            for each_member in empty_trj_feature.get_dynamic_attribute(each_array_name):
                each_member: AbstractTrajectoryFeature
                updated_list.append(each_member.empty())

            empty_trj_feature.__setattr__(each_array_name, updated_list)

        for each_array_name in self.trajectory_array_field_names(
            non_trajectory_containers_array_only=True
        ):
            each_trj_array = empty_trj_feature.__getattribute__(each_array_name)
            if isinstance(each_trj_array, list):
                empty_trj_feature.__setattr__(each_array_name, [])
            elif isinstance(each_trj_array, tuple):
                empty_trj_feature.__setattr__(each_array_name, tuple)

        return empty_trj_feature

    def __str__(self):
        """User representation. Dynamically handle property added at run time"""
        in_sp, nested_sp, out_sp, repr_str = self._repr_pre()

        for k, v in self.__dict__.items():
            if k in self.container_internal_field():
                pass
            elif k == "timesteps_indices" and self.is_nested():
                pass
            elif k == "bag_recorded_timestamps" and self.is_nested() and v is None:
                pass
            elif k in self.trajectory_array_field_names(
                trajectory_containers_array_only=True
            ):
                indent_v = []
                for each in v:
                    for each_line in str(each).splitlines():
                        indent_v.append(f"{out_sp}{in_sp}{nested_sp*2}{each_line}")
                    indent_v[-1] = f"{indent_v[-1]},"
                indent_v = "\n".join(indent_v)
                repr_str += f"{out_sp}{in_sp}{k}: ["
                repr_str += f"{indent_v}"
                repr_str += f"\n{out_sp}{in_sp}]\n"
            elif k in self.trajectory_array_field_names(
                non_trajectory_containers_array_only=True
            ):

                nested_type = ""
                if len(v) > 0:
                    nested_type = f"[{extract_class_name_from_instance(v[0])}]"
                class_type = f"{extract_class_name_from_instance(v)}{nested_type}"

                dimension_type, _ = self.get_cls_public_field_type(k)
                if isinstance(dimension_type, (int, float)):
                    if len(v) == 0:
                        range_str = f"empty"
                    else:
                        range_str = f"range {min(v)} ←→ {max(v)}"
                    repr_str += (
                        f"{out_sp}{in_sp}{k}: ({class_type}) "
                        f"len {len(v)} {range_str}\n"
                    )
                else:
                    if len(v) == 0:
                        range_str = f"empty"
                    elif len(v) == 1:
                        range_str = f"[{v[0]}]"
                    elif len(v) == 2:
                        range_str = f"[{v[0]}, {v[1]}]"
                    else:
                        range_str = f"[{v[0]}, ..., {v[-1]}]"
                    repr_str += (
                        f"{out_sp}{in_sp}{k}: ({class_type}) "
                        f"len {len(v)} {range_str}\n"
                    )

            elif isinstance(v, (np.ndarray, Timestamps)):
                repr_str = _repr_ndarray_and_timestamps_obj(
                    repr_str, k, v, nested_sp, in_sp, out_sp
                )
            elif isinstance(v, AbstractTrajectoryFeature):
                repr_str = _repr_nested_AbstractTrajectoryFeature_obj(
                    repr_str, k, v, in_sp, out_sp, nested_sp
                )
            else:
                repr_str += (
                    f"{out_sp}{in_sp}{k}: ({extract_class_name_from_instance(v)}) {v}\n"
                )
        repr_str += f"{out_sp})"
        return repr_str
