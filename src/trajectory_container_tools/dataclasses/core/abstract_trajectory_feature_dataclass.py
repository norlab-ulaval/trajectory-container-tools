# coding=utf-8
from copy import deepcopy
from dataclasses import dataclass, field
import numpy as np
from typing import List, Optional, Union

from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass_common import (
    AbstractTrajectoryCommon,
)
from trajectory_container_tools.temporal import Timestamps
from trajectory_container_tools.temporal import validate_timestep_indices
from trajectory_container_tools.utils.general import (
    extract_class_name_from_instance,
)


@dataclass()
class AbstractTrajectoryFeature(AbstractTrajectoryCommon):
    """
    AbstractTrajectoryFeature serves as a structured representation for trajectory data,
    providing methods for metadata management, data manipulation, and field extraction.

    This dataclass is designed to handle trajectory-related data encapsulated in structured
    fields. It includes methods for custom initialization, metadata management, and data
    manipulation. Each instance is equipped to process multi-dimensional data arrays,
    facilitate adjustments, and encapsulate metadata in an organized manner. Subclasses
    are expected to extend this class to define domain-specific behaviors and additional
    fields.

    :ivar feature_name: Name of the feature associated with the trajectory.
    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    """

    _timestep_indexes: np.ndarray = field(default=None, init=False)
    _iter_index: int = field(default=0, init=False)
    _transposed: bool = field(default=False, init=False)
    feature_name: Optional[str] = field(default=None, kw_only=True)
    batch: bool = field(default=False, compare=True, kw_only=True)

    # Note on timesteps_indices:
    #   - Can be explicitly set by user, TCT fct or automaticaly set post-init.
    #   - timesteps_indices make no assumption about the beginning indices e.g., trajectory could
    #     be a selected intervall from a larger trajectory
    timesteps_indices: np.ndarray = field(default=None, compare=True, kw_only=True)

    @classmethod
    def _dataclass_internal_field(cls) -> List[str]:
        return super()._dataclass_internal_field() + [
            "_timestep_indexes",
            "_iter_index",
            "_transposed",
            "feature_name",
            "timesteps_indices",
            "batch",
        ]

    @property
    def _time_axis(self) -> int:
        """
        The numpy array axe on which is the trajectory time index at dataclass initialization.

        :return: The trajectory array axe.
        """
        if self.batch:
            return 1
        else:
            return 0

    @property
    def trajectory_len(self) -> int:
        return self._timestep_indexes.size

    def __len__(self):
        return self.trajectory_len

    def ravel_dimensions_in_place(self) -> None:
        """
        Ravels all NumPy ndarray attributes associated with the object's dimensions in-place.

        This method processes all data properties associated with the object's dimensions
        and modifies them in-place by flattening their arrays using NumPy's `ravel` function.
        If a given data property is part of the trajectory metadata field, it is ignored.
        Otherwise, the method retrieves the corresponding attribute, checks if it is a NumPy
        ndarray, and flattens it in-place.

        :return: This method does not return a value and performs all operations in-place.
        """
        for each_data_property in self.get_dimension_names():
            if each_data_property in self.non_trajectory_field():
                pass
            else:
                attribute_ = self.__getattribute__(each_data_property)
                if isinstance(attribute_, np.ndarray):
                    ravel__copy = attribute_.ravel()
                    self.__setattr__(each_data_property, ravel__copy)
                elif isinstance(attribute_, AbstractTrajectoryFeature):
                    attribute_.ravel_dimensions_in_place()

        return None

    def __post_init__(self):
        if not self.get_dimension_names():
            raise TypeError(
                f"[TCT error] AbstractTrajectoryFeature is an abstract baseclass, "
                f"it must be subclassed in order to be instanciated."
            )

        self.on_begin_post_init_callback()

        self.set_parent_container_reference_tracking()

        for each_name in self.get_dimension_names():
            if each_name in self.non_trajectory_field():
                pass
            else:
                self.post_init_feature_callback(feature_name=each_name)

                data_property = self.__getattribute__(each_name)

                # .... Setup timestep indexing ....................................................
                if isinstance(data_property, (AbstractTrajectoryFeature, Timestamps)):
                    # Case nested container: Init timesteps using nested entity trajectory_len
                    if self._timestep_indexes is None:
                        self._timestep_indexes = np.arange(len(data_property))

                    if self.timesteps_indices is None:
                        self.timesteps_indices = self._timestep_indexes
                    elif self.timesteps_indices is not None:
                        assert isinstance(self.timesteps_indices, np.ndarray)
                        _timesteps_indices_vs_index_len_check(
                            self.timesteps_indices, self._timestep_indexes
                        )
                        validate_timestep_indices(self.timesteps_indices)

                elif isinstance(data_property, np.ndarray):
                    # Case leaf: initialize time-steps index
                    data_property: np.ndarray

                    # [Re-]Compute trajectory length from data arrays
                    data_property_trajectory_len = data_property.shape[self._time_axis]

                    if self._timestep_indexes is None:
                        self._timestep_indexes = np.arange(data_property_trajectory_len)

                    # Init timesteps with dataclass trajectory_len
                    if self.timesteps_indices is None:
                        self.timesteps_indices = self._timestep_indexes
                    elif self.timesteps_indices is not None:
                        assert isinstance(self.timesteps_indices, np.ndarray)
                        _timesteps_indices_vs_index_len_check(
                            self.timesteps_indices, self._timestep_indexes
                        )

                    if data_property_trajectory_len != self.trajectory_len:
                        raise ValueError(
                            f"{data_property_trajectory_len} != {self.trajectory_len}\n"
                            f"[TCT error] `{self.feature_name}` with container `"
                            f"{each_name}`"
                            " received numpy arrays which do not match "
                            "the trajectory length"
                        )

        self.on_exit_post_init_callback()

        return None

    def __del__(self):
        try:
            for each_name in self.get_dimension_names():
                data_property = self.__getattribute__(each_name)
                if isinstance(data_property, AbstractTrajectoryFeature):
                    del data_property
        except AttributeError as e:
            # Skip missing attribute.
            pass

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
            repr_str += f'{out_sp}{in_sp}feature_name: "{v}"\n'

        if not self.is_nested():
            repr_str += f"{out_sp}{in_sp}trajectory_len: {self.trajectory_len}\n"
            if self.batch:
                repr_str += f"{out_sp}{in_sp}batch: {self.batch}\n"
            repr_str += f"{out_sp}{in_sp}transposed: {self._transposed}\n"

        for k, v in self.__dict__.items():
            if k in self._dataclass_internal_field():
                pass
            elif k == "timesteps_indices" and self.is_nested():
                pass
            elif isinstance(v, (np.ndarray, Timestamps)):
                if isinstance(v, Timestamps):
                    indent_v = []
                    for each_line in str(v).splitlines():
                        indent_v.append(f"{out_sp}{in_sp}{nested_sp}{each_line}\n")
                    indent_v = "".join(indent_v)
                    repr_str += f"{out_sp}{in_sp}{k}:{indent_v}"
                else:
                    if v.size == 0:
                        range_str = f"empty"
                    else:
                        range_str = f"range {np.min(v)} ←→ {np.max(v)}"
                    repr_str += (
                        f"{out_sp}{in_sp}{k}: ({extract_class_name_from_instance(v)}) "
                        f"shape {v.shape} {range_str}\n"
                    )
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
    def current_trj_axe(self):
        if self._transposed:
            return -1
        else:
            return self._time_axis

    def __getitem__(self, index):
        feature_dataclass_at_t = deepcopy(self)

        feature_dataclass_at_t.__setattr__(
            "_timestep_indexes", self._timestep_indexes[index]
        )
        feature_dataclass_at_t.__setattr__(
            "timesteps_indices", self.timesteps_indices[index]
        )
        for each_name in self.get_dimension_names():
            if each_name in self.non_trajectory_field():
                pass
            else:
                each_attribute = self.__getattribute__(each_name)

                if isinstance(
                    each_attribute,
                    (np.ndarray, AbstractTrajectoryFeature, Timestamps),
                ):
                    if self.current_trj_axe == 0:
                        # Case: time-serie
                        data_value = each_attribute[index]
                    elif self.current_trj_axe == 1:
                        # Case: batch
                        data_value = each_attribute[:, index, ...]
                    elif self.current_trj_axe == -1:
                        # Case: transposed
                        data_value = each_attribute[..., index]
                    else:
                        raise ValueError(
                            f"Unexpected trajectory time axe {self.current_trj_axe=}"
                        )

                    feature_dataclass_at_t.__setattr__(each_name, data_value)
                else:
                    feature_dataclass_at_t.__setattr__(each_name, each_attribute)

        return feature_dataclass_at_t

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index < self.trajectory_len:
            item = self[self._iter_index]
            self._iter_index += 1
            return item
        else:
            raise StopIteration

    @property
    def T(self):
        """Flips the axes of the ndarray properties."""
        for each_name in self.get_dimension_names():
            if each_name in self.non_trajectory_field():
                pass
            else:
                data_property = self.__getattribute__(each_name)

                if isinstance(data_property, (np.ndarray, AbstractTrajectoryFeature)):
                    self.__setattr__(each_name, data_property.T)

        self._transposed = not self._transposed
        return self


def _timesteps_indices_vs_index_len_check(
    timesteps_indices: np.ndarray, _timestep_indexes: np.ndarray
) -> None:
    ts_id_len = timesteps_indices.shape[-1]
    ts_idx_len = _timestep_indexes.shape[-1]
    assert ts_idx_len == ts_id_len, (
        f"[TCT error] timesteps_indices expecte " f"lemgth {ts_idx_len} != {ts_id_len}"
    )
    return None
