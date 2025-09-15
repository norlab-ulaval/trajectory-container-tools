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

The most straightforward way to create a trajectory is by extending `BaseTrajectoryDataclass`:

```python
from dataclasses import dataclass
import numpy as np
from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import BaseTrajectoryDataclass


@dataclass()
class Simple2DTrajectory(BaseTrajectoryDataclass):
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
```terminaloutput
Created trajectory with 50 timesteps
Available dimensions: ('x', 'y', 'timestamps')

          Simple2DTrajectory(
             feature_name: 2D coordinate
             trajectory_len: 50
             transposed: False
             dimensions:
                timesteps_indices: (ndarray) shape (50,) range 0 ⟶ 49
                x: (ndarray) shape (50,) range -0.9998286683840896 ⟶ 0.9991927284190055
                y: (ndarray) shape (50,) range -0.9997651572585272 ⟶ 1.0
                timestamps: (ndarray) shape (50,) range 0.0 ⟶ 4.9
          )
```

### Nested Trajectory Container Structure

For more complex data organization, use `NestedBaseTrajectoryDataclass` for custom implementation or use dataclasses from `primitive_dataclass` module:

```python
from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import NestedBaseTrajectoryDataclass
from trajectory_container_tools.trj_dataclasses.primitive_dataclass import Vector2D


@dataclass()
class CustomPoseContainer(NestedBaseTrajectoryDataclass):
    x: np.ndarray
    y: np.ndarray


@dataclass()
class ComplexTrajectory(BaseTrajectoryDataclass):
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
```terminaloutput
         ComplexTrajectory(
            feature_name: mock
            trajectory_len: 50
            transposed: False
            dimensions:
               timesteps_indices: (ndarray) shape (50,) range 0 ⟶ 49
               timestamps: (ndarray) shape (50,) range 0.0 ⟶ 4.9
               position:          
                   CustomPoseContainer(
                         x: (ndarray) shape (50,) range -0.9998286683840896 ⟶ 0.9991927284190055
                         y: (ndarray) shape (50,) range -0.9997651572585272 ⟶ 1.0
                   )
               velocity:          
                   Vector2D(
                         x: (ndarray) shape (50,) range 1.0 ⟶ 1.0
                         y: (ndarray) shape (50,) range 1.0 ⟶ 1.0
                   )
         )
```

## 2. Factory-Based Creation

TCT provides factory functions for dynamic trajectory dataclass creation:

```python
from trajectory_container_tools.utils.factory import (
    TrjDataClassFeatureSpecification,
    trajectory_dataclass_factory
    )

mock_data = np.random.randn(100, 4)  # 100 timesteps, 4 dimensions

# Define the specification
spec = TrjDataClassFeatureSpecification(
        new_feature_dataclass_type='DynamicTrajectory',
        dimension_names=('x', 'y', 'velocity', 'acceleration')
        )

# Create the dataclass type
DynamicTrajectory = trajectory_dataclass_factory(specification=spec)

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
```terminaloutput
         DynamicTrajectory(
            feature_name: Factory-made-mock-trajectory
            trajectory_len: 100
            transposed: False
            dimensions:
               timesteps_indices: (ndarray) shape (100,) range 0 ⟶ 99
               x: (ndarray) shape (100,) range -2.668217448357629 ⟶ 1.7040474539547208
               y: (ndarray) shape (100,) range -2.899056595784132 ⟶ 2.1778232004028846
               velocity: (ndarray) shape (100,) range -2.988045089298118 ⟶ 2.3266689826139912
               acceleration: (ndarray) shape (100,) range -3.268652367137654 ⟶ 3.207941836262994
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
```terminaloutput
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
# Create batch trajectories (3 trajectories, 20 timesteps each)
batch_size, time_steps = 3, 20
batch_x = np.random.randn(batch_size, time_steps)
batch_y = np.random.randn(batch_size, time_steps)
batch_frame = np.random.randn(batch_size, time_steps, 10)
batch_timestamps = np.tile(np.arange(time_steps) * 0.1, (batch_size, 1))

@dataclass()
class Simple2DCoordinateTrajectory(BaseTrajectoryDataclass):
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
```terminaloutput
Batch trajectory shape: (3, 20)
Number of trajectories: 3
Timesteps per trajectory: 20
Trajectory length: 20

          Simple2DCoordinateTrajectory(
             feature_name: batch 2d coordinate
             trajectory_len: 20
             batch: True
             transposed: False
             dimensions:
                timesteps_indices: (ndarray) shape (20,) range 0 ⟶ 19
                x: (ndarray) shape (3, 20) range -2.4020509174861138 ⟶ 2.5615769128477175
                frame: (ndarray) shape (3, 20, 10) range -2.6836947874667425 ⟶ 2.771730818854544
                y: (ndarray) shape (3, 20) range -2.8252275991392053 ⟶ 1.779143195513082
                timestamps: (ndarray) shape (3, 20) range 0.0 ⟶ 1.9000000000000001
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
```terminaloutput
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

- `AbstractTrajectoryDataclass`: Abstract base providing core functionality
- `BaseTrajectoryDataclass`: Standard flat trajectory container
- `NestedBaseTrajectoryDataclass`: Support for nested data structures

### Factory Functions

- `TrjDataClassFeatureSpecification`: Specification class for dynamic creation
- `trajectory_dataclass_factory()`: Creates dataclass types from specifications
- `parse_to_feature_dataclass()`: Parses feature specifications for dataclass generation

## Usage Recommendations

1. **Start Simple**: Begin with `BaseTrajectoryDataclass` for basic use cases
2. **Use Factories**: Leverage factory functions for dynamic, configurable trajectory types
3. **Validate Early**: Take advantage of built-in validation to catch data inconsistencies
4. **Batch When Appropriate**: Use batch processing for multiple trajectory analysis
5. **Structure Wisely**: Choose between flat and nested structures based on data complexity

For more advanced features including rosbag integration and pandas dataframe extraction, refer to the additional
documentation files in this directory.
