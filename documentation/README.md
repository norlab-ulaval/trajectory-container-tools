# Trajectory Container Tools Documentation

Welcome to the comprehensive documentation for **Trajectory Container Tools (TCT)** - a Python library for managing trajectory-related data across multiple sources and formats.

## 📚 Table of Contents

<!-- TOC -->
* [Trajectory Container Tools Documentation](#trajectory-container-tools-documentation)
  * [📚 Table of Contents](#-table-of-contents)
  * [Overview](#overview)
  * [Usage Guides](#usage-guides)
  * [Core Concepts](#core-concepts)
  * [Data Sources & Converters](#data-sources--converters)
  * [Trajectory Dataclasses](#trajectory-dataclasses)
  * [Utilities](#utilities)
  * [API Reference](#api-reference)
  * [Need Help?](#need-help)
<!-- TOC -->

## Overview

TCT provides a unified interface for working with trajectory data from various sources:
- **Direct instantiation** → Custom trajectory containers
- **ROS bags** → Trajectory containers  
- **Pandas DataFrames** → Trajectory containers

The library is designed for robotics research, autonomous systems, and trajectory analysis workflows.

---

## Interactive [Jupyter notebook examples](../notebooks/):

- **[TCT Dataclass Usage Examples](../notebooks/direct_instanciation_usage_example.ipynb)** - Direct trajectory container instantiation
- **[DataFrame To TCT Usage Examples](../notebooks/dataframe_usage_example.ipynb)** - Convert pandas DataFrames to trajectory containers
- **[ROS Bag To TCT Usage Examples](../notebooks/rosbag_usage_example.ipynb)** - Extract trajectory data from ROS bags


## Usage Guides

### 🔧 [TCT Direct Instantiation Guide](direct_instantiation.md)
Guide for creating trajectory containers directly from data:
- Custom dataclass creation
- Data validation setup
- Advanced customization patterns
- Integration with existing workflows

### 📊 [DataFrame To TCT Usage Guide](dataframe_usage.md)
Complete guide for converting pandas DataFrames to trajectory containers:
- Basic conversion examples
- Custom post-processing
- Multi-feature aggregation
- Data validation and sanity checks

### 🤖 [ROS Bag To TCT  Usage Guide](rosbag_usage.md)  
Comprehensive guide for extracting trajectory data from ROS bags:
- Topic inspection and selection
- Message type handling
- Timestamp management


---


## Core Concepts

### Trajectory Containers

Trajectory containers are type-safe dataclasses that store trajectory data with:
- **Structured access** to trajectory dimensions (x, y, z, roll, pitch, yaw, etc.)
- **Metadata management** (timestamps, dataset information)
- **Data validation** (shape consistency, monotonic timestamps)

### Factory Pattern

TCT uses a factory pattern to dynamically create trajectory containers based on configuration:

```python
features_config = {
    'pose': StatePose2D,
    'velocity': ('CustomVel', 'vx', 'vy', 'vtheta'),
    'commands': CmdStandard
}
```

### Feature Specifications

Features are defined using either:
- **Predefined dataclasses**: `StatePose2D`, `StatePose3D`, `Velocity`, etc.
- **Tuple specifications**: `('ClassName', 'dim1', 'dim2', ...)`

## Data Sources & Converters

### 1. Pandas DataFrame Converter

Convert structured DataFrame data to trajectory containers:

**Key Functions:**
- `aggregate_multiple_features_from_dataframe()` - Multiple features from DataFrame
- `extract_single_feature_from_dataframe()` - Single feature extraction
- `unpack_dataframe_and_show_topic()` - Inspect DataFrame structure

**Requirements:**
- DataFrame with timestep-indexed columns (e.g., `feature_1`, `feature_2`, ...)
- One trajectory per row or single trajectory with timestep columns

### 2. ROS Bag Converter

Extract trajectory data from ROS bag files:

**Key Functions:**
- `aggregate_multiple_features_from_rosbag()` - Multiple ROS topics
- `extract_single_feature_from_rosbag()` - Single topic extraction
- `check_rosbag_path_and_show_available_topics()` - Inspect available topics

**Requirements:**
- ROS2


### 3. Direct Instantiation

Create trajectory containers directly from data arrays:

**Available Dataclasses:**
- `BaseTrajectoryDataclass` - Basic trajectory container
- `NestedBaseTrajectoryDataclass` - Basic trajectory container intended to be nested in a `BaseTrajectoryDataclass` 
- Custom dataclasses inheriting from `AbstractTrajectoryDataclass`

## Trajectory Dataclasses

### Abstract Base Classes

#### `AbstractTrajectoryDataclass`
- Base class for all trajectory containers
- Provides core functionality: indexing, iteration, dimension access
- Abstract methods for customization

#### `AbstractMultifeatureDataclass`
- Container for multiple trajectory features
- Aggregates related trajectory data
- Provides unified access to all features

### Predefined Dataclasses

#### DataFrame Feature Dataclasses
- `StatePose2D` - 2D pose (x, y, yaw)
- `StatePose3D` - 3D pose (x, y, z, roll, pitch, yaw)
- `Velocity` - Linear/angular velocities
- `VelocitySkidSteer` - Skid-steer robot velocities
- `CmdStandard` - Standard command interface
- `CmdSkidSteer` - Skid-steer command interface

#### ROS Bag Feature Dataclasses
- `RosStampedDataclass` - Base for ROS message containers
- `NavMsgsOdometry` - nav_msgs/Odometry messages
- `AckermannMsgsAckermannDriveStamped` - teleop or cmd messages 
- `Tf2MsgsTFMessage` - transform messages
- `SensorMsgsImu` - imu messages

### Specialized Dataclasses
- `ErllTrajectoryDataclass` - ERLL-specific trajectories
- `F110GymTrajectoryDataclass` - F110 racing trajectories
- `MathGymnasiumTrajectoryDataclass` - Math Gymnasium environments


## Utilities

### Data Validation (`utils/data_sanity_checks.py`)
- `dataframe_timestep_indexing_sanity_check()` - Validate DataFrame structure
- Trajectory data consistency checks
- Dimension and shape validation

### Container Validation (`utils/containers_sanity_checks.py`)
- Trajectory container integrity checks
- Multi-feature consistency validation
- Metadata validation

### Factory Functions (`utils/factory.py`)
- `trajectory_dataclass_factory()` - Dynamic dataclass creation
- `TrjDataClassFeatureSpecification` - Feature specification handling
- Configuration validation

### General Utilities (`utils/general.py`)
- Class name extraction and conversion
- Progress bar setup
- Common helper functions

### ROS Utilities (`utils/ros2_utils.py`)
- ROS 2 type system integration
- Message type registration
- Typestore management

### Plotting Tools (`utils/plot.py`)
- Trajectory visualization utilities
- Multi-feature plotting
- Research-ready plot formatting

### Optimization Tools (`utils/optimization.py`)
- Performance optimization utilities
- Memory management helpers

## API Reference

### Main Modules

#### `trajectory_container_tools.dataframe_to_tct`
```python
def aggregate_multiple_features_from_dataframe(
    dataset_frame: pd.DataFrame,
    dataset_info: str,
    features_config: Dict[str, Union[type[BaseDataframeFeatureDataclass], Tuple[str, ...]]]
) -> AbstractMultifeatureDataclass

def extract_single_feature_from_dataframe(
    dataset: pd.DataFrame,
    feature_name: str,
    data_container_type: type[BaseDataframeFeatureDataclass]
) -> BaseDataframeFeatureDataclass
```

#### `trajectory_container_tools.rosbag_to_tct`
```python
def aggregate_multiple_features_from_rosbag(
    rosbag_path: Path,
    dataset_info: Optional[str],
    features_config: Dict[str, Union[type[RosStampedDataclass], Tuple[str, ...]]],
    start: Optional[int] = None,
    stop: Optional[int] = None,
    typestore: Optional[Typestore] = None
) -> AbstractMultifeatureDataclass

def extract_single_feature_from_rosbag(
    rosbag_path: Path,
    feature_name: str,
    data_container_type: type[RosStampedDataclass],
    start: Optional[int] = None,
    stop: Optional[int] = None,
    typestore: Optional[Typestore] = None
) -> RosStampedDataclass
```

---

## Need Help?

- 💻 Run the [Jupyter notebook examples](../notebooks/) for hands-on learning in the `notebooks/` directory
- 🐛 Report issues on [GitHub Issues](https://github.com/norlab-ulaval/trajectory-container-tools/issues)

---
