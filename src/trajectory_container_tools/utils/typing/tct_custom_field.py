# coding=utf-8
from numbers import Number
from typing import Any, Generic, Sequence, TypeVar, Annotated, Protocol

import numpy as np

NonTrajectorySequence = TypeVar(
    "NonTrajectorySequence", Sequence[bool | str | Number | Any], np.ndarray
)
TCTInternalVar = TypeVar(
    "TCTInternalVar",
    bool,
    str,
    Number,
    Sequence[bool | str | Number | Any],
    np.ndarray,
)


class NonTrajectoryField(Protocol[NonTrajectorySequence]):
    """
    A class representing a non-trajectory field specialization.

    This class is used as a generic container for non-trajectory-related
    sequences or similar objects. It serves as a marker
    class for specific types of sequences that do not pertain to
    trajectory-type functionalities. The primary purpose is to allow
    code modularity and clarity when handling various types of fields.
    """

    pass


class ContainerInternalField(Protocol[TCTInternalVar]):
    """
    A generic class representing an TrajectoryContainer internal field that are not be exposed
    to user but can be potentialy used as a dataclass constructor argument or keyword argument.
    """

    pass
