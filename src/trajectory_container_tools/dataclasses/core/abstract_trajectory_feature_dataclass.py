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
    size_zero_array_like,
)
from trajectory_container_tools.utils.typing.tct_custom_field import (
    NonTrajectoryField,
    ContainerInternalField,
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

    Note on the 'timesteps_indices' field:
      - Can be explicitly set by the user, by an arbitrary TCT fct or automaticaly set post-init.
      - 'timesteps_indices' make no assumption about the beginning indices e.g., trajectory could
        be a intervall window from a larger trajectory.

    :ivar feature_name: Name of the feature associated with the trajectory.
    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    """

    _timestep_indexes: ContainerInternalField[np.ndarray] = field(default=None, init=False)
    _iter_index: ContainerInternalField[int] = field(default=0, init=False)
    _transposed: ContainerInternalField[bool] = field(default=False, init=False)
    feature_name: ContainerInternalField[Optional[str]] = field(default=None, kw_only=True)
    batch: ContainerInternalField[bool] = field(default=False, compare=True, kw_only=True)
    timesteps_indices: ContainerInternalField[np.ndarray] = field(
        default=None, compare=True, kw_only=True
    )

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
        for each_attribute in self.get_public_attribute_names():
            if each_attribute in self.non_trajectory_field():
                continue

            attribute_ = self.__getattribute__(each_attribute)
            if isinstance(attribute_, np.ndarray):
                ravel__copy = attribute_.ravel()
                self.__setattr__(each_attribute, ravel__copy)
            elif isinstance(attribute_, AbstractTrajectoryFeature):
                attribute_.ravel_dimensions_in_place()

        return None

    def __post_init__(self):
        # .... Pre-condition ......................................................................
        if not self.get_cls_public_field_names(include_non_init_dim=False):
            raise TypeError(
                f"[TCT error] AbstractTrajectoryFeature is an abstract baseclass, "
                f"it must be subclassed in order to be instanciated."
            )

        # .... Base class initialization logic ....................................................
        self.set_parent_container_reference_tracking()

        for each_name in self.get_cls_public_field_names(include_non_init_dim=True):
            if each_name not in self.non_trajectory_field():
                self._setup_timestep_indexing(each_name)

        # .... Callback and attribute customization logic .........................................
        self.on_begin_post_init_callback()
        for each_name in self.get_cls_public_field_names(include_non_init_dim=True):
            self.post_init_feature_callback(feature_name=each_name)

        self.on_exit_post_init_callback()

        return None

    def _setup_timestep_indexing(self, each_name: str):
        data_property = self.__getattribute__(each_name)
        if isinstance(data_property, (AbstractTrajectoryFeature, Timestamps)):
            # Case nested container: Init timesteps using nested entity trajectory_len
            if self._timestep_indexes is None:
                self._timestep_indexes = np.arange(len(data_property))

            if self.timesteps_indices is None:
                self.timesteps_indices = self._timestep_indexes
            elif self.timesteps_indices is not None and len(self._timestep_indexes) > 0:
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
        return None

    def __del__(self):
        try:
            for each_name in self.get_public_attribute_names():
                data_property = self.__getattribute__(each_name)
                if isinstance(data_property, AbstractTrajectoryFeature):
                    del data_property
        except AttributeError as e:
            # Skip missing attribute.
            pass

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

    def _repr_pre(self) -> tuple[
        str,
        str,
        str,
        str,
    ]:
        out_sp = " " * 0
        in_sp = " " * 3
        nested_sp = " " * 3
        dataclass_name = extract_class_name_from_instance(self)
        repr_str = f"\n{out_sp}{dataclass_name}(\n"
        v: Union[np.ndarray, AbstractTrajectoryFeature, str, int, float]

        v = self.__dict__.get("feature_name")
        if v is not None:
            repr_str += f"{out_sp}{in_sp}feature_name: '{v}'\n"

        if not self.is_nested():
            repr_str += f"{out_sp}{in_sp}trajectory_len: {self.trajectory_len}\n"
            if self.batch:
                repr_str += f"{out_sp}{in_sp}batch: {self.batch}\n"
            repr_str += f"{out_sp}{in_sp}transposed: {self._transposed}\n"
        return in_sp, nested_sp, out_sp, repr_str

    @property
    def current_trj_axe(self):
        if self._transposed:
            return -1
        else:
            return self._time_axis

    def __getitem__(self, index) -> "AbstractTrajectoryFeature":
        trj_feature_at_t = deepcopy(self)
        trj_feature_at_t.__setattr__("_timestep_indexes", self._timestep_indexes[index])
        trj_feature_at_t.__setattr__("timesteps_indices", self.timesteps_indices[index])

        for each_name in self.get_public_attribute_names():
            each_attribute = self.__getattribute__(each_name)

            if each_name in self.non_trajectory_field():
                continue

            if isinstance(each_attribute, Timestamps):
                trj_feature_at_t.__setattr__(each_name, each_attribute[index])
            elif isinstance(
                each_attribute, AbstractTrajectoryFeature
            ) or self.is_trajectory_sequence(each_attribute):

                try:
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
                    trj_feature_at_t.__setattr__(each_name, data_value)
                except IndexError:
                    # Not a trajectory array
                    pass
                except ValueError:
                    raise

        return trj_feature_at_t

    def is_trajectory_sequence(
        self,
        sequence: Union[ContainerInternalField, NonTrajectoryField, np.ndarray, list, tuple],
    ) -> bool:
        """
        Determines whether a given sequence is a trajectory.

        This function checks whether the input sequence matches the predefined trajectory
        length based on its type and shape. The sequence can be represented as a NumPy
        array, list, or tuple, with specific cases being handled for time-series, batch,
        and transposed formats. If the provided sequence does not match the expected
        dimensions or type, it is treated using a fallback comparison.

        :param sequence: The input sequence to check, which can be of types
            `ContainerInternalField`, `NonTrajectoryField`, `np.ndarray`, `list`, or `tuple`.
        :return: A boolean indicating if the input sequence qualifies as a trajectory.
        """
        is_trajectory = False

        if isinstance(sequence, np.ndarray):
            try:
                is_trajectory = (
                    sequence.shape[self.current_trj_axe] == self.trajectory_len
                )
            except IndexError:
                is_trajectory = sequence.size == self.trajectory_len
        elif isinstance(sequence, (list, tuple)):
            try:
                if self.current_trj_axe == 0:
                    # Case: time-serie
                    is_trajectory = len(sequence) == self.trajectory_len
                elif self.current_trj_axe == 1:
                    # Case: batch
                    is_trajectory = len(sequence[0]) == self.trajectory_len
                elif self.current_trj_axe == -1:
                    # Case: transposed
                    is_trajectory = len(sequence[0][0]) == self.trajectory_len
            except (IndexError, TypeError):
                is_trajectory = len(sequence) == self.trajectory_len

        return is_trajectory

    def empty(self) -> "AbstractTrajectoryFeature":
        """
        Creates an empty copy of the current trajectory feature with the same structure.

        This method generates a deep copy of the instance with all trajectory-related
        attributes emptied, while maintaining the original structure and types.
        Non-trajectory-related fields remain unchanged. It is useful for initializing
        or resetting trajectory-related data while retaining the overall object schema.

        :return: A new instance of the same class where all trajectory-related fields
            have been reset to empty, and non-trajectory-related fields stay unchanged.
        """
        empty_trj_feature = deepcopy(self)

        empty_trj_feature.__setattr__(
            "_timestep_indexes", size_zero_array_like(self._timestep_indexes)
        )
        empty_trj_feature.__setattr__(
            "timesteps_indices", size_zero_array_like(self.timesteps_indices)
        )
        for each_name in self.get_public_attribute_names():
            each_attribute = self.__getattribute__(each_name)

            if each_name in self.non_trajectory_field():
                continue

            if isinstance(each_attribute, np.ndarray):
                empty_trj_feature.__setattr__(
                    each_name, size_zero_array_like(each_attribute)
                )
            elif isinstance(each_attribute, (AbstractTrajectoryFeature, Timestamps)):
                empty_trj_feature.__setattr__(each_name, each_attribute.empty())

        return empty_trj_feature

    def __iter__(self) -> "AbstractTrajectoryFeature":
        self._iter_index = 0
        return self

    def __next__(self) -> "AbstractTrajectoryFeature":
        if self._iter_index < self.trajectory_len:
            item = self[self._iter_index]
            self._iter_index += 1
            return item
        else:
            raise StopIteration

    @property
    def T(self) -> "AbstractTrajectoryFeature":
        """Flips the axes of the ndarray properties."""
        for each_name in self.get_public_attribute_names():
            if each_name in self.non_trajectory_field():
                continue

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


def _repr_ndarray_and_timestamps_obj(
    repr_str: str,
    k: str,
    v: np.ndarray,
    nested_sp: str,
    in_sp: str,
    out_sp: str,
) -> str:
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
    return repr_str


def _repr_nested_AbstractTrajectoryFeature_obj(
    repr_str: str,
    k: str,
    v: "AbstractTrajectoryFeature",
    in_sp: str,
    out_sp: str,
    nested_sp: str,
) -> str:
    indent_v = []
    for each_line in str(v).splitlines():
        indent_v.append(f"{out_sp}{in_sp}{nested_sp}{each_line}\n")
    indent_v = "".join(indent_v)
    repr_str += f"{out_sp}{in_sp}{k}:{indent_v}"
    return repr_str
