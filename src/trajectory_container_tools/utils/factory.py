# coding=utf-8
from dataclasses import dataclass, make_dataclass
from typing import Tuple, Union

import numpy as np

from trajectory_container_tools.typing import TrajectoryDataclass
from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import BaseTrajectoryDataclass


@dataclass()
class TrjDataClassFeatureSpecification:
    """
    Represents the specification of a trajectory dataclass features with its new data type
    and feature names.

    This class is designed to encapsulate the core properties of a trajectory dataclass,
    mainly focusing on its data type and dimensional aspects. It includes
    attributes to store the type of the feature's data and the names of dimensions
    associated with it, ensuring a structured way to manage feature configurations.

    :ivar new_feature_dataclass_type: Indicates the data type of the feature.
    :type new_feature_dataclass_type: str
    :ivar dimension_names: A tuple containing the names of the dimensions
        associated with the feature.
    :type dimension_names: Tuple[str, ...]
    """
    new_feature_dataclass_type: str
    dimension_names: Tuple[str, ...]


def create_dataclass(
        specification: TrjDataClassFeatureSpecification,
        trj_dataclass_subclass: type[TrajectoryDataclass] = BaseTrajectoryDataclass,
        ) -> Union[type, type[TrajectoryDataclass]]:
    """A factory function for dynnamicaly creates new `AbstractTrajectoryDataclass` subclass
    from a TrjDataClassFeatureSpecification dataclass object.

    Usage example:

    >>> spec_ = TrjDataClassFeatureSpecification(
    >>>             new_feature_dataclass_type='my_new_feature_type',
    >>>             dimension_names=('xx', 'yy', 'yawww')
    >>>         )
    >>> the_new_cls = create_dataclass(specification=spec_)
    >>> assert issubclass(the_new_cls, BaseTrajectoryDataclass)
    True
    >>> assert isinstance(the_new_cls, BaseTrajectoryDataclass)
    False

    :param specification: A TrjDataClassFeatureSpecification object,
    :param trj_dataclass_subclass: a subclass of 'AbstractTrajectoryDataclass'
    :return: A new subclass of AbstractTrajectoryDataclass
    """
    try:
        new_feature_dataclass_type: str = specification.new_feature_dataclass_type
        dimension_names: Tuple[str, ...] = specification.dimension_names
        if (
                (type(new_feature_dataclass_type) is not str)
                or (type(dimension_names) is not tuple)
                or (any([type(name) is not str for name in dimension_names]))
        ):
            raise AttributeError
    except KeyError as e:
        raise KeyError(
                f"[TCT error] The key {e} is missing from the `specification` dictionary passed "
                f"in argument."
                )
    except AttributeError as e:
        raise AttributeError(
                "[TCT error] The `specification` dictionary must contain key "
                "'new_feature_dataclass_type' with value of type "
                f"string and key `dimension_names` with value of type tuple of string. {e}"
                )

    properties_field = [(name, np.ndarray) for name in dimension_names]

    trajectory_dataclass = make_dataclass(new_feature_dataclass_type,
                                          bases=(trj_dataclass_subclass,),
                                          fields=properties_field, )
    return trajectory_dataclass


def parse_feature_spec(feature_dataclass_spec: tuple[str, ...],
                       target_subclass: type[TrajectoryDataclass],
                       feature_name: str) -> type[TrajectoryDataclass]:
    """ Parses the feature specification tuple to generate a new TrajectoryDataclass type based on
    the provided specification and target subclass.

    :param feature_dataclass_spec: A tuple that includes the new feature dataclass type name as
     the first element, followed by names of the dimensions or fields to be extracted (e.g.,
     ('<NewFeatureDataclassTypeName>', '<topic_property_name_1>', '<topic_property_name_2>', ...)).
    :param target_subclass: The target subclass of TrajectoryDataclass to which the new
     dataclass will belong.
    :param feature_name: The name of the feature being processed. Used for error logging and
     validation.
    :return: A new type of TrajectoryDataclass generated based on the provided specification and
     target subclass.
    """
    if len(feature_dataclass_spec) == 1:
        raise KeyError(
                f"[TCT error] Check your `features_config` dict. "
                f"You forgot to specify the field to extract from topic '{feature_name}'."
                f"Need to have the form ('<NewFeatureDataclassTypeName>', "
                f"'<topic_property_name_1>', '<topic_property_name_2>', ...)"
                )

    new_type_name, *dimensions = feature_dataclass_spec
    feat_spec = TrjDataClassFeatureSpecification(
            new_feature_dataclass_type=new_type_name, dimension_names=tuple(dimensions)
            )

    feature_dataclass = create_dataclass(
            specification=feat_spec, trj_dataclass_subclass=target_subclass
            )
    return feature_dataclass
