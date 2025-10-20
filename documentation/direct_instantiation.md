# Trajectory Container Tools - Direct Instantiation Guide

This document covers the essential functionality of Trajectory Container Tools (TCT) for creating and working with
trajectory data through direct instantiation of dataclasses.

## Overview

TCT provides a flexible system for managing trajectory-related data through specialized dataclasses. The library offers:

- **Trajectory dataclasses** of various types
- **Factory functions** for dynamic dataclass creation
- **Data validation** and consistency checks
- **Trajectory slicing** and iteration
- **Batch processing** capabilities

## 1. Basic Trajectory Creation

### Simple Trajectory Container Structure

The most straightforward way to create a trajectory is by extending `BaseTrajectoryFeature`:

```python
from dataclasses import dataclass
import numpy as np
import trajectory_container_tools as tct


@dataclass()
class Simple2DTrajectory(tct.BaseTrajectoryFeature):
    x: np.ndarray
    y: np.ndarray
    timestamps: np.ndarray


# Create sample data
timesteps = 50
time_array = np.linspace(0, 5, timesteps)
x_positions = np.sin(time_array)
y_positions = np.cos(time_array)
timestamps = np.arange(timesteps) * 0.1  # 10 Hz sampling

# Instantiate trajectory
trajectory = Simple2DTrajectory(
        feature_name="2D coordinate",
        x=x_positions,
        y=y_positions,
        timestamps=timestamps
        )

print((
        f"Created trajectory with {trajectory.trajectory_len} timesteps\n"
        f"Available dimensions: {trajectory.get_dimension_names()}\n"
), trajectory)
```
```text
Created trajectory with 50 timesteps
Available dimensions: ('x', 'y', 'timestamps')
 
Simple2DTrajectory(
   feature_name: "2D coordinate"
   trajectory_len: 50
   transposed: False
   x: (ndarray) shape (50,) range -0.9998286683840896 ←→ 0.9991927284190055
   y: (ndarray) shape (50,) range -0.9997651572585272 ←→ 1.0
   timestamps: (ndarray) shape (50,) range 0.0 ←→ 4.9
)
```

### Nested Trajectory Container Structure

For more complex data organization, use `NestedBaseTrajectory` for custom implementation or use dataclasses from `primitive_dataclass` module:

```python
from trajectory_container_tools.dataclasses import BaseTrajectoryFeature, NestedBaseTrajectory,

Vector2D


@dataclass()
class CustomPoseContainer(NestedBaseTrajectory):
    x: np.ndarray
    y: np.ndarray


@dataclass()
class ComplexTrajectory(BaseTrajectoryFeature):
    timestamps: np.ndarray
    position: CustomPoseContainer
    velocity: Vector2D


sin_cos_trajectory_object = ComplexTrajectory(feature_name="mock",
                                              timestamps=timestamps,
                                              position=CustomPoseContainer(x_positions, y_positions),
                                              velocity=Vector2D(np.ones_like(x_positions), np.ones_like(y_positions))
                                              )

print(sin_cos_trajectory_object)
```
```text
ComplexTrajectory(
   feature_name: "mock"
   trajectory_len: 50
   transposed: False
   timestamps: (ndarray) shape (50,) range 0.0 ←→ 4.9
   position:      
      CustomPoseContainer(
         x: (ndarray) shape (50,) range -0.9998286683840896 ←→ 0.9991927284190055
         y: (ndarray) shape (50,) range -0.9997651572585272 ←→ 1.0
      )
   velocity:      
      Vector2D(
         x: (ndarray) shape (50,) range 1.0 ←→ 1.0
         y: (ndarray) shape (50,) range 1.0 ←→ 1.0
      )
)
```

## 2. Factory-Based Creation

TCT provides factory functions for dynamic trajectory dataclass creation:

```python
import trajectory_container_tools as tct

mock_data = np.random.randn(100, 4)  # 100 timesteps, 4 dimensions

# Define the specification
spec = tct.factory.TrjDataClassFeatureSpecification(
        new_feature_dataclass_type="DynamicTrajectory",
        dimension_names=("x", "y", "velocity", "acceleration"),
        )

# Create the dataclass type
DynamicTrajectory = tct.factory.create_dataclass(specification=spec)

# Use the dynamically created class
factory_generated_trajectory = DynamicTrajectory(
        feature_name="Factory-made-mock-trajectory",
        x=mock_data[:, 0],
        y=mock_data[:, 1],
        velocity=mock_data[:, 2],
        acceleration=mock_data[:, 3]
        )

print(factory_generated_trajectory)
```
```text
DynamicTrajectory(
   feature_name: "Factory-made-mock-trajectory"
   trajectory_len: 100
   transposed: False
   x: (ndarray) shape (100,) range -2.8067159942539015 ←→ 2.018059742950711
   y: (ndarray) shape (100,) range -3.5676843050150926 ←→ 2.0816464902167486
   velocity: (ndarray) shape (100,) range -4.021012195862169 ←→ 2.298877879591126
   acceleration: (ndarray) shape (100,) range -2.4792498489875174 ←→ 2.636162133054269
)
```

## 3. Data Access and Manipulation

### Basic Data Access

```python
# Access individual dimensions
print(f"X position range: [{ trajectory.x.min():.2f}, { trajectory.x.max():.2f}]")
print(f"Y position range: [{ trajectory.y.min():.2f}, { trajectory.y.max():.2f}]")
print(f"Time range: [{ trajectory.timestamps.min():.2f}, { trajectory.timestamps.max():.2f}] seconds")
```

### Trajectory Slicing

Extract portions of trajectories using standard Python slicing:

```python
# Get timesteps 10-30
partial_trajectory = trajectory[10:30]
print(f"Original length: {trajectory.trajectory_len}")
print(f"Partial length: {partial_trajectory.trajectory_len}")

# Access sliced data
print(f"Partial X range: [{partial_trajectory.x.min():.2f}, {partial_trajectory.x.max():.2f}]")
```

### Iteration Through Trajectory Points

```python
# Iterate through trajectory points
print("First 5 trajectory points:")
for i, point in enumerate(trajectory):
    if i >= 5:
        break
    print(f"Point {i}: x={point.x:.3f}, y={point.y:.3f}")
```
```text
First 5 trajectory points:
Point 0: x=0.000, y=1.000
Point 1: x=0.102, y=0.995
Point 2: x=0.203, y=0.979
Point 3: x=0.301, y=0.954
Point 4: x=0.397, y=0.918
```


## 4. Batch Processing

TCT supports batch trajectories for processing multiple trajectories simultaneously:

```python
from trajectory_container_tools.dataclasses import BaseTrajectoryFeature

# Create batch trajectories (3 trajectories, 20 timesteps each)
batch_size, time_steps = 3, 20
batch_x = np.random.randn(batch_size, time_steps)
batch_y = np.random.randn(batch_size, time_steps)
batch_frame = np.random.randn(batch_size, time_steps, 10)
batch_timestamps = np.tile(np.arange(time_steps) * 0.1, (batch_size, 1))


@dataclass()
class Simple2DCoordinateTrajectory(BaseTrajectoryFeature):
    x: np.ndarray
    frame: np.ndarray
    y: np.ndarray
    timestamps: np.ndarray


batch_trajectory = Simple2DCoordinateTrajectory(
        feature_name="batch 2d coordinate",
        x=batch_x,
        y=batch_y,
        frame=batch_frame,
        timestamps=batch_timestamps,
        batch=True
        )

print(f"Batch trajectory shape: {batch_trajectory.x.shape}")
print(f"Number of trajectories: {batch_trajectory.x.shape[0]}")
print(f"Timesteps per trajectory: {batch_trajectory.x.shape[1]}")
print(f"Trajectory length: {len(batch_trajectory)}")

print(batch_trajectory)
```
```text
Batch trajectory shape: (3, 20)
Number of trajectories: 3
Timesteps per trajectory: 20
Trajectory length: 20

Simple2DCoordinateTrajectory(
   feature_name: "batch 2d coordinate"
   trajectory_len: 20
   batch: True
   transposed: False
   x: (ndarray) shape (3, 20) range -2.5113839987831215 ←→ 1.681015962925701
   frame: (ndarray) shape (3, 20, 10) range -2.73686385455718 ←→ 3.420971060958493
   y: (ndarray) shape (3, 20) range -1.8188956133014138 ←→ 2.0797921599919524
   timestamps: (ndarray) shape (3, 20) range 0.0 ←→ 1.9000000000000001
)
```


## 5. Data Validation

TCT automatically validates data consistency during instantiation:

```python
# Example of data validation - this will work
trajectory_length = 5
valid_x = np.arange(trajectory_length)
valid_y = np.arange(trajectory_length)
valid_frame = np.random.randn(trajectory_length, 10)
valid_timestamps = np.arange(trajectory_length) * 0.1


# Create trajectory container
valid_trajectory = Simple2DCoordinateTrajectory(
    feature_name="2D coordinate – valid",
    x=valid_x,
    y=valid_y,
    frame=valid_frame,
    timestamps=valid_timestamps
)

print("Valid trajectory created successfully!")
print(f"Trajectory length: {valid_trajectory.trajectory_len}\n")

# Demonstrate error handling with mismatched dimensions
try:
    # This should raise an error due to mismatched array lengths
    invalid_y = np.arange(trajectory_length - 1)  # 4 elements - mismatch!

    invalid_trajectory = Simple2DCoordinateTrajectory(
        feature_name="2D coordinate – invalid",
        x=valid_x,
        y=invalid_y,
        frame=valid_frame,
        timestamps=valid_timestamps
    )

except ValueError as e:
    print(f"Expected error caught: {type(e).__name__}")
    print(e)
```
```text
Valid trajectory created successfully!
Trajectory length: 5

Expected error caught: ValueError
4 != 5
[TCT error] `2D coordinate – invalid` with container `y` received numpy arrays which do not match the trajectory length
```

## 6. Key Features Summary

### Essential Capabilities

1. **Flexible Dataclass Definition**: Create custom trajectory types by extending base classes
2. **Dynamic Creation**: Use factory functions to generate dataclasses at runtime
3. **Data Validation**: Automatic consistency checking for array dimensions
4. **Trajectory Operations**: Slicing, iteration, and batch processing
5. **Nested Structures**: Support for complex, hierarchical data organization

### Base Classes

- `AbstractTrajectoryFeature`: Abstract base providing core functionality
- `BaseTrajectoryFeature`: Standard flat trajectory container
- `NestedBaseTrajectory`: Support for nested data structures

### Factory Functions

- `TrjDataClassFeatureSpecification`: Specification class for dynamic creation
- `create_dataclass()`: Creates dataclass types from specifications
- `parse_feature_spec()`: Parses feature specifications for dataclass generation

## 7. Working with Timestamps

TCT provides enhanced timestamp utilities through the `Timestamps` class for managing and querying temporal data:

### Creating Timestamps

```python
import numpy as np
import trajectory_container_tools as tct

# Create timestamps in nanoseconds (ROS2 format)
stamps_ns = np.array([
    1695601812731601521,
    1695601812751577171,
    1695601812771552821,
    1695601812791528471,
    1695601812811504121
])

timestamps = tct.temporal.Timestamps(stamps_ns)
print(timestamps)
```

### Timestamp Indexing and Slicing

```python
# Index access
first_stamp = timestamps[0]
last_stamp = timestamps[-1]

# Slice timestamps
first_three = timestamps[0:3]
print(f"First three timestamps: {first_three}")

# Get length
print(f"Number of timestamps: {len(timestamps)}")
```

### Finding Nearest Timestamps

```python
# Find nearest timestamp to a query time
query_time = 1695601812741589346

# Get nearest future timestamp (default)
nearest_future = timestamps.get_nearest_stamp(query_time, future=True)
print(f"Nearest future stamp: {nearest_future}")

# Get nearest past timestamp
nearest_past = timestamps.get_nearest_stamp(query_time, future=False)
print(f"Nearest past stamp: {nearest_past}")

# Convenience methods
nearest_future = timestamps.get_nearest_futur_stamp(query_time)
nearest_past = timestamps.get_nearest_past_stamp(query_time)
```

### Timestamp Queries and Validation

```python
# Check timestamp bounds
min_stamp = timestamps.min()
max_stamp = timestamps.max()
print(f"Timestamp range: {min_stamp} to {max_stamp}")

# Check if timestamps are within bounds
query_stamp = 1695601812751577171
if timestamps.is_timestamps_in_bounds(query_stamp):
    print(f"Timestamp {query_stamp} is within bounds")

# Check if timestamp exists
if query_stamp in timestamps:
    print(f"Timestamp {query_stamp} exists in the dataset")

# Get indices for specific timestamps
query_stamps = [1695601812731601521, 1695601812771552821]
try:
    indices = timestamps.get_indexes(query_stamps)
    print(f"Indices for query timestamps: {indices}")
except tct.TimestampMissingError as e:
    print(f"Timestamp exists but not in stamps: {e}")
except tct.TimestampOutOfBoundError as e:
    print(f"Timestamp out of bounds: {e}")

# Validate timestamp ordering (causal consistency check)
try:
    timestamps.causal_ordering_sanity_check(show_offending_in_nanoseconds=True)
    print("Timestamps are causally ordered (monotonically increasing)")
except tct.TimestampCausalOrderingError as e:
    print(f"Timestamp ordering error: {e}")
```

### Time Conversion Utilities

```python
# Convert nanoseconds to seconds
seconds = tct.temporal.to_seconds(stamps_ns)
print(f"Timestamps in seconds: {seconds}")

# Convert to seconds and nanoseconds components
secs, nsecs = tct.temporal.to_seconds_nanoseconds(stamps_ns)
print(f"Seconds: {secs}, Nanoseconds: {nsecs}")

# Compute delta timestamps (time differences)
delta_stamps = tct.temporal.compute_delta_timestamp(stamps_ns)
print(f"Time deltas: {delta_stamps}")
```

### Practical Example: Synchronizing Data Sources

```python
# Synchronize data from two sensors with different sampling rates
sensor_a_timestamps = tct.temporal.Timestamps(np.array([100, 120, 140, 160, 180]))
sensor_b_timestamps = tct.temporal.Timestamps(np.array([105, 125, 145, 165, 185]))

# Find matching timestamps from sensor B for each sensor A timestamp
synchronized_indices = []
for stamp_a in sensor_a_timestamps.stamps:
    # Find nearest past timestamp in sensor B
    nearest_b = sensor_b_timestamps.get_nearest_past_stamp(stamp_a)
    idx_b = sensor_b_timestamps.get_indexes([nearest_b])[0]
    synchronized_indices.append(idx_b)

print(f"Synchronized indices: {synchronized_indices}")
```

### Key Timestamp Features

- **Boundary Methods**: Get min/max timestamps and check if timestamps are within bounds
- **Enhanced Error Handling**: Specific exceptions for missing vs out-of-bound timestamps
- **Indexing & Slicing**: Full numpy-like indexing support
- **Nearest Neighbor Search**: Find closest timestamps (past/future) for data synchronization
- **Membership Testing**: Check if specific timestamps exist using `in` operator
- **Index Retrieval**: Get array indices for timestamp values with robust error handling
- **Causal Ordering Validation**: Ensure timestamps are monotonically increasing
- **Time Conversions**: Convert between nanoseconds, seconds, and (seconds, nanoseconds) pairs
- **Delta Computation**: Calculate time differences between consecutive timestamps

For more advanced timestamp operations including trajectory features bag timestamp aggregation, see the [Timestamp Utilities Guide](timestamp_utilities.md).

## Usage Recommendations

1. **Start Simple**: Begin with `BaseTrajectoryFeature` for basic use cases
2. **Use Factories**: Leverage factory functions for dynamic, configurable trajectory types
3. **Validate Early**: Take advantage of built-in validation to catch data inconsistencies
4. **Batch When Appropriate**: Use batch processing for multiple trajectory analysis
5. **Structure Wisely**: Choose between flat and nested structures based on data complexity

For more advanced features including rosbag integration and pandas dataframe extraction, refer to the additional
documentation files in this directory.

---

## Documentation
- [Landing page](../README.md#_trajectory-container-tools_)
- [Overview and Core concept](README.md#trajectory-container-tools-documentation)
  - ↳ [Post-Processing Callbacks Guide](./post_processing_callbacks.md#post-processing-callbacks-in-tct)
  - ↳ [DataFrame To TCT Usage Guide](dataframe_usage.md) - Convert pandas DataFrames to trajectory containers
  - ↳ [ROS To TCT Bag Usage Guide](rosbag_usage.md) - Learn to extract trajectory data from ROS bags
  - ↳ [Timestamp Utilities Guide](timestamp_utilities.md) - Advanced timestamp operations
- Interactive Jupyter notebook examples:
    - [Direct Instanciation Usage Examples](../notebooks/direct_instanciation_usage_example.ipynb) - Direct trajectory
      container instantiation
    - [ROS Bag Usage Examples](../notebooks/rosbag_usage_example.ipynb) - Extract trajectory data from ROS bags
    - [DataFrame Usage Examples](../notebooks/dataframe_usage_example.ipynb) - Convert pandas DataFrames to trajectory
      containers

