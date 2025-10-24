# Timestamp Utilities Guide

This guide covers the timestamp-related utilities and methods available in Trajectory Container Tools (TCT).

## 📚 Table of Contents

- [Overview](#overview)
- [Timestamps Class](#timestamps-class)
  - [Basic Properties](#basic-properties)
  - [Boundary Methods](#boundary-methods)
  - [Nearest Timestamp Search](#nearest-timestamp-search)
  - [Index Operations](#index-operations)
  - [Error Handling](#error-handling)
- [TrajectoryFeaturesBag Timestamp Methods](#trajectoryfeaturesbag-timestamp-methods)
  - [The `get_timestamps()` method](#the-get_timestamps-method)
  - [The `trajectory_timestamps` and `trajectory_timestamps_limits` properties](#the-trajectory_timestamps-and-trajectory_timestamps_limits-properties)
- [Use Cases and Examples](#use-cases-and-examples)

## Overview

TCT provides comprehensive timestamp handling capabilities for working with trajectory data from ROS bags and other sources. The timestamp utilities enable:

- **Boundary checking** to validate timestamp ranges
- **Nearest timestamp search** for data synchronization
- **Timestamp slicing** to extract data within specific time windows
- **Aggregated timestamp access** across multiple features
- **Robust error handling** for missing or out-of-bound timestamps

## Timestamps Class

The `Timestamps` class is the core component for managing timestamp arrays with validation and search capabilities.

### Basic Properties

```python
from trajectory_container_tools.temporal import Timestamps
import numpy as np

# Create a Timestamps object
stamps = Timestamps(stamps=np.array([1000, 2000, 3000, 4000, 5000]))

# Access basic properties
print(stamps.stamps)        # Array of timestamps
print(stamps.delta_stamps)  # Array of time differences between consecutive stamps
print(stamps.shape)         # Shape of the timestamp array
print(len(stamps))          # Number of timestamps
```

### Boundary Methods

New methods added for checking timestamp boundaries:

```python
# Get minimum and maximum timestamps
min_time = stamps.min()  # Returns 1000
max_time = stamps.max()  # Returns 5000

# Check if timestamps are within bounds
is_valid = stamps.is_timestamps_in_bounds(2500)  # True
is_valid = stamps.is_timestamps_in_bounds(6000)  # False

# Check multiple timestamps
timestamps_to_check = [1500, 2500, 3500]
is_valid = stamps.is_timestamps_in_bounds(timestamps_to_check)  # True

# Out of bounds check
timestamps_out = [500, 6000]
is_valid = stamps.is_timestamps_in_bounds(timestamps_out)  # False
```

**Use Case:** Validate timestamp ranges before performing slicing or indexing operations to prevent errors.

### Nearest Timestamp Search

Find the nearest timestamp in the past or future:

```python
# Find nearest future timestamp
future_stamp = stamps.get_nearest_futur_stamp(2500)  # Returns 3000

# Find nearest past timestamp  
past_stamp = stamps.get_nearest_past_stamp(2500)  # Returns 2000

# Generic nearest stamp with options
nearest = stamps.get_nearest_stamp(
    timestamp=2500,
    future=True,      # Look forward in time
    include=True      # Include exact match if it exists
)
```

**Use Case:** Synchronize data from sensors with different sampling rates by finding the closest timestamp match.

### Index Operations

Get indices for specific timestamps with enhanced error handling:

```python
# Get index for a single timestamp
index = stamps.get_indexes(3000)  # Returns 2

# Get indices for multiple timestamps
indices = stamps.get_indexes([2000, 4000])  # Returns [1, 3]

# Check if timestamp exists
if 3000 in stamps:
  print("Timestamp exists")

# Contains check for multiple timestamps
if [2000, 3000, 4000] in stamps:
  print("All timestamps exist")
```

### Error Handling

TCT provides specific exception types for timestamp errors:

```python
from trajectory_container_tools.temporal import (
    TimestampMissingError,
    TimestampOutOfBoundError,
    TimestampCausalOrderingError
)

try:
    # Attempt to get index for timestamp not in stamps (but in bounds)
    index = stamps.get_indexes(2500)
except TimestampMissingError as e:
    print(f"Timestamp is in bounds but not in stamps: {e}")

try:
    # Attempt to get index for timestamp out of bounds
    index = stamps.get_indexes(10000)
except TimestampOutOfBoundError as e:
    print(f"Timestamp is out of bounds: {e}")

try:
    # Validate causal ordering
    stamps.causal_ordering_sanity_check()
except TimestampCausalOrderingError as e:
    print(f"Timestamps are not monotonically increasing: {e}")
```

**Benefits:**
- **TimestampMissingError**: Raised when timestamp is within bounds but not present in the stamps array
- **TimestampOutOfBoundError**: Raised when timestamp is outside the valid range
- **TimestampCausalOrderingError**: Raised when timestamps violate monotonic ordering

## TrajectoryFeaturesBag Timestamp Methods

For `AbstractTrajectoryStampedFeaturesBag` containers (e.g., extracted from ROS bags with multiple topics), TCT provides methods to work with timestamps across all features.

### The `get_timestamps()` method

Retrieve trajectory data within a specified timestamp range:

```python
import trajectory_container_tools as tct

# Extract trajectory features data from ROS bag
trajectory_features_bag = tct.extractor.from_rosbag(
        rosbag_path=rosbag_path,
        features_config={
                '/odom': tct.dataclasses.NavMsgsOdometry,
                '/cmd':  tct.dataclasses.AckermannMsgsAckermannDriveStamped,
                },
        chunk_on="/cmd",
        )

# Extract data within specific timestamp window
start_time = 1695601812731601521
stop_time = 1695601815000000000

windowed_data = trajectory_features_bag.get_timestamps(
        start=start_time,
        stop=stop_time,
        startpoint=True,  # Include start timestamp
        endpoint=False  # Exclude end timestamp
        )

print(f"Original chunks: {trajectory_features_bag.chunks_total}")
print(f"Windowed chunks: {windowed_data.chunks_total}")
```

**Parameters:**
- `start` (int): Starting timestamp value (in nanoseconds)
- `stop` (int, optional): Stopping timestamp value. If not specified, retrieves a single timestep
- `startpoint` (bool): Include the starting timestamp (default: True)
- `endpoint` (bool): Include the ending timestamp (default: False)

**Returns:** A new trajectory features bag container containing only data within the specified timestamp range.

**Use Cases:**
- Extract specific time windows from long recordings
- Focus analysis on regions of interest
- Remove warm-up or cool-down periods from experiments
- Synchronize with external event timestamps

### The `trajectory_timestamps` and `trajectory_timestamps_limits` properties

#### `trajectory_timestamps`
Access all unique timestamps across all features (excluding bag_timestamps):

```python
# Get sorted unique timestamps from all features
all_timestamps = trajectory_features_bag.trajectory_timestamps

print(f"Total unique timestamps: {len(all_timestamps)}")
```
**Returns:** A sorted numpy array of unique timestamps across all features (excluding `bag_timestamps`).

**Use Cases:**
- Analyze timestamp distribution across all sensors
- Identify gaps in multi-sensor data
- Create unified time axis for visualization

#### `trajectory_timestamps_limits`

Get the first and last timestamps across all features:

```python
ts_limits = trajectory_features_bag.trajectory_timestamps_limits
print(f"First timestamp: {ts_limits.first}")
print(f"Last timestamp: {ts_limits.last}")
print(f"Recording duration: {ts_limits.duration}")

# Use for validation
if limits.first <= my_timestamp and my_timestamp <= limits.last:
    print("Timestamp is within trajectory bounds")
```

**Returns:** A `TrajectoryTimestampsMetadata` named tuple with `first` and `last` timestamps.

**Use Cases:**
- Quick boundary checks without computing all unique timestamps
- Validate external timestamps against trajectory range
- Display recording time span in user interfaces
- Determine if time windows overlap with available data

## Use Cases and Examples

### Example 1: Synchronize Multi-Sensor Data

```python
import trajectory_container_tools as tct

# Extract multi-sensor data
robot_data = tct.extractor.from_rosbag(
        rosbag_path=rosbag_path,
        features_config={
                "/odom": tct.dataclasses.NavMsgsOdometry,
                "/imu":  tct.dataclasses.SensorMsgsImu,
                "/cmd":  tct.dataclasses.AckermannMsgsAckermannDriveStamped,
                },
        chunk_on="/cmd",
        )

# Get timestamps for each sensor
odom_stamps = robot_data.topic_odom.header.timestamps
cmd_stamps = robot_data.topic_cmd.header.timestamps

# Find synchronized timestamps
for cmd_stamp in cmd_stamps.stamps[:10]:  # First 10 commands
  # Find nearest future odometry reading
  if odom_stamps.is_timestamps_in_bounds(cmd_stamp):
    nearest_odom_stamp = odom_stamps.get_nearest_stamp(
            cmd_stamp, future=True, include=False
            )
    print(f"Command at {cmd_stamp} -> Odom at {nearest_odom_stamp}")

```

### Example 2: Extract Data During Specific Event

```python
# Define event time window (e.g., detected obstacle avoidance)
event_start = 1695601815000000000
event_stop = 1695601820000000000

# Extract data during event
event_data = robot_data.get_timestamps(
    start=event_start,
    stop=event_stop,
    startpoint=True,
    endpoint=True
)

# Analyze event-specific behavior
print(f"Event timestamps limits: ", event_data.trajectory_timestamps_limits)
print(f"Commands during event: {event_data.chunks_total}")

# Access sensor data during event
event_odom = event_data.topic_odom
event_imu = event_data.topic_imu
```

### Example 3: Validate Timestamp Coverage

```python
# Check if trajectory covers required time range
required_start = 1695601812000000000
required_stop = 1695601830000000000

limits = robot_data.trajectory_timestamps_limits

if limits.first <= required_start and limits.last >= required_stop:
    print("Trajectory covers required time range")
else:
    print(f"Coverage gap:")
    print(f"  Required: {required_start} to {required_stop}")
    print(f"  Available: {limits.first} to {limits.last}")
```

---

## Documentation

- [Landing page](../README.md#_trajectory-container-tools_)
- [Overview and Core concept](README.md#trajectory-container-tools-documentation)
  - ↳ [Direct Instantiation](./direct_instantiation.md#trajectory-container-tools---direct-instantiation-guide)
  - ↳ [Post-Processing Callbacks Guide](./post_processing_callbacks.md#post-processing-callbacks-in-tct)
  - ↳ [ROS Bag Usage](./rosbag_usage.md#ros-bag-to-tct--usage-guide)
  - ↳ [Pandas DataFrame Usage](./dataframe_usage.md#dataframe-to-tct-usage-guide)
  - ↳ **Timestamp Utilities** (this guide)
- Interactive Jupyter notebook examples:
  - [Direct Instanciation Usage Examples](../notebooks/direct_instanciation_usage_example.ipynb)
  - [ROS Bag Usage Examples](../notebooks/rosbag_usage_example.ipynb)
  - [DataFrame Usage Examples](../notebooks/dataframe_usage_example.ipynb)
