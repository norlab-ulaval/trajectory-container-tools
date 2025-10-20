# coding=utf-8
import abc
from dataclasses import dataclass, field, fields
from typing import Any, List, Optional, Tuple, Union

import numpy as np
from deprecated import deprecated

from trajectory_container_tools.utils.general import (
    check_typing_list_and_extract_list_type,
    check_typing_union_and_extract_first_union_type,
)


@dataclass()
class AbstractTrajectoryCommon(abc.ABC):
    """
    Provides an abstract base dataclass for dynamically interacting with and managing object
    attributes, including dynamic fields creation and nested attribute retrieval.

    This class serves as a foundation for implementing objects that must support
    dynamically added fields, as well as hierarchical retrieval of nested attributes. It is
    an abstract base class (ABC) and requires implementation of the `__post_init__` method
    in subclasses.

    """

    _parent: Optional["AbstractTrajectoryCommon"] = field(default=None, init=False)

    def set_parent_container_reference_tracking(self):
        """
        Updates nested trajectory container parent container reference tracking.

        This method iterates through all the attribute names and updates the parent
        reference for any data property that is an instance of `AbstractTrajectoryCommon`.

        :return: None
        """
        for each_name in self.get_dimension_names():
            attribute = self.__getattribute__(each_name)
            if isinstance(attribute, list) and isinstance(attribute[0], AbstractTrajectoryCommon):
                for idx in range(len(attribute)):
                    attribute[idx]._parent = self
            else:
                if isinstance(attribute, AbstractTrajectoryCommon):
                    attribute._parent = self
        return None

    def get_parent_container(self) -> Union["AbstractTrajectoryCommon", None]:
        """
        Retrieve the parent container associated with the object.

        This method returns the parent container object of the current instance,
        if such a reference exists. If no parent container is set for the object,
        this method will return None.

        :return: The parent container of the current object, or None if not set.
        """
        return self._parent

    def get_root_container(self) -> "AbstractTrajectoryCommon":
        """
        Recursively retrieves the root container in a hierarchy.

        This method checks if the current object has a parent. If it does, it continues
        to traverse up the hierarchy by calling the same method on the parent object,
        until it reaches the top-most container (the root). If the current object
        does not have a parent, it considers itself the root and returns the current
        object.

        :return: The top-most container in the hierarchy.
        """
        if self._parent is None:
            return self

        # Recursively search up the parent chain
        return self._parent.get_root_container()

    def is_nested(self) -> bool:
        """
        Determines if the current object is nested within another object.

        A nested object is identified by the presence of a parent object.
        This method checks whether the current instance has a parent and
        returns a boolean indicating the nesting status.

        :return: Boolean value indicating if the object is nested.
        """
        return self._parent is not None

    @abc.abstractmethod
    def __post_init__(self):
        """
        Defines an abstract method to be implemented by subclasses ensuring post-initialization logic
        is enforced for dataclass-like constructs.

        This method serves as a placeholder for a post-construction initialization hook that should
        be provided when subclassing. It is marked as abstract to mandate its implementation.

        Expect the following at minimum:

        >>> def __post_init__(self):
        >>>     # .... Pre-condition ..............................................................
        >>>     if not self.get_dimension_names():
        >>>         raise TypeError(
        >>>             f"[TCT error] {self.__class__.__name__} is an abstract baseclass, "
        >>>             f"it must be subclassed in order to be instanciated."
        >>>         )
        >>>
        >>>     # .... Base class initialization logic ............................................
        >>>     self.set_parent_container_reference_tracking()
        >>>
        >>>     # .... Callback and attribute customization logic .................................
        >>>     self.on_begin_post_init_callback()
        >>>
        >>>     for each_name in self.get_dimension_names():
        >>>         self.post_init_feature_callback(feature_name=each_name)
        >>>
        >>>     self.on_exit_post_init_callback()
        >>>
        >>>     return None

        :raises NotImplementedError: If the subclass does not implement this method.
        """
        pass

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
        return ["_parent"]

    @classmethod
    def non_trajectory_field(cls) -> List[str]:
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
        >>>     def non_trajectory_field(cls) -> List[str]:
        >>>         return super().non_trajectory_field() + ["initiale_pose"]

        :return: A list of string names corresponding to the fields skipped.
        """
        return []

    def get_dynamic_field(self, feature_name: str) -> Any:
        """Retrieves the value of a dynamicaly declared attribute from the object.

        This function allows accessing nested attributes of an object dynamically, based on a
        string representation of the attribute's hierarchical structure. It takes a dot-separated
        attribute name, traverses the object's nested levels sequentially, and retrieves the final
        attribute e.g., "topic_odom.pose.pose.position.x" would sequentialy crawl into nested
        container "topic_odom" -> "pose" -> "pose" -> "position" -> "x".

        Example:

        >>> position_x_value = self.get_dynamic_field("topic_odom.pose.pose.position.x")

        :param feature_name: A dot-separated string representing the hierarchical
          structure of the attribute to retrieve.
        :return: The value of the requested attribute.
        """
        nested_attribute = self
        for each in feature_name.split("."):
            nested_attribute = nested_attribute.__getattribute__(each)
        return nested_attribute

    def set_dynamic_field(self, feature_name: str, value: Any) -> None:
        """Sets a dynamically resolved nested field or attribute within an object.

        This function dynamically locates and assigns the specified value to a
        nested attribute within an object. The attribute path is determined
        based on the `feature_name`, which can include dot-delimited strings to
        specify multi-level nested attributes.

        Example:

        >>> self.set_dynamic_field("topic_odom.pose.pose.position.x", 10)

        :param feature_name: A string specifying the name of the target attribute
            to set. It can be dot-delimited to specify a path to a nested
            attribute within the object.
        :param value: The value to assign to the specified feature or attribute.
        :return: None
        """
        # ToDo: update documentation (re task TCT-65)

        nested_attribute = self
        feature_name_split = feature_name.split(".")
        target = feature_name_split.pop()
        for each in feature_name_split:
            nested_attribute = nested_attribute.__getattribute__(each)
        nested_attribute.__setattr__(target, value)
        return None

    @deprecated(
        reason="Functionality of `fetch_nested_attribute` as been merged into `get_dynamic_field` method."
    )
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
        # ToDo: TCT-65 feat: unify dynamic_field getter setter with fetch_nested_attribute method
        nested_attribute = self
        for each in nested_attribute_path.split("."):
            nested_attribute = nested_attribute.get_dynamic_field(each)
        return nested_attribute

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
              and `non_trajectory_field`.

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
