# coding=utf-8
import abc
import datetime
from copy import deepcopy
from dataclasses import dataclass, field, fields
import numpy as np
from typing import Any, List, Tuple, Type, Union

from rclpy.time import Time

from ..utils.general import extract_class_name_from_instance


@dataclass()
class AbstractTrajectoryDataclassCommon(abc.ABC):

    def get_dynamic_field(self, feature_name: str) -> Any:
        """ Retrieves the value of a dynamicaly declared attribute from the object.

        :param feature_name: The name of the attribute to retrieve.
        :return: The value of the requested attribute.
        """
        return self.__getattribute__(feature_name)

    def set_dynamic_field(self, feature_name: str, value: Any) -> None:
        """ Updates or creates a dynamic attribute on an object.

        :param feature_name: The name of the attribute to update or create.
        :param value: The value to assign to the attribute.
        :return: None
        """
        self.__setattr__(feature_name, value)
        return None

    def fetch_nested_attribute(self, nested_attribute_list: str) -> Any:
        """ Retrieves a nested attribute from an object based on a dot-separated string.

        This function allows accessing nested attributes of an object dynamically, based on a
        string representation of the attribute's hierarchical structure.
        It takes a dot-separated attribute name, traverses the object's nested levels
        sequentially, and retrieves the final attribute
        e.g., "topic_odom.pose.pose.position_x" would sequentialy crawl into nested container
        "topic_odom" -> "pose" -> "pose" -> "position_x".

        Example:

            >>> position_x_value = self.fetch_nested_attribute("topic_odom.pose.pose.position_x")

        :param nested_attribute_list: A dot-separated string representing the hierarchical
          structure of the attribute to retrieve.
        :return: The value of the resolved nested attribute.
        """
        return _fetch_nested_attribute(self, nested_attribute_list)

    @abc.abstractmethod
    def __post_init__(self):
        pass


@dataclass()
class AbstractTrajectoryDataclass(AbstractTrajectoryDataclassCommon):
    """
    An abstract base dataclass for trajectory-related data manipulation
    """

    feature_name: str
    timestep_index: np.ndarray

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
        return ["feature_name", "timestep_index"]

    @classmethod
    def trajectory_metadata_field(cls) -> List[str]:
        """
        List fields that are declared as trajectory wide metadata i.e. not per timestep.
        Usefulll for skipping field of type ndarray that are not trajectory timestep information.

        This method provides a default implementation for specifying the fields
        that should be excluded from certain process such as `__post_init__`, transpose `T` and
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
        # Note: "header_FrameId" and "childFrameId" are rosbag generated field
        return ["header_FrameId", "childFrameId"]

    def on_begin_post_init_callback(self) -> None:
        """Overide this methode to execute custom computation on feature dataclass at the begining
         of `__post_init__` method execution.
        Note: The method scope include all field.

        Example:
            >>> @dataclass
            >>> class StatePose2DSteadyState(StatePose2D):
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
            >>>     def post_init_feature_callback(self, feature_name):
            >>>         feature = self.get_dynamic_field(feature_name)
            >>>         if isinstance(feature, np.ndarray):
            >>>             feature_ini = feature[0, ...]
            >>>             if self.current_trj_axe == -1:
            >>>                 feature_ini = feature[..., 0]
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
            >>>     def on_exit_post_init_callback(self):
            >>>         feature = self.get_dynamic_field("<feature-name>")
            >>>         assert len(feature) > 0
            >>>         return None

        """
        pass

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

    @classmethod
    def get_dimension_type(cls, dimension_name: str) -> Type[Any]:
        container_properties = fields(cls)
        dimension_type = None
        for each_field in container_properties:
            if each_field.name is dimension_name:
                dimension_type = each_field.type
        return dimension_type

    @property
    def _init_trj_axe(self) -> int:
        """
        The numpy array axe on which is the trajectory time index at dataclass initialization.

        This property provides the initialized value of a trajectory axis, which is set to -1 by
        default. This could have further implications where such initialization is required for
        trajectory handling, depending on the context of the application e.g. data fetch from
        dataframe vs from rosbag. This property is meant to be overriden.

        :return: The trajectory array axe.
        """
        return -1

    @property
    def trajectory_len(self) -> int:
        return self.timestep_index.size

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
        self._iter_index: int = 0
        self.transposed: bool = False

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

                data_property = self.__getattribute__(each_name)

                if isinstance(data_property, AbstractTrajectoryDataclass):

                    # Init timestep_index with nested dataclass trajectory_len
                    if self.timestep_index is None:
                        self.timestep_index = np.arange(data_property.trajectory_len)

                elif isinstance(data_property, np.ndarray):
                    data_property: np.ndarray
                    data_property_trajectory_len = data_property.shape[self._init_trj_axe]

                    # Init timestep_index with dataclass trajectory_len
                    if self.timestep_index is None:
                        self.timestep_index = np.arange(data_property_trajectory_len)

                    if data_property_trajectory_len != self.trajectory_len:
                        raise ValueError(
                                f"{data_property_trajectory_len} != {self.trajectory_len}\n"
                                f"[TCT error] Topic `{self.feature_name}` with container `"
                                f"{each_name}`" " received numpy arrays which do not match "
                                "the trajectory length"
                                )
                else:
                    raise TypeError(
                            f"[TCT error] Property `{each_name}` is not a numpy ndarray")

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

        repr_str += f"{m_sp}trajectory_len: {self.trajectory_len}\n"
        repr_str += f"{m_sp}transposed: {self.transposed}\n"
        repr_str += f"{m_sp}dimensions:\n"

        for k, v in self.__dict__.items():
            if k in ["_iter_index", "transposed", "feature_name", "timestep_index"]:
                pass
            elif isinstance(v, np.ndarray):
                if v.ndim > 0 and isinstance(v[0], Time):
                    range_str = f"range(nanosec) {np.min(v).nanoseconds} ⟶ {np.max(v).nanoseconds}"
                else:
                    range_str = f"range {np.min(v)} ⟶ {np.max(v)}"
                repr_str += (f"{m_sp}{item_space}{k}: ({extract_class_name_from_instance(v)}) "
                             f"shape {v.shape} {range_str}\n")
            elif isinstance(v, AbstractTrajectoryDataclass):
                indent_v = []
                for each_line in str(v).splitlines():
                    indent_v.append(f"{t_sp}{each_line}\n")
                indent_v = "".join(indent_v)
                repr_str += f"{m_sp}{item_space}{k}:{indent_v}"
            else:
                repr_str += f"{m_sp}{item_space}{k}: ({extract_class_name_from_instance(v)}) {v}\n"
        repr_str += f"{m_sp})"
        return repr_str

    @property
    def current_trj_axe(self):
        if self._init_trj_axe == -1 and self.transposed == True:
            return 0
        elif self._init_trj_axe == 0 and self.transposed == True:
            return -1
        else:
            return self._init_trj_axe

    def __getitem__(self, key):
        feature_dataclass_at_t = deepcopy(self)

        feature_dataclass_at_t.__setattr__("timestep_index", self.timestep_index[key])
        for each_name in self.get_dimension_names():
            if each_name in self.trajectory_metadata_field():
                pass
            else:
                data_property = self.__getattribute__(each_name)

                if isinstance(data_property, (np.ndarray, AbstractTrajectoryDataclass)):
                    if self.current_trj_axe == -1:
                        data_value = data_property[..., key]
                    else:
                        data_value = data_property[key]

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
        self.transposed = not self.transposed
        return self


@dataclass
class AbstractMultifeatureDataclass(AbstractTrajectoryDataclassCommon):
    dataset_info: str
    aggregated_date: datetime.datetime = field(init=False)

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
            elif k == "aggregated_date":
                pass
            else:
                # repr_str += f"{m_sp}{k}( {str(v)}\n{m_sp*2})\n"
                repr_str += f"{m_sp}{k}: {str(v)}\n"
        repr_str += f"{m_sp})"
        return repr_str

    @property
    def summary(self) -> None:
        print(self)
        return None


def _fetch_nested_attribute(self_, nested_attribute_list: str) -> Any:
    nested_attribute = self_
    for each in nested_attribute_list.split('.'):
        nested_attribute = nested_attribute.get_dynamic_field(each)
    return nested_attribute
