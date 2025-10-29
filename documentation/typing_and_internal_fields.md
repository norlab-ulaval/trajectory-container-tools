# Typing and Internal Fields Guide

This guide explains how to use TCT typing markers to control which fields participate in per‑timestep logic, public exposure, and post‑processing callbacks.

## Overview

TCT provides two typing protocols to classify fields in your dataclasses:

- `tct.typing.NonTrajectoryField[T]`
  - Marks fields that are not sampled per timestep (e.g., metadata, labels, static calibration arrays).
  - Excluded from iteration, `T` transpose, and ravel operations.
  - Still part of the public API and included by `get_public_attribute_names()`.
  - Visited by `post_init_feature_callback` like other public fields (you may guard inside the callback if needed).

- `tct.typing.ContainerInternalField[T]`
  - Marks internal implementation details for containers.
  - Hidden from user‑facing API (e.g., omitted by `get_public_attribute_names()`).
  - Ignored by user‑level `post_init_feature_callback` (but not by base‑class internal logic).

These markers are detected by the base classes and automatically integrated in container behavior.

## Quick Example

```python
from dataclasses import dataclass, field
import numpy as np
import trajectory_container_tools as tct

@dataclass
class TrajectoryWithMeta(tct.BaseTrajectoryFeature):
    x: np.ndarray
    y: np.ndarray
    timestamps: np.ndarray

    # Non‑trajectory field: not per timestep
    metadata: tct.typing.NonTrajectoryField[np.ndarray] = field(
        default_factory=lambda: np.array([1, 2, 3])
    )

    # Internal field: implementation detail, not exposed publicly
    _timestep_indexes: tct.typing.ContainerInternalField[np.ndarray] = field(
        default=None, init=False
    )

traj = TrajectoryWithMeta(
    feature_name="demo",
    x=np.arange(5, dtype=float),
    y=np.arange(5, dtype=float),
    timestamps=np.arange(5, dtype=int)
)

print(traj.get_public_attribute_names())
# -> ('x', 'y', 'timestamps', 'metadata')
# '_timestep_indexes' (ContainerInternalField) is hidden
```

## Effects on Container Behavior

- Public attributes:
  - `get_public_attribute_names()` excludes `ContainerInternalField` members and private attributes (those starting with `_`).
- Iteration and indexing:
  - Only per‑timestep features participate; non‑trajectory fields are ignored by per‑timestep logic.
- Transformation utilities:
  - `T` transpose and `ravel_dimensions_in_place()` skip non‑trajectory fields to avoid shape mismatches.
- Post‑processing callbacks:
  - `post_init_feature_callback(feature_name)` is invoked for every public field (i.e., excluding `ContainerInternalField`).
  - `on_begin_post_init_callback()` and `on_exit_post_init_callback()` can still access all attributes via dynamic accessors.

## Dynamic Attribute Access Helpers

You can manipulate attributes (including nested ones) dynamically:

```python
# Add a derived feature
traj.set_dynamic_attribute('x_cumsum', np.cumsum(traj.x))

# Query by name
assert traj.has_dynamic_attribute('x_cumsum')
print(traj.get_dynamic_attribute('x_cumsum'))

# Nested example (if you have nested containers):
traj.set_dynamic_attribute('pose.position.x', 42)
```

## Best Practices

- Prefer explicit typing of non‑trajectory and internal fields to ensure predictable behavior.
- Keep private internal fields prefixed (e.g., `_field_name`) for readability.
- Use `on_begin_post_init_callback` for setup and `on_exit_post_init_callback` for finalization when you need to read/write dynamic attributes.

## Related Documentation

- [Direct Instantiation Guide](direct_instantiation.md)
- [Post‑Processing Callbacks Guide](post_processing_callbacks.md)
- [Timestamp Utilities](timestamp_utilities.md)
