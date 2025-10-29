# coding=utf-8
import abc
import weakref
from dataclasses import dataclass, field, fields
from typing import Any, List, Optional, Tuple, Union

import numpy as np
from deprecated import deprecated

from trajectory_container_tools.utils.typing.tct_custom_field import (
    NonTrajectoryField,
    ContainerInternalField,
)
from trajectory_container_tools.utils.general import (
    check_typing_list_and_extract_list_type,
    check_typing_union_and_extract_first_union_type,
)

from typing import get_origin


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

    _parent: ContainerInternalField[Optional["AbstractTrajectoryCommon"]] = field(
        default=None, init=False
    )

    def set_parent_container_reference_tracking(self):
        """
        Updates nested trajectory container parent container reference tracking.

        This method iterates through all the attribute names and updates the parent
        reference for any data property that is an instance of `AbstractTrajectoryCommon`.

        :return: None
        """
        for each_name in self.get_public_attribute_names():
            attribute = self.__getattribute__(each_name)
            if isinstance(attribute, list) and isinstance(
                attribute[0], AbstractTrajectoryCommon
            ):
                for idx in range(len(attribute)):
                    attribute[idx]._parent = weakref.ref(self)
            else:
                if isinstance(attribute, AbstractTrajectoryCommon):
                    attribute._parent = weakref.ref(self)
        return None

    def get_parent_container(self) -> Union["AbstractTrajectoryCommon", None]:
        """
        Retrieve the parent container associated with the object.

        This method returns the parent container object of the current instance,
        if such a reference exists. If no parent container is set for the object,
        this method will return None.

        :return: The parent container of the current object, or None if not set.
        """
        if not self.is_nested():
            return None
        return self._parent()

    def get_container_root(
        self, include_feature_bag=False
    ) -> "AbstractTrajectoryCommon":
        """
        Recursively retrieves the root container in a hierarchy.

        This method checks if the current object has a parent. If it does, it continues
        to traverse up the hierarchy by calling the same method on the parent object,
        until it reaches the top-most container (the root). If the current object
        does not have a parent, it considers itself the root and returns the current
        object.

        :param include_feature_bag: Include 'TrajectoryFeaturesBag' as root (True), will stop at 'TrajectoryFeaturesBag' root otherwise (Default False).
        :return: The top-most container in the hierarchy.
        """
        parent_container = self.get_parent_container()
        if parent_container is not None:
            from .abstract_trajectory_features_bag_dataclass import (
                AbstractTrajectoryFeaturesBag,
            )

            parent_is_feature_bag = isinstance(
                parent_container, AbstractTrajectoryFeaturesBag
            )

            if include_feature_bag and parent_is_feature_bag:
                return parent_container
            elif not include_feature_bag and parent_is_feature_bag:
                return self

        if not self.is_nested():
            return self

        # Recursively search up the parent chain
        return parent_container.get_container_root(include_feature_bag)

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
        >>>     if not self.get_cls_public_field_names():
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
        >>>     for each_name in self.get_cls_public_field_names(include_non_init_dim=True):
        >>>         self.post_init_feature_callback(feature_name=each_name)
        >>>
        >>>     self.on_exit_post_init_callback()
        >>>
        >>>     return None

        :raises NotImplementedError: If the subclass does not implement this method.
        """
        pass

    @classmethod
    def container_internal_field(cls) -> List[str]:
        """
        List of field marked as internal. Those are field name that will be omited by
        `get_cls_public_field_names` class method and `get_public_attribute_names` method.

        This method is intended to return a predefined list of attribute names that are
        specific to the internal logic of a data class. These fields often represent
        key information required for specialized operations or manipulations within
        the class.

        >>> import trajectory_container_tools as tct
        >>>
        >>> @dataclass()
        >>> class TestMotionTrajectoryDataclass(tct.dataclasses.TestTrajectoryDataclass):
        >>>     trajectory_pose: np.ndarray
        >>>     internal_field: tct.typing.ContainerInternalField[np.ndarray]

        :return: A list containing the names of internal fields used in the data class.
        """
        internal_field = []
        for each in fields(cls):
            origin = get_origin(each.type)
            if origin is ContainerInternalField:
                internal_field.append(each.name)
        return internal_field

    @classmethod
    def non_trajectory_field(cls) -> List[str]:
        """
        List fields that are declared as non trajectory field i.e. not per timestep.

        Usefulll for skipping field of type ndarray that are not trajectory timestep information
        that should be excluded from certain processes such as iterable related logic,
        transpose `T` and `ravel_dimensions_in_place`.

        Usage:

        Mark the field type using `tct.typing.NonTrajectorySequence[SEQUENCE-TYPE]` with
        SEQUENCE-TYPE being one of numpy array, list, or tuple.

        >>> import trajectory_container_tools as tct
        >>>
        >>> @dataclass()
        >>> class TestMotionTrajectoryDataclass(tct.dataclasses.TestTrajectoryDataclass):
        >>>     trajectory_pose: np.ndarray
        >>>     initiale_pose: tct.typing.NonTrajectorySequence[np.ndarray]

        :return: A list of string names corresponding to the fields skipped.
        """
        non_trajectory_fields = []
        for each in fields(cls):
            origin = get_origin(each.type)
            if origin is NonTrajectoryField:
                non_trajectory_fields.append(each.name)
        return non_trajectory_fields

    def get_dynamic_attribute(self, feature_name: str) -> Any:
        """Retrieves the value of a dynamicaly declared attribute from the object.

        This function allows accessing nested attributes of an object dynamically, based on a
        string representation of the attribute's hierarchical structure. It takes a dot-separated
        attribute name, traverses the object's nested levels sequentially, and retrieves the final
        attribute e.g., "feature_name=topic_odom.pose.pose.position.x" would sequentialy crawl into
        nested container "topic_odom" -> "pose" -> "pose" -> "position" -> "x".

        Example:

        >>> position_x_value = self.get_dynamic_attribute("topic_odom.pose.pose.position.x")

        :param feature_name: A dot-separated string representing the hierarchical
          structure of the attribute to retrieve.
        :return: The value of the requested attribute.
        """
        nested_attribute = self
        for each in feature_name.split("."):
            nested_attribute = nested_attribute.__getattribute__(each)
        return nested_attribute

    def has_dynamic_attribute(self, feature_name) -> bool:
        """
        Check if a dynamicaly declared attribute exists in the object.

        This function allows checking nested attributes of an object dynamically, based on a
        string representation of the attribute's hierarchical structure. It takes a dot-separated
        attribute name, traverses the object's nested levels sequentially until reaching the final
        attribute in which case it returns True
        e.g., "feature_name=topic_odom.pose.pose.position.x" would sequentialy crawl into nested
        container "topic_odom" -> "pose" -> "pose" -> "position" -> "x"  ->  True.

        Example:

        >>> self.has_dynamic_attribute("topic_odom.pose.pose.position.x")

        :param feature_name: A dot-separated string representing the hierarchical
          structure of the attribute to retrieve.
        :return: True if the dynamic field exists, False otherwise.
        """
        try:
            self.get_dynamic_attribute(feature_name)
            return True
        except AttributeError:
            return False

    def set_dynamic_attribute(self, feature_name: str, value: Any) -> None:
        """Sets a dynamically resolved nested field or attribute within an object.

        This function dynamically locates and assigns the specified value to a
        nested attribute within an object. The attribute path is determined
        based on the `feature_name`, which can include dot-delimited strings to
        specify multi-level nested attributes.

        Example:

        >>> self.set_dynamic_attribute("topic_odom.pose.pose.position.x", 10)

        :param feature_name: A string specifying the name of the target attribute
            to set. It can be dot-delimited to specify a path to a nested
            attribute within the object.
        :param value: The value to assign to the specified feature or attribute.
        :return: None
        """
        nested_attribute = self
        feature_name_split = feature_name.split(".")
        target = feature_name_split.pop()
        for each in feature_name_split:
            nested_attribute = nested_attribute.__getattribute__(each)
        nested_attribute.__setattr__(target, value)
        return None

    def get_public_attribute_names(self) -> tuple[str, ...]:
        """
        Retrieves the names of the dataclass public attributes.

        This method evaluates all instance attributes including dataclass field and dynamicaly
        created attribute and excludes attributes that are private (starting with an underscore)
        or considered internal to the dataclass.

        :return: A tuple containing the names of all public attributes in the instance.
        """
        container_attributes = vars(self)
        public_attribute_name = []
        for each in container_attributes:
            # Strip private attributes and field marked as tct internal
            if (
                not each.startswith("_")
                and each not in self.container_internal_field()
            ):
                public_attribute_name.append(each)

        return tuple(public_attribute_name)

    @classmethod
    def get_cls_public_field_type(cls, dimension_name: str) -> Tuple[type[Any], bool]:
        """
        Get the type and whether it is a list for a given dimension name.

        The method inspects the class fields, determining the type of the field associated with the provided dimension name. It identifies whether the type is a list or a union, returning the underlying type if applicable.

        :param dimension_name: The name of the dimension to query.
        :return: A tuple containing the type of the dimension and a boolean indicating if the dimension is a list.
        """
        container_fields = fields(cls)
        dimension_type = None
        is_list_of_type = False
        for each_field in container_fields:
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
    def get_cls_public_field_names(cls, include_non_init_dim=True) -> Tuple[str, ...]:
        """
        Provides the dimension names of the data class fields that are exposed to user.

        This method retrieves the field names from the data class that are not marked
        as internal fields. It returns these names as a tuple of strings, making it
        useful for querying the explicitly defined data attributes of the class.

        :return: A tuple containing the names of non-internal fields defined in the class.
        """
        container_fields = fields(cls)

        if not include_non_init_dim:
            # Remove non-init fields
            container_fields = (each for each in container_fields if each.init == True)

        field_name = []
        for each_field in container_fields:
            if each_field.name not in cls.container_internal_field():
                field_name.append(each_field.name)
        return tuple(field_name)

    def on_begin_post_init_callback(self) -> None:
        """Overide this methode to execute custom computation on feature dataclass at the begining
         of `__post_init__` method execution.
        Note: The method scope include all field.

        Example:

        >>> @dataclass
        >>> class StatePose2DSteadyState(StatePose2D):
        >>>
        >>>     def on_begin_post_init_callback(self):
        >>>         feature = self.get_dynamic_attribute("<feature-name>")
        >>>         self.set_dynamic_attribute(f"<other-feature>", np.cumsum(feature))
        >>>         return None

        """
        pass

    def post_init_feature_callback(self, feature_name: str) -> None:
        """Overide this methode to execute feature-aware custom computation.
        Useful for post-processing dynamically declared fields.

        Note:
            - Executed once for each PUBLIC field.
            - Excludes only fields marked by `container_internal_field`.
            - Fields marked as `non_trajectory_field` ARE included; add guards in your
              implementation if you intend to skip them.

        Example:

        >>> steady_state_mask = dataset_snow['steady_state_mask'].to_numpy() == True
        >>>
        >>> @dataclass
        >>> class StatePose2DSteadyState(StatePose2D):
        >>>
        >>>     def post_init_feature_callback(self, feature_name):
        >>>         # Example for creating an explicit timestep t=0 property named "<feature_name>_init"
        >>>         feature = self.get_dynamic_attribute(feature_name)
        >>>         if isinstance(feature, np.ndarray):
        >>>             if self.batch:
        >>>                 # Case batch data
        >>>                 feature_ini = feature[:, 0, ...]
        >>>             else:
        >>>                 # Case time-serie data
        >>>                 feature_ini = feature[0, ...]
        >>>             self.set_dynamic_attribute(f"{feature_name}_init", feature_ini)
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
        >>>         feature = self.get_dynamic_attribute("<feature-name>")
        >>>         assert len(feature) > 0
        >>>         return None

        """
        pass

    @deprecated(
        reason="Functionality of `fetch_nested_attribute` as been merged into `get_dynamic_attribute` method."
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
        nested_attribute = self
        for each in nested_attribute_path.split("."):
            nested_attribute = nested_attribute.get_dynamic_attribute(each)
        return nested_attribute
