# coding=utf-8
from dataclasses import dataclass, make_dataclass
from typing import Tuple, Type

import numpy as np

from ..dataclasses.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
)
from ..dataclasses.base_trajectory_dataclass import BaseTrajectoryDataclass


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


def trajectory_dataclass_factory(
    specification: TrjDataClassFeatureSpecification,
    trj_dataclass_subclass: Type[AbstractTrajectoryDataclass] = BaseTrajectoryDataclass,
) -> type(AbstractTrajectoryDataclass):
    """A factory function for dynnamicaly creates new `AbstractTrajectoryDataclass` subclass
    from a TrjDataClassFeatureSpecification dataclass object.

    Usage example:
        >>> spec_ = TrjDataClassFeatureSpecification(new_feature_dataclass_type='my_new_feature_type',
        >>>                              dimension_names=('xx', 'yy', 'yawww'))
        >>> the_new_cls = trajectory_dataclass_factory(specification=spec_)
        >>> assert issubclass(the_new_cls, BaseTrajectoryDataclass)
        >>> # True
        >>> assert isinstance(the_new_cls, BaseTrajectoryDataclass)
        >>> # False

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
            f"(!) The key {e} is missing from the `specification` dictionary passed in argument."
        )
    except AttributeError as e:
        raise AttributeError(
            "(!) The `specification` dictionary must contain key "
            "'new_feature_dataclass_type' with value of type "
            f"string and key `dimension_names` with value of type tuple of string. {e}"
        )

    properties_field = [(name, np.ndarray) for name in dimension_names]

    return make_dataclass(
        new_feature_dataclass_type,
        bases=(trj_dataclass_subclass,),
        fields=properties_field,
    )
