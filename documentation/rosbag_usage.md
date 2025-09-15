# ROS Bag To TCT  Usage Guide

This guide covers how to extract trajectory data from ROS bag files using Trajectory Container Tools (TCT).

## 📚 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Basic Usage](#basic-usage)
- [Supported Message Types](#supported-message-types)
- [Advanced Examples](#advanced-examples)
- [Custom Message Types](#custom-message-types)
- [Troubleshooting](#troubleshooting)

## Overview

The ROS bag converter extracts trajectory data from ROS 2 bag files and converts them into type-safe trajectory containers. This is ideal for:
- Processing recorded robot trajectories from experiments
- Converting ROS data for analysis and visualization
- Integrating ROS workflows with trajectory analysis pipelines

## Prerequisites

### ROS Bag Requirements

- ROS2 distro and `rosbags` packages
    ```bash
    pip install rosbags
    ```
- **ROS 2 bag files** (`.db3` format with `metadata.yaml`)
- Trajectory-related topics (odometry, pose, twist messages)
- Consistent message timestamps


### Supported ROS Distributions

- ROS 2 Galactic, Humble, Iron, Jazzy
- Automatic distribution detection
- Custom typestore support

## Basic Usage

### 1. Import Required Modules

```python
from pathlib import Path
from trajectory_container_tools.rosbag_to_tct import (
    aggregate_multiple_features_from_rosbag,
    extract_single_feature_from_rosbag,
    check_rosbag_path_and_show_available_topics
    )
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import (
    NavMsgsOdometry, RosStampedDataclass
    )
```

### 2. Inspect ROS Bag Contents

```python
# Inspect available topics in the bag
rosbag_path = Path("path/to/your/rosbag")
check_rosbag_path_and_show_available_topics(rosbag_path)
```

**Example Output:**
```
Available topics in rosbag:
  /odom (nav_msgs/msg/Odometry): 1245 messages
  /cmd_vel (geometry_msgs/msg/Twist): 892 messages
  /pose (geometry_msgs/msg/PoseStamped): 1245 messages
  /imu (sensor_msgs/msg/Imu): 6225 messages
```

### 3. Define Feature Configuration

```python
# Define which topics to extract and their types
features_config = {
    '/odometry': NavMsgsOdometry,     # nav_msgs/Odometry
    '/commands': ('CustomCommands', 'steering_angle', 'steering_angle_velocity', 'speed' ) 
}
```

### 4. Extract Trajectory Data

```python
# Extract multiple features from rosbag
trajectory_container = aggregate_multiple_features_from_rosbag(
    rosbag_path=rosbag_path,
    dataset_info="Robot experiment - Outdoor navigation",
    features_config=features_config
)

print(trajectory_container)
```

## Supported Message Types

### Built-in Message Types

#### Navigation Messages

```python
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import NavMsgsOdometry

# nav_msgs/Odometry -> pose + pose covariance + twist + twist covariance data
features_config = {
        '/odometry': NavMsgsOdometry
        }
```

#### Custom Messages
```python
features_config = {
    '/robot_pose': ('PoseStamped', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw')
}
```

## Advanced Examples

### Example 1: Multi-Topic Robot Data

```python
from pathlib import Path
from trajectory_container_tools.rosbag_to_tct import aggregate_multiple_features_from_rosbag
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import NavMsgsOdometry

rosbag_path = Path("experiments/robot_nav_2024_01_15.db3").parent

# Configure multiple ROS topics
features_config = {
        # Navigation data
        '/odometry':          NavMsgsOdometry,
        '/ground_truth_pose': ('GroundTruth', 'pose_pose_position_x', 'pose_pose_position_y',
                               'pose_pose_orientation_z'),

        # Control data  
        '/velocity_commands': ('VelCmd', 'linear_x', 'linear_y', 'angular_z'),

        # Sensor data
        '/imu_readings':      ('IMUData', 'linear_acceleration_x', 'linear_acceleration_y', 'angular_velocity_z'),
        '/lidar_features':    ('LidarFeatures', 'ranges[0]', 'ranges[90]', 'ranges[180]', 'ranges[270]')
        }

# Extract trajectory data
robot_data = aggregate_multiple_features_from_rosbag(
        rosbag_path=rosbag_path,
        dataset_info="Outdoor navigation experiment - 2024-01-15",
        features_config=features_config
        )

# Access extracted data
print(f"Odometry data shape: {robot_data.odometry.x.shape}")
print(f"Velocity commands shape: {robot_data.velocity_commands.linear_x.shape}")
print(f"IMU data shape: {robot_data.imu_readings.linear_acceleration_x.shape}")

# Analyze trajectory
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(robot_data.odometry.x, robot_data.odometry.y, 'b-', label='Odometry')
plt.plot(robot_data.ground_truth_pose.x, robot_data.ground_truth_pose.y, 'r--', label='Ground Truth')
plt.xlabel('X Position (m)')
plt.ylabel('Y Position (m)')
plt.legend()
plt.title('Robot Trajectory Comparison')
plt.axis('equal')
plt.show()
```

### Example 2: Single Topic Extraction

```python
from trajectory_container_tools.rosbag_to_tct import extract_single_feature_from_rosbag

# Extract only odometry data
odom_container = extract_single_feature_from_rosbag(
    rosbag_path=rosbag_path,
    feature_name="odom",  # ROS topic name
    data_container_type=NavMsgsOdometry
)

print(f"Odometry timestamps: {len(odom_container.header.timestamps)}")
print(f"Position data shape: {odom_container.x.shape}")
print(f"Available dimensions: {odom_container.get_dimension_names()}")

# Access pose data
positions = odom_container.x, odom_container.y, odom_container.z
orientations = odom_container.qx, odom_container.qy, odom_container.qz, odom_container.qw

# Access twist data  
linear_vel = odom_container.twist.linear.x, odom_container.twist.linear.y
angular_vel = odom_container.twist.angular.z
```

### Example 3: Time-Sliced Extraction

```python
# Extract only a portion of the rosbag
partial_data = aggregate_multiple_features_from_rosbag(
    rosbag_path=rosbag_path,
    dataset_info="Partial trajectory - middle section",
    features_config=features_config,
    start=1000,  # Start from message index 1000
    stop=5000    # Stop at message index 5000
)

print(f"Partial trajectory length: {partial_data.odometry.trajectory_len}")
```

## Custom Message Types

### Registering Custom Messages

```python
from trajectory_container_tools.utils.ros2_non_native_msg import register_ros2_non_native_msg
from rosbags.typesys import get_types_from_msg, register_types

# Register custom message type
custom_msg_def = """
# custom_msgs/TrajectoryPoint
float64 x
float64 y  
float64 theta
float64 velocity
uint32 timestamp
"""

register_ros2_non_native_msg('custom_msgs/msg/TrajectoryPoint', custom_msg_def)

# Use in feature configuration
features_config = {
    'trajectory_points': ('TrajectoryPoint', 'x', 'y', 'theta', 'velocity')
}
```

### Custom Dataclass for Complex Messages

```python
from dataclasses import dataclass
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import RosStampedDataclass
import numpy as np


@dataclass
class CustomRobotState(RosStampedDataclass):
    """Custom dataclass for complex robot state messages"""
    x: np.ndarray
    y: np.ndarray
    theta: np.ndarray
    velocity: np.ndarray
    battery_level: np.ndarray

    def post_init_feature_callback(self, feature_name: str):
        """Custom processing after feature extraction"""
        if feature_name == 'theta':
            # Wrap angles to [-pi, pi]
            theta = getattr(self, feature_name)
            wrapped_theta = np.arctan2(np.sin(theta), np.cos(theta))
            setattr(self, feature_name, wrapped_theta)


# Use custom dataclass
features_config = {
        'robot_state': CustomRobotState
        }
```


## Troubleshooting

### Common Issues

#### 1. Topic Not Found

```
Error: Topic '/odom' not found in rosbag
```

**Solutions:**
```python
# Check available topics
check_rosbag_path_and_show_available_topics(rosbag_path)

# Common topic name variations
common_odom_topics = ['/odom', '/odometry', '/robot/odom', '/base_link/odom']

# Try different topic names
for topic in common_odom_topics:
    try:
        container = extract_single_feature_from_rosbag(rosbag_path, topic, NavMsgsOdometry)
        print(f"Success with topic: {topic}")
        break
    except:
        continue
```

#### 2. Message Type Mismatch

```
Error: Expected nav_msgs/Odometry but found geometry_msgs/PoseStamped
```

**Solutions:**
```python
# Check actual message type
from rosbags.rosbag2 import Reader

with Reader(rosbag_path) as reader:
    for topic_info in reader.topics.values():
        print(f"Topic: {topic_info.name}, Type: {topic_info.msgtype}")

# Use correct dataclass for the message type
if msg_type == "geometry_msgs/msg/PoseStamped":
    features_config = {'pose': ('PoseData', 'pose_position_x', 'pose_position_y')}
```

#### 3. Memory Issues with Large Bags

```
Error: MemoryError - Unable to allocate array
```

**Solutions:**
```python
# Use chunked processing
chunks = process_large_rosbag(rosbag_path, features_config, chunk_size=5000)

# Or use start/stop parameters
partial_data = aggregate_multiple_features_from_rosbag(
    rosbag_path=rosbag_path,
    features_config=features_config,
    start=0,
    stop=10000  # Process first 10k messages only
)
```

---

## Documentation
- [Landing page](../README.md#_trajectory-container-tools_)
- [Overview and Core concept](README.md#trajectory-container-tools-documentation)
  - ↳ **[DataFrame To TCT Usage Guide](dataframe_usage.md)** - Convert pandas DataFrames to trajectory containers
  - ↳ **[TCT Direct Instantiation Guide](direct_instantiation.md)** - Create trajectory containers directly
- Interactive Jupyter notebook examples:
    - [Direct Instanciation Usage Examples](../notebooks/direct_instanciation_usage_example.ipynb) - Direct trajectory
      container instantiation
    - [ROS Bag Usage Examples](../notebooks/rosbag_usage_example.ipynb) - Extract trajectory data from ROS bags
    - [DataFrame Usage Examples](../notebooks/dataframe_usage_example.ipynb) - Convert pandas DataFrames to trajectory
      containers

