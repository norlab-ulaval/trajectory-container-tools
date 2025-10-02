# coding=utf-8
import abc
from dataclasses import dataclass, fields
from typing import Any, List, Tuple

from trajectory_container_tools.utils.general import check_typing_list_and_extract_list_type, \
    check_typing_union_and_extract_first_union_type


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


def _fetch_nested_attribute(self_, nested_attribute_list: str) -> Any:
    nested_attribute = self_
    for each in nested_attribute_list.split("."):
        nested_attribute = nested_attribute.get_dynamic_field(each)
    return nested_attribute
