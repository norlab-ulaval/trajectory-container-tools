# coding=utf-8
import abc
import datetime
from copy import deepcopy
from dataclasses import dataclass, field, fields
import numpy as np
from typing import Any, List, Optional, Tuple, Union

import trajectory_container_tools as tct
from trajectory_container_tools.temporal import Timestamps
from trajectory_container_tools.temporal import validate_timestep_indices
from ..utils.general import (
    check_typing_list_and_extract_list_type,
    extract_class_name_from_instance,
    check_typing_union_and_extract_first_union_type,
)


@dataclass()
class AbstractTrajectoryDataclassCommon(abc.ABC):
    """
    Provides an abstract base dataclass for dynamically interacting with and managing object
    attributes, including dynamic fields creation and nested attribute retrieval.

    This class serves as a foundation for implementing objects that must support
    dynamically added fields, as well as hierarchical retrieval of nested attributes. It is
    an abstract base class (ABC) and requires implementation of the `__post_init__` method
    in subclasses.

    """

    @classmethod
    def _dataclass_internal_field(cls) -> List[str]:
        """
        List of field marked as internal. Those are field name that will be omited by
        `get_dimension_names` class method.

        This method is intended to return a predefined list of attribute names that are
        specific to the internal logic of a data class. These fields often represent
        key information required for specialized operations or manipulations within
        the class. The method should be used internally and not be exposed for
        general use.

        :return: A list containing the names of internal fields used in the data class.
        """
        return []

    def get_dynamic_field(self, feature_name: str) -> Any:
        """Retrieves the value of a dynamicaly declared attribute from the object.

        :param feature_name: The name of the attribute to retrieve.
        :return: The value of the requested attribute.
        """
        return self.__getattribute__(feature_name)

    def set_dynamic_field(self, feature_name: str, value: Any) -> None:
        """Updates or creates a dynamic attribute on an object.

        :param feature_name: The name of the attribute to update or create.
        :param value: The value to assign to the attribute.
        :return: None
        """
        self.__setattr__(feature_name, value)
        return None

    def fetch_nested_attribute(self, nested_attribute_path: str) -> Any:
        """Retrieves a nested attribute from an object based on a dot-separated string.

        This function allows accessing nested attributes of an object dynamically, based on a
        string representation of the attribute's hierarchical structure.
        It takes a dot-separated attribute name, traverses the object's nested levels
        sequentially, and retrieves the final attribute
        e.g., "topic_odom.pose.pose.position.x" would sequentialy crawl into nested container
        "topic_odom" -> "pose" -> "pose" -> "position" -> "x".

        Example:

            >>> position_x_value = self.fetch_nested_attribute("topic_odom.pose.pose.position.x")

        :param nested_attribute_path: A dot-separated string representing the hierarchical
          structure of the attribute to retrieve.
        :return: The value of the resolved nested attribute.
        """
        return _fetch_nested_attribute(self, nested_attribute_path)

    @abc.abstractmethod
    def __post_init__(self):
        pass

    @classmethod
    def get_dimension_type(cls, dimension_name: str) -> Tuple[type[Any], bool]:
        """
        Get the type and whether it is a list for a given dimension name.

        The method inspects the class fields, determining the type of the field associated with the provided dimension name. It identifies whether the type is a list or a union, returning the underlying type if applicable.

        :param dimension_name: The name of the dimension to query.
        :return: A tuple containing the type of the dimension and a boolean indicating if the dimension is a list.
        """
        container_properties = fields(cls)
        dimension_type = None
        is_list_of_type = False
        for each_field in container_properties:
            if each_field.name is dimension_name:
                is_list_of_type, dimension_type = (
                    check_typing_list_and_extract_list_type(each_field.type)
                )
                if not is_list_of_type:
                    is_union, dimension_type = (
                        check_typing_union_and_extract_first_union_type(each_field.type)
                    )
        return dimension_type, is_list_of_type

    @classmethod
    def get_dimension_names(cls) -> Tuple[str, ...]:
        """
        Provides the dimension names of the data class fields that are exposed to user.

        This method retrieves the field names from the data class that are not marked
        as internal fields. It returns these names as a tuple of strings, making it
        useful for querying the explicitly defined data attributes of the class.

        :return: A tuple containing the names of non-internal fields defined in the class.
        """
        container_properties = fields(cls)
        field_name = []
        for each_field in container_properties:
            if each_field.name not in cls._dataclass_internal_field():
                field_name.append(each_field.name)
        return tuple(field_name)


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


@dataclass()
class AbstractTrajectoryDataclass(AbstractTrajectoryDataclassCommon):
    """
    AbstractTrajectoryDataclass serves as a structured representation for trajectory data,
    providing methods for metadata management, data manipulation, and field extraction.

    This dataclass is designed to handle trajectory-related data encapsulated in structured
    fields. It includes methods for custom initialization, metadata management, and data
    manipulation. Each instance is equipped to process multi-dimensional data arrays,
    facilitate adjustments, and encapsulate metadata in an organized manner. Subclasses
    are expected to extend this class to define domain-specific behaviors and additional
    fields.

    :ivar feature_name: Name of the feature associated with the trajectory.
    :ivar timesteps_indices: NumPy array representing the indices of timesteps in
        the trajectory. These may pertain to a subset of a larger trajectory, ignoring
        prior indices.
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    """

    _timestep_indexes: np.ndarray = field(default=None, init=False)
    _iter_index: int = field(default=0, init=False)
    _transposed: bool = field(default=False, init=False)
    _nested: bool = field(default=False, init=False)
    feature_name: str
    batch: bool = field(default=False, compare=True, kw_only=True)

    # Note on timesteps_indices:
    #   - Can be explicitly set by user, TCT fct or automaticaly set post-init.
    #   - timesteps_indices make no assumption about the beginning indices e.g., trajectory could
    #     be a selected intervall from a larger trajectory
    timesteps_indices: np.ndarray = field(default=None, compare=True, kw_only=True)

    @classmethod
    def _dataclass_internal_field(cls) -> List[str]:
        return [
            "feature_name",
            "timesteps_indices",
            "_timestep_indexes",
            "_iter_index",
            "_transposed",
            "_nested",
            "batch",
        ]

    @classmethod
    def trajectory_metadata_field(cls) -> List[str]:
        """
        List fields that are declared as trajectory wide metadata i.e. not per timestep.
        Usefulll for skipping field of type ndarray that are not trajectory timestep information.

        This method provides a default implementation for specifying the fields
        that should be excluded from certain processes such as `__post_init__`, transpose `T` and
        `ravel_dimensions_in_place`.

        Usage:

        >>> @dataclass()
        >>> class TestMotionTrajectoryDataclass(TestTrajectoryDataclass):
        >>>     initiale_pose: np.ndarray
        >>>
        >>>     @classmethod
        >>>     def trajectory_metadata_field(cls) -> List[str]:
        >>>         return super().trajectory_metadata_field() + ["initiale_pose"]

        :return: A list of string names corresponding to the fields skipped.
        """
        return []

    def on_begin_post_init_callback(self) -> None:
        """Overide this methode to execute custom computation on feature dataclass at the begining
         of `__post_init__` method execution.
        Note: The method scope include all field.

        Example:
            >>> @dataclass
            >>> class StatePose2DSteadyState(StatePose2D):
            >>>
            >>>     def on_begin_post_init_callback(self):
            >>>         feature = self.get_dynamic_field("<feature-name>")
            >>>         self.set_dynamic_field(f"<other-feature>", np.cumsum(feature))
            >>>         return None

        """
        pass

    def post_init_feature_callback(self, feature_name: str) -> None:
        """Overide this methode to execute feature aware custom computation.
        Usefull for post-processing dynamicaly declare field.

        Note:
            - Will be executed once for each feature.
            - The method scope does not include field marked by `_dataclass_internal_field`
              and `trajectory_metadata_field`.

        Example:
            >>> steady_state_mask = dataset_snow['steady_state_mask'].to_numpy() == True
            >>>
            >>> @dataclass
            >>> class StatePose2DSteadyState(StatePose2D):
            >>>
            >>>     def post_init_feature_callback(self, feature_name):
            >>>         # Example for creating an explicit timestep t=0 property named "<feature_name>_init"
            >>>         feature = self.get_dynamic_field(feature_name)
            >>>         if isinstance(feature, np.ndarray):
            >>>             if self.batch:
            >>>                 # Case batch data
            >>>                 feature_ini = feature[:, 0, ...]
            >>>             else:
            >>>                 # Case time-serie data
            >>>                 feature_ini = feature[0, ...]
            >>>             self.set_dynamic_field(f"{feature_name}_init", feature_ini)
            >>>         return None

        """
        pass

    def on_exit_post_init_callback(self) -> None:
        """Overide this methode to execute custom computation on feature dataclass at the end
         of `__post_init__` method execution.
        Note: The method scope include all field.

        Example:
            >>> @dataclass
            >>> class StatePose2DSteadyState(StatePose2D):
            >>>
            >>>     def on_exit_post_init_callback(self):
            >>>         feature = self.get_dynamic_field("<feature-name>")
            >>>         assert len(feature) > 0
            >>>         return None

        """
        pass

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
            if each_data_property in self.trajectory_metadata_field():
                pass
            else:
                attribute_ = self.__getattribute__(each_data_property)
                if isinstance(attribute_, np.ndarray):
                    ravel__copy = attribute_.ravel()
                    self.__setattr__(each_data_property, ravel__copy)
                elif isinstance(attribute_, AbstractTrajectoryDataclass):
                    attribute_.ravel_dimensions_in_place()

        return None

    def __post_init__(self):
        self.on_begin_post_init_callback()

        if not self.get_dimension_names():
            raise TypeError(
                f"[TCT error] AbstractTrajectoryDataclass is an abstract baseclass, "
                f"it must be subclassed in order to be instanciated."
            )

        for each_name in self.get_dimension_names():
            if each_name in self.trajectory_metadata_field():
                pass
            else:
                self.post_init_feature_callback(feature_name=each_name)

                # .... Setup timestep indexing ....................................................
                data_property = self.__getattribute__(each_name)

                if isinstance(data_property, (AbstractTrajectoryDataclass, Timestamps)):
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
                if isinstance(data_property, AbstractTrajectoryDataclass):
                    del data_property
        except AttributeError as e:
            # Skip missing attribute.
            pass

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

        if not self._nested:
            repr_str += f"{m_sp}trajectory_len: {self.trajectory_len}\n"
            if self.batch:
                repr_str += f"{m_sp}batch: {self.batch}\n"
            repr_str += f"{m_sp}transposed: {self._transposed}\n"
            repr_str += f"{m_sp}dimensions:\n"

        for k, v in self.__dict__.items():
            if k in [
                "_iter_index",
                "_transposed",
                "feature_name",
                "_timestep_indexes",
                "batch",
            ]:
                pass
            elif k == "timesteps_indices" and self._nested:
                pass
            elif isinstance(v, (np.ndarray, Timestamps)):
                if isinstance(v, Timestamps):
                    range_str = (
                        f"range(nanosec) {np.min(v.stamps)} ⟶ {np.max(v.stamps)}"
                    )
                else:
                    if v.size == 0:
                        range_str = f"empty"
                    else:
                        range_str = f"range {np.min(v)} ⟶ {np.max(v)}"
                repr_str += (
                    f"{m_sp}{item_space}{k}: ({extract_class_name_from_instance(v)}) "
                    f"shape {v.shape} {range_str}\n"
                )
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

    @property
    def current_trj_axe(self):
        if self._transposed:
            return -1
        else:
            return self._time_axis

    def __getitem__(self, key):
        feature_dataclass_at_t = deepcopy(self)

        feature_dataclass_at_t.__setattr__(
            "_timestep_indexes", self._timestep_indexes[key]
        )
        feature_dataclass_at_t.__setattr__(
            "timesteps_indices", self.timesteps_indices[key]
        )
        for each_name in self.get_dimension_names():
            if each_name in self.trajectory_metadata_field():
                pass
            else:
                data_property = self.__getattribute__(each_name)

                if isinstance(
                    data_property, (np.ndarray, AbstractTrajectoryDataclass, Timestamps)
                ):
                    # if isinstance(data_property, Timestamps):
                    #     # raise NotImplementedError("(CRITICAL) ToDo: implement fix")

                    if self.current_trj_axe == 0:
                        # Case: time-serie
                        data_value = data_property[key]
                    elif self.current_trj_axe == 1:
                        # Case: batch
                        data_value = data_property[:, key, ...]
                    elif self.current_trj_axe == -1:
                        # Case: transposed
                        data_value = data_property[..., key]
                    else:
                        raise ValueError(
                            f"Unexpected trajectory time axe {self.current_trj_axe=}"
                        )

                    feature_dataclass_at_t.__setattr__(each_name, data_value)

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
            if each_name in self.trajectory_metadata_field():
                pass
            else:
                data_property = self.__getattribute__(each_name)

                if isinstance(data_property, (np.ndarray, AbstractTrajectoryDataclass)):
                    self.__setattr__(each_name, data_property.T)
        # noinspection PyAttributeOutsideInit
        self._transposed = not self._transposed
        return self


@dataclass
class AbstractMultifeatureDataclass(AbstractTrajectoryDataclassCommon):
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
        print(self)
        return None

    @property
    def topic_key_list(self):
        return [
            topic.name for topic in fields(self) if str(topic.name).startswith("topic_")
        ]


def _fetch_nested_attribute(self_, nested_attribute_list: str) -> Any:
    nested_attribute = self_
    for each in nested_attribute_list.split("."):
        nested_attribute = nested_attribute.get_dynamic_field(each)
    return nested_attribute


def _timesteps_indices_vs_index_len_check(
    timesteps_indices: np.ndarray, _timestep_indexes: np.ndarray
) -> None:
    ts_id_len = timesteps_indices.shape[-1]
    ts_idx_len = _timestep_indexes.shape[-1]
    assert ts_idx_len == ts_id_len, (
        f"[TCT error] timesteps_indices expecte " f"lemgth {ts_idx_len} != {ts_id_len}"
    )
    return None
