# coding=utf-8
"""
Factory functions for creating trajectory dataclasses dynamically.

Usage:

>>> import trajectory_container_tools as tct
>>>
>>> spec = tct.factory.TrjDataClassFeatureSpecification(
>>>     new_feature_dataclass_type='CustomType',
>>>     dimension_names=('x', 'y', 'z')
>>> )
>>>
>>> new_class = tct.factory.create_dataclass(spec)

"""

from .utils.factory import (
    create_dataclass,
    parse_feature_spec,
    TrjDataClassFeatureSpecification
)

__all__ = [
    'create_dataclass',
    'parse_feature_spec', 
    'TrjDataClassFeatureSpecification',
]
